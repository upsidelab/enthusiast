from importlib import import_module

from enthusiast_common.services.file import BaseFileParser, BaseFileService, NotSupportedFileTypeException

from pecl import settings


class FileService(BaseFileService):
    def process(self) -> str:
        parser = self._get_parser()
        return parser.parse_content(self.file)

    @staticmethod
    def _load_parser_class(parser_path: str) -> BaseFileParser:
        module_name, class_name = parser_path.rsplit(".", 1)
        module = import_module(module_name)
        parser_class = getattr(module, class_name)
        return parser_class()

    def _get_parser(self) -> BaseFileParser:
        file_type = self._get_file_type()
        for key in settings.FILE_PARSER_CLASSES.keys():
            if file_type in key:
                return self._load_parser_class(settings.FILE_PARSER_CLASSES[key])
        raise NotSupportedFileTypeException()
