from unittest.mock import MagicMock, patch

import pytest
from django.urls import reverse
from django.utils import timezone
from enthusiast_common.agent_execution import BaseAgentExecution, ExecutionInputType, ExecutionResult
from model_bakery import baker
from rest_framework import status
from rest_framework.test import APIClient

from account.models import User
from agent.models.agent import Agent
from agent.models.agent_execution import AgentExecution
from catalog.models import DataSet

pytestmark = pytest.mark.django_db

DUMMY_AGENT_TYPE = "dummy-agent-type"


class DummyExecutionInput(ExecutionInputType):
    required_field: str
    optional_field: int = 10


class DummyExecution(BaseAgentExecution):
    EXECUTION_KEY = "dummy"
    AGENT_KEY = DUMMY_AGENT_TYPE
    NAME = "Dummy Execution"
    INPUT_TYPE = DummyExecutionInput

    def run(self, input_data: DummyExecutionInput) -> ExecutionResult:
        return ExecutionResult(output={})


class AllDefaultsExecutionInput(ExecutionInputType):
    optional_field: int = 10


class AllDefaultsExecution(BaseAgentExecution):
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
    return baker.make(AgentExecution, agent=agent, input={"required_field": "hello"})


class TestAgentExecutionListView:
    @pytest.fixture
    def url(self):
        return reverse("agent-execution-list")

    def test_returns_200(self, api_client, execution, url):
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["id"] == execution.id

    def test_filters_by_agent_id(self, api_client, dataset, url):
        agent1 = baker.make(Agent, deleted_at=None, dataset=dataset)
        agent2 = baker.make(Agent, deleted_at=None, dataset=dataset)
        exec1 = baker.make(AgentExecution, agent=agent1, input={})
        baker.make(AgentExecution, agent=agent2, input={})

        response = api_client.get(url, {"agent_id": agent1.id})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["id"] == exec1.id

    def test_returns_401_when_unauthenticated(self, url):
        response = APIClient().get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_returns_results_ordered_newest_first(self, api_client, agent, url):
        older = baker.make(AgentExecution, agent=agent, input={})
        newer = baker.make(AgentExecution, agent=agent, input={})

        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        ids = [r["id"] for r in response.data["results"]]
        assert ids.index(newer.id) < ids.index(older.id)


