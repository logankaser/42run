#!/usr/bin/env python3
"""main."""

import ctypes
import numpy as np
from pyrr import matrix44
from collections import deque
from window import Window
from entity import Entity
from render_context import RenderContext
from math import pi
import OpenGL
OpenGL.ERROR_CHECKING = False
from OpenGL.GL import *


class Player(Entity):
    """Class represent the player."""

    def __init__(self):
        """Create a player."""
        super().__init__("42", [0, 0, 0], [0, 0, 0])


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


def update(entities, ctx):
    """Game update loop."""
    for e in entities:
        if e.model == "monkey":
            e.pos[2] -= 0.1
            if e.pos[2] <= 0:
                e.pos[2] = 60
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
        Entity("monkey", [0, 0, 40], [0, 0, 0]),
        Entity("monkey", [0, 0, 20], [0, 0, 0]),
        Entity("monkey", [0, 0, 60], [0, 0, 0]),
        Player()
    ]
    # mainloop

    while window:
        update(entities, ctx)
        render(ctx)
        window.swap_buffers()
    window.close()


if __name__ == "__main__":
    main()
