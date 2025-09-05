from rest_framework import serializers

from agent.models import Conversation, Message
from agent.models.conversation import ConversationFile
from agent.serializers.configuration import AgentListSerializer


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

    def validate_conversation_id(self, value):
        if not Conversation.objects.filter(id=value).exists():
            raise serializers.ValidationError(
                f"Conversation with the given ID ({value}) does not exist. Either skip this parameter (a new conversation will be created), or provide a valid ID of an existing conversation"
            )
        return value


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
    # Serializer to get list of messages exchanged during a given conversation.
    class Meta:
        model = Message
        fields = ["id", "text", "role"]


class ConversationContentSerializer(serializers.ModelSerializer):
    # This serializer returns conversation details extended with history.
    history = MessagesSerializer(many=True, source="messages")

    agent = AgentListSerializer()

    class Meta:
        model = Conversation
        fields = ["id", "started_at", "summary", "history", "agent"]


class ConversationFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConversationFile
        fields = ["id", "file", "conversation", "content_type", "created_at", "updated_at"]

    def create(self, validated_data):
        file_obj = validated_data["file"]
        validated_data["content_type"] = getattr(file_obj, "content_type", None)
        return super().create(validated_data)


class ConversationMultiFileUploadSerializer(serializers.Serializer):
    files = serializers.ListField(child=serializers.FileField(), allow_empty=False)

    def create(self, validated_data):
        files = validated_data["files"]
        conversation = self.context.get("conversation")
        if not conversation:
            raise serializers.ValidationError("Conversation is required")

        objs = []
        for f in files:
            obj = ConversationFile.objects.create(
                conversation=conversation,
                file=f,
                content_type=getattr(f, "content_type", None),
            )
            objs.append(obj)
        return objs
