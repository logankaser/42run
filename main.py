#!/usr/bin/env python3
"""main."""

import ctypes
import numpy as np
from pyrr import matrix44
from collections import deque
from window import Window, glfw
from entity import Entity
from context import Context
from math import pi
import OpenGL
OpenGL.ERROR_CHECKING = False
from OpenGL.GL import *


class Player(Entity):
    """Player."""

    def __init__(self):
        """Create a player."""
        super().__init__("42", [0, 0, 0], [0, 0, 0])
        self.velocity = np.array([0, 0, 0], dtype=np.float32)

    def update(self, ctx, win):
        """Update."""
        # Jump, meat to be "floatyish"
        if win.key(glfw.KEY_SPACE) and self.pos[1] <= 0.0 and self.velocity[1] <= 0.02:
            self.velocity[1] += 0.5
        elif self.pos[1] <= 0.0:
            self.velocity[1] = 0.0
        elif self.velocity[1] >= -0.15:
            self.velocity[1] -= 0.02
        self.pos[1] += self.velocity[1]


class Obstacle(Entity):
    """Obstacle."""

    def __init__(self, pos):
        """Create a player."""
        super().__init__("monkey", pos, [0, 0, -pi])

    def update(self, ctx, win):
        """Update."""
        for c in self.collisions:
            exit("YOU DIED")
        self.pos[2] -= 0.1
        if self.pos[2] < -1:
            self.pos[2] += 60


def render(ctx):
    """Render a frame."""
    ctx.refresh()

    while len(ctx.draw_queue):
        model_name, transform = ctx.draw_queue.pop()
        m = ctx.models[model_name]
        ctx.update_uniforms(transform)
        glBindTexture(GL_TEXTURE_2D, m["texture"])
        glDrawArrays(GL_TRIANGLES, m["offset"], m["indices"])
    err = glGetError()
    if (err != GL_NO_ERROR):
        exit("GLERROR: ", gluErrorString(err))


def update(player, entities, ctx, win):
    """Game update loop."""
    player_radius = ctx.models[player.model]["radius"]
    if player.pos[1] < 0.5:
        for e in entities:
            e.collisions.clear()
            if e.pos[2] - ctx.models[e.model]["radius"] <= player.pos[2] + player_radius and e.pos[2] + ctx.models[e.model]["radius"] >= player.pos[2] - player_radius:
                e.collisions.append(player)

    player.update(ctx, win)
    player.draw(ctx)
    for e in entities:
        e.update(ctx, win)
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
    ctx = Context(V, 60, window)
    ctx.load_shaders("assets/42run.frag", "assets/42run.vert")
    ctx.load_models(["monkey", "42"])

    entities = [
        Obstacle([0, 0, 40]),
        Obstacle([0, 0, 20]),
        Obstacle([0, 0, 60]),
    ]
    player = Player()
    # mainloop

    while window:
        update(player, entities, ctx, window)
        render(ctx)
        window.swap_buffers()
    window.close()


if __name__ == "__main__":
    main()
