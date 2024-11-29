from langchain_openai import ChatOpenAI


class LlmProvider:
    @staticmethod
    def provide_llm_instance():
        return ChatOpenAI(model="gpt-4o")
