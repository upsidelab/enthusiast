from abc import ABC

from .base_agent_friendly_error import BaseAgentFriendlyError


class RetrieverError(BaseAgentFriendlyError, ABC):
    pass
