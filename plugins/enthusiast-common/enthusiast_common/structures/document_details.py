from dataclasses import dataclass


@dataclass
class DocumentDetails:
    url: str
    title: str
    content: str
