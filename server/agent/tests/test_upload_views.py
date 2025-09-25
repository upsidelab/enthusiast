import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from agent.models.conversation import ConversationFile

pytestmark = pytest.mark.django_db


class TestConversationFileUploadView:
    @pytest.fixture
    def url(self, conversation):
        return reverse("conversation-upload", kwargs={"conversation_id": conversation.id})

    def test_upload_unauthenticated_returns_401(self, url):
        test_file = SimpleUploadedFile("test.txt", b"test content", content_type="text/plain")
        data = {"files": [test_file]}
        client = APIClient()

        response = client.post(url, data, format="multipart")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_upload_single_file_success(self, api_client, url, conversation):
        test_file = SimpleUploadedFile("test.txt", b"test content", content_type="text/plain")
        data = {"files": [test_file]}

        response = api_client.post(url, data, format="multipart")

        assert response.status_code == status.HTTP_201_CREATED
        assert len(response.data) == 1
        uploaded_file = response.data[0]
        assert uploaded_file["conversation"] == conversation.id
        assert uploaded_file["content_type"] == "text/plain"
        assert "id" in uploaded_file
        assert "file" in uploaded_file
        assert "created_at" in uploaded_file
        assert "updated_at" in uploaded_file
        assert ConversationFile.objects.filter(conversation=conversation).count() == 1
        file_obj = ConversationFile.objects.get(conversation=conversation)
        assert file_obj.content_type == "text/plain"

    def test_upload_multiple_files_success(self, api_client, url, conversation):
        file1 = SimpleUploadedFile("test1.txt", b"content1", content_type="text/plain")
        file2 = SimpleUploadedFile("test2.pdf", b"content2", content_type="application/pdf")
        data = {"files": [file1, file2]}

        response = api_client.post(url, data, format="multipart")

        assert response.status_code == status.HTTP_201_CREATED
        assert len(response.data) == 2
        assert ConversationFile.objects.filter(conversation=conversation).count() == 2
        files = ConversationFile.objects.filter(conversation=conversation)
        content_types = [f.content_type for f in files]
        assert "text/plain" in content_types
        assert "application/pdf" in content_types

    def test_upload_nonexistent_conversation_returns_404(self, api_client):
        url = reverse("conversation-upload", kwargs={"conversation_id": 99999})
        test_file = SimpleUploadedFile("test.txt", b"test content", content_type="text/plain")
        data = {"files": [test_file]}

        response = api_client.post(url, data, format="multipart")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_upload_empty_files_list_returns_400(self, api_client, url):
        data = {"files": []}

        response = api_client.post(url, data, format="multipart")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "files" in response.data

    def test_upload_missing_files_field_returns_400(self, api_client, url):
        data = {}

        response = api_client.post(url, data, format="multipart")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "files" in response.data

    def test_upload_with_invalid_data_format_returns_400(self, api_client, url):
        data = {"files": ["not_a_file"]}

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
