from celery.result import AsyncResult

from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from agent.models import Conversation
from agent.serializers import AskQuestionSerializer, ConversationSerializer


class GetAnswer(APIView):
    permission_classes = [IsAuthenticated]
    """
    View to handle the question message and return the answer.
    """

    def post(self, request):
        serializer = AskQuestionSerializer(data=request.data)
        if serializer.is_valid():
            from agent.tasks import answer_question_task
            # Collect params.
            conversation_id = serializer.validated_data.get('conversation_id')
            embedding_model_name = serializer.validated_data.get('embedding_model_name')
            embedding_dimensions_value = serializer.validated_data.get('embedding_dimensions')
            user_name = serializer.validated_data.get('user_name')
            system_name = serializer.validated_data.get('system_name')
            question_message = serializer.validated_data.get('question_message')

            # Run the task asynchronously.
            task = answer_question_task.apply_async(args=[conversation_id,
                                                          embedding_model_name,
                                                          embedding_dimensions_value,
                                                          user_name,
                                                          system_name,
                                                          question_message])

            return Response({"task_id": task.id}, status=status.HTTP_202_ACCEPTED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetTaskStatus(APIView):
    permission_classes = [IsAuthenticated]
    """
    View to check status of an enqueued task that's runed in the background.
    """

    def get(self, request, task_id):
        task_result = AsyncResult(task_id)
        if task_result.state == 'PENDING':
            response = {"state": task_result.state, "status": "Pending..."}
        elif task_result.state == 'SUCCESS':
            response = {
                "state": task_result.state,
                "result": task_result.result
            }
        elif task_result.state == 'FAILURE':
            response = {
                "state": task_result.state,
                "status": str(task_result.info)
            }
        else:
            response = {"state": task_result.state}

        return Response(response)


class ConversationListView(ListAPIView):
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Conversation.objects.filter(data_set_id=self.kwargs['data_set_id']).select_related('model', 'dimensions', 'data_set')