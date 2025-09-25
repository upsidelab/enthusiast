import logging

from rest_framework import serializers

from agent.models import Conversation, Message
from agent.models.conversation import ConversationFile
from agent.serializers.configuration import AgentListSerializer

logger = logging.getLogger(__name__)


class AskQuestionSerializer(serializers.Serializer):
    """A serializer to ask questions.

    Arguments:
        data_set_id:
            Integer, Provide an ID of a data set to be used
        question_message:
            Str, A question message.
    """

    data_set_id = serializers.IntegerField(
        required=False, allow_null=False, error_messages={"null": "Data Set ID cannot be blank"}
    )

    question_message = serializers.CharField(
        required=True, allow_blank=False, error_messages={"blank": "Query message cannot be blank."}
    )
    streaming = serializers.BooleanField(
        default=False,
        required=False,
    )
    file_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True,
    )

    def validate(self, attrs):
        conversation_id = self.context.get("conversation_id")
        conversation = Conversation.objects.get(pk=conversation_id)
        if not conversation:
            raise serializers.ValidationError(
                {
                    "conversation_id": f"Conversation with the given ID ({conversation_id}) does not exist. Either skip this parameter (a new conversation will be created), or provide a valid ID of an existing conversation"
                }
            )
        if attrs.get("file_ids", None):
            valid_file_ids = set(conversation.files.values_list("id", flat=True))
            invalid_ids = [file_id for file_id in attrs["file_ids"] if file_id not in valid_file_ids]
            if invalid_ids:
                raise serializers.ValidationError(
                    {"file_ids": f"The following file IDs do not belong to the conversation: {invalid_ids}"}
                )
        return attrs


class ConversationCreationSerializer(serializers.Serializer):
    agent_id = serializers.IntegerField(
        required=True,
        allow_null=False,
    )


class ConversationSerializer(serializers.ModelSerializer):
    agent = AgentListSerializer()

    class Meta:
        model = Conversation
        fields = ["id", "started_at", "summary", "agent"]


class MessageFeedbackSerializer(serializers.ModelSerializer):
    rating = serializers.IntegerField(min_value=1, max_value=5, required=True)
    feedback = serializers.CharField(
        required=True,
        allow_blank=False,
        error_messages={"blank": "Feedback cannot be blank.", "required": "Feedback is required."},
    )

    class Meta:
        model = Message
        fields = ["rating", "feedback"]


class MessagesSerializer(serializers.ModelSerializer):
    text = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ["id", "text", "type", "file_type", "file_name"]

    def get_text(self, obj: Message):
        if obj.type == Message.MessageType.FILE:
            return ""
        else:
            return obj.text


class ConversationContentSerializer(serializers.ModelSerializer):
    # This serializer returns conversation details extended with history.
    history = MessagesSerializer(many=True, source="messages")

    agent = AgentListSerializer()

    class Meta:
        model = Conversation
        fields = ["id", "started_at", "summary", "history", "agent"]


class ConversationFileSerializer(serializers.ModelSerializer):
    filename = serializers.SerializerMethodField()
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = ConversationFile
        fields = ["id", "filename", "file_url", "content_type"]

    def get_filename(self, obj):
        return obj.file.name.split("/")[-1] if obj.file else ""

    def get_file_url(self, obj):
        return obj.file.url if obj.file else ""

    def create(self, validated_data):
        file_obj = validated_data["file"]
        validated_data["content_type"] = getattr(file_obj, "content_type", None)
        return super().create(validated_data)


class FileUploadTaskResponseSerializer(serializers.Serializer):
    task_id = serializers.CharField()


class FileUploadStatusResponseSerializer(serializers.Serializer):
    task_id = serializers.CharField()
    status = serializers.CharField()
    result = serializers.JSONField(required=False, allow_null=True)


class SupportedFileTypesSerializer(serializers.Serializer):
    supported_extensions = serializers.ListField(child=serializers.CharField())
