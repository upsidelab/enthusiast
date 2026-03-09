from abc import ABC, abstractmethod
from typing import ClassVar, Type

from .input import ExecutionInputType
from .result import ExecutionResult


class BaseExecutionValidator(ABC):
    """Pluggable strategy that decides whether an execution should continue.

    Implementations track per-item success/failure rates and produce a human-
    readable issue summary when the execution completes or is stopped early.
    """

    @abstractmethod
    def should_continue(self) -> bool:
        """Return True if the execution should proceed to the next item.

        Returns:
            bool: False when the stop threshold has been reached.
        """
        pass

    @abstractmethod
    def get_issue_summary(self) -> list[str]:
        """Return a list of human-readable descriptions of non-fatal issues.

        Returns:
            list[str]: Issue descriptions collected during the run so far.
        """
        pass


class BaseAgentExecution(ABC):
    """Abstract base class for all agentic executions.

    Subclasses must declare :attr:`EXECUTION_KEY` (a unique slug used as the
    identifier throughout the system) and :attr:`NAME` (a human-readable UI
    label).  Optionally override :attr:`INPUT_TYPE` with a concrete
    :class:`ExecutionInputType` subclass to declare structured input.

    The server discovers available execution types via
    ``settings.AVAILABLE_AGENT_EXECUTIONS`` and registers them in
    ``AgentExecutionRegistry``.

    Example::

        class CatalogEnrichmentExecution(BaseAgentExecution):
            EXECUTION_KEY = "catalog-enrichment"
            NAME = "Catalog Enrichment"
            INPUT_TYPE = CatalogEnrichmentExecutionInput

            def run(self, input_data: CatalogEnrichmentExecutionInput) -> ExecutionResult:
                ...
    """

    EXECUTION_KEY: ClassVar[str]
    NAME: ClassVar[str]
    INPUT_TYPE: ClassVar[Type[ExecutionInputType]] = ExecutionInputType

    @abstractmethod
    def run(self, input_data: ExecutionInputType) -> ExecutionResult:
        """Execute the agent job and return its result.

        This method is called by the Celery task after the execution record has
        been marked ``in_progress``.  It must return an :class:`ExecutionResult`
        on success and raise an exception on failure — the task wrapper handles
        transitioning the record to the appropriate terminal state.

        Args:
            input_data: Validated input produced by deserializing the stored
                ``AgentExecution.input`` JSON via :attr:`INPUT_TYPE`.

        Returns:
            ExecutionResult: The structured output and optional summary/issues.
        """
        pass
