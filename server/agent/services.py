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

    def initialize_conversation(self, user_id, data_set_id, conversation_id=None, system_name=None):
        user = User.objects.get(id=user_id)
        data_set = user.data_sets.get(id=data_set_id)
        # Create a new or continue an existing conversation.
        if conversation_id is not None:
            conversation = Conversation.objects.get(id=conversation_id, data_set=data_set, user=user)
        else:
            # Start a new conversation.
            conversation = Conversation.objects.create(started_at=datetime.now(),
                                                       user=user,
                                                       system_name=system_name,
                                                       data_set=data_set)
        return conversation

    def process_question(self, conversation, question_message):
        # Define a question.
        question = Message.objects.create(conversation=conversation,
                                          created_at=datetime.now(),
                                          role='user',
                                          text=question_message)
        # Define an answer.
        answer = Message.objects.create(conversation=conversation,
                                        created_at=datetime.now(),
                                        role='agent',
                                        text=self.get_answer(conversation, question.text))
        return answer

    def answer_question(self, conversation_id, data_set_id, user_id, system_name, question_message):

        # Get conversation.
        conversation = self.initialize_conversation(user_id=user_id,
                                                    data_set_id=data_set_id,
                                                    conversation_id=conversation_id,
                                                    system_name=system_name)

        # Get the answer.
        return self.process_question(conversation, question_message)

    def record_error(self, conversation_id: int, user_id: int, data_set_id: int, error: Exception):
        error_message = "We couldn't process your request at this time"

        conversation = self.initialize_conversation(user_id=user_id, data_set_id=data_set_id, conversation_id=conversation_id)
        Message.objects.create(conversation=conversation,
                               created_at=datetime.now(),
                               role="agent_error",
                               text=error_message)