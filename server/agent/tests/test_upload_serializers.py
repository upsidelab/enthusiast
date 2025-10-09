from unittest.mock import Mock, patch

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from model_bakery import baker

from agent.models.conversation import ConversationFile
from agent.serializers.conversation import ConversationFileSerializer


@pytest.fixture
def conversation_file():
    return baker.make(
        ConversationFile,
        file="conversations/1/test.txt",
        content_type="text/plain",
        created_at="2023-01-01T00:00:00Z",
        updated_at="2023-01-01T00:00:00Z",
    )


@pytest.mark.django_db
class TestConversationFileSerializer:
    def test_serialize_conversation_file(self, conversation_file):
        serializer = ConversationFileSerializer(conversation_file)
        data = serializer.data

        assert data["id"] == 1
        assert data["filename"] == "test.txt"
        assert data["content_type"] == "text/plain"

    def test_create_conversation_file_with_content_type(self, conversation):
        file_obj = SimpleUploadedFile("test.txt", b"test content", content_type="text/plain")
        validated_data = {"conversation": conversation, "file": file_obj}

        with patch("agent.serializers.conversation.ConversationFile.objects.create") as mock_create:
            mock_create.return_value = Mock(id=1, content_type="text/plain")
            serializer = ConversationFileSerializer()
            serializer.create(validated_data)

        mock_create.assert_called_once()
        call_args = mock_create.call_args[1]
        assert call_args["conversation"] == conversation
        assert call_args["file"] == file_obj
        assert call_args["content_type"] == "text/plain"

    def test_create_conversation_file_without_content_type(self):
        conversation = Mock()
        file_obj = SimpleUploadedFile("test.txt", b"test content")
        validated_data = {"conversation": conversation, "file": file_obj}

        with patch("agent.serializers.conversation.ConversationFile.objects.create") as mock_create:
            mock_create.return_value = Mock(id=1, content_type=None)
            serializer = ConversationFileSerializer()
            serializer.create(validated_data)

        mock_create.assert_called_once()
        call_args = mock_create.call_args[1]
        assert call_args["conversation"] == conversation
        assert call_args["file"] == file_obj
        assert call_args["content_type"] == "text/plain"
