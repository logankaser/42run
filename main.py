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
from text import Text
from typing import List
import math


def ease_linear(t, start, end):
    """Linear easing."""
    diff = end - start
    return start + (diff * t)


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


class Player(Entity):
    """Player."""

    def __init__(self, pos=[0, 0, 0], rot=[0, 0, 0]):
        """Create a player."""
        super().__init__("ship", pos, rot)
        self.velocity = np.array([0, 0, 0], dtype=np.float32)
        self.lane = 1
        self.lanes = [-3, 0, 3]
        self.target_lane = 1
        self.switch_duration = 0.33
        self.switch_timer = 0.0

    def update(self, dt, ctx, win, hits):
        """Update."""
        if self.switch_timer < self.switch_duration:
            start_x = self.lanes[self.lane]
            target_x = self.lanes[self.target_lane]
            self.pos[0] = ease_linear(
                self.switch_timer / self.switch_duration, start_x, target_x
            )
        else:
            self.lane = self.target_lane
            self.pos[0] = self.lanes[self.lane]

        self.switch_timer += dt
        if hits[self.lane] > 0:
            print("hit" + str(hash(dt)))

        if win.key(glfw.KEY_A) and self.lane < 2 and self.lane == self.target_lane:
            self.target_lane = self.lane + 1
            self.switch_timer = 0.0
        if win.key(glfw.KEY_D) and self.lane > 0 and self.lane == self.target_lane:
            self.target_lane = self.lane - 1
            self.switch_timer = 0.0


class Obstacle(Entity):
    """Obstacle."""

    def __init__(self, pos, hitogram: List[int] = [0, 0, 0], speed=4):
        """Create a player."""
        super().__init__("asteroid", pos, [0, 0, -math.pi])
        self.hitogram = hitogram
        self.pos[1] = 1
        self.rot_vel = np.random.rand(3) * random.random()
        self.speed = speed

    def update(self, dt, ctx, win):
        """Update."""
        if self.pos[2] < -30:
            self.alive = False
            return
        self.pos[2] -= self.speed * dt
        self.rot += self.rot_vel * dt


def game(window, ctx):
    """Run game."""
    # load assets into the default vao
    ctx.use_vao("default")
    entities = [
        Obstacle([0, 0, 60], [0, 1, 0]),
        Obstacle([0, 0, 50], [0, 1, 0]),
        Obstacle([0, 0, 40], [0, 1, 0]),
        Obstacle([0, 0, 35], [0, 1, 0]),
        Obstacle([0, 0, 20], [0, 1, 0]),
    ]

    distance = Text(ctx, [-0.3, 7, -9], "<score>")
    cam = GameCamera()
    player = Player()
    skybox = Skybox(ctx, "assets/skybox")

    # mainloop
    old_time = glfw.get_time()
    distance_timer = 0.0
    while window:
        hits = [0, 0, 0]
        new_time = glfw.get_time()
        dt = new_time - old_time
        cam.wobble(dt)
        cam.set_target_y(player.pos[1] + 5)
        for e in entities:
            e.update(dt, ctx, window)
            if e and e.pos[2] < 1 and e.pos[2] > 0:
                hits = list(map(max, zip(hits, entity.hitogram)))
        entities = [e for e in entities if e]
        player.update(dt, ctx, window, hits)
        old_time = new_time

        # Render
        ctx.clear()
        ctx.use_vao("default")
        for entity in entities:
            entity.draw(ctx, cam)
        player.draw(ctx, cam)
        # print(hits)
        skybox.draw(ctx, cam)
        distance.draw(ctx, cam)
        distance_timer += dt
        if distance_timer > 0.1:
            distance.update(str(new_time)[: str(new_time).find(".") + 2])
            distance_timer = 0.0
        window.swap_buffers()
    window.close()


if __name__ == "__main__":
    """main."""
    window = Window(1024, 1024)

    ctx = Context()
    ctx.create_program("42run")
    ctx.create_program("text")
    ctx.load_models(["ship", "skybox", "asteroid", "plane"])
    game(window, ctx)
