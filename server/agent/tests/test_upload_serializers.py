from unittest.mock import Mock, patch

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from model_bakery import baker
from rest_framework import serializers

from agent.models.conversation import ConversationFile
from agent.serializers.conversation import ConversationFileSerializer, ConversationMultiFileUploadSerializer


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
        assert data["file"].endswith("conversations/1/test.txt")
        assert data["conversation"] == conversation_file.conversation.id
        assert data["content_type"] == "text/plain"
        assert data["created_at"] == "2023-01-01T00:00:00Z"
        assert data["updated_at"] == "2023-01-01T00:00:00Z"

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


@pytest.mark.django_db
class TestConversationMultiFileUploadSerializer:
    """Test cases for ConversationMultiFileUploadSerializer."""

    def test_validate_files_field(self):
        data = {"files": []}

        serializer = ConversationMultiFileUploadSerializer(data=data)

        assert not serializer.is_valid()
        assert "files" in serializer.errors

    def test_validate_files_field_with_valid_files(self):
        file1 = SimpleUploadedFile("test1.txt", b"content1", content_type="text/plain")
        file2 = SimpleUploadedFile("test2.txt", b"content2", content_type="text/plain")
        data = {"files": [file1, file2]}

        serializer = ConversationMultiFileUploadSerializer(data=data)

        assert serializer.is_valid()

    def test_create_without_conversation_context(self):
        file1 = SimpleUploadedFile("test1.txt", b"content1", content_type="text/plain")
        data = {"files": [file1]}
        context = {}

        serializer = ConversationMultiFileUploadSerializer(data=data, context=context)
        serializer.is_valid()

        with pytest.raises(serializers.ValidationError) as exc_info:
            serializer.save()
        assert "Conversation is required" in str(exc_info.value)

    def test_create_with_none_conversation_context(self):
        file1 = SimpleUploadedFile("test1.txt", b"content1", content_type="text/plain")
        data = {"files": [file1]}
        context = {"conversation": None}

        serializer = ConversationMultiFileUploadSerializer(data=data, context=context)
        serializer.is_valid()

        with pytest.raises(serializers.ValidationError) as exc_info:
            serializer.save()
        assert "Conversation is required" in str(exc_info.value)

    def test_serializer_fields(self):
        serializer = ConversationMultiFileUploadSerializer()

        assert "files" in serializer.fields
        files_field = serializer.fields["files"]
        assert isinstance(files_field, serializers.ListField)
        assert not files_field.allow_empty
        assert isinstance(files_field.child, serializers.FileField)
