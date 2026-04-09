import io
from unittest.mock import MagicMock, patch

import pytest
from enthusiast_common.agentic_execution import BaseAgenticExecutionDefinition, ExecutionInputType, ExecutionResult
from model_bakery import baker

from account.models import User
from agent.agentic_execution.services import (
    AgenticExecutionService,
    FileUploadNotSupportedError,
    UnsupportedFileTypeError,
)
from agent.models.agent import Agent
from agent.models.agentic_execution import AgenticExecution
from agent.models.conversation import ConversationFile
from catalog.models import DataSet

pytestmark = pytest.mark.django_db

DUMMY_AGENT_TYPE = "dummy-agent-type"
SUPPORTED_EXTENSIONS = {(".pdf", ".txt"): "some.parser.Class"}


class DummyExecutionInput(ExecutionInputType):
    pass


class DummyExecution(BaseAgenticExecutionDefinition):
    EXECUTION_KEY = "dummy"
    AGENT_KEY = DUMMY_AGENT_TYPE
    NAME = "Dummy"
    INPUT_TYPE = DummyExecutionInput

    def run(self, input_data): return ExecutionResult(output={})


@pytest.fixture
def user():
    return baker.make(User)


@pytest.fixture
def dataset():
    return baker.make(DataSet)


@pytest.fixture
def agent(dataset):
    return baker.make(Agent, deleted_at=None, dataset=dataset, agent_type=DUMMY_AGENT_TYPE, file_upload=True)


@pytest.fixture
def service():
    return AgenticExecutionService()


def _make_file(name="doc.pdf", content=b"data", content_type="application/pdf"):
    f = io.BytesIO(content)
    f.name = name
    f.content_type = content_type
    return f


class TestStart:
    @pytest.fixture(autouse=True)
    def mock_task(self):
        with patch("agent.execution.services.run_agentic_execution_task.delay") as mock:
            mock.return_value = MagicMock(id="fake-celery-id")
            yield mock

    def test_creates_conversation_linked_to_agent_and_user(self, service, agent, user):
        execution = service.start(agent=agent, user=user, execution_key="dummy", validated_input={}, uploaded_files=[])

        assert execution.conversation.agent == agent
        assert execution.conversation.data_set == agent.dataset
        assert execution.conversation.user == user

    def test_creates_execution_record_with_input_and_key(self, service, agent, user):
        execution = service.start(agent=agent, user=user, execution_key="dummy", validated_input={"foo": "bar"}, uploaded_files=[])

        assert execution.input == {"foo": "bar"}
        assert execution.execution_key == "dummy"
        assert execution.status == AgenticExecution.Status.PENDING

    def test_stores_celery_task_id(self, service, agent, user):
        execution = service.start(agent=agent, user=user, execution_key="dummy", validated_input={}, uploaded_files=[])

        assert execution.celery_task_id == "fake-celery-id"

    def test_enqueues_task_with_execution_id(self, service, agent, user, mock_task):
        execution = service.start(agent=agent, user=user, execution_key="dummy", validated_input={}, uploaded_files=[])

        mock_task.assert_called_once_with(execution.pk)

    def test_raises_when_files_sent_to_non_file_upload_agent(self, service, user, dataset):
        non_upload_agent = baker.make(Agent, deleted_at=None, dataset=dataset, file_upload=False)

        with pytest.raises(FileUploadNotSupportedError):
            service.start(agent=non_upload_agent, user=user, execution_key="dummy", validated_input={}, uploaded_files=[_make_file()])

    def test_raises_for_unsupported_file_extension(self, service, agent, user):
        with patch("agent.execution.services.settings.FILE_PARSER_CLASSES", SUPPORTED_EXTENSIONS):
            with pytest.raises(UnsupportedFileTypeError) as exc_info:
                service.start(agent=agent, user=user, execution_key="dummy", validated_input={}, uploaded_files=[_make_file("photo.jpg")])

        assert exc_info.value.ext == ".jpg"

    def test_attaches_files_as_conversation_files(self, service, agent, user):
        with patch("agent.execution.services.settings.FILE_PARSER_CLASSES", SUPPORTED_EXTENSIONS), \
             patch("agent.execution.services.FileService.process", return_value="extracted"):
            execution = service.start(
                agent=agent, user=user, execution_key="dummy", validated_input={}, uploaded_files=[_make_file()]
            )

        conv_files = ConversationFile.objects.filter(conversation=execution.conversation)
        assert conv_files.count() == 1
        cf = conv_files.first()
        assert cf.is_hidden is False
        assert cf.llm_content == "extracted"
        assert cf.file_category == ConversationFile.FileCategory.FILE

    def test_detects_image_file_category(self, service, agent, user):
        with patch("agent.execution.services.settings.FILE_PARSER_CLASSES", {(".jpg",): "some.Class"}), \
             patch("agent.execution.services.FileService.process", return_value=""):
            execution = service.start(
                agent=agent, user=user, execution_key="dummy", validated_input={}, uploaded_files=[_make_file("photo.jpg", content_type="image/jpeg")]
            )

        cf = ConversationFile.objects.get(conversation=execution.conversation)
        assert cf.file_category == ConversationFile.FileCategory.IMAGE

    def test_no_conversation_files_created_when_no_files(self, service, agent, user):
        execution = service.start(agent=agent, user=user, execution_key="dummy", validated_input={}, uploaded_files=[])

        assert ConversationFile.objects.filter(conversation=execution.conversation).count() == 0
