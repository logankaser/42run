"""Entity."""

from pyrr import matrix44
import numpy as np
import OpenGL
from typing import List

OpenGL.ERROR_CHECKING = False
from OpenGL.GL import *


class Entity:
    """Game Entity."""

    def __init__(self, model, position, rotation):
        """Create entity."""
        self.model = model
        self.pos = np.array(position, dtype=np.float32)
        self.rot = np.array(rotation, dtype=np.float32)
        self.transform = None
        self.alive = True
        self.hitogram = [0, 0, 0]

    def _update_transform(self):
        self.transform = matrix44.multiply(
            matrix44.create_from_eulers(self.rot, dtype=np.float32),
            matrix44.create_from_translation(self.pos, dtype=np.float32),
        )

    def draw(self, ctx, camera):
        """Draw da thing."""
        ctx.use_program("42run")
        self._update_transform()
        camera_uniforms = camera.gen_uniforms(self.transform)
        model = ctx.get_model(self.model)
        ctx.update_uniforms(camera_uniforms)
        glBindTexture(GL_TEXTURE_2D, model.texture)
        glActiveTexture(GL_TEXTURE0)
        glDrawArrays(GL_TRIANGLES, model.offset, model.indices)
        err = glGetError()
        if err != GL_NO_ERROR:
            exit("GLERROR: ", gluErrorString(err))

    def update(self, dt, ctx, win):
        """Update."""
        pass

    def __bool__(self) -> bool:
        """Is alive?."""
        return self.alive
