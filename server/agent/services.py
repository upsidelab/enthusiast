from datetime import datetime

from account.models import CustomUser
from agent.core import Agent
from agent.models import Conversation, Message
from ecl.models import EmbeddingModel, EmbeddingDimension


class ConversationManager:

    def get_answer(self, conversation: Conversation, question_message):
        """Formulate an answer to a given question and store the decision-making process.

        Engine calculates embedding for a question and using similarity search collects documents that may contain
        relevant content.
        """
        agent = Agent(data_set=conversation.data_set,
                      embedding_model=conversation.model,
                      embedding_dimensions=conversation.dimensions,
                      messages=conversation.get_messages())
        response = agent.process_user_request(question_message)

        return response["output"]

    def initialize_conversation(self, user_id, data_set_id, conversation_id=None,embedding_model=None,
                                embedding_dimensions=None, system_name=None):
        user = CustomUser.objects.get(id=user_id)
        data_set = user.data_sets.get(id=data_set_id)
        # Create a new or continue an existing conversation.
        if conversation_id is not None:
            conversation = Conversation.objects.get(id=conversation_id, data_set=data_set)
        else:
            # Load default model and dimensions if not defined in params.
            if not embedding_model:
                embedding_model = EmbeddingModel.objects.first()
            if not embedding_dimensions:
                embedding_dimensions = EmbeddingDimension.objects.first()

            # Start a new conversation.
            conversation = Conversation.objects.create(started_at=datetime.now(),
                                                       model=embedding_model,
                                                       dimensions=embedding_dimensions,
                                                       user=CustomUser.objects.get(id=user_id),
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

    def answer_question(self, conversation_id, data_set_id, embedding_model_name, embedding_dimensions_value,
                        user_id, system_name, question_message):

        # Collect required objects.
        embedding_dimensions = embedding_model = None
        if embedding_model_name:
            embedding_model = EmbeddingModel.objects.get(name=embedding_model_name)
        if embedding_dimensions_value:
            embedding_dimensions = EmbeddingDimension.objects.get(dimensions=embedding_dimensions_value)

        # Get conversation.
        conversation = self.initialize_conversation(user_id=user_id,
                                                    data_set_id=data_set_id,
                                                    conversation_id=conversation_id,
                                                    embedding_model=embedding_model,
                                                    embedding_dimensions=embedding_dimensions,
                                                    system_name=system_name)

        # Get the answer.
        return self.process_question(conversation, question_message)
