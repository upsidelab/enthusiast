from enthusiast_common.config import (
    AgentCallbackHandlerConfig,
    AgentConfigWithDefaults,
    CallbackHandlerConfig,
    LLMConfig,
    LLMToolConfig,
    RetrieverConfig,
    RetrieversConfig,
)
from enthusiast_common.config.base import PromptTemplateConfig
from langchain_core.callbacks import StdOutCallbackHandler

from agent.callbacks import AgentActionWebsocketCallbackHandler, ReactAgentWebsocketCallbackHandler
from agent.core.agents.product_search_react_agent.agent import ProductSearchReActAgent
from agent.core.agents.product_search_react_agent.prompt import PRODUCT_FINDER_AGENT_PROMPT
from agent.retrievers import DocumentRetriever
from agent.retrievers.product_vs_retriever import ProductVectorStoreRetriever
from agent.tools import ProductVectorStoreSearchTool
from agent.tools.verify_product_tool import ProductVerificationTool


def get_config(conversation_id: int, streaming: bool) -> AgentConfigWithDefaults:
    return AgentConfigWithDefaults(
        conversation_id=conversation_id,
        prompt_template=PromptTemplateConfig(
            input_variables=["tools", "tool_names", "input", "agent_scratchpad"], template=PRODUCT_FINDER_AGENT_PROMPT
        ),
        agent_class=ProductSearchReActAgent,
        llm_tools=[
            LLMToolConfig(
                tool_class=ProductVectorStoreSearchTool,
            ),
            LLMToolConfig(tool_class=ProductVerificationTool),
        ],
        llm=LLMConfig(
            callbacks=[
                CallbackHandlerConfig(
                    handler_class=ReactAgentWebsocketCallbackHandler, args={"conversation_id": conversation_id}
                ),
                CallbackHandlerConfig(handler_class=StdOutCallbackHandler),
            ],
            streaming=streaming,
        ),
        retrievers=RetrieversConfig(
            document=RetrieverConfig(retriever_class=DocumentRetriever),
            product=RetrieverConfig(retriever_class=ProductVectorStoreRetriever, extra_kwargs={"max_objects": 30}),
        ),
        agent_callback_handler=AgentCallbackHandlerConfig(
            handler_class=AgentActionWebsocketCallbackHandler, args={"conversation_id": conversation_id}
        ),
    )
