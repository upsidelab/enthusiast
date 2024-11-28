from celery.result import AsyncResult

from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from agent.models import Conversation, Message
from agent.serializers import AskQuestionSerializer, ConversationSerializer, ConversationContentSerializer, \
    MessageFeedbackSerializer, ConversationCreationSerializer
from agent.services import ConversationManager


class GetTaskStatus(APIView):
    permission_classes = [IsAuthenticated]
    """
    View to check status of an enqueued task that's running in the background.
    """

    def get(self, request, task_id):
        task_result = AsyncResult(task_id)
        if task_result.state == 'FAILURE':
            response = {
                "state": task_result.state,
                "status": str(task_result.info)
            }
        else:
            response = {"state": task_result.state}

        return Response(response)


class ConversationCreateView(APIView):
    permission_classes = [IsAuthenticated]
    """
    View to initialize a new conversation.
    """

    def post(self, request):
        manager = ConversationManager()
        input_serializer = ConversationCreationSerializer(data=request.data)
        if not input_serializer.is_valid():
            return Response(input_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        conversation = manager.initialize_conversation(user_id=request.user.id,
                                                       data_set_id=input_serializer.validated_data.get("data_set_id"))

        conversation_data = ConversationSerializer(conversation).data

        serializer = ConversationContentSerializer({
            **conversation_data,  # Conversation details
            "history": []
        })
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ConversationRetrieveView(APIView):
    permission_classes = [IsAuthenticated]
    """
    View to retrieve details of an existing conversation.
    """
    def get(self, request, conversation_id):
        conversation = Conversation.objects.get(id=conversation_id)

        messages = Message.objects.filter(conversation=conversation).order_by('id')

        conversation_data = ConversationSerializer(conversation).data

        serializer = ConversationContentSerializer({
            **conversation_data,  # Conversation details
            "history": messages
        })
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, conversation_id):
        serializer = AskQuestionSerializer(data=request.data)
        if serializer.is_valid():
            from agent.tasks import answer_question_task
            # Collect params.
            data_set_id = serializer.validated_data.get('data_set_id')
            embedding_model_name = serializer.validated_data.get('embedding_model_name')

            embedding_dimensions_value = serializer.validated_data.get('embedding_dimensions')
            system_name = serializer.validated_data.get('system_name')
            question_message = serializer.validated_data.get('question_message')

            # Run the task asynchronously.
            task = answer_question_task.apply_async(args=[conversation_id,
                                                          data_set_id,
                                                          embedding_model_name,
                                                          embedding_dimensions_value,
                                                          request.user.id,
                                                          system_name,
                                                          question_message])

            return Response({"task_id": task.id}, status=status.HTTP_202_ACCEPTED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ConversationListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ConversationSerializer

    def get_queryset(self):
        return Conversation.objects.filter(data_set_id=self.kwargs['data_set_id'])


class MessageFeedbackView(APIView):
    permission_classes = [IsAuthenticated]
    """View to provide feedback on a message."""
    def patch(self, request, id):
        try:
            message = Message.objects.get(id=id)
        except Message.DoesNotExist:
            return Response({"error": "Message not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = MessageFeedbackSerializer(message, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
