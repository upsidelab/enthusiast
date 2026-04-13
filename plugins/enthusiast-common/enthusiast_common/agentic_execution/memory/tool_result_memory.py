from typing import Optional

from .tool_call_result import ToolCallResult


class ToolResultMemory:
    """Shared store that tools write to and validators read from during an agentic execution turn.

    One instance is created per ``ExecutionConversation`` and made available to tools
    via the injector. Tools that want their results to be inspectable by validators must
    explicitly call :meth:`record` inside their ``run()`` method. Validators receive the
    same instance and can query it by tool name.

    This is an opt-in contract between a tool implementation and a validator — the
    framework does not record anything automatically.

    Usage in a tool::

        def run(self, ...) -> str:
            result = do_work(...)
            if memory := self._injector.tool_result_memory:
                memory.record(self.NAME, result)
            return result

    Usage in a validator::

        class MyValidator(BaseExecutionValidator):
            def validate(self, response: str, tool_result_memory: Optional[ToolResultMemory] = None) -> ValidatorResponse:
                if tool_result_memory is None:
                    return ValidatorSuccessResponse()
                results = tool_result_memory.get_results("my_tool_name")
                # inspect what the tool chose to record...
    """

    def __init__(self) -> None:
        self._results: list[ToolCallResult] = []

    def record(self, tool_name: str, result: str) -> None:
        """Record an entry from a tool.

        Must be called explicitly inside the tool's ``run()`` method. The tool
        decides what to store — typically its return value, but it can be any
        string representation meaningful to the paired validator.

        Args:
            tool_name: The ``NAME`` class attribute of the tool.
            result: The value the tool chooses to persist for validator inspection.
        """
        self._results.append(ToolCallResult(tool_name=tool_name, result=result))

    def get_results(self, tool_name: Optional[str] = None) -> list[ToolCallResult]:
        """Return recorded results, optionally filtered by tool name.

        Args:
            tool_name: If provided, return only results for that tool.
                If ``None``, return all results.

        Returns:
            A snapshot list of :class:`ToolCallResult` objects.
        """
        if tool_name is None:
            return list(self._results)
        return [r for r in self._results if r.tool_name == tool_name]

    def clear(self) -> None:
        """Discard all recorded results.

        Called by ``BaseAgenticExecutionDefinition.run()`` before each retry
        so that validators only see tool results from the current attempt.
        """
        self._results.clear()
