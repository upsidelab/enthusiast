---
sidebar_position: 6
---

# Concept: Data extraction Agent
This example will walk you through a concept of Agent(ReAct), which extracts data from web page verifies results.


## Creating an Agent
Start by creating an agent directory, and then create:

### Prompt
A structured ReAct-style prompt:
````python
DATA_EXTRACTION_AGENT_PROMPT = """

I want you to help extract data from webpage HTML about {products_type} products using the ReACT (Reasoning and Acting) approach.
Answer should be always in shape: {output_format}
Always verify your answer
Use a json blob to specify a tool by providing an action key (tool name) and an action_input key (tool input).

Valid "action" values: {tool_names}

Provide only ONE action per $JSON_BLOB, as shown:

```
{{
  "action": $TOOL_NAME,
  "action_input": $INPUT
}}
```
For each step, follow the format:
User query: Web page Html
Thought: what you should do next
Action: 
{{
  "action": "<tool>",
  "action_input": <tool_input>
}}
Observation: the result returned by the tool
... (repeat Thought/Action/Action Input/Observation as needed)
Thought: I now have the necessary information
Final Answer: the response to the user

Here are the tools you can use:
{tools}

Example 1:
User query: web page data
Thought: I need to extract relevant data
Action: {{
 "action": the tool to use, one of [{tool_names}],
 "action_input": <tool_input>
 }}
Observation: I got the data.
Thought: I need to verify it.
Action:
 {{
 "action": the verification tool to use, one of [{tool_names}],
 "action_input": <tool_input>
 }}
Observation: I got verified data.
Final Answer: extracted data


Do not came up with any other types of JSON than specified above.
Your output to user should always begin with '''Final Answer: <output>'''
Begin!
Chat history: {chat_history}
User query: {input}
{agent_scratchpad}"""
````
### Output parser
Reuse output parser from previous example.

### Tools
Create two tools
1. Data Extraction Tool – responsible for scrape data from website.

```python
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from enthusiast_common.injectors import BaseInjector
from enthusiast_common.tools import BaseLLMTool
from langchain_core.language_models import BaseLanguageModel
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field



class DataExtractionToolInput(BaseModel):
    url: str = Field(description="URL for website to get data from")


class DataExtractionTool(BaseLLMTool):
    NAME = "data_extraction_tool"
    DESCRIPTION = (
        "Always use this tool. Use this tool to data from web page."
    )
    ARGS_SCHEMA = DataExtractionToolInput
    RETURN_DIRECT = False

    def __init__(
        self,
        data_set_id: int,
        llm: BaseLanguageModel,
        injector: BaseInjector | None,
    ):
        super().__init__(data_set_id=data_set_id, llm=llm, injector=injector)
        self.data_set_id = data_set_id
        self.llm = llm
        self.injector = injector


    def _is_valid_url(self, url: str) -> bool:
        parsed = urlparse(url)
        return all([parsed.scheme, parsed.netloc])

    def run(self, url: str) -> str:
        if not self._is_valid_url(url):
            return "Invalid URL"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        return soup.get_text(separator="\n", strip=True)
```
2. Data Verification Tool – verifies whether the retrieved data it relevant.
```python
from enthusiast_common.injectors import BaseInjector
from enthusiast_common.tools import BaseLLMTool
from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field


VERIFY_DATA_PROMPT_TEMPLATE = """
You are verifying extracted data that describes a hotel.

{data}

Check if any extracted values are realistic for a hotel room.

Ignore minor deviations.
Flag only when the data is extremely unlikely to be true for a hotel.

Return:
Brief summary of anything that looks suspicious.
"""


class DataVerificationToolInput(BaseModel):
    data: str = Field(description="extracted data")


class DataVerificationTool(BaseLLMTool):
    NAME = "data_verification_tool"
    DESCRIPTION = (
        "Always use this tool. Use this tool to verify if a data has expected shape and it's relevant to product type."
    )
    ARGS_SCHEMA = DataVerificationToolInput
    RETURN_DIRECT = False

    def __init__(
        self,
        data_set_id: int,
        llm: BaseLanguageModel,
        injector: BaseInjector | None,
    ):
        super().__init__(data_set_id=data_set_id, llm=llm, injector=injector)
        self.data_set_id = data_set_id
        self.llm = llm
        self.injector = injector

    def run(self, data: str) -> StructuredTool:
        prompt = PromptTemplate.from_template(VERIFY_DATA_PROMPT_TEMPLATE)
        chain = prompt | self.llm

        llm_result = chain.invoke(
            {
                "data": data,
            }
        )
        return f"You received the following validation report {llm_result.content}. Respond with the product json, and if any field looks suspicious, add a field called <fieldname>_warning with description of the issue."
```
### Agent
```python
import json

from enthusiast_agent_re_act import BaseReActAgent

class DataExtractionReActAgent(BaseReActAgent):
    def get_answer(self, input_text: str) -> str:
        agent_executor = self._build_agent_executor()
        template_dict = {
            "check_in_time": "<time>",
            "checkout_time": "<time>",
            "pets_allowed": "<boolean>",
            "quite_hours": "<time-time>",
            "address": "<full address string>",
            "price": "<number with currency>",
            "rating": "<number>"
        }

        output_format = json.dumps(template_dict)
        agent_output = agent_executor.invoke(
            {
                "input": input_text,
                "output_format": output_format,
                "products_type": "Hotel",
            },
            config=self._build_invoke_config()
        )
        result = agent_output["output"]
        try:
            parsed = json.loads(result)
            result = json.dumps(parsed, indent=4)
        except json.JSONDecodeError:
            pass

        return result
```

### Callback handlers
Re-use Callback handlers from previous example.

### Configuration
Create configuration inside `config.py` file:
```python
from enthusiast_common.config import (
    AgentCallbackHandlerConfig,
    AgentConfigWithDefaults,
    LLMConfig,
    LLMToolConfig,
)
from langchain_core.callbacks import StdOutCallbackHandler
from langchain_core.prompts import PromptTemplate

from .callbacks import AgentActionWebsocketCallbackHandler, ReactAgentWebsocketCallbackHandler
from .agent import DataExtractionReActAgent
from .prompt import DATA_EXTRACTION_AGENT_PROMPT
from .tools.data_extraction import DataExtractionTool
from .tools.data_verification import DataVerificationTool


def get_config(conversation_id: int, streaming: bool) -> AgentConfigWithDefaults:
    return AgentConfigWithDefaults(
        conversation_id=conversation_id,
        prompt_template=PromptTemplate(
            input_variables=["tools", "tool_names", "input", "agent_scratchpad"], template=DATA_EXTRACTION_AGENT_PROMPT
        ),
        agent_class=DataExtractionReActAgent,
        llm_tools=[
            LLMToolConfig(
                tool_class=DataVerificationTool,
            ),
            LLMToolConfig(
                tool_class=DataExtractionTool,
            )
        ],
        llm=LLMConfig(
            callbacks=[ReactAgentWebsocketCallbackHandler(conversation_id), StdOutCallbackHandler()],
            streaming=streaming,
        ),
        agent_callback_handler=AgentCallbackHandlerConfig(
            handler_class=AgentActionWebsocketCallbackHandler, args={"conversation_id": conversation_id}
        ),
    )

```
Finally add your agent to `settings_override.py`:
```python
AVAILABLE_AGENTS = {
    "Data Extraction Agent": "enthusiast_custom.examples.data_extraction.data_extraction",
}
```
