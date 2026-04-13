from abc import ABC, abstractmethod
from typing import Optional

from ..input import ExecutionInputType
from ..memory import ToolResultMemory
from .response import ValidatorResponse


class BaseExecutionValidator(ABC):
    """Pluggable validator that inspects a single LLM response string.

    Attach validators to an agentic execution definition class via ``VALIDATORS``. After each
    ``execute()`` call the retry loop runs every validator in order. The first
    failing ``ValidatorResponse`` drives what the loop does next:

    - ``validation_successful=True`` on all validators → execution succeeds.
    - ``validation_successful=False, retry_needed=True`` → feedback is sent back
      to the LLM and the attempt is retried (up to ``MAX_RETRIES`` times).
    - ``validation_successful=False, retry_needed=False`` → the loop stops
      immediately without retrying; ``feedback`` is used as the failure summary.

    The ``tool_result_memory`` argument gives validators access to what tools explicitly chose
    to record during the attempt — not just the final LLM text. This is an opt-in
    contract: only tools that call ``self._injector.tool_result_memory.record()`` in their
    ``run()`` contribute data here. Validators that don't need tool results can ignore it.
    """

    @abstractmethod
    def validate(self,
                 response: str,
                 execution_input: ExecutionInputType,
                 tool_result_memory: Optional[ToolResultMemory] = None) -> ValidatorResponse:
        """Inspect the LLM response and return a structured result.

        Args:
            response: Raw string returned by ``execute()``.
            execution_input: Execution input received at execution creation.
            tool_result_memory: Entries recorded by tools during this attempt via
                ``self._injector.tool_result_memory.record()``. ``None`` when
                called outside an agentic execution context (e.g. in unit tests).
                Validators that do not inspect tool results can safely ignore this argument.

        Returns:
            A :class:`ValidatorResponse` describing whether the response is
            acceptable and, if not, what the loop should do next.
        """
