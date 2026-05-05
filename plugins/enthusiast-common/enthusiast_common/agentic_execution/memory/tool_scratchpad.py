from typing import Any


class ToolScratchpad:
    """Shared store that tools write to and validators read from during an agentic execution turn.

    One instance is created per ``ExecutionConversation`` and made available to tools
    via the injector. Each tool name maps to a single stored value — recording again
    overwrites the previous entry. Validators receive the same instance and query it
    by tool name.

    This is an opt-in contract between a tool implementation and a validator — the
    framework does not record anything automatically.

    Usage in a tool::

        def run(self, ...) -> str:
            result = do_work(...)
            if scratchpad := self._injector.tool_scratchpad:
                scratchpad.record(self.NAME, result)
            return result

    Usage in a validator::

        entry = tool_scratchpad.read("my_tool_name")
        if entry is None:
            return ValidatorSuccessResponse()
        # inspect what the tool chose to record...
    """

    def __init__(self) -> None:
        self._store: dict[str, Any] = {}

    def record(self, tool_name: str, result: Any) -> None:
        """Record a result for a tool, overwriting any previous entry."""
        self._store[tool_name] = result

    def read(self, tool_name: str) -> Any | None:
        """Return the recorded result for the given tool, or ``None`` if not recorded."""
        return self._store.get(tool_name)

    def clear(self) -> None:
        """Discard all recorded results.

        Called by ``BaseAgenticExecutionDefinition.run()`` before each retry
        so that validators only see tool results from the current attempt.
        """
        self._store.clear()
