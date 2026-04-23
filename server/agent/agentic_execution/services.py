import os

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import UploadedFile

from agent.agentic_execution.registry import AgenticExecutionDefinitionRegistry
from agent.agentic_execution.tasks import run_agentic_execution_task
from agent.models.agent import Agent
from agent.models.agentic_execution import AgenticExecution
from agent.models.conversation import Conversation, ConversationFile
from agent.services import ConversationFileMessageService, FileParsingService
from pecl import settings

User = get_user_model()


class UnsupportedFileTypeError(Exception):
    """Raised when an uploaded file's extension is not supported."""

    def __init__(self, ext: str, supported: list[str]):
        self.ext = ext
        self.supported = supported
        super().__init__(f"File type '{ext}' is not supported. Supported: {', '.join(supported)}.")


class FileUploadNotSupportedError(Exception):
    """Raised when files are submitted to an agent that does not support file uploads."""


class AgenticExecutionService:
    """Orchestrates the creation of an AgenticExecution and its associated resources."""

    def start(
        self,
        agent: Agent,
        user: User,
        execution_key: str,
        validated_input: dict,
        uploaded_files: list[UploadedFile],
    ) -> AgenticExecution:
        if uploaded_files and not agent.file_upload:
            raise FileUploadNotSupportedError()

        if uploaded_files:
            self._validate_file_extensions(uploaded_files)

        conversation = Conversation.objects.create(
            user=user,
            data_set=agent.dataset,
            agent=agent,
        )

        for f in uploaded_files:
            self._attach_file(conversation, f)

        execution = AgenticExecution.objects.create(
            agent=agent,
            execution_key=execution_key,
            conversation=conversation,
            input=validated_input,
        )
        task = run_agentic_execution_task.delay(execution.pk)
        execution.celery_task_id = task.id
        execution.save(update_fields=["celery_task_id"])

        return execution

    def get_execution_types(self, agent: Agent) -> list:
        """Return all registered agentic execution definition classes for the given agent type."""
        return AgenticExecutionDefinitionRegistry().get_by_agent_type(agent.agent_type)

    def _validate_file_extensions(self, uploaded_files: list[UploadedFile]) -> None:
        supported = []
        for extensions_tuple in settings.FILE_PARSER_CLASSES.keys():
            supported.extend(extensions_tuple)
        for f in uploaded_files:
            ext = os.path.splitext(f.name)[1].lower()
            if ext not in supported:
                raise UnsupportedFileTypeError(ext, supported)

    def _attach_file(self, conversation: Conversation, f: UploadedFile) -> None:
        content_type = getattr(f, "content_type", "") or ""
        file_category = (
            ConversationFile.FileCategory.IMAGE
            if content_type.startswith("image/")
            else ConversationFile.FileCategory.FILE
        )
        django_file = ContentFile(f.read(), name=f.name)
        llm_content = FileParsingService(django_file, content_type).process() or ""
        conversation_file = ConversationFile.objects.create(
            conversation=conversation,
            file=django_file,
            file_category=file_category,
            content_type=content_type,
            llm_content=llm_content,
            is_hidden=False,
        )
        ConversationFileMessageService.create_for_file(conversation_file)
