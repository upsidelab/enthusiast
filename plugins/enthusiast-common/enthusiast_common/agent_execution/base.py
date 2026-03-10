import json
from abc import ABC, abstractmethod
from typing import ClassVar, Protocol, Type

from .errors import ExecutionFailureCode
from .input import ExecutionInputType
from .result import ExecutionResult
from .validators import BaseExecutionValidator, IsValidJsonValidator


class ExecutionConversationInterface(Protocol):
    """Minimal protocol for conversation interaction during an execution run."""

    def ask(self, message: str) -> str:
        ...


class BaseAgentExecution(ABC):
    """Abstract base class for all agentic executions."""

    EXECUTION_KEY: ClassVar[str]
    AGENT_KEY: ClassVar[str]
    NAME: ClassVar[str]
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
        """Orchestrate the validator retry loop and return the final result."""

        response = self.execute(input_data, conversation)

        for attempt in range(self.MAX_RETRIES + 1):
            feedback = self._first_validator_feedback(response)

            if feedback is None:
                return ExecutionResult(success=True, output=self._build_output(response))

            if attempt < self.MAX_RETRIES:
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
        """Perform a single execution attempt and return the raw LLM response."""

        pass

    def _first_validator_feedback(self, response: str) -> str | None:
        """Run all validators and return the first feedback message, or None."""

        for validator_cls in self.VALIDATORS:
            feedback = validator_cls().validate(response)
            if feedback is not None:
                return feedback
        return None

    def _build_output(self, response: str) -> dict:
        try:
            return json.loads(response)
        except (json.JSONDecodeError, TypeError):
            return {"response": response}
