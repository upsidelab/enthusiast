import base64
from io import BytesIO
from typing import IO, AnyStr

from enthusiast_common.services.file import BaseFileParser
from PIL import Image, ImageOps


class ImageFileParser(BaseFileParser):
    def parse_content(self, file: IO[AnyStr]) -> str:
        file.seek(0)
        image = Image.open(file)

        try:
            image = ImageOps.exif_transpose(image)
        except Exception:
            pass

        has_transparency = image.mode in ("RGBA", "LA") or (
            image.mode == "P" and image.info.get("transparency") is not None
        )

        if has_transparency:
            rgba = image.convert("RGBA")
            background = Image.new("RGB", rgba.size, (255, 255, 255))
            alpha = rgba.split()[-1]
            background.paste(rgba, mask=alpha)
            image = background
        else:
            image = image.convert("RGB")

        stream = BytesIO()
        image.save(stream, format="JPEG", quality=40, optimize=True)
        stream.seek(0)
        return base64.b64encode(stream.getvalue()).decode("utf-8")
