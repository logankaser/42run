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
from math import pi, sin, sqrt
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
        super().__init__("ship", [0, 0, 0], [0, 0, 0])
        self.flames = Entity("flames", [0, 0, 0], [0, 0, 0])
        self.velocity = np.array([0, 0, 0], dtype=np.float32)
        self.lane = 1
        self.target_lane = 1
        self.switch_duration = 0.33
        self.switch_timer = 0.0
        self.rot_timer = 0.0

    def update(self, dt, ctx, win):
        """Update."""
        self.rot_timer += dt
        if self.rot_timer >= 0.1:
            self.flames.rot[2] = random.random() * pi * 2
            self.rot_timer = 0.0
        self.rot[2] += 1.0 * dt

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
        self.flames.pos = self.pos

    def draw(self, ctx):
        """Add entity to the global draw queue."""
        super().draw(ctx)
        self.flames.draw(ctx)


class Obstacle(Entity):
    """Obstacle."""

    def __init__(self, pos):
        """Create a player."""
        super().__init__("asteroid", pos, [0, 0, -pi])
        self.lane = random.choice([0, 1, 2])
        self.pos[1] = random.choice([0, 5, 10])

    def update(self, dt, ctx, win):
        """Update."""
        for c in self.collisions:
            exit("YOU DIED")
        self.pos[2] -= 1 * dt
        if self.pos[2] < -4:
            self.pos[2] += 10
        if self.pos[1] < -20:
            self.pos[1] = 20
        self.pos[0] = [-2, 0, 2][self.lane]
        self.pos[1] -= 4 * dt
        self.rot[2] += 1 * dt
        self.rot[1] += 1 * dt


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


def update(dt, camera, player, entities, ctx, win):
    """Game update loop."""
    """
    player_radius = ctx.models[player.model]["radius"]
    if player.pos[1] < 0.2:
        for e in [x for x in entities if x.lane == player.lane]:
            e.collisions.clear()
            if e.pos[2] - ctx.models[e.model]["radius"] <= player.pos[2] \
                + player_radius and e.pos[2] + ctx.models[e.model]["radius"] \
                    >= player.pos[2] - player_radius:
                e.collisions.append(player)
    """

    player.update(dt, ctx, win)
    player.draw(ctx)
    for e in entities:
        e.update(dt, ctx, win)
        e.draw(ctx)


if __name__ == "__main__":
    """main."""
    window = Window(1024, 1024)

    ctx = Context()
    ctx.load_program("42run")
    ctx.load_models(["ship", "flames", "skybox", "asteroid"])

    entities = [
        Obstacle([0, 0, 12]),
        Obstacle([0, 0, 10]),
        Obstacle([0, 0, 13]),
        Obstacle([0, 0, 16]),
        Obstacle([0, 0, 14])
    ]

    cam = Camera(
        pos=[0, -1, -20],
        target=[0, 0, 6]
    )
    player = Player()

    skybox = Skybox(ctx, "assets/skybox")

    # mainloop
    old_time = glfw.get_time()
    while window:
        new_time = glfw.get_time()
        dt = new_time - old_time
        update(dt, cam, player, entities, ctx, window)
        old_time = new_time
        render(cam, skybox, ctx)
        window.swap_buffers()
    window.close()
