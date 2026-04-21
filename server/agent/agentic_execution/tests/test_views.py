from unittest.mock import patch

import pytest
from django.urls import reverse
from django.utils import timezone
from enthusiast_common.agentic_execution import BaseAgenticExecutionDefinition, ExecutionInputType, ExecutionResult
from model_bakery import baker
from rest_framework import status
from rest_framework.test import APIClient

from account.models import User
from agent.agentic_execution.registry import AgenticExecutionDefinitionRegistry
from agent.agentic_execution.services import FileUploadNotSupportedError, UnsupportedFileTypeError
from agent.models.agent import Agent
from agent.models.agentic_execution import AgenticExecution
from catalog.models import DataSet

pytestmark = pytest.mark.django_db

DUMMY_AGENT_TYPE = "dummy-agent-type"


class DummyExecutionInput(ExecutionInputType):
    required_field: str
    optional_field: int = 10


class DummyExecution(BaseAgenticExecutionDefinition):
    EXECUTION_KEY = "dummy"
    AGENT_KEY = DUMMY_AGENT_TYPE
    NAME = "Dummy Execution"
    INPUT_TYPE = DummyExecutionInput

    def run(self, input_data: DummyExecutionInput) -> ExecutionResult:
        return ExecutionResult(output={})


class AllDefaultsExecutionInput(ExecutionInputType):
    optional_field: int = 10


class AllDefaultsExecution(BaseAgenticExecutionDefinition):
    EXECUTION_KEY = "all-defaults"
    AGENT_KEY = DUMMY_AGENT_TYPE
    NAME = "All Defaults Execution"
    INPUT_TYPE = AllDefaultsExecutionInput

    def run(self, input_data: AllDefaultsExecutionInput) -> ExecutionResult:
        return ExecutionResult(output={})


@pytest.fixture
def user():
    return baker.make(User)


@pytest.fixture
def api_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def dataset():
    return baker.make(DataSet)


@pytest.fixture
def agent(dataset):
    return baker.make(Agent, deleted_at=None, dataset=dataset, agent_type=DUMMY_AGENT_TYPE)


@pytest.fixture
def execution(agent):
    return baker.make(AgenticExecution, agent=agent, input={"required_field": "hello"})


class TestAgenticExecutionListView:
    @pytest.fixture
    def url(self):
        return reverse("agentic-execution-list")

    def test_returns_200(self, api_client, execution, url):
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["id"] == execution.id

    def test_filters_by_agent_id(self, api_client, dataset, url):
        agent1 = baker.make(Agent, deleted_at=None, dataset=dataset)
        agent2 = baker.make(Agent, deleted_at=None, dataset=dataset)
        exec1 = baker.make(AgenticExecution, agent=agent1, input={})
        baker.make(AgenticExecution, agent=agent2, input={})

        response = api_client.get(url, {"agent_id": agent1.id})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["id"] == exec1.id

    def test_returns_401_when_unauthenticated(self, url):
        response = APIClient().get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_returns_results_ordered_newest_first(self, api_client, agent, url):
        older = baker.make(AgenticExecution, agent=agent, input={})
        newer = baker.make(AgenticExecution, agent=agent, input={})

        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        ids = [r["id"] for r in response.data["results"]]
        assert ids.index(newer.id) < ids.index(older.id)


