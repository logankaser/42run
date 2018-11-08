#!/usr/bin/env python3
"""main."""

import ctypes
import numpy as np
from pyrr import matrix44
from collections import deque
from window import Window, glfw
from entity import Entity
from render_context import RenderContext
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

    def update(self, win):
        """Update."""
        if win.key(glfw.KEY_SPACE):
            self.velocity[1] += 0.1
        elif self.pos[1] <= 0.0:
            self.velocity[1] = 0.0
        else:
            self.velocity[1] -= 0.1
        self.pos[1] += self.velocity[1]


class Obstacle(Entity):
    """Obstacle."""

    def __init__(self, pos):
        """Create a player."""
        super().__init__("monkey", pos, [0, 0, 0])

    def update(self, win):
        """Update."""
        self.pos[2] -= 0.1


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


def update(entities, ctx, win):
    """Game update loop."""
    for e in entities:
        e.update(win)
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
    ctx = RenderContext(V, 60, window)
    ctx.load_shaders("assets/42run.frag", "assets/42run.vert")
    ctx.load_models(["monkey", "42"])

    entities = [
        Obstacle([0, 0, 40]),
        Obstacle([0, 0, 20]),
        Obstacle([0, 0, 60]),
        Player()
    ]
    # mainloop

    while window:
        update(entities, ctx, window)
        render(ctx)
        window.swap_buffers()
    window.close()


if __name__ == "__main__":
    main()
