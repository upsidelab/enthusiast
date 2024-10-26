from datetime import datetime

from django.shortcuts import render
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from agent.models import Conversation, Question
from agent.serializers import AskQuestionSerializer, ConversationSerializer
from ecl.models import EmbeddingModel, EmbeddingDimension, DataSet


def initialize_conversation(conversation_id, embedding_model, embedding_dimensions, user_name, system_name):
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
                                    user_name=user_name,
                                    system_name=system_name,
                                    data_set=DataSet.objects.first())
        conversation.save()  # Save it now to allow adding child entities such as questions (connected by foreign key).
    return conversation


def process_question(conversation, question_message):
    # Ask your question.
    question = Question(conversation=conversation,
                        asked_at=datetime.now(),
                        question=question_message)
    question.save()  # Save it now to allow adding child entities such as relevant documents (connected by foreign key).
    question.get_answer()
    question.save()
    return question


class GetAnswer(APIView):
    permission_classes = [IsAuthenticated]
    """
    View to handle the question message and return the answer.
    """

    def post(self, request):
        serializer = AskQuestionSerializer(data=request.data)
        if serializer.is_valid():
            # Collect params.
            conversation_id = serializer.validated_data.get('conversation_id')
            embedding_model_name = serializer.validated_data.get('embedding_model_name')
            embedding_dimensions = serializer.validated_data.get('embedding_dimensions')
            user_name = serializer.validated_data.get('user_name')
            system_name = serializer.validated_data.get('system_name')
            question_message = serializer.validated_data.get('question_message')

            # Collect required objects.
            embedding_model = None
            if embedding_model_name:
                embedding_model = EmbeddingModel.objects.get(name=embedding_model_name)

            # Get conversation.
            conversation = initialize_conversation(conversation_id,
                                                   embedding_model,
                                                   embedding_dimensions,
                                                   user_name,
                                                   system_name)
            # Get the answer.
            question = process_question(conversation, question_message)

            return Response({
                'conversation_id': question.conversation.id,
                'query_message': question.question,
                'answer': question.answer},
                status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ConversationListView(ListAPIView):
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Conversation.objects.filter(data_set_id=self.kwargs['data_set_id']).select_related('model', 'dimensions', 'data_set')