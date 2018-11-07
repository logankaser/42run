"""Render context module."""

import ctypes
import numpy as np
from PIL import Image
from pyrr import matrix44
from pywavefront import Wavefront
from collections import deque
import OpenGL
OpenGL.ERROR_CHECKING = False
from OpenGL.GL import *
from OpenGL.GL import shaders
from OpenGL.raw.GL.EXT.texture_filter_anisotropic import *


class RenderContext:
    """OpenGL ."""

    def __init__(self, V, fov, win):
        """Create render context."""
        self.window = win
        self.V = V
        self.fov = fov
        self.P = matrix44.create_perspective_projection(
            fov, win.width / win.height, 0.1, 100)
        self.program_id = None
        self.uniforms = {}
        self.draw_queue = deque()
        self.models = {}
        self.textures = {}
        # create vao
        vao = glGenVertexArrays(1)
        glBindVertexArray(vao)
        glClearColor(0.3, 0.3, 0.3, 1)
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)

    def refresh(self):
        """Clear buffer."""
        self.P = matrix44.create_perspective_projection(
            self.fov, self.window.width / self.window.height, 0.1, 100)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    def load_shaders(self, frag, vert):
        """Load shaders."""
        try:
            with open(frag, "r") as src:
                frag_src = src.read()
            with open(vert, "r") as src:
                vert_src = src.read()
        except Exception as e:
            exit("Error reading shader from disk")
        # compile shaders and program
        try:
            frag_shader = shaders.compileShader(frag_src, GL_FRAGMENT_SHADER)
            vert_shader = shaders.compileShader(vert_src, GL_VERTEX_SHADER)
            program_id = shaders.compileProgram(vert_shader, frag_shader)
        except RuntimeError as e:
            print(str(e).replace("\\n", "\n").replace("\\", ""))
            exit("Shaders failed to compile")
        self.program_id = program_id
        glUseProgram(self.program_id)
        self.uniforms["MVP"] = glGetUniformLocation(self.program_id, "MVP")
        self.uniforms["MV"] = glGetUniformLocation(self.program_id, "MV")
        self.uniforms["M"] = glGetUniformLocation(self.program_id, "M")
        self.uniforms["V"] = glGetUniformLocation(self.program_id, "V")

    def update_uniforms(self, model_transform):
        """Send matrixes to the GPU."""
        MV = matrix44.multiply(model_transform, self.V)
        glUniformMatrix4fv(
            self.uniforms["MV"], 1, GL_FALSE,
            MV
        )
        glUniformMatrix4fv(
            self.uniforms["MVP"], 1, GL_FALSE,
            matrix44.multiply(MV, self.P)
        )
        glUniformMatrix4fv(
            self.uniforms["M"], 1, GL_FALSE,
            model_transform
        )
        glUniformMatrix4fv(
            self.uniforms["V"], 1, GL_FALSE,
            self.V
        )

    def load_models(self, names):
        """Load models."""
        all_vertices = []
        model_offset = 0
        models = {}
        for model_name in names:
            model_indices = 0
            obj = Wavefront(f"assets/{model_name}.obj", parse=True)
            for name, mat in obj.materials.items():
                if (mat.vertex_format != "T2F_N3F_V3F"):
                    exit("Vertx format must be T2F_N3F_V3F")
                if (mat.texture and not self.textures.get(mat.texture.path)):
                    self.load_texture(mat.texture.path)
                texture = self.textures.get(mat.texture.path)
                all_vertices.append(np.array(mat.vertices, dtype=np.float32))
                model_indices += len(mat.vertices) // 8
            models[model_name] = {
                "offset": model_offset,
                "indices": model_indices,
                "texture": texture
            }
            model_offset += model_indices

        vertices = np.concatenate(all_vertices).ravel()

        # upload to GPU
        vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, vbo)
        glBufferData(
            GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

        s = 4 * (2 + 3 + 3)
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, s, ctypes.c_void_p(0))

        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, s, ctypes.c_void_p(8))

        glEnableVertexAttribArray(2)
        glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, s, ctypes.c_void_p(20))
        self.models = models

    def load_texture(self, path):
        """Upload a texture to GPU."""
        try:
            im = Image.open(path).convert("RGBA")
        except Exception as e:
            exit("Error reading texture:" + e)
        data = im.tobytes("raw", "RGBA", 0, -1)

        # generate a new texture id
        texture_id = glGenTextures(1)
        self.textures[path] = texture_id
        glBindTexture(GL_TEXTURE_2D, texture_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_BASE_LEVEL, 0)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAX_LEVEL, 0)
        # TODO improve filter options
        glTexParameteri(
            GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glGenerateMipmap(GL_TEXTURE_2D)
        antr = glGetFloatv(GL_MAX_TEXTURE_MAX_ANISOTROPY_EXT)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAX_ANISOTROPY_EXT, antr)
        # upload a texture
        glTexImage2D(
            GL_TEXTURE_2D,
            0,
            GL_RGBA,
            im.width,
            im.height,
            0,
            GL_RGBA,
            GL_UNSIGNED_BYTE,
            data
        )
