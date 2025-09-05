from celery.result import AsyncResult
from django.conf import settings
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.generics import ListAPIView
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from agent.conversation import ConversationManager
from agent.core.registries.agents.agent_registry import AgentRegistry
from agent.core.registries.language_models import LanguageModelRegistry
from agent.core.repositories import DjangoDataSetRepository
from agent.filters import AgentFilter
from agent.models import Conversation, Message
from agent.models.agent import Agent
from agent.serializers.configuration import (
    AgentListSerializer,
    AgentSerializer,
    AvailableAgentsResponseSerializer,
)
from agent.serializers.conversation import (
    AskQuestionSerializer,
    ConversationContentSerializer,
    ConversationCreationSerializer,
    ConversationFileSerializer,
    ConversationMultiFileUploadSerializer,
    ConversationSerializer,
    MessageFeedbackSerializer,
)
from agent.tasks import respond_to_user_message_task
from agent.utils.functions import get_model_descriptor_from_class_field
from catalog.models import DataSet


class GetTaskStatus(APIView):
    permission_classes = [IsAuthenticated]
    """
    View to check status of an enqueued task that's running in the background.
    """

    @swagger_auto_schema(
        operation_description="Check the status of a task",
        manual_parameters=[
            openapi.Parameter("task_id", openapi.IN_PATH, description="ID of the task", type=openapi.TYPE_STRING)
        ],
        responses={
            200: openapi.Response(
                description="Task status",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT, properties={"state": openapi.Schema(type=openapi.TYPE_STRING)}
                ),
            )
        },
    )
    def get(self, request, task_id):
        task_result = AsyncResult(task_id)
        response = {"state": task_result.state}

        return Response(response)


class ConversationView(APIView):
    permission_classes = [IsAuthenticated]
    """
    View to retrieve details of an existing conversation.
    """

    @swagger_auto_schema(
        operation_description="Retrieve details of a conversation",
        manual_parameters=[
            openapi.Parameter(
                "conversation_id", openapi.IN_PATH, description="ID of the conversation", type=openapi.TYPE_INTEGER
            )
        ],
        responses={200: ConversationContentSerializer()},
    )
    def get(self, request, conversation_id):
        conversation = (
            Conversation.objects.select_related("agent")
            .prefetch_related(Prefetch("messages", queryset=Message.objects.order_by("id")))
            .get(id=conversation_id, user=request.user)
        )
        serializer = ConversationContentSerializer(conversation)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Ask a question in a conversation",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "data_set_id": openapi.Schema(type=openapi.TYPE_INTEGER, description="ID of the data set"),
                "question_message": openapi.Schema(type=openapi.TYPE_STRING, description="Question message"),
            },
        ),
    )
    def post(self, request, conversation_id):
        conversation = get_object_or_404(Conversation, id=conversation_id)
        serializer = AskQuestionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        if conversation.agent.deleted_at is not None:
            return Response({"detail": "Conversation locked."}, status=status.HTTP_400_BAD_REQUEST)

        data_set_id = serializer.validated_data.get("data_set_id")
        question_message = serializer.validated_data.get("question_message")
        streaming = serializer.validated_data.get("streaming")
        data_set = Conversation.objects.get(id=conversation_id).data_set
        data_set_repo = DjangoDataSetRepository(DataSet)
        language_model_provider_class = LanguageModelRegistry(data_set_repo).provider_for_dataset(data_set.id)
        task = respond_to_user_message_task.apply_async(
            kwargs={
                "conversation_id": conversation_id,
                "data_set_id": data_set_id,
                "user_id": request.user.id,
                "message": question_message,
                "streaming": streaming,
            }
        )

        return Response(
            {"task_id": task.id, "streaming": language_model_provider_class.STREAMING_AVAILABLE and streaming},
            status=status.HTTP_202_ACCEPTED,
        )


class ConversationListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ConversationSerializer

    @swagger_auto_schema(
        operation_description="List conversations for a user",
        manual_parameters=[
            openapi.Parameter(
                "data_set_id", openapi.IN_QUERY, description="ID of the data set", type=openapi.TYPE_INTEGER
            )
        ],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        user = self.request.user
        data_set_id = self.request.query_params.get("data_set_id")
        if data_set_id:
            return Conversation.objects.filter(data_set_id=data_set_id, user=user).order_by("-started_at")
        else:
            return Conversation.objects.filter(user=user).order_by("-started_at")

    @swagger_auto_schema(
        operation_description="Create a new conversation",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={"data_set_id": openapi.Schema(type=openapi.TYPE_INTEGER, description="ID of the data set")},
        ),
    )
    def post(self, request):
        manager = ConversationManager()
        input_serializer = ConversationCreationSerializer(data=request.data)
        if not input_serializer.is_valid():
            return Response(input_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        try:
            conversation = manager.create_conversation(
                user_id=request.user.id,
                agent_id=input_serializer.validated_data.get("agent_id"),
            )
        except Agent.DoesNotExist:
            raise NotFound("Agent not found.")

        conversation = Conversation.objects.select_related("agent").prefetch_related("messages").get(pk=conversation.pk)
        serializer = ConversationContentSerializer(conversation)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MessageFeedbackView(APIView):
    permission_classes = [IsAuthenticated]
    """View to provide feedback on a message."""

    @swagger_auto_schema(
        operation_description="Provide feedback on a message",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "feedback": openapi.Schema(type=openapi.TYPE_STRING, description="Feedback"),
                "rating": openapi.Schema(type=openapi.TYPE_INTEGER, description="Rating"),
            },
        ),
        manual_parameters=[
            openapi.Parameter("id", openapi.IN_PATH, description="ID of the message", type=openapi.TYPE_INTEGER)
        ],
    )
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


