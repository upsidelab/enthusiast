from enthusiast_common.config import (
    AgentConfigWithDefaults,
    RetrieverConfig,
    RetrieversConfig,
)
from enthusiast_common.config.prompts import ChatPromptTemplateConfig, Message, MessageRole

from ..document_retriever import DocumentRetriever
from ..product_retriever import ProductRetriever
from ..product_retriever_prompt import CUSTOM_QUERY_PROMPT_TEMPLATE
from .agent import ProductSearchToolCallingAgent
from .prompt import PRODUCT_SEARCH_TOOL_CALLING_AGENT_PROMPT


def get_config() -> AgentConfigWithDefaults:
    return AgentConfigWithDefaults(
        prompt_template=ChatPromptTemplateConfig(
            messages=[
                Message(
                    role=MessageRole.SYSTEM,
                    content=PRODUCT_SEARCH_TOOL_CALLING_AGENT_PROMPT,
                ),
                Message(role=MessageRole.PLACEHOLDER, content="{chat_history}"),
                Message(role=MessageRole.USER, content="{input}"),
                Message(role=MessageRole.PLACEHOLDER, content="{agent_scratchpad}"),
            ]
        ),
        agent_class=ProductSearchToolCallingAgent,
        tools=ProductSearchToolCallingAgent.TOOLS,
        retrievers=RetrieversConfig(
            document=RetrieverConfig(retriever_class=DocumentRetriever),
            product=RetrieverConfig(
                retriever_class=ProductRetriever,
                extra_kwargs={
                    "prompt_template": CUSTOM_QUERY_PROMPT_TEMPLATE,
                    "max_sample_products": 12,
                    "number_of_products": 12,
                },
            ),
        ),
    )
