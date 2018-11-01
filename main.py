#!/usr/bin/env python3
"""main."""

import ctypes
import numpy as np
from OpenGL.GL import *
from OpenGL.GL import shaders
from PIL import Image
import glfw
from pyrr import matrix44

VERTEX_SHADER = """
#version 410 core

layout (location=0) in vec4 position;
layout (location=1) in vec4 color;

smooth out vec4 theColor;

void main()
{
    gl_Position = position;
    theColor = color;
}
"""

FRAGMENT_SHADER = """
#version 410 core

smooth in vec4 theColor;
out vec4 outputColor;

void main()
{
    outputColor = theColor;
}
"""

shaderProgram = None
VAO = None

def initialize():
    global VERTEX_SHADER
    global FRAGMENT_SHADER

    # create VAO
    VAO = glGenVertexArrays(1)
    glBindVertexArray(VAO)

    # compile shaders and program
    try:
        vertexShader = shaders.compileShader(VERTEX_SHADER, GL_VERTEX_SHADER)
        fragmentShader = shaders.compileShader(FRAGMENT_SHADER, GL_FRAGMENT_SHADER)
        shaderProgram = shaders.compileProgram(vertexShader, fragmentShader)
    except RuntimeError as e:
        print(str(e).replace("\\n", "\n").replace("\\", ""))
        exit("Shaders failed to compile")

    # position
    posData = np.array([
            0.0, 0.5, 0.0, 1.0,
            0.5, -0.366, 0.0, 1.0,
            -0.5, -0.366, 0.0, 1.0,
        ],
        dtype=np.float32
    )

    # color
    colorData = np.array([
            1.0, 0.0, 0.0, 1.0,
            0.0, 1.0, 0.0, 1.0,
            0.0, 0.0, 1.0, 1.0,
        ],
        dtype=np.float32
    )

    # create VBO
    VBO = glGenBuffers(2)
    glBindBuffer(GL_ARRAY_BUFFER, VBO[0])
    glBufferData(GL_ARRAY_BUFFER, posData.nbytes, posData, GL_STATIC_DRAW)
    glEnableVertexAttribArray(0)
    glVertexAttribPointer(0, 4, GL_FLOAT, GL_FALSE, 0, None)

    glBindBuffer(GL_ARRAY_BUFFER, VBO[1])
    glBufferData(GL_ARRAY_BUFFER, colorData.nbytes, colorData, GL_STATIC_DRAW)
    glEnableVertexAttribArray(1)
    glVertexAttribPointer(1, 4, GL_FLOAT, GL_FALSE, 0, None)

    #glBindBuffer(GL_ARRAY_BUFFER, 0)
    #glBindVertexArray(0)
    glUseProgram(shaderProgram)


def render():
    """Render a frame."""
    glClearColor(0, 0, 0, 1)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glDrawArrays(GL_TRIANGLES, 0, 3)


class Scene:
    """Stores the state of the scene."""

    def __init__(self, shaders=[]):
        """Create scene."""
        self.shaders = shaders


class GLContext:
    """Class to make handling OpenGL context easy."""

    def __init__(self, clear_color=(0.1, 0.1, 0.12, 1)):
        """Init GLContext."""
        vao_id = GLuint(0)
        glGenVertexArrays(1, ctypes.byref(vao_id))
        glBindVertexArray(vao_id)
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)
        cc = clear_color
        glClearColor(cc[0], cc[1], cc[2], cc[3])

    def set_clear_color(r, g, b, a):
        """Set clear color."""
        glClearColor(r, g, b, a)


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

    camera = matrix44.create_look_at(
        np.array([0, 0, -1]),  # position
        np.array([0, 0, 0]),  # target
        np.array([0, 1, 0])  # up vector
    )
    print(camera)
    project = matrix44.create_perspective_projection(80, 1, 0.1, 100)
    print(project)
    res = project * camera
    print(res)

    initialize()

    # mainloop
    while not glfw.window_should_close(window):
        glClear(GL_COLOR_BUFFER_BIT)
        render()
        glfw.swap_buffers(window)
        glfw.poll_events()

    glfw.terminate()
    return window


if __name__ == "__main__":
    main()
