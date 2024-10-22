from langchain.agents.agent_toolkits import create_conversational_retrieval_agent
from langchain_core.messages import SystemMessage

from ecl.models import DataSet, EmbeddingModel, EmbeddingDimension
from agent.core.llm_provider import LlmProvider
from agent.tools import CreateContentTool


class Agent:
    def __init__(self, data_set: DataSet, embedding_model: EmbeddingModel, embedding_dimensions: EmbeddingDimension):
        self._llm = LlmProvider.provide_llm_instance()
        self._tools = [CreateContentTool(
            data_set=data_set,
            embedding_model=embedding_model,
            embedding_dimensions=embedding_dimensions,
            chat_model=self._llm.model_name
        )]
        self._system_message = SystemMessage(
            "You are an agent that knows everything about company\'s product catalog and content")
        self._agent = create_conversational_retrieval_agent(
            llm=self._llm,
            tools=self._tools,
            system_message=self._system_message,
            verbose=True
        )

    def process_user_request(self, prompt: str):
        return self._agent.invoke({"input": prompt})
