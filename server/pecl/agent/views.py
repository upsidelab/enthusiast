from datetime import datetime

from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from agent.models import Conversation, Question
from agent.serializers import AskQuestionSerializer
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


def conversation_view(request, conversation_id=None, embedding_model=None):
    # Populate context.
    available_models = []
    for m in EmbeddingModel.objects.all():
        available_models.append(m)
    available_dimensions = []
    for d in EmbeddingDimension.objects.all():
        available_dimensions.append(d)

    question_message = conversation_history = embedding_dimensions = embedding_model = None
    if request.method == 'POST':
        question_message = request.POST.get('user_message')
        selected_model_id = request.POST.get('selected_model')
        if selected_model_id:
            embedding_model = EmbeddingModel.objects.get(id=selected_model_id)
        selected_dimensions_id = request.POST.get('selected_dimensions')
        if selected_dimensions_id:
            embedding_dimensions = EmbeddingDimension.objects.get(id=selected_dimensions_id).dimension

    # Get conversation.
    conversation = initialize_conversation(conversation_id,
                                           embedding_model,
                                           embedding_dimensions,
                                           "WebUser",
                                           "WebSystem")

    conversation_history = conversation.get_history()

    # Get the answer if the question message was provided (a user pushed 'Send' button on a conversation page).
    if question_message:
        question = process_question(conversation, question_message)
        # Extend history with current question-answer pair.
        conversation_history += question.get_qa_str()

    context = {
        'conversation_id': conversation.id,
        'embedding_model': conversation.model.name,
        'embedding_dimensions': conversation.dimensions,
        'user_name': conversation.user_name,
        'system_name': conversation.system_name,
        'started_at': conversation.started_at,
        'available_models': available_models,
        'available_dimensions': available_dimensions,
        'conversation_history': conversation_history,
    }
    return render(request, 'ecl/conversation.html', context)


class GetAnswer(APIView):
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
