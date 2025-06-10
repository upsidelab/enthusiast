from langchain.memory import ConversationTokenBufferMemory

from agent.core.persist_intermediate_steps_mixin import PersistIntermediateStepsMixin


class LimitedChatMemory(PersistIntermediateStepsMixin, ConversationTokenBufferMemory):
    """
    This memory persists intermediate steps, and limits the amount of tokens passed back to the agent to
    what's defined as max_token_limit.
    """

    pass
