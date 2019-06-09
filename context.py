"""Render context module."""

import ctypes
import numpy as np
import glob
import os.path
from PIL import Image
from pywavefront import Wavefront
import OpenGL

OpenGL.ERROR_CHECKING = False
from OpenGL.GL import *
from OpenGL.GL import shaders
from OpenGL.raw.GL.EXT.texture_filter_anisotropic import *


class Model:
    """Holds information about a model to be rendered."""

    def __init__(self, offset, indices, texture):
        """Create model."""
        self.offset = offset
        self.indices = indices
        self.texture = texture


class VAO:
    """Holds ids that are managed by a VAO."""

    def __init__(self):
        """Create model."""
        self.id = glGenVertexArrays(1)
        self.buffer_ids = []
        self.texture_ids = []


class Uniform:
    """Uniform id, type, and size."""

    def __init__(self, id, type, size):
        """Create model."""
        self.id = id
        self.type = type
        self.size = size


class Context:
    """Context."""

    GL_CUBE_MAP_FACES = [
        GL_TEXTURE_CUBE_MAP_POSITIVE_X,
        GL_TEXTURE_CUBE_MAP_NEGATIVE_X,
        GL_TEXTURE_CUBE_MAP_POSITIVE_Y,
        GL_TEXTURE_CUBE_MAP_NEGATIVE_Y,
        GL_TEXTURE_CUBE_MAP_POSITIVE_Z,
        GL_TEXTURE_CUBE_MAP_NEGATIVE_Z,
    ]

    def __init__(self):
        """Create render context."""
        self.program_ids = {}
        self.active_program = None
        self.uniforms = {}
        self.models = {}
        self.textures = {}
        # create vao
        self.vertex_arrays = {}
        self.active_vertex_array = None
        self.create_vao("default")
        self.use_vao("default")
        glClearColor(0.0, 0.0, 0.0, 1.0)
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    def clear(self):
        """Clear buffer."""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    def create_program(self, name):
        """Load shaders."""
        if name in self.program_ids:
            return
        try:
            with open(os.path.join("assets", name + ".frag"), "r") as src:
                frag_src = src.read()
            with open(os.path.join("assets", name + ".vert"), "r") as src:
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
            uni_name, uni_size, uni_type = glGetActiveUniform(program_id, i)
            uni_name = uni_name.decode("utf-8")
            uni_id = glGetUniformLocation(program_id, uni_name)
            self.uniforms[name][uni_name] = Uniform(uni_id, uni_type, uni_size)

    def update_uniforms(self, new_uniforms):
        """Send matrixes to the GPU."""
        CAMERA_UNIFORMS = set(["MVP", "MV", "V", "M", "P"])
        active_uniforms = self.uniforms[self.active_program]
        for uni in new_uniforms:
            if uni in CAMERA_UNIFORMS and uni not in active_uniforms:
                continue
            glUniformMatrix4fv(active_uniforms[uni].id, 1, GL_FALSE, new_uniforms[uni])

    def uniform(self, name):
        """Get the uniform with name from the currently active program."""
        return self.uniforms[self.active_program][name]

    def use_program(self, name):
        """Make program active."""
        if self.active_program != name:
            glUseProgram(self.program_ids[name])
            self.active_program = name

    def create_vao(self, name):
        """Create a new vertex array object."""
        if name in self.vertex_arrays:
            raise RuntimeError("VAO with that name already exists")
        self.vertex_arrays[name] = VAO()
        self.models.setdefault(name, {})
        self.textures.setdefault(name, {})

    def use_vao(self, name):
        """Make vao active.

        Following calling this, all calls to load_{x} functions will use the
        specified vao.
        """
        if self.active_vertex_array != name:
            glBindVertexArray(self.vertex_arrays[name].id)
            self.active_vertex_array = name

    def load_models(self, names, vao="default"):
        """Load or reload models into a vao."""
        glBindVertexArray(self.vertex_arrays[vao].id)
        while self.vertex_arrays[vao].buffer_ids:
            buff_id = self.vertex_arrays[vao].buffer_ids.pop()
            glDeleteBuffers(buff_id, 1)
        while self.vertex_arrays[vao].texture_ids:
            tex_id = self.vertex_arrays[vao].texture_ids.pop()
            glDeleteTextures(tex_id)

        all_vertices = []
        model_offset = 0
        models = {}
        for model_name in names:
            model_indices = 0
            obj = Wavefront(f"assets/{model_name}.obj", parse=True)
            for name, mat in obj.materials.items():
                if mat.vertex_format != "T2F_N3F_V3F":
                    exit(
                        f"Error in {model_name}.obj"
                        + " vertex format must be T2F_N3F_V3F"
                    )
                texture = self.load_texture(mat.texture.path) if mat.texture else None
                if texture:
                    self.vertex_arrays[vao].texture_ids.append(texture)
                verts = np.array(mat.vertices, dtype=np.float32)
                all_vertices.append(verts)
                model_indices += len(mat.vertices) // 8
            models[model_name] = Model(model_offset, model_indices, texture)
            model_offset += model_indices

        vertices = np.concatenate(all_vertices).ravel()

        # upload to GPU
        new_vbo = glGenBuffers(1)
        self.vertex_arrays[vao].buffer_ids.append(new_vbo)
        glBindBuffer(GL_ARRAY_BUFFER, new_vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

        s = np.dtype(np.float32).itemsize * (2 + 3 + 3)
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, s, ctypes.c_void_p(0))

        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, s, ctypes.c_void_p(8))

        glEnableVertexAttribArray(2)
        glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, s, ctypes.c_void_p(20))
        self.models[vao] = models

    def get_model(self, name):
        """Get the model with name from the currently bound VAO."""
        return self.models[self.active_vertex_array][name]

    def load_texture(self, path, vao="default"):
        """Upload a texture to GPU."""
        if path in self.textures[vao]:
            return self.textures[vao][path]
        try:
            im = Image.open(path).convert("RGBA")
        except Exception as e:
            exit("Error reading texture: " + path)
        glBindVertexArray(self.vertex_arrays[vao].id)
        data = im.tobytes("raw", "RGBA", 0, -1)

        # generate a new texture id
        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)

        max_af = min(glGetFloatv(GL_MAX_TEXTURE_MAX_ANISOTROPY_EXT), 16.0)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAX_ANISOTROPY_EXT, max_af)
        # upload texture
        glTexImage2D(
            GL_TEXTURE_2D,
            0,
            GL_RGBA,
            im.width,
            im.height,
            0,
            GL_RGBA,
            GL_UNSIGNED_BYTE,
            data,
        )
        glGenerateMipmap(GL_TEXTURE_2D)
        self.textures[vao][path] = texture_id
        return texture_id

    def load_texture_cubemap(self, path, vao="default"):
        """Load cubemap texture."""
        # Generate a new texture id
        if path in self.textures[vao]:
            return self.textures[vao][path]
        glBindVertexArray(self.vertex_arrays[vao].id)
        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_CUBE_MAP, texture_id)

        i = 0
        sides = ["right", "left", "top", "bottom", "front", "back"]
        for face in self.GL_CUBE_MAP_FACES:
            try:
                face_path = None
                face_path = glob.glob(os.path.join(path, sides[i] + ".*"))[0]
                im = Image.open(face_path).convert("RGBA")
            except Exception as e:
                exit(
                    "Error reading cubemap texture: "
                    + (face_path if face_path else str(i) + ".*")
                )
            i += 1
            data = im.tobytes("raw", "RGBA", 0, -1)
            # Upload a texture
            glTexImage2D(
                face, 0, GL_RGB, im.width, im.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, data
            )
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_EDGE)
        self.textures[vao][path] = texture_id
        return texture_id
