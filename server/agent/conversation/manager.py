from datetime import datetime

from account.models import User
from agent.core import Agent
from agent.models import Conversation, Message


class ConversationManager:

    def get_answer(self, conversation: Conversation, question_message):
        """Formulate an answer to a given question and store the decision-making process.

        Engine calculates embedding for a question and using similarity search collects documents that may contain
        relevant content.
        """
        agent = Agent(data_set=conversation.data_set,
                      messages=conversation.get_messages())
        response = agent.process_user_request(question_message)

        return response["output"]

    def create_conversation(self, user_id: int, data_set_id: int):
        user = User.objects.get(id=user_id)
        data_set = user.data_sets.get(id=data_set_id)

        conversation = Conversation.objects.create(started_at=datetime.now(),
                                                   user=user,
                                                   data_set=data_set)
        return conversation

    def get_conversation(self, user_id: int, data_set_id: int, conversation_id: int):
        user = User.objects.get(id=user_id)
        data_set = user.data_sets.get(id=data_set_id)
        return Conversation.objects.get(id=conversation_id, data_set=data_set, user=user)

    def respond_to_user_message(self, conversation_id: int, data_set_id: int, user_id: int, message: str):
        conversation = self.get_conversation(user_id=user_id,
                                             data_set_id=data_set_id,
                                             conversation_id=conversation_id)

        user_message = Message.objects.create(conversation=conversation,
                                              created_at=datetime.now(),
                                              role='user',
                                              text=message)

        # Set the conversation summary if it's the first message
        if not conversation.summary:
            conversation.summary = user_message.text
            conversation.save()

        response_text = self.get_answer(conversation, user_message.text)
        response = Message.objects.create(conversation=conversation,
                                          created_at=datetime.now(),
                                          role='agent',
                                          text=response_text)

        return response

    def record_error(self, conversation_id: int, user_id: int, data_set_id: int, error: Exception):
        error_message = "We couldn't process your request at this time"

        conversation = self.get_conversation(user_id=user_id, data_set_id=data_set_id, conversation_id=conversation_id)
        Message.objects.create(conversation=conversation,
                               created_at=datetime.now(),
                               role="agent_error",
                               text=error_message)