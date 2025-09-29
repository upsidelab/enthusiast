import base64
from typing import IO, AnyStr

from enthusiast_common.services.file import BaseFileParser


class PlainTextFileParser(BaseFileParser):
    def parse_content(self, file: IO[AnyStr]) -> str:
        return base64.b64encode(file.read()).decode("utf-8")
