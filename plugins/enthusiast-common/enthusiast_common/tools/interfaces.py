from abc import ABC, abstractmethod
from typing import Any


class BaseWidgetResponseSerializer(ABC):
    def __init__(self, data: Any):
        self.data = data

    @abstractmethod
    def serialize(self):
        pass
