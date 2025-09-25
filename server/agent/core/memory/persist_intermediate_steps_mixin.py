import json
from abc import ABC
from typing import Any, Dict, Literal, cast

from langchain.agents.output_parsers.tools import ToolAgentAction
from langchain.memory import ConversationBufferMemory
from langchain_core.messages import AIMessage, BaseMessage, FunctionMessage, HumanMessage

from agent.models import Message


class WidgetMessage(BaseMessage):
    type: Literal["widget"] = "widget"
    widget_data: dict


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
                if isinstance(agent_action, ToolAgentAction):
                    intermediate_step_message = BaseMessage(
                        type=Message.MessageType.INTERMEDIATE_STEP, content=agent_action.log
                    )
                else:
                    intermediate_step_message = BaseMessage(
                        type=Message.MessageType.INTERMEDIATE_STEP, content=agent_action.messages[0].content
                    )
                self_as_conversation_memory.chat_memory.add_message(intermediate_step_message)
                if result:
                    function_message = FunctionMessage(name=agent_action.tool, content=result)
                    self_as_conversation_memory.chat_memory.add_message(function_message)
        if outputs.get("output") is not None:
            try:
                json_object = json.loads(outputs["output"])
                ai_message = WidgetMessage(
                    content=f"Widget representation of data: {json_object['data']}", widget_data=json_object
                )
                self_as_conversation_memory.chat_memory.add_message(ai_message)
            except Exception:
                ai_message = AIMessage(outputs["output"])
                self_as_conversation_memory.chat_memory.add_message(ai_message)
