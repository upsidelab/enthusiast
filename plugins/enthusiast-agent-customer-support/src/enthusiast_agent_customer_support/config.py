from enthusiast_common.config import (
    AgentConfigWithDefaults,
    RetrieverConfig,
    RetrieversConfig,
)
from enthusiast_common.config.prompts import PromptTemplateConfig

from .agent import UserManualReActAgent
from .document_retriever import ManualsDocumentRetriever
from .product_retriever import QUERY_PROMPT_TEMPLATE, ProductRetriever
from .prompt import USER_MANUAL_AGENT_PROMPT


def get_config() -> AgentConfigWithDefaults:
    return AgentConfigWithDefaults(
        prompt_template=PromptTemplateConfig(
            input_variables=["tools", "tool_names", "input", "agent_scratchpad"],
            prompt_template=USER_MANUAL_AGENT_PROMPT,
        ),
        agent_class=UserManualReActAgent,
        tools=UserManualReActAgent.TOOLS,
        retrievers=RetrieversConfig(
            document=RetrieverConfig(retriever_class=ManualsDocumentRetriever),
            product=RetrieverConfig(
                retriever_class=ProductRetriever,
                extra_kwargs={
                    "prompt_template": QUERY_PROMPT_TEMPLATE,
                    "max_sample_products": 12,
                    "number_of_products": 12,
                },
            ),
        ),
    )
