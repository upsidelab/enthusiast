from agent.models import Conversation, Message
from agent.registries.agents.agent_registry import AgentRegistry


class ConversationManager:
    def get_answer(self, conversation: Conversation, question_message, streaming) -> str:
        """Formulate an answer to a given question and store the decision-making process.

        Engine calculates embedding for a question and using similarity search collects documents that may contain
        relevant content.
        """
        agent = AgentRegistry().get_agent_by_name(conversation, streaming)
        response = agent.get_answer(question_message)

        return response

    def create_conversation(self, user_id: int, data_set_id: int, agent_name: str) -> Conversation:
        user = User.objects.get(id=user_id)
        data_set = user.data_sets.get(id=data_set_id)

        conversation = Conversation.objects.create(started_at=datetime.now(), user=user, data_set=data_set, agent=agent_name)
        return conversation

    def get_conversation(self, user_id: int, data_set_id: int, conversation_id: int) -> Conversation:
        user = User.objects.get(id=user_id)
        data_set = user.data_sets.get(id=data_set_id)
        return Conversation.objects.get(id=conversation_id, data_set=data_set, user=user)

    def respond_to_user_message(
        self, conversation_id: int, data_set_id: int, user_id: int, message: str, streaming: bool
    ) -> Message:
        conversation = self.get_conversation(user_id=user_id, data_set_id=data_set_id, conversation_id=conversation_id)

        # Set the conversation summary if it's the first message
        if not conversation.summary:
            conversation.summary = message
            conversation.save()

        self.get_answer(conversation, message, streaming)
        response = conversation.messages.order_by("created_at").last()

        return response

    def record_error(self, conversation_id: int, user_id: int, data_set_id: int, error: Exception):
        error_message = "We couldn't process your request at this time"

        conversation = self.get_conversation(user_id=user_id, data_set_id=data_set_id, conversation_id=conversation_id)
        Message.objects.create(conversation=conversation, created_at=datetime.now(), role="system", text=error_message)
