from unittest.mock import MagicMock, patch

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db


class TestConversationFileUploadView:
    @pytest.fixture
    def url(self, conversation):
        return reverse("conversation-upload", kwargs={"conversation_id": conversation.id})

    def test_upload_unauthenticated_returns_401(self, url):
        test_file = SimpleUploadedFile("test.txt", b"test content", content_type="text/plain")
        data = {"file": test_file}
        client = APIClient()

        response = client.post(url, data, format="multipart")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @override_settings(
        FILE_PARSER_CLASSES={
            (".txt",): "FakeClass",
        }
    )
    @patch("agent.views.process_file_upload_task.apply_async")
    def test_upload_single_file_success(self, mock_task, api_client, url, conversation):
        mock_task.return_value = MagicMock(id="fake-task-id")
        test_file = SimpleUploadedFile("test.txt", b"test content", content_type="text/plain")
        data = {"file": test_file}

        response = api_client.post(url, data, format="multipart")

        assert response.status_code == status.HTTP_202_ACCEPTED
        assert response.data["task_id"] == "fake-task-id"
        mock_task.assert_called_once()

        # Check that task was called with correct parameters
        call_kwargs = mock_task.call_args[1]["kwargs"]
        assert call_kwargs["conversation_id"] == conversation.id
        assert call_kwargs["filename"] == "test.txt"
        assert call_kwargs["content_type"] == "text/plain"
        assert call_kwargs["file_content"] == b"test content"

    def test_upload_nonexistent_conversation_returns_404(self, api_client):
        url = reverse("conversation-upload", kwargs={"conversation_id": 99999})
        test_file = SimpleUploadedFile("test.txt", b"test content", content_type="text/plain")
        data = {"file": test_file}

        response = api_client.post(url, data, format="multipart")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_upload_missing_file_returns_400(self, api_client, url):
        data = {}

        response = api_client.post(url, data, format="multipart")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "error" in response.data
        assert "No file provided" in response.data["error"]

    @patch("agent.views.process_file_upload_task.apply_async")
    def test_upload_unsupported_file_type_returns_400(self, mock_task, api_client, url):
        test_file = SimpleUploadedFile("test.xyz", b"test content", content_type="application/xyz")
        data = {"file": test_file}

        response = api_client.post(url, data, format="multipart")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "error" in response.data
        assert "File type .xyz is not supported" in response.data["error"]
        mock_task.assert_not_called()

    @override_settings(
        FILE_PARSER_CLASSES={
            (".pdf",): "agent.parsers.TextFileParser",
        }
    )
    @patch("agent.views.process_file_upload_task.apply_async")
    def test_upload_supported_file_type_success(self, mock_task, api_client, url):
        mock_task.return_value = MagicMock(id="fake-task-id")
        test_file = SimpleUploadedFile("test.pdf", b"test content", content_type="application/pdf")
        data = {"file": test_file}

        response = api_client.post(url, data, format="multipart")

        assert response.status_code == status.HTTP_202_ACCEPTED
        assert response.data["task_id"] == "fake-task-id"
        mock_task.assert_called_once()

    def test_upload_with_invalid_data_format_returns_415(self, api_client, url):
        data = {"file": "not_a_file"}

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_415_UNSUPPORTED_MEDIA_TYPE


class TestFileUploadStatusView:
    @pytest.fixture
    def url(self):
        return reverse("file-upload-status", kwargs={"task_id": "fake-task-id"})

    def test_get_status_unauthenticated_returns_401(self, url):
        client = APIClient()

        response = client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @patch("agent.views.AsyncResult")
    def test_get_status_success(self, mock_async_result, api_client, url):
        mock_result = MagicMock()
        mock_result.status = "SUCCESS"
        mock_result.result = {"status": "SUCCESS", "result": {"file_id": 123, "filename": "test.txt"}}
        mock_async_result.return_value = mock_result

        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["task_id"] == "fake-task-id"
        assert response.data["status"] == "SUCCESS"
        assert response.data["result"]["file_id"] == 123
        assert response.data["result"]["filename"] == "test.txt"

    @patch("agent.views.AsyncResult")
    def test_get_status_failure(self, mock_async_result, api_client, url):
        mock_result = MagicMock()
        mock_result.status = "FAILURE"
        mock_result.result = Exception("Processing failed")
        mock_async_result.return_value = mock_result

        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["task_id"] == "fake-task-id"
        assert response.data["status"] == "FAILURE"
        assert "error" in response.data["result"]

    @patch("agent.views.AsyncResult")
    def test_get_status_pending(self, mock_async_result, api_client, url):
        mock_result = MagicMock()
        mock_result.status = "PENDING"
        mock_result.result = None
        mock_async_result.return_value = mock_result

        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["task_id"] == "fake-task-id"
        assert response.data["status"] == "PENDING"

    @patch("agent.views.AsyncResult")
    def test_get_status_exception_returns_500(self, mock_async_result, api_client, url):
        mock_async_result.side_effect = Exception("Celery error")

        response = api_client.get(url)

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "error" in response.data
        assert "Failed to get task status" in response.data["error"]


class TestSupportedFileTypesView:
    @pytest.fixture
    def url(self):
        return reverse("supported-file-types")

    def test_get_supported_file_types_unauthenticated_returns_401(self, url):
        client = APIClient()

        response = client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @patch(
        "agent.views.settings.FILE_PARSER_CLASSES", {(".txt", ".pdf"): "parser_class", (".jpg", ".png"): "image_parser"}
    )
    def test_get_supported_file_types_success(self, api_client, url):
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert "supported_extensions" in response.data
        supported_extensions = response.data["supported_extensions"]

        # Should include all extensions from FILE_PARSER_CLASSES
        assert ".txt" in supported_extensions
        assert ".pdf" in supported_extensions
        assert ".jpg" in supported_extensions
        assert ".png" in supported_extensions

    @patch("agent.views.settings.FILE_PARSER_CLASSES", {})
    def test_get_supported_file_types_empty_list(self, api_client, url):
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert "supported_extensions" in response.data
        assert response.data["supported_extensions"] == []

    @patch("agent.views.settings.FILE_PARSER_CLASSES", {(".txt",): "parser_class"})
    def test_get_supported_file_types_single_extension(self, api_client, url):
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["supported_extensions"] == [".txt"]