class AgentTypesView(APIView):
    permission_classes = [IsAuthenticated]

    """View to get available agents."""

    @swagger_auto_schema(
        operation_description="Get available Agents", responses={200: AvailableAgentsResponseSerializer()}
    )
    def get(self, request):
        agent_registry = AgentRegistry()
        choices = []
        for key, value in settings.AVAILABLE_AGENTS.items():
            agent_class = agent_registry.get_agent_class_by_type(agent_type=key)
            choices.append(
                {
                    "name": value["name"],
                    "key": key,
                    "agent_args": get_model_descriptor_from_class_field(agent_class, "AGENT_ARGS"),
                    "prompt_input": get_model_descriptor_from_class_field(agent_class, "PROMPT_INPUT"),
                    "prompt_extension": get_model_descriptor_from_class_field(agent_class, "PROMPT_EXTENSION"),
                    "tools": [
                        get_model_descriptor_from_class_field(tool_config.tool_class, "CONFIGURATION_ARGS")
                        for tool_config in agent_class.TOOLS
                    ],
                }
            )
        response_serializer = AvailableAgentsResponseSerializer(data={"choices": choices})
        response_serializer.is_valid(raise_exception=True)

        return Response(response_serializer.data, status=status.HTTP_200_OK)


class AgentView(APIView):
    permission_classes = [IsAuthenticated]
    """View to get/create agents"""

    @swagger_auto_schema(
        operation_description="List all agents for a dataset",
        manual_parameters=[
            openapi.Parameter(
                "dataset",
                openapi.IN_QUERY,
                description="ID of the dataset",
                type=openapi.TYPE_INTEGER,
                required=True,
            )
        ],
        responses={200: AgentListSerializer(many=True)},
    )
    def get(self, request):
        if request.user.is_staff:
            queryset = Agent.objects.all().order_by("created_at")
        else:
            queryset = Agent.objects.filter(corrupted=False).order_by("created_at")
        filterset = AgentFilter(request.GET, queryset=queryset)
        if not filterset.is_valid():
            return Response(filterset.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer = AgentListSerializer(filterset.qs, many=True)
        return Response(serializer.data, status=200)

    @swagger_auto_schema(
        operation_description="Create a new agent.",
        request_body=AgentSerializer,
        responses={201: AgentSerializer()},
    )
    def post(self, request):
        serializer = AgentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        return Response(AgentSerializer(instance).data, status=status.HTTP_201_CREATED)


class AgentDetailsView(APIView):
    permission_classes = [IsAuthenticated]
    """View to get manage agents"""

    @swagger_auto_schema(operation_description="Get a single configuration by id.", responses={200: AgentSerializer()})
    def get(self, request, pk):
        instance = get_object_or_404(Agent, pk=pk)
        serializer = AgentSerializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Update an existing configuration by id.",
        request_body=AgentSerializer,
        responses={200: AgentSerializer()},
    )
    def put(self, request, pk=None):
        instance = get_object_or_404(Agent, pk=pk)

        serializer = AgentSerializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(corrupted=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Delete a configuration by id.", responses={204: "No Content", 404: "Not Found"}
    )
    def delete(self, request, pk=None):
        instance = get_object_or_404(Agent, pk=pk)
        instance.set_deleted_at()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ConversationFileUploadView(APIView):
    parser_classes = (MultiPartParser,)
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Upload files to conversation.",
        request_body=ConversationMultiFileUploadSerializer,
        responses={200: ConversationFileSerializer(many=True)},
    )
    def post(self, request, conversation_id, *args, **kwargs):
        conversation = get_object_or_404(Conversation, pk=conversation_id)

        serializer = ConversationMultiFileUploadSerializer(data=request.data, context={"conversation": conversation})
        serializer.is_valid(raise_exception=True)

        objs = serializer.save()

        return Response(
            ConversationFileSerializer(objs, many=True).data,
            status=status.HTTP_201_CREATED,
        )
