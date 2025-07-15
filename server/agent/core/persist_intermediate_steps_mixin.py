import typing
from abc import ABC
from typing import Any, Dict

from langchain.memory import ConversationBufferMemory
from langchain_core.messages import AIMessage, FunctionMessage, HumanMessage


class PersistIntermediateStepsMixin(ABC):
    """
    This mixin can be added to a ConversationBufferMemory class in order to persist agent's function calls.
    """

    def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, str]) -> None:
        self_as_conversation_memory = typing.cast(ConversationBufferMemory, self)

        human_message = HumanMessage(inputs["input"])
        self_as_conversation_memory.chat_memory.add_message(human_message)

        if "intermediate_steps" in outputs:
            for agent_action, result in outputs["intermediate_steps"]:
                self_as_conversation_memory.chat_memory.add_message(agent_action.messages[0])

                function_message = FunctionMessage(name=agent_action.tool, content=result)
                self_as_conversation_memory.chat_memory.add_message(function_message)

        ai_message = AIMessage(outputs["output"])
        self_as_conversation_memory.chat_memory.add_message(ai_message)
