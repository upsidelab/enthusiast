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
    data_set_id = serializers.IntegerField(
        required=False,
        allow_null=False,
        error_messages={
            "null": "Data Set ID cannot be blank. Either skip this parameter, or provide a valid ID of a data set"
        },
    )
    agent = serializers.CharField(
        required=False,
        allow_null=False,
        allow_blank=False,
    )


class ConversationSerializer(serializers.ModelSerializer):
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


class ConversationContentSerializer(ConversationSerializer):
    # This serializer returns conversation details extended with history.
    history = MessagesSerializer(many=True)

    class Meta(ConversationSerializer.Meta):
        fields = ConversationSerializer.Meta.fields + ["history"]


class NamePathSerializer(serializers.Serializer):
    name = serializers.CharField()
    path = serializers.CharField()


class RepositoriesConfigSerializer(serializers.Serializer):
    user = NamePathSerializer(many=True)
    message = NamePathSerializer(many=True)
    conversation = NamePathSerializer(many=True)
    data_set = NamePathSerializer(many=True)
    document_chunk = NamePathSerializer(many=True)
    product = NamePathSerializer(many=True)
    product_chunk = NamePathSerializer(many=True)


class RetrieversConfigSerializer(serializers.Serializer):
    document = NamePathSerializer(many=True)
    product = NamePathSerializer(many=True)


class RegistriesConfigSerializer(serializers.Serializer):
    llm = NamePathSerializer(many=True)
    embeddings = NamePathSerializer(many=True)
    model = NamePathSerializer(many=True)


class ToolsConfigSerializer(serializers.Serializer):
    function = NamePathSerializer(many=True)
    llm = NamePathSerializer(many=True)
    agent = NamePathSerializer(many=True)


class ConfigSerializer(serializers.Serializer):
    agents = NamePathSerializer(many=True)
    prompt_templates = NamePathSerializer(many=True)
    llm = NamePathSerializer(many=True)
    llm_callback_handlers = NamePathSerializer(many=True)
    agent_callback_handlers = NamePathSerializer(many=True)
    repositories = RepositoriesConfigSerializer()
    retrievers = RetrieversConfigSerializer()
    injectors = NamePathSerializer(many=True)
    registries = RegistriesConfigSerializer()
    tools = ToolsConfigSerializer()
