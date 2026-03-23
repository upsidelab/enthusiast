from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.parsers import JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from agent.execution.registry import AgentExecutionRegistry
from agent.execution.services import (
    AgentExecutionService,
    FileUploadNotSupportedError,
    UnsupportedFileTypeError,
)
from agent.models.agent import Agent
from agent.models.agent_execution import AgentExecution
from agent.serializers.agent_execution import (
    AgentExecutionDetailSerializer,
    AgentExecutionSerializer,
    AgentExecutionTypeSerializer,
    StartAgentExecutionSerializer,
)


class AgentExecutionTypesView(APIView):
    """List available execution types for a specific agent."""

    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Return all execution types registered for the given agent.",
        responses={
            200: AgentExecutionTypeSerializer(many=True),
            404: "Not Found — agent does not exist.",
        },
    )
    def get(self, request, agent_id):
        try:
            agent = Agent.objects.get(pk=agent_id)
        except Agent.DoesNotExist:
            return Response({"detail": "Agent not found."}, status=status.HTTP_404_NOT_FOUND)

        execution_classes = AgentExecutionService().get_execution_types(agent)
        data = [
            {
                "key": cls.EXECUTION_KEY,
                "name": cls.NAME,
                "description": cls.DESCRIPTION,
                "input_schema": cls.INPUT_TYPE.model_json_schema(),
            }
            for cls in execution_classes
        ]
        return Response(AgentExecutionTypeSerializer(data, many=True).data)


class StartAgentExecutionView(APIView):
    """Start a new execution for a specific agent."""

    parser_classes = (MultiPartParser, JSONParser)
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Start a new execution for the given agent. Accepts application/json or multipart/form-data (with optional files when agent.file_upload=True).",
        request_body=StartAgentExecutionSerializer,
        responses={
            202: AgentExecutionSerializer(),
            400: "Bad Request — execution_key is invalid, input is invalid, or files sent to a non-file-upload agent.",
            404: "Not Found — agent does not exist.",
        },
    )
    def post(self, request, agent_id):
        try:
            agent = Agent.objects.get(pk=agent_id)
        except Agent.DoesNotExist:
            return Response({"detail": "Agent not found."}, status=status.HTTP_404_NOT_FOUND)

        execution_key = request.data.get("execution_key", "")
        try:
            execution_cls = AgentExecutionRegistry().get_by_key(execution_key)
        except KeyError:
            return Response(
                {"detail": f"No execution class registered with EXECUTION_KEY='{execution_key}'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if execution_cls.AGENT_KEY != agent.agent_type:
            return Response(
                {"detail": f"Execution '{execution_key}' does not belong to this agent."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = StartAgentExecutionSerializer(
            data=request.data, context={"execution_cls": execution_cls}
        )
        serializer.is_valid(raise_exception=True)

        service = AgentExecutionService()
        try:
            execution = service.start(
                agent=agent,
                user=request.user,
                execution_key=execution_key,
                validated_input=serializer.validated_data["input"],
                uploaded_files=request.FILES.getlist("files"),
            )
        except FileUploadNotSupportedError:
            return Response({"detail": "This agent does not support file uploads."}, status=status.HTTP_400_BAD_REQUEST)
        except UnsupportedFileTypeError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(AgentExecutionSerializer(execution).data, status=status.HTTP_202_ACCEPTED)


class AgentExecutionListView(ListAPIView):
    """Paginated list of past executions, newest first."""

    permission_classes = [IsAuthenticated]
    serializer_class = AgentExecutionSerializer

    @swagger_auto_schema(
        operation_description="List all past agent executions, newest first. Optionally filter by agent_id.",
        manual_parameters=[
            openapi.Parameter(
                "dataset_id", openapi.IN_QUERY, description="Filter by dataset ID", type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                "agent_id", openapi.IN_QUERY, description="Filter by agent ID", type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                "status", openapi.IN_QUERY, description="Filter by status (pending, in_progress, finished, failed)", type=openapi.TYPE_STRING
            ),
        ],
        responses={200: AgentExecutionSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        qs = AgentExecution.objects.select_related("agent")
        dataset_id = self.request.query_params.get("dataset_id")
        if dataset_id:
            qs = qs.filter(agent__dataset_id=dataset_id)
        agent_id = self.request.query_params.get("agent_id")
        if agent_id:
            qs = qs.filter(agent_id=agent_id)
        status = self.request.query_params.get("status")
        if status:
            qs = qs.filter(status=status)
        return qs.order_by("-started_at")


class AgentExecutionDetailView(RetrieveAPIView):
    """Fetch a single execution record (used for status polling)."""

    permission_classes = [IsAuthenticated]
    serializer_class = AgentExecutionDetailSerializer

    @swagger_auto_schema(
        operation_description="Fetch a single execution record by ID.",
        manual_parameters=[
            openapi.Parameter("id", openapi.IN_PATH, description="ID of the execution", type=openapi.TYPE_INTEGER)
        ],
        responses={200: AgentExecutionDetailSerializer(), 404: "Not Found"},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return AgentExecution.objects.select_related("agent", "conversation")
