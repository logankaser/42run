#!/usr/bin/env python3
"""main."""

import ctypes
import numpy as np
import random
from pyrr import matrix44
from collections import deque
from window import Window, glfw
from entity import Entity
from context import Context
from camera import Camera
from skybox import Skybox
from math import pi, sin
import OpenGL
OpenGL.ERROR_CHECKING = False
from OpenGL.GL import *


def ease_linear(t, start, end):
    """Linear easing."""
    diff = end - start
    return start + (diff * t)


def run_timer(dt, time):
    """Run a timer."""
    if time - dt > 0:
        time -= dt
    else:
        time = 0.0
    return time


class Player(Entity):
    """Player."""

    def __init__(self):
        """Create a player."""
        super().__init__("42", [0, 0, 0], [0, 0, 0])
        self.velocity = np.array([0, 0, 0], dtype=np.float32)
        self.lane = 1
        self.target_lane = 1
        self.switch_duration = 0.33
        self.switch_timer = 0.0

    def update(self, dt, ctx, win):
        """Update."""
        if win.key(glfw.KEY_SPACE) and self.pos[1] <= 0.0 and \
                self.velocity[1] <= 0.02:
            self.velocity[1] += 0.5
        elif self.pos[1] <= 0.0:
            self.velocity[1] = 0.0
        elif self.velocity[1] >= -0.15:
            self.velocity[1] -= 0.02
        self.pos += self.velocity

        if self.switch_timer > 0.0:
            lanes = [-2, 0, 2]
            start_x = lanes[self.lane]
            target_x = lanes[self.target_lane]
            self.pos[0] = ease_linear(
                1.0 - self.switch_timer / self.switch_duration,
                start_x,
                target_x
            )
        else:
            self.lane = self.target_lane
            self.pos[0] = [-2, 0, 2][self.lane]

        self.switch_timer = run_timer(dt, self.switch_timer)

        if win.key(glfw.KEY_A) and self.lane < 2 and \
                self.lane == self.target_lane:
            self.target_lane = self.lane + 1
            self.switch_timer = self.switch_duration
        if win.key(glfw.KEY_D) and self.lane > 0 and \
                self.lane == self.target_lane:
            self.target_lane = self.lane - 1
            self.switch_timer = self.switch_duration


class Obstacle(Entity):
    """Obstacle."""

    def __init__(self, pos):
        """Create a player."""
        super().__init__("monkey", pos, [0, 0, -pi])
        self.lane = random.choice([0, 1, 2])

    def update(self, dt, ctx, win):
        """Update."""
        for c in self.collisions:
            exit("YOU DIED")
        self.pos[2] -= 10 * dt
        if self.pos[2] < -4:
            self.pos[2] += 104
        self.pos[0] = [-2, 0, 2][self.lane]
        self.pos[1] = sin(self.pos[2] * 0.5) * 0.3


def render(camera, skybox, ctx):
    """Render a frame."""
    ctx.clear()
    ctx.use_program("42run")
    while len(ctx.draw_queue):
        model_name, model_transform = ctx.draw_queue.pop()
        camera_uniforms = camera.gen_uniforms(model_transform)
        m = ctx.models[model_name]
        ctx.update_uniforms(camera_uniforms)
        glBindTexture(GL_TEXTURE_2D, m["texture"])
        glActiveTexture(GL_TEXTURE0)
        glDrawArrays(GL_TRIANGLES, m["offset"], m["indices"])
    err = glGetError()
    if (err != GL_NO_ERROR):
        exit("GLERROR: ", gluErrorString(err))
    skybox.draw(ctx, camera)


def update(dt, player, entities, ctx, win):
    """Game update loop."""
    player_radius = ctx.models[player.model]["radius"]
    if player.pos[1] < 0.2:
        for e in [x for x in entities if x.lane == player.lane]:
            e.collisions.clear()
            if e.pos[2] - ctx.models[e.model]["radius"] <= player.pos[2] \
                + player_radius and e.pos[2] + ctx.models[e.model]["radius"] \
                    >= player.pos[2] - player_radius:
                e.collisions.append(player)

    player.update(dt, ctx, win)
    player.draw(ctx)
    for e in entities:
        e.update(dt, ctx, win)
        e.draw(ctx)


def main():
    """main."""
    window = Window(1024, 1024)

    V = matrix44.create_look_at(
        np.array([0, 3, -6]),  # position
        np.array([0, 2, 6]),  # target
        np.array([0, 1, 0])  # up vector
    )
    P = matrix44.create_perspective_projection(60, 1, 0.1, 100)
    ctx = Context()
    ctx.load_program("42run")
    ctx.use_program("42run")
    ctx.load_models(["monkey", "42", "skybox"])

    entities = [
        Obstacle([0, 0, 40]),
        Obstacle([0, 0, 20]),
        Obstacle([0, 0, 60]),
        Obstacle([0, 0, 80]),
        Obstacle([0, 0, 100]),
    ]
    player = Player()

    cam = Camera(V, 1)
    skybox = Skybox(ctx, "assets/skybox")
    # mainloop
    old_time = glfw.get_time()
    while window:
        new_time = glfw.get_time()
        dt = new_time - old_time
        update(dt, player, entities, ctx, window)
        old_time = new_time
        render(cam, skybox, ctx)
        window.swap_buffers()
    window.close()


if __name__ == "__main__":
    main()
