"""Camera."""
from pyrr import matrix44
import numpy as np


class Camera:
    """Game camera."""

    def __init__(
        self,
        pos=np.array([0.0, 0.0, 0.0], dtype=np.float32),
        target=np.array([0.0, 0.0, 1.0], dtype=np.float32),
        aspect=1.0,
        fov=60.0,
    ):
        """Create camera."""
        self.fov = fov
        self.aspect = aspect
        if isinstance(pos, np.ndarray):
            self.pos = pos
        else:
            self.pos = np.array(pos, dtype=np.float32)
        self.target = target
        if isinstance(target, np.ndarray):
            self.target = target
        else:
            self.target = np.array(target, dtype=np.float32)
        self.V = matrix44.create_look_at(
            self.pos,  # position
            self.target,  # target
            np.array([0, 1, 0]),  # up vector
        )
        self.regen_view = False
        self.P = matrix44.create_perspective_projection(
            self.fov, aspect, 0.1, 300, dtype=np.float32
        )
        self.regen_prespective = False

    def set_aspect(self, aspect):
        """Set camera aspect ratio."""
        self.aspect = aspect
        self.regen_prespective = True

    def set_fov(self, fov):
        """Set camera fov."""
        self.fov = fov
        self.regen_prespective = True

    def set_pos(self, pos):
        """Set camera position."""
        self.pos = pos
        self.regen_view = True

    def set_target(self, target):
        """Set camera target."""
        self.target = target
        self.regen_view = True

    def _regen_prespective(self):
        self.P = matrix44.create_perspective_projection(
            self.fov, self.aspect, 0.1, 100, dtype=np.float32
        )
        self.regen_prespective = False

    def _regen_view(self):
        self.V = matrix44.create_look_at(
            np.array(self.pos),  # position
            np.array(self.target),  # target
            np.array([0, 1, 0]),  # up vector
        )
        self.regen_view = False

    def gen_uniforms(self, M):
        """Generate standard camera uniforms."""
        if self.regen_prespective:
            self._regen_prespective()
        if self.regen_view:
            self._regen_view()
        MV = matrix44.multiply(M, self.V)
        MVP = matrix44.multiply(MV, self.P)
        return {"M": M, "V": self.V, "MV": MV, "MVP": MVP}
