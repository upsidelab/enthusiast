import json
from abc import ABC, abstractmethod
from typing import ClassVar, Optional, Protocol, Type

from .errors import ExecutionFailureCode
from .input import ExecutionInputType
from .result import ExecutionResult
from .validators import BaseExecutionValidator, IsValidJsonValidator, ValidatorResponse


class ExecutionConversationInterface(Protocol):
    """Protocol for the conversation handle passed to ``execute()``.

    The server provides a concrete implementation backed by a real ``Conversation``
    record. Each ``ask()`` call appends a user message, runs the full agent turn
    (including tool calls), and returns the agent's final text response.
    """

    def ask(self, message: str) -> str:
        """Send a message to the agent and return its response.

        Args:
            message: User-side message to append to the conversation.

        Returns:
            The agent's text response after completing its tool-call loop.
        """
        ...


class BaseAgenticExecutionDefinition(ABC):
    """Abstract base class for all agentic execution definition types.

    Subclass this in an agent plugin to implement a specific autonomous task.
    Register the subclass in ``settings.AVAILABLE_AGENTIC_EXECUTION_DEFINITIONS`` so the
    server can discover it.

    Minimal implementation::

        class MyExecution(BaseAgenticExecutionDefinition):
            EXECUTION_KEY = "my-execution"
            AGENT_KEY = "my-agent-plugin-key"
            NAME = "My Execution"
            INPUT_TYPE = MyExecutionInput

            def execute(self, input_data, conversation):
                return conversation.ask("Do the thing.")
    """

    EXECUTION_KEY: ClassVar[str]
    AGENT_KEY: ClassVar[str]
    NAME: ClassVar[str]
    DESCRIPTION: ClassVar[Optional[str]] = None
    INPUT_TYPE: ClassVar[Type[ExecutionInputType]] = ExecutionInputType
    VALIDATORS: ClassVar[list[Type[BaseExecutionValidator]]] = [IsValidJsonValidator]
    MAX_RETRIES: ClassVar[int] = 3
    FAILURE_CODES: ClassVar[Type[ExecutionFailureCode]] = ExecutionFailureCode
    FAILURE_SUMMARY_PROMPT: ClassVar[str] = (
        "You were unable to produce a valid response after multiple attempts. "
        "Please provide a brief (max 100 words), plain-language summary of what went wrong."
    )

    def run(
        self,
        input_data: ExecutionInputType,
        conversation: ExecutionConversationInterface,
    ) -> ExecutionResult:
        """Orchestrate the validator retry loop and return the final result.

        Calls ``execute()`` and runs all ``VALIDATORS`` against the response. If
        any validator returns feedback the message is sent back to the LLM and
        ``execute()`` is retried, up to ``MAX_RETRIES`` times. Returns
        ``ExecutionResult(success=True)`` as soon as all validators pass, or
        ``ExecutionResult(success=False, failure_code=MAX_RETRIES_EXCEEDED)``
        once retries are exhausted.
        """

        response = self.execute(input_data, conversation)

        for attempt in range(self.MAX_RETRIES + 1):
            validator_response = self._first_failed_validator_response(response)

            if validator_response is None:
                return ExecutionResult(success=True, output=self._build_output(response))

            if not validator_response.retry_needed:
                return ExecutionResult(
                    success=False,
                    failure_code=validator_response.failure_code or self.FAILURE_CODES.VALIDATION_FAILED,
                    failure_summary=validator_response.feedback,
                )

            if attempt < self.MAX_RETRIES:
                feedback = validator_response.feedback or "The previous response was invalid. Please try again."
                response = conversation.ask(feedback)
            else:
                failure_summary = conversation.ask(self.FAILURE_SUMMARY_PROMPT)
                return ExecutionResult(
                    success=False,
                    failure_code=self.FAILURE_CODES.MAX_RETRIES_EXCEEDED,
                    failure_summary=failure_summary,
                )

        # Unreachable — satisfies the type checker.
        return ExecutionResult(success=False)  # pragma: no cover

    @abstractmethod
    def execute(
        self,
        input_data: ExecutionInputType,
        conversation: ExecutionConversationInterface,
    ) -> str:
        """Perform a single execution attempt and return the raw LLM response.

        Called by ``run()`` on each attempt. Use ``conversation.ask()`` to drive
        the agent. The return value is passed to each validator in ``VALIDATORS``;
        if all pass it becomes the ``output`` of the ``ExecutionResult``.

        Args:
            input_data: Validated input, already cast to ``INPUT_TYPE``.
            conversation: Conversation handle for the execution's internal session.

        Returns:
            The agent's raw response string (typically JSON).
        """

    def _first_failed_validator_response(self, response: str) -> Optional[ValidatorResponse]:
        """Run all validators and return the first failing response, or ``None`` if all pass."""

        for validator_cls in self.VALIDATORS:
            result = validator_cls().validate(response)
            if not result.validation_successful:
                return result
        return None

    def _build_output(self, response: str) -> dict:
        try:
            return json.loads(response)
        except (json.JSONDecodeError, TypeError):
            return {"response": response}
