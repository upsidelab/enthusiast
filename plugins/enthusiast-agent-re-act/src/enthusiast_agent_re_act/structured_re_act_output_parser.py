import json
import re
from typing import Union

from langchain.agents.chat.output_parser import FINAL_ANSWER_ACTION
from langchain.agents.output_parsers import ReActSingleInputOutputParser
from langchain_core.agents import AgentAction, AgentFinish
from langchain_core.exceptions import OutputParserException


class StructuredReActOutputParser(ReActSingleInputOutputParser):
    ACTION_PATTERN: str = r"Action:\s*({[\s\S]*})"
    JSON_PATTERN: str = r"```json\s*\n([\s\S]*?)\n```"

    def parse(self, text: str) -> Union[AgentAction, AgentFinish]:
        if FINAL_ANSWER_ACTION in text:
            return AgentFinish({"output": text.split(FINAL_ANSWER_ACTION)[-1].strip()}, text)

        if match := re.search(self.ACTION_PATTERN, text, re.DOTALL):
            return self._return_action(match, text)
        if match := re.search(self.JSON_PATTERN, text, re.DOTALL):
            return self._return_action(match, text)
        raise OutputParserException(f"Could not parse LLM output: `{text}`")

    def _return_action(self, match: re.Match[str], text: str) -> AgentAction:
        json_str = match.group(1)
        action_response = json.loads(json_str)
        if action := action_response.get("action", None):
            return AgentAction(action, action_response.get("action_input", {}), text)
        raise OutputParserException(f"Could not parse LLM output: `{text}`")
