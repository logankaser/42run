#!/usr/bin/env python3
"""main."""

import ctypes
import numpy as np
import random
from pyrr import matrix44
from collections import deque
from window import Window, glfw
from entity import Entity, Drawable, DrawableEntity
from context import Context
from camera import Camera
from skybox import Skybox
from text import Text
from typing import List
import math

lanes = [3, 0, -3]
speed = 35.0


def ease_in_linear(t):
    """Linear easing."""
    return t


def ease_in_cubic(t):
    """Cubic easing."""
    return t * t * t


def ease_out_cubic(t):
    """Cubic easing."""
    t = 1 - t
    return 1 - (t * t * t)


def ease_in_out_cubic(t):
    """Cubic easing."""
    if t < 0.5:
        return ease_in_cubic(t * 2.0) / 2.0
    return 1 - ease_in_cubic((1 - t) * 2.0) / 2.0


class GameCamera(Camera):
    """Game camera."""

    def __init__(self, pos=[0, 6, -12], target=[0, 5, 0]):
        """Create a 42Run Camera."""
        super().__init__(pos=pos, target=target)
        self.wobble_timer = 0.0
        self.y = self.pos[1]

    def wobble(self, dt):
        """Wobble camera around the target."""
        self.wobble_timer += dt
        self.pos[1] = self.y + math.sin(self.wobble_timer * 0.5) * 0.1 - 0.1
        self.regen_view = True

    def set_target_y(self, y):
        """Set the target y value."""
        self.target[1] = y
        self.regen_view = True


class Player(DrawableEntity):
    """Player."""

    def __init__(self, pos=[0, 0, 0], rot=[0, 0, 0]):
        """Create a player."""
        super().__init__("marvin", pos, rot)
        self.velocity = np.array([0, 0, 0], dtype=np.float32)
        self.lane = 1
        self.target_lane = 1
        self.jump = False
        self.switch_duration = 0.33
        self.switch_timer = 0.0
        self.jump_timer = 0.0
        self.jump_duration = 0.66
        self.hp = 30

    def update(self, dt, ctx, win, hits):
        """Update."""
        if self.switch_timer < self.switch_duration:
            start_x = lanes[self.lane]
            change_x = lanes[self.target_lane] - start_x
            self.pos[0] = start_x + change_x * ease_in_linear(
                self.switch_timer / self.switch_duration
            )
        else:
            self.lane = self.target_lane
            self.pos[0] = lanes[self.lane]

        self.switch_timer += dt
        self.jump_timer += dt

        if self.jump_timer > self.jump_duration:
            self.jump = False

        if self.jump:
            self.pos[1] = 3.5 * ease_out_cubic(self.jump_timer / self.jump_duration)
        else:
            self.pos[1] = self.pos[1] * 0.8

        if hits[self.lane] > self.jump:
            self.hp -= 1

        if self.hp <= 0:
            self.alive = False

        if not self.jump:
            if win.key(glfw.KEY_A) and self.lane > 0 and self.lane == self.target_lane:
                self.target_lane = self.lane - 1
                self.switch_timer = 0.0
            elif (
                win.key(glfw.KEY_D) and self.lane < 2 and self.lane == self.target_lane
            ):
                self.target_lane = self.lane + 1
                self.switch_timer = 0.0
            elif win.key(glfw.KEY_SPACE):
                self.jump = True
                self.jump_timer = 0.0


def gen_hitogram():
    hitogram = np.random.randint(0, 3, size=3)
    if sum(hitogram) == 6:
        hitogram[np.random.randint(0, 3)] -= np.random.randint(1, 3)
    elif sum(hitogram) == 0:
        hitogram[np.random.randint(0, 3)] = np.random.randint(1, 3)
    return hitogram


class Obstacle(Entity):
    """Obstacle."""

    def __init__(self, pos):
        """Create a player."""
        super().__init__(pos=pos)
        self.drawables = []
        self.offsets = []
        self.hitogram = gen_hitogram()
        for i, h in enumerate(self.hitogram):
            while h:
                if h == 2:
                    self.drawables.append(Drawable("mac"))
                else:
                    self.drawables.append(Drawable("table"))
                self.offsets.append((lanes[i], (h - 1) * 2))
                h -= 1
        self.pos[1] = 1
        self.rot_vel = np.random.rand(3) * random.random()

    def update(self, dt, ctx, win):
        """Update."""
        if self.pos[2] < -30:
            self.alive = False
            return
        self.pos[2] -= speed * dt
        self.rot += self.rot_vel * dt
        for d, (off_x, off_y) in zip(self.drawables, self.offsets):
            np.copyto(d.pos, self.pos)
            d.pos[0] += off_x
            d.pos[1] += off_y
            # np.copyto(d.rot, self.rot)

    def draw(self, ctx, camera):
        for d in self.drawables:
            d.draw(ctx, camera)


def game(window: Window, ctx: Context):
    """Run game."""
    # load assets in the default vao
    ctx.use_vao("default")
    entities = []
    textbox = Text(ctx, [-0.25, 7, -9], "<score>")
    cam = GameCamera()
    player = Player()
    skybox = Skybox(ctx, "assets/skybox")

    # mainloop
    old_time = glfw.get_time()
    spawn_timer = 0.0
    spawn_delay = 4.0
    while window and player:
        hits = [0, 0, 0]
        new_time = glfw.get_time()
        dt = new_time - old_time
        cam.wobble(dt)
        cam.set_target_y(player.pos[1] * 0.2 + 5)
        skybox.rot[2] += dt * 0.01

        spawn_timer += dt
        if spawn_timer > spawn_delay:
            # Spawn new Obstacle
            spawn_timer = 0.0
            entities.append(Obstacle([0, 0, 200]))

        if spawn_delay > 0.8:
            spawn_delay -= dt * 0.1

        for e in entities:
            e.update(dt, ctx, window)
            if e and abs(e.pos[2] - player.pos[2]) < 1.0:
                hits = list(map(max, zip(hits, e.hitogram)))
        entities = [e for e in entities if e]
        player.update(dt, ctx, window, hits)
        old_time = new_time

        # Render
        ctx.clear()
        ctx.use_vao("default")
        for entity in entities:
            entity.draw(ctx, cam)
        player.draw(ctx, cam)
        skybox.draw(ctx, cam)
        textbox.draw(ctx, cam)
        textbox.update(
            str(new_time)[: str(new_time).find(".") + 2] + f"\n hp{player.hp}"
        )
        window.swap_buffers()
    ctx.clear()
    return str(new_time)[: str(new_time).find(".") + 2]


def end_screen(window: Window, ctx: Context, score: str):
    cam = Camera(pos=[0, 6, -12], target=[0, 5, 0])
    ctx.load_models(["plane"])
    ctx.use_vao("default")
    now = glfw.get_time()
    textbox = Text(ctx, [-0.25, 6, -9], "<msg>")
    while glfw.get_time() < now + 4.0:
        ctx.clear()
        if glfw.get_time() < now + 2.0:
            textbox.update(f"Game Over", color=(255, 0, 0, 255))
        else:
            textbox.update(f"Score: {score}")
        textbox.draw(ctx, cam)
        window.swap_buffers()
    window.close()


if __name__ == "__main__":
    """main."""
    window = Window(1024, 1024)

    ctx = Context()
    ctx.create_program("42run")
    ctx.create_program("text")
    ctx.load_models(["marvin", "skybox", "table", "plane", "mac"])
    score = game(window, ctx)
    if window:
        end_screen(window, ctx, score)
