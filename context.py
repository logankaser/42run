"""Render context module."""

import ctypes
import numpy as np
from os import path
from PIL import Image
from pywavefront import Wavefront
from collections import deque
import OpenGL
OpenGL.ERROR_CHECKING = False
from OpenGL.GL import *
from OpenGL.GL import shaders
from OpenGL.raw.GL.EXT.texture_filter_anisotropic import *


def get_radius(vertices):
    """Get bounding column."""
    lengths = vertices[5::8]**2 + vertices[6::8]**2

    # find the maximum value
    maximum = lengths.max()

    # square root this, this is the radius
    radius = np.sqrt(maximum)
    return radius


class Context:
    """Context."""

    def __init__(self):
        """Create render context."""
        self.program_ids = {}
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

    def clear(self):
        """Clear buffer."""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    def load_program(self, name):
        """Load shaders."""
        try:
            with open(path.join("assets", name + ".frag"), "r") as src:
                frag_src = src.read()
            with open(path.join("assets", name + ".vert"), "r") as src:
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
        self.program_ids[name] = program_id
        self.uniforms[name] = {}
        # map uniform names to uniform ids
        num_uniforms = glGetProgramiv(program_id, GL_ACTIVE_UNIFORMS)
        for i in range(0, num_uniforms):
            buff = np.array(glGetActiveUniformName(program_id, i, 256))
            uni = buff[:np.count_nonzero(buff)].tostring().decode()
            self.uniforms[name][uni] = glGetUniformLocation(program_id, uni)

    def update_uniforms(self, new_uniforms):
        """Send matrixes to the GPU."""
        CAMERA_UNIFORMS = set(["MVP", "MV", "V", "M", "P"])
        active_uniforms = self.uniforms[self.active_program]
        for uni in new_uniforms:
            if uni in CAMERA_UNIFORMS and uni not in active_uniforms:
                continue
            glUniformMatrix4fv(
                active_uniforms[uni], 1, GL_FALSE,
                new_uniforms[uni]
            )

    def use_program(self, name):
        """Make program active."""
        glUseProgram(self.program_ids[name])
        self.active_program = name

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
                verts = np.array(mat.vertices, dtype=np.float32)
                all_vertices.append(verts)
                model_indices += len(mat.vertices) // 8
            models[model_name] = {
                "offset": model_offset,
                "indices": model_indices,
                "texture": texture,
                "radius": get_radius(verts)
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
