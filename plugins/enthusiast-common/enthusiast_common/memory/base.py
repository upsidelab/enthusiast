from abc import ABC, abstractmethod
from typing import Optional


class BaseMemoryCompactor(ABC):
    """
    Interface for compacting conversation history into a summary.

    Implementations should persist the summary and return it on demand.
    The summary is then injected into the LLM context alongside recent messages,
    preserving conversation context that would otherwise be lost to token trimming.
    """

    @abstractmethod
    def get_summary(self) -> Optional[str]:
        """Return the current persisted summary, or None if not yet generated."""
        pass

    @abstractmethod
    def compact_if_needed(self) -> None:
        """
        Check whether a new summary should be generated and, if so, generate and persist it.

        Should be called after new messages have been added to history.
        """
        pass
