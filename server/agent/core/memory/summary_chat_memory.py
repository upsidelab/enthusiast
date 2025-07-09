from langchain.memory import ConversationSummaryBufferMemory

from .persist_intermediate_steps_mixin import PersistIntermediateStepsMixin


class SummaryChatMemory(PersistIntermediateStepsMixin, ConversationSummaryBufferMemory):
    """
    This memory persists intermediate steps, and summarizes the history passed back to the agent if the history
    exceeds the token limit.
    """

    pass
