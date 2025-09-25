import base64
from io import BytesIO
from typing import IO, AnyStr

from enthusiast_common.services.file import BaseFileParser
from PIL import ImageOps
from pypdf import PdfWriter


class PDFFileParser(BaseFileParser):
    def parse_content(self, file: IO[AnyStr]) -> str:
        writer = PdfWriter(fileobj=file)

        for page in writer.pages:
            for img in page.images:
                img.replace(ImageOps.grayscale(img.image), quality=5)

        pdf_stream = BytesIO()
        writer.write(pdf_stream)
        pdf_stream.seek(0)
        return base64.b64encode(pdf_stream.getvalue()).decode("utf-8")
