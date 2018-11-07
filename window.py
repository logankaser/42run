"""Window."""
import glfw
from PIL import Image


class Window:
    """Wrap GLFW."""

    def __init__(self, width, height):
        """Create a new window."""
        if not glfw.init():
            exit("Error starting glfw")

        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 4)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 1)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, True)
        glfw.window_hint(glfw.SAMPLES, 4)

        self.glfw_window = glfw.create_window(
            width, height, "42run", None, None)
        if not self.glfw_window:
            glfw.terminate()
            exit("Error creating window")

        self.width = width
        self.height = height
        glfw.set_window_size_callback(
            self.glfw_window, self._window_resize_handler)
        glfw.make_context_current(self.glfw_window)

        icon = Image.open("assets/icon.png")
        glfw.set_window_icon(self.glfw_window, 1, [icon])

    def __bool__(self):
        """Return false if window should close."""
        return not glfw.window_should_close(self.glfw_window)

    def _window_resize_handler(self, win, width, height):
        self.width, self.height = width, height

    def close(self):
        """Close the window."""
        glfw.terminate()

    def swap_buffers(self):
        """Copy framebuffer to window, call every frame."""
        glfw.swap_buffers(self.glfw_window)
        glfw.poll_events()
