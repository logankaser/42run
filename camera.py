from pyrr import matrix44


class Camera:
    """Game camera."""

    def __init__(self, V, aspect, fov=60):
        """Create camera."""
        self.fov = fov
        self.V = V
        self.P = matrix44.create_perspective_projection(
            self.fov, aspect, 0.1, 100)

    def update_aspect(self, aspect):
        """Recreate perspective matrix with new aspect ratio."""
        self.P = matrix44.create_perspective_projection(
            self.fov, aspect, 0.1, 100)

    def gen_uniforms(self, M):
        """Generate standard camera uniforms."""
        MV = matrix44.multiply(M, self.V)
        MVP = matrix44.multiply(MV, self.P)
        return {
            "M": M,
            "V": self.V,
            "MV": MV,
            "MVP": MVP
        }
