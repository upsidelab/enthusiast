import mimetypes
from abc import ABC, abstractmethod
from typing import IO, AnyStr


class FileServiceException(Exception):
    pass


class NotSupportedFileTypeException(FileServiceException):
    def __init__(self, message="Unsupported file type."):
        super().__init__(message)


class FileParsingException(FileServiceException):
    def __init__(self, message="Failed to extract content from file."):
        super().__init__(message)


class BaseFileParser(ABC):
    @abstractmethod
    def parse_content(self, file: IO[AnyStr]) -> str:
        pass


class BaseFileService(ABC):
    def __init__(self, file: IO[AnyStr], content_type: str):
        self.file = file
        self.content_type = content_type

    @abstractmethod
    def process(self) -> str:
        pass

    @abstractmethod
    def _get_parser(self) -> BaseFileParser:
        pass

    def _get_file_type(self) -> str:
        return mimetypes.guess_extension(self.content_type)
