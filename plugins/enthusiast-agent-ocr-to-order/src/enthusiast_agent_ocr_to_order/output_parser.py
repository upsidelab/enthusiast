from typing import Union

from enthusiast_agent_re_act import StructuredReActOutputParser
from langchain.agents.chat.output_parser import FINAL_ANSWER_ACTION
from langchain_core.agents import AgentAction, AgentFinish
from langchain_core.exceptions import OutputParserException


class CustomStructuredReActOutputParser(StructuredReActOutputParser):
    def parse(self, text: str) -> Union[AgentAction, AgentFinish]:
        try:
            return super().parse(text)
        except OutputParserException:
            raise OutputParserException(
                f"Could not parse LLM output: `{text}`",
                observation=f"If it's answer or question for a user add '{FINAL_ANSWER_ACTION}' prefix",
                llm_output=text,
                send_to_llm=True,
            )
