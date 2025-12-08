from enthusiast_common.config import (
    AgentConfigWithDefaults,
    RetrieverConfig,
    RetrieversConfig,
)
from enthusiast_common.config.prompts import PromptTemplateConfig

from ..document_retriever import DocumentRetriever
from ..product_retriever import ProductRetriever
from ..product_retriever_prompt import CUSTOM_QUERY_PROMPT_TEMPLATE
from .agent import ProductSearchReActAgent
from .prompt import PRODUCT_SEARCH_AGENT_PROMPT


def get_config() -> AgentConfigWithDefaults:
    return AgentConfigWithDefaults(
        prompt_template=PromptTemplateConfig(
            input_variables=["tools", "tool_names", "input", "agent_scratchpad"],
            prompt_template=PRODUCT_SEARCH_AGENT_PROMPT,
        ),
        agent_class=ProductSearchReActAgent,
        tools=ProductSearchReActAgent.TOOLS,
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
