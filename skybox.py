"""Entity."""

from pyrr import matrix44
import numpy as np
import OpenGL
from math import pi
OpenGL.ERROR_CHECKING = False
from OpenGL.GL import *


class Skybox:
    """Game Entity."""

    def __init__(self, ctx, path):
        """Create entity."""
        self.skybox_texture_id = ctx.load_texture_cubemap(path)
        ctx.load_program("skybox")

    def draw(self, ctx, camera):
        """Draw skybox."""
        ctx.use_program("skybox")

        old_cull_face_mode = glGetIntegerv(GL_CULL_FACE_MODE)
        old_depth_func_mode = glGetIntegerv(GL_DEPTH_FUNC)

        glCullFace(GL_FRONT)
        glDepthFunc(GL_LEQUAL)

        glBindTexture(GL_TEXTURE_CUBE_MAP, self.skybox_texture_id)
        uniforms = camera.gen_uniforms(
            matrix44.create_from_translation(camera.pos, dtype=np.float32)
        )
        ctx.update_uniforms(uniforms)
        m = ctx.models["skybox"]
        glActiveTexture(GL_TEXTURE0)
        glDrawArrays(
            GL_TRIANGLES, m["offset"], m["indices"]
        )
        glCullFace(old_cull_face_mode)
        glDepthFunc(old_depth_func_mode)
