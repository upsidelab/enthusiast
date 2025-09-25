import base64
from io import BytesIO
from typing import IO, AnyStr

from enthusiast_common.services.file import BaseFileParser
from PIL import Image


class ImageFileParser(BaseFileParser):
    def parse_content(self, file: IO[AnyStr]) -> str:
        file.seek(0)
        image = Image.open(file)
        output_format = image.format or "PNG"

        stream = BytesIO()
        image.save(stream, format=output_format)
        stream.seek(0)

        return base64.b64encode(stream.getvalue()).decode("utf-8")
