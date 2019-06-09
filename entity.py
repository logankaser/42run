"""Entity."""

from pyrr import matrix44
import numpy as np
import OpenGL
from typing import List

OpenGL.ERROR_CHECKING = False
from OpenGL.GL import *


class Drawable:
    """Drawable."""

    def __init__(self, model, pos=[0, 0, 0], rot=[0, 0, 0]):
        """Create entity."""
        self.model = model
        self.pos = np.array(pos, dtype=np.float32)
        self.rot = np.array(rot, dtype=np.float32)
        self.transform = None
        self.alive = True

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
        # err = glGetError()
        # if err != GL_NO_ERROR:
        #    exit("GLERROR: ", gluErrorString(err))


class DrawableEntity(Drawable):
    """Game Entity."""

    def update(self, dt, ctx, win):
        """Update."""
        pass

    def __bool__(self) -> bool:
        """Is alive?."""
        return self.alive


class Entity:
    """Game Entity without builtin drawable."""

    def __init__(self, pos=[0, 0, 0], rot=[0, 0, 0]):
        """Create entity."""
        self.pos = np.array(pos, dtype=np.float32)
        self.rot = np.array(rot, dtype=np.float32)
        self.alive = True

    def update(self, dt, ctx, win):
        """Update."""
        pass

    def __bool__(self) -> bool:
        """Is alive?."""
        return self.alive
