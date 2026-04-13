from dataclasses import dataclass


@dataclass
class ToolCallResult:
    """A single entry recorded by a tool into :class:`ToolResultMemory`.

    Attributes:
        tool_name: The ``NAME`` of the tool that recorded this entry.
        result: Whatever the tool chose to persist — typically its ``run()`` return value,
            but the tool implementation decides what and how much to store.
    """

    tool_name: str
    result: str
