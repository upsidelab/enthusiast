from abc import ABC, abstractmethod


class BaseAgentFriendlyError(Exception, ABC):
    @property
    @abstractmethod
    def agent_friendly_message(self) -> str:
        pass
