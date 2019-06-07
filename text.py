"""Text."""

import OpenGL
from entity import Entity
from PIL import Image, ImageFont, ImageDraw
import math

OpenGL.ERROR_CHECKING = False
from OpenGL.GL import *
from OpenGL.raw.GL.EXT.texture_filter_anisotropic import *


class Text(Entity):
    """Arbitrary text that may be position in 3d."""

    def __init__(self, ctx, pos, text, font_name="futura"):
        """Create entity."""
        super().__init__("plane", pos, [0, math.pi / 2, -math.pi / 2])
        self.text = text

        self.image = Image.new("RGBA", (512, 512), (255, 0, 0, 0))

        self.font = ImageFont.truetype(f"assets/{font_name}.otf", size=120)
        self.image_draw = ImageDraw.Draw(self.image)
        self.image_draw.text(
            (0, 196), text, (255, 255, 255, 255), self.font, align="center"
        )

        data = self.image.tobytes("raw", "RGBA", 0, -1)

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
            self.image.width,
            self.image.height,
            0,
            GL_RGBA,
            GL_UNSIGNED_BYTE,
            data,
        )
        glGenerateMipmap(GL_TEXTURE_2D)
        self.texture_id = texture_id

    def draw(self, ctx, camera):
        """Draw da thing."""
        glDisable(GL_DEPTH_TEST)
        ctx.use_program("text")
        super()._update_transform()
        camera_uniforms = camera.gen_uniforms(self.transform)
        model = ctx.get_model(self.model)
        ctx.update_uniforms(camera_uniforms)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.texture_id)
        glDrawArrays(GL_TRIANGLES, model.offset, model.indices)
        glEnable(GL_DEPTH_TEST)

    def update(self, text):
        """Update."""
        glDeleteTextures(self.texture_id)
        self.image_draw.rectangle([0, 0, 512, 512], (0, 0, 0, 0))
        self.image_draw.text(
            (0, 196), text, (255, 255, 255, 255), self.font, align="center"
        )

        data = self.image.tobytes("raw", "RGBA", 0, -1)

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
            self.image.width,
            self.image.height,
            0,
            GL_RGBA,
            GL_UNSIGNED_BYTE,
            data,
        )
        glGenerateMipmap(GL_TEXTURE_2D)
        self.texture_id = texture_id
