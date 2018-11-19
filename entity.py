"""Entity."""

from pyrr import matrix44
import numpy as np


class Entity:
    """Game Entity."""

    def __init__(self, model, position, rotation):
        """Create entity."""
        self.model = model
        self.collisions = []
        self.pos = np.array(position, dtype=np.float32)
        self.rot = np.array(rotation, dtype=np.float32)
        self.transform = None

    def draw(self, ctx):
        """Add entity to the global draw queue."""
        self.transform = matrix44.multiply(
            matrix44.create_from_eulers(self.rot, dtype=np.float32),
            matrix44.create_from_translation(self.pos, dtype=np.float32)
        )
        ctx.draw_queue.append((self.model, self.transform))

    def collide(self):
        """Collide."""