class TestAgentExecutionDetailView:
    @pytest.fixture
    def url(self, execution):
        return reverse("agent-execution-detail", kwargs={"pk": execution.pk})

    def test_returns_200(self, api_client, execution, url):
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == execution.id
        assert response.data["status"] == AgentExecution.Status.PENDING

    def test_returns_all_expected_fields(self, api_client, execution, url):
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        for field in ("id", "agent", "conversation", "status", "input", "result",
                      "failure_code", "failure_explanation", "celery_task_id",
                      "started_at", "finished_at", "duration_seconds"):
            assert field in response.data

    def test_returns_404_for_nonexistent(self, api_client):
        url = reverse("agent-execution-detail", kwargs={"pk": 99999})

        response = api_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_returns_401_when_unauthenticated(self, execution):
        url = reverse("agent-execution-detail", kwargs={"pk": execution.pk})

        response = APIClient().get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestStartAgentExecutionView:
    @pytest.fixture
    def url(self, agent):
        return reverse("agent-execution-start", kwargs={"agent_id": agent.pk})

    @pytest.fixture(autouse=True)
    def mock_registry(self):
        with patch(
            "agent.execution.views.AgentExecutionRegistry.get_by_agent_type",
            return_value=DummyExecution,
        ) as mock:
            yield mock

    def test_returns_404_for_nonexistent_agent(self, api_client):
        url = reverse("agent-execution-start", kwargs={"agent_id": 99999})

        response = api_client.post(url, {"input": {"required_field": "hello"}}, format="json")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_returns_404_for_soft_deleted_agent(self, api_client, dataset):
        deleted_agent = baker.make(Agent, deleted_at=timezone.now(), dataset=dataset, agent_type=DUMMY_AGENT_TYPE)
        url = reverse("agent-execution-start", kwargs={"agent_id": deleted_agent.pk})

        response = api_client.post(url, {"input": {"required_field": "hello"}}, format="json")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_returns_400_when_agent_type_has_no_execution_class(self, api_client, url, mock_registry):
        mock_registry.side_effect = KeyError("no class")

        response = api_client.post(url, {"input": {"required_field": "hello"}}, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_returns_400_when_required_input_field_missing(self, api_client, url):
        response = api_client.post(url, {"input": {}}, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "required_field" in response.data["input"]

    def test_empty_input_succeeds_when_all_fields_have_defaults(self, api_client, agent, mock_registry):
        mock_registry.return_value = AllDefaultsExecution
        url = reverse("agent-execution-start", kwargs={"agent_id": agent.pk})

        with patch("agent.execution.views.run_agent_execution_task.delay") as mock_delay:
            mock_delay.return_value = MagicMock(id="fake-celery-id")
            response = api_client.post(url, {"input": {}}, format="json")

        assert response.status_code == status.HTTP_202_ACCEPTED
        execution = AgentExecution.objects.get(pk=response.data["id"])
        assert execution.input == {"optional_field": 10}

    def test_returns_400_when_input_field_has_wrong_type(self, api_client, url):
        response = api_client.post(url, {"input": {"required_field": "ok", "optional_field": "not-an-int"}}, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "optional_field" in response.data["input"]

    def test_returns_400_when_input_has_extra_fields(self, api_client, url):
        response = api_client.post(
            url, {"input": {"required_field": "ok", "unknown_field": "surprise"}}, format="json"
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "unknown_field" in response.data["input"]

    def test_returns_401_when_unauthenticated(self, agent):
        url = reverse("agent-execution-start", kwargs={"agent_id": agent.pk})

        response = APIClient().post(url, {"input": {"required_field": "hello"}}, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_happy_path_creates_execution_record(self, api_client, url, agent):
        with patch("agent.execution.views.run_agent_execution_task.delay") as mock_delay:
            mock_delay.return_value = MagicMock(id="fake-celery-id")
            response = api_client.post(url, {"input": {"required_field": "hello"}}, format="json")

        assert response.status_code == status.HTTP_202_ACCEPTED
        assert AgentExecution.objects.filter(agent=agent).exists()
        execution = AgentExecution.objects.get(agent=agent)
        assert execution.input == {"required_field": "hello", "optional_field": 10}
        assert execution.status == AgentExecution.Status.PENDING

    def test_happy_path_coerces_input_types(self, api_client, url):
        with patch("agent.execution.views.run_agent_execution_task.delay") as mock_delay:
            mock_delay.return_value = MagicMock(id="fake-celery-id")
            response = api_client.post(
                url, {"input": {"required_field": "hello", "optional_field": "42"}}, format="json"
            )

        assert response.status_code == status.HTTP_202_ACCEPTED
        execution = AgentExecution.objects.get(pk=response.data["id"])
        assert execution.input["optional_field"] == 42

    def test_happy_path_enqueues_celery_task_with_execution_id(self, api_client, url):
        with patch("agent.execution.views.run_agent_execution_task.delay") as mock_delay:
            mock_delay.return_value = MagicMock(id="fake-celery-id")
            response = api_client.post(url, {"input": {"required_field": "hello"}}, format="json")

        assert response.status_code == status.HTTP_202_ACCEPTED
        execution_id = response.data["id"]
        mock_delay.assert_called_once_with(execution_id)

    def test_happy_path_stores_celery_task_id(self, api_client, url):
        with patch("agent.execution.views.run_agent_execution_task.delay") as mock_delay:
            mock_delay.return_value = MagicMock(id="fake-celery-id")
            response = api_client.post(url, {"input": {"required_field": "hello"}}, format="json")

        assert response.status_code == status.HTTP_202_ACCEPTED
        execution = AgentExecution.objects.get(pk=response.data["id"])
        assert execution.celery_task_id == "fake-celery-id"
