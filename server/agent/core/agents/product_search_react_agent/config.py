from enthusiast_common.config import (
    AgentCallbackHandlerConfig,
    AgentConfig,
    AgentConfigWithDefaults,
    LLMConfig,
    LLMToolConfig,
    RetrieverConfig,
    RetrieversConfig,
)
from langchain_core.callbacks import StdOutCallbackHandler
from langchain_core.prompts import PromptTemplate

from agent.callbacks import AgentActionWebsocketCallbackHandler, ReactAgentWebsocketCallbackHandler
from agent.core.agents.default_config import merge_config
from agent.core.agents.product_search_react_agent.agent import ProductSearchReActAgent
from agent.core.agents.product_search_react_agent.prompt import PRODUCT_FINDER_AGENT_PROMPT
from agent.models import Conversation
from agent.retrievers import DocumentRetriever
from agent.retrievers.product_vs_retriever import ProductVectorStoreRetriever
from agent.tools import ProductVectorStoreSearchTool
from agent.tools.verify_product_tool import ProductVerificationTool


def get_config(conversation: Conversation, streaming: bool) -> AgentConfig:
    base_config = AgentConfigWithDefaults(
        conversation_id=conversation.id,
        prompt_template=PromptTemplate(
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
            callbacks=[ReactAgentWebsocketCallbackHandler(conversation.id), StdOutCallbackHandler()],
            streaming=streaming,
        ),
        retrievers=RetrieversConfig(
            document=RetrieverConfig(retriever_class=DocumentRetriever),
            product=RetrieverConfig(retriever_class=ProductVectorStoreRetriever, extra_kwargs={"max_objects": 30}),
        ),
        agent_callback_handler=AgentCallbackHandlerConfig(
            handler_class=AgentActionWebsocketCallbackHandler, args={"conversation_id": conversation.id}
        ),
    )
    return merge_config(base_config)
