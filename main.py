#!/usr/bin/env python3
"""main."""

import ctypes
import numpy as np
from OpenGL.GL import *
from OpenGL.GL import shaders
from PIL import Image
import glfw
from pyrr import matrix44
from wavefront_reader import read_wavefront




def load_models():
    """Load models."""
    all_vert = []
    all_uv = []
    all_norm = []
    for obj_file in ["assets/test.obj"]:
        for mesh in read_wavefront(obj_file).values():
            all_vert.append(np.array(mesh["v"], dtype=np.float32))
            all_uv.append(np.array(mesh["vt"], dtype=np.float32))
            all_norm.append(np.array(mesh["vn"], dtype=np.float32))

    vert = np.concatenate(all_vert).ravel()
    uv = np.concatenate(all_uv).ravel()
    norm = np.concatenate(all_norm).ravel()

    # create vbo
    vbo = glGenBuffers(3)
    glBindBuffer(GL_ARRAY_BUFFER, vbo[0])
    glBufferData(GL_ARRAY_BUFFER, vert.nbytes, vert, GL_STATIC_DRAW)
    glEnableVertexAttribArray(0)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)

    glBindBuffer(GL_ARRAY_BUFFER, vbo[1])
    glBufferData(GL_ARRAY_BUFFER, uv.nbytes, uv, GL_STATIC_DRAW)
    glEnableVertexAttribArray(1)
    glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 0, None)

    glBindBuffer(GL_ARRAY_BUFFER, vbo[2])
    glBufferData(GL_ARRAY_BUFFER, norm.nbytes, norm, GL_STATIC_DRAW)
    glEnableVertexAttribArray(2)
    glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 0, None)
    return len(vert) // 3


def render(ctx, num_verts):
    """Render a frame."""
    ctx.clear()
    ctx.upload_matrixes()
    glDrawArrays(GL_TRIANGLES, 0, num_verts)
    err = glGetError()
    if (err != GL_NO_ERROR):
        print("GLERROR: ", gluErrorString(err))
        sys.exit()


class GlContext:
    """Store GL state."""
    def __init__(self, V, P):
        self.V = V
        self.P = P
        self.program_id = None
        self.V_id = None
        self.VP_id = None
        # create vao
        vao = glGenVertexArrays(1)
        glBindVertexArray(vao)
        glClearColor(0.3, 0.3, 0.3, 1)
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)

    def clear(self):
        """Clear buffer."""
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
        self.V_id = glGetUniformLocation(self.program_id, "VP")
        self.VP_id = glGetUniformLocation(self.program_id, "P")

    def upload_matrixes(self):
        """Send matrixes to the GPU."""
        glUniformMatrix4fv(
            self.VP_id, 1, GL_FALSE, matrix44.multiply(self.V, self.P)
        )
        glUniformMatrix4fv(self.V_id, 1, GL_FALSE, self.V)


def main():
    """main."""
    if not glfw.init():
        exit("Error starting glfw")

    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 4)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 1)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, True)

    window = glfw.create_window(1024, 1024, "42run", None, None)
    if not window:
        glfw.terminate()
        exit("Error creating window")

    glfw.make_context_current(window)

    icon = Image.open("assets/icon.png")
    glfw.set_window_icon(window, 1, [icon])

    V = matrix44.create_look_at(
        np.array([0, 0, -1]),  # position
        np.array([0, 0, 0]),  # target
        np.array([0, 1, 0])  # up vector
    )
    P = matrix44.create_perspective_projection(80, 1, 0.1, 100)
    ctx = GlContext(V, P)
    ctx.load_shaders("assets/42run.frag", "assets/42run.vert")

    num_verts = load_models()

    # mainloop
    while not glfw.window_should_close(window):
        glClear(GL_COLOR_BUFFER_BIT)
        render(ctx, num_verts)
        glfw.swap_buffers(window)
        glfw.poll_events()

    glfw.terminate()
    return window


if __name__ == "__main__":
    main()
