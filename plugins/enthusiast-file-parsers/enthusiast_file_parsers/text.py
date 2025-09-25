from typing import IO, AnyStr

from enthusiast_common.services.file import BaseFileParser


class PlainTextFileParser(BaseFileParser):
    def parse_content(self, file: IO[AnyStr]) -> str:
        return file.read().decode("utf-8")
