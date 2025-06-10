from rest_framework import serializers

from agent.models import Conversation, Message


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

    def validate_conversation_id(self, value):
        if not Conversation.objects.filter(id=value).exists():
            raise serializers.ValidationError(
                f"Conversation with the given ID ({value}) does not exist. Either skip this parameter (a new conversation will be created), or provide a valid ID of an existing conversation"
            )
        return value


class ConversationCreationSerializer(serializers.Serializer):
    data_set_id = serializers.IntegerField(
        required=False,
        allow_null=False,
        error_messages={
            "null": "Data Set ID cannot be blank. Either skip this parameter, or provide a valid ID of a data set"
        },
    )


class ConversationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversation
        fields = ["id", "started_at", "summary"]


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


class ConversationContentSerializer(ConversationSerializer):
    # This serializer returns conversation details extended with history.
    history = MessagesSerializer(many=True)

    class Meta(ConversationSerializer.Meta):
        fields = ConversationSerializer.Meta.fields + ["history"]
