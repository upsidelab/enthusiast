from dataclasses import dataclass
from typing import Any

from .file_types import FileTypes


@dataclass
class LLMFile:
    id: Any
    content: str
    file_category: FileTypes
    filename: str
    content_type: str
