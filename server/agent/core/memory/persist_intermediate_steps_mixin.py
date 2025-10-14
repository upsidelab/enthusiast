from abc import ABC
from typing import Any, Dict, cast

from langchain.memory import ConversationBufferMemory
from langchain_core.messages import AIMessage, BaseMessage, FunctionMessage, HumanMessage

from agent.models import Message


class PersistIntermediateStepsMixin(ABC):
    """
    This mixin can be added to a ConversationBufferMemory class in order to persist agent's function calls.
    """

    def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, str]) -> None:
        self_as_conversation_memory = cast(ConversationBufferMemory, self)

        human_message = HumanMessage(inputs["input"])
        self_as_conversation_memory.chat_memory.add_message(human_message)

        if "intermediate_steps" in outputs:
            for agent_action, result in outputs["intermediate_steps"]:
                intermediate_step_message = BaseMessage(
                    type=Message.MessageType.INTERMEDIATE_STEP, content=agent_action.messages[0].content
                )
                self_as_conversation_memory.chat_memory.add_message(intermediate_step_message)

                function_message = FunctionMessage(name=agent_action.tool, content=result)
                self_as_conversation_memory.chat_memory.add_message(function_message)

        ai_message = AIMessage(outputs["output"])
        self_as_conversation_memory.chat_memory.add_message(ai_message)
