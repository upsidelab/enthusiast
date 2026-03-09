from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from agent.execution.registry import AgentExecutionRegistry
from agent.models.agent_execution import AgentExecution
from agent.serializers.agent_execution import (
    AgentExecutionSerializer,
    AgentExecutionTypeSerializer,
    StartAgentExecutionSerializer,
)
from agent.tasks import run_agent_execution_task


class AgentExecutionTypeListView(APIView):
    """List all available execution types with their input JSON Schemas."""

    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="List all available execution types with their input JSON Schemas.",
        responses={200: AgentExecutionTypeSerializer(many=True)},
    )
    def get(self, request):
        registry = AgentExecutionRegistry()
        data = [
            {
                "key": cls.EXECUTION_KEY,
                "name": cls.NAME,
                "input_schema": cls.INPUT_TYPE.model_json_schema(),
            }
            for cls in registry.get_all()
        ]
        serializer = AgentExecutionTypeSerializer(data, many=True)
        return Response(serializer.data)


class AgentExecutionListView(ListAPIView):
    """Paginated list of past executions (newest first) and start a new one."""

    permission_classes = [IsAuthenticated]
    serializer_class = AgentExecutionSerializer
    queryset = AgentExecution.objects.all()

    @swagger_auto_schema(
        operation_description="List all past agent executions, newest first.",
        responses={200: AgentExecutionSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Start a new agent execution.",
        request_body=StartAgentExecutionSerializer,
        responses={202: AgentExecutionSerializer()},
    )
    def post(self, request):
        serializer = StartAgentExecutionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        execution = AgentExecution.objects.create(
            execution_type=serializer.validated_data["execution_type"],
            input=serializer.validated_data["input"],
        )
        task = run_agent_execution_task.delay(execution.pk)
        execution.celery_task_id = task.id
        execution.save(update_fields=["celery_task_id"])

        return Response(AgentExecutionSerializer(execution).data, status=status.HTTP_202_ACCEPTED)


class AgentExecutionDetailView(RetrieveAPIView):
    """Fetch a single execution record (used for status polling)."""

    permission_classes = [IsAuthenticated]
    serializer_class = AgentExecutionSerializer
    queryset = AgentExecution.objects.all()

    @swagger_auto_schema(
        operation_description="Fetch a single execution record by ID.",
        manual_parameters=[
            openapi.Parameter("id", openapi.IN_PATH, description="ID of the execution", type=openapi.TYPE_INTEGER)
        ],
        responses={200: AgentExecutionSerializer(), 404: "Not Found"},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
