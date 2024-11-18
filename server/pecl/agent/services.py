from datetime import datetime
from agent.models import Conversation, Question
from account.models import CustomUser
from ecl.models import EmbeddingModel, EmbeddingDimension, DataSet

class ConversationManager:
    def initialize_conversation(self, conversation_id, embedding_model, embedding_dimensions, user_id, system_name):
        # Create a new or continue an existing conversation.
        if conversation_id is not None:
            conversation = Conversation.objects.get(id=conversation_id)
        else:
            # Load default model and dimensions if not defined in params.
            if not embedding_model:
                embedding_model = EmbeddingModel.objects.first()
            if not embedding_dimensions:
                embedding_dimensions = EmbeddingDimension.objects.first()

            # Start a new conversation.
            conversation = Conversation(started_at=datetime.now(),
                                        model=embedding_model,
                                        dimensions=embedding_dimensions,
                                        user=CustomUser.objects.get(id=user_id),
                                        system_name=system_name,
                                        data_set=DataSet.objects.first())
            conversation.save()  # Save it now to allow adding child entities such as questions (connected by foreign key).
        return conversation

    def process_question(self, conversation, question_message):
        # Ask your question.
        question = Question(conversation=conversation,
                            asked_at=datetime.now(),
                            question=question_message)
        question.save()  # Save it now to allow adding child entities such as relevant documents (connected by foreign key).
        question.get_answer()
        question.save()
        return question

    def answer_question(self, conversation_id, embedding_model_name, embedding_dimensions_value,
                        user_id, system_name, question_message):

        # Collect required objects.
        embedding_dimensions = embedding_model = None
        if embedding_model_name:
            embedding_model = EmbeddingModel.objects.get(name=embedding_model_name)
        if embedding_dimensions_value:
            embedding_dimensions = EmbeddingDimension.objects.get(dimensions=embedding_dimensions_value)

        # Get conversation.
        conversation = self.initialize_conversation(conversation_id,
                                               embedding_model,
                                               embedding_dimensions,
                                               user_id,
                                               system_name)

        # Get the answer.
        return self.process_question(conversation, question_message)
