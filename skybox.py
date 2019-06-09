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
        ctx.create_program("skybox")
        self.rot = np.array([0.0, 0.0, 0.0], dtype=np.float32)

    def __del__(self):
        glDeleteTextures(self.skybox_texture_id)

    def draw(self, ctx, camera):
        """Draw skybox."""
        ctx.use_program("skybox")

        old_cull_face_mode = glGetIntegerv(GL_CULL_FACE_MODE)
        old_depth_func_mode = glGetIntegerv(GL_DEPTH_FUNC)

        glCullFace(GL_FRONT)
        glDepthFunc(GL_LEQUAL)

        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_CUBE_MAP, self.skybox_texture_id)
        uniforms = camera.gen_uniforms(
            matrix44.multiply(
                matrix44.create_from_eulers(self.rot, dtype=np.float32),
                matrix44.create_from_translation(camera.pos, dtype=np.float32),
            )
        )
        ctx.update_uniforms(uniforms)
        model = ctx.get_model("skybox")
        glDrawArrays(GL_TRIANGLES, model.offset, model.indices)
        glCullFace(old_cull_face_mode)
        glDepthFunc(old_depth_func_mode)