class TestAgenticExecutionDetailView:
    @pytest.fixture
    def url(self, execution):
        return reverse("agentic-execution-detail", kwargs={"pk": execution.pk})

    def test_returns_200(self, api_client, execution, url):
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == execution.id
        assert response.data["status"] == AgenticExecution.Status.PENDING

    def test_returns_all_expected_fields(self, api_client, execution, url):
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        for field in ("id", "agent", "execution_key", "conversation", "status", "input", "result",
                      "failure_code", "failure_explanation", "celery_task_id",
                      "started_at", "finished_at", "duration_seconds"):
            assert field in response.data

    def test_returns_404_for_nonexistent(self, api_client):
        url = reverse("agentic-execution-detail", kwargs={"pk": 99999})

        response = api_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_returns_401_when_unauthenticated(self, execution):
        url = reverse("agentic-execution-detail", kwargs={"pk": execution.pk})

        response = APIClient().get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestAgenticExecutionDefinitionTypesView:
    @pytest.fixture
    def url(self, agent):
        return reverse("agentic-execution-definitions", kwargs={"agent_id": agent.pk})

    @pytest.fixture(autouse=True)
    def mock_registry(self):
        with patch(
            "agent.agentic_execution.services.AgenticExecutionDefinitionRegistry.get_by_agent_type",
            return_value=[DummyExecution, AllDefaultsExecution],
        ) as mock:
            yield mock

    def test_returns_200_with_execution_types(self, api_client, url):
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    def test_returns_expected_fields_for_each_type(self, api_client, url):
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        for item in response.data:
            for field in ("key", "name", "description", "input_schema"):
                assert field in item

    def test_returns_correct_keys(self, api_client, url):
        response = api_client.get(url)

        keys = [item["key"] for item in response.data]
        assert "dummy" in keys
        assert "all-defaults" in keys

    def test_returns_404_for_nonexistent_agent(self, api_client):
        url = reverse("agentic-execution-definitions", kwargs={"agent_id": 99999})

        response = api_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_returns_401_when_unauthenticated(self, agent):
        url = reverse("agentic-execution-definitions", kwargs={"agent_id": agent.pk})

        response = APIClient().get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestStartAgenticExecutionView:
    @pytest.fixture
    def url(self, agent):
        return reverse("agentic-execution-start", kwargs={"agent_id": agent.pk})

    @pytest.fixture(autouse=True)
    def mock_registry(self):
        with patch.object(AgenticExecutionDefinitionRegistry, "get_by_key", return_value=DummyExecution) as mock:
            yield mock

    def test_returns_404_for_nonexistent_agent(self, api_client):
        url = reverse("agentic-execution-start", kwargs={"agent_id": 99999})

        response = api_client.post(
            url, {"execution_key": "dummy", "input": {"required_field": "hello"}}, format="json"
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_returns_404_for_soft_deleted_agent(self, api_client, dataset):
        deleted_agent = baker.make(Agent, deleted_at=timezone.now(), dataset=dataset, agent_type=DUMMY_AGENT_TYPE)
        url = reverse("agentic-execution-start", kwargs={"agent_id": deleted_agent.pk})

        response = api_client.post(
            url, {"execution_key": "dummy", "input": {"required_field": "hello"}}, format="json"
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_returns_400_when_execution_key_has_no_class(self, api_client, url, mock_registry):
        mock_registry.side_effect = KeyError("no class")

        response = api_client.post(
            url, {"execution_key": "unknown", "input": {"required_field": "hello"}}, format="json"
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_returns_400_when_required_input_field_missing(self, api_client, url):
        response = api_client.post(url, {"execution_key": "dummy", "input": {}}, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "required_field" in response.data["input"]

    def test_returns_400_when_input_field_has_wrong_type(self, api_client, url):
        response = api_client.post(
            url,
            {"execution_key": "dummy", "input": {"required_field": "ok", "optional_field": "not-an-int"}},
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "optional_field" in response.data["input"]

    def test_returns_400_when_input_has_extra_fields(self, api_client, url):
        response = api_client.post(
            url,
            {"execution_key": "dummy", "input": {"required_field": "ok", "unknown_field": "surprise"}},
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "unknown_field" in response.data["input"]

    def test_returns_400_when_service_raises_file_upload_not_supported(self, api_client, url):
        with patch("agent.agentic_execution.views.AgenticExecutionService.start", side_effect=FileUploadNotSupportedError()):
            response = api_client.post(
                url, {"execution_key": "dummy", "input": {"required_field": "hello"}}, format="json"
            )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "file upload" in response.data["detail"].lower()

    def test_returns_400_when_service_raises_unsupported_file_type(self, api_client, url):
        with patch("agent.agentic_execution.views.AgenticExecutionService.start", side_effect=UnsupportedFileTypeError(".xyz", [".pdf"])):
            response = api_client.post(
                url, {"execution_key": "dummy", "input": {"required_field": "hello"}}, format="json"
            )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_returns_401_when_unauthenticated(self, agent):
        url = reverse("agentic-execution-start", kwargs={"agent_id": agent.pk})

        response = APIClient().post(
            url, {"execution_key": "dummy", "input": {"required_field": "hello"}}, format="json"
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_happy_path_returns_202_with_execution_data(self, api_client, url):
        with patch("agent.agentic_execution.views.AgenticExecutionService.start") as mock_start, \
             patch("agent.agentic_execution.services.run_agentic_execution_task.delay"):
            mock_execution = baker.prepare(AgenticExecution)
            mock_execution.pk = 1
            mock_start.return_value = mock_execution
            response = api_client.post(
                url, {"execution_key": "dummy", "input": {"required_field": "hello"}}, format="json"
            )

        assert response.status_code == status.HTTP_202_ACCEPTED

    def test_happy_path_passes_correct_args_to_service(self, api_client, url, agent, user):
        with patch("agent.agentic_execution.views.AgenticExecutionService.start") as mock_start, \
             patch("agent.agentic_execution.services.run_agentic_execution_task.delay"):
            mock_start.return_value = baker.make(AgenticExecution, agent=agent, execution_key="dummy")
            api_client.post(
                url, {"execution_key": "dummy", "input": {"required_field": "hello"}}, format="json"
            )

        mock_start.assert_called_once()
        call_kwargs = mock_start.call_args.kwargs
        assert call_kwargs["agent"] == agent
        assert call_kwargs["user"] == user
        assert call_kwargs["execution_key"] == "dummy"
        assert call_kwargs["validated_input"] == {"required_field": "hello", "optional_field": 10}
        assert call_kwargs["uploaded_files"] == []
