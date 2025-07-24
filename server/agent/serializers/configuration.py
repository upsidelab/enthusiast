from rest_framework import serializers

from agent.models.agent_config import AgentConfiguration
from catalog.models import DataSet


class NamePathSerializer(serializers.Serializer):
    name = serializers.CharField()
    path = serializers.CharField()


class RepositoriesListConfigSerializer(serializers.Serializer):
    user = NamePathSerializer(many=True)
    message = NamePathSerializer(many=True)
    conversation = NamePathSerializer(many=True)
    data_set = NamePathSerializer(many=True)
    document_chunk = NamePathSerializer(many=True)
    product = NamePathSerializer(many=True)
    product_chunk = NamePathSerializer(many=True)


class RetrieversListConfigSerializer(serializers.Serializer):
    document = NamePathSerializer(many=True)
    product = NamePathSerializer(many=True)


class RegistriesListConfigSerializer(serializers.Serializer):
    llm = NamePathSerializer(many=True)
    embeddings = NamePathSerializer(many=True)
    model = NamePathSerializer(many=True)


class ToolsListConfigSerializer(serializers.Serializer):
    function = NamePathSerializer(many=True)
    llm = NamePathSerializer(many=True)
    agent = NamePathSerializer(many=True)


class ListConfigSerializer(serializers.Serializer):
    agents = NamePathSerializer(many=True)
    prompt_templates = NamePathSerializer(many=True)
    llm = NamePathSerializer(many=True)
    llm_callback_handlers = NamePathSerializer(many=True)
    agent_callback_handlers = NamePathSerializer(many=True)
    repositories = RepositoriesListConfigSerializer()
    retrievers = RetrieversListConfigSerializer()
    injectors = NamePathSerializer(many=True)
    registries = RegistriesListConfigSerializer()
    tools = ToolsListConfigSerializer()


class RetrieverConfigSerializer(serializers.Serializer):
    retriever_class = serializers.CharField()
    extra_kwargs = serializers.DictField(child=serializers.CharField(), required=False)


class RetrieversConfigSerializer(serializers.Serializer):
    document = RetrieverConfigSerializer()
    product = RetrieverConfigSerializer()


class RepositoriesConfigSerializer(serializers.Serializer):
    user = serializers.CharField()
    message = serializers.CharField()
    conversation = serializers.CharField()
    data_set = serializers.CharField()
    document_chunk = serializers.CharField()
    product = serializers.CharField()
    product_chunk = serializers.CharField()


class CallbackHandlerConfigSerializer(serializers.Serializer):
    handler_class = serializers.CharField()


class LLMConfigSerializer(serializers.Serializer):
    llm_class = serializers.CharField()
    callbacks = serializers.ListField(child=CallbackHandlerConfigSerializer(), required=False, allow_null=True)


class LLMToolConfigSerializer(serializers.Serializer):
    tool_class = serializers.CharField()
    data_set_id = serializers.CharField(required=False, allow_null=True)
    llm = serializers.CharField(required=False, allow_null=True)


class AgentToolConfigSerializer(serializers.Serializer):
    tool_class = serializers.CharField()
    agent = serializers.CharField()


class EmbeddingsRegistryConfigSerializer(serializers.Serializer):
    registry_class = serializers.CharField()
    providers = serializers.DictField(child=serializers.CharField(), required=False, allow_null=True)


class LLMRegistryConfigSerializer(serializers.Serializer):
    registry_class = serializers.CharField()
    providers = serializers.DictField(child=serializers.CharField(), required=False, allow_null=True)


class ModelsRegistryConfigSerializer(serializers.Serializer):
    registry_class = serializers.CharField()
    models_config = serializers.DictField(child=serializers.CharField(), required=False, allow_null=True)


class RegistryConfigSerializer(serializers.Serializer):
    llm = LLMRegistryConfigSerializer()
    embeddings = EmbeddingsRegistryConfigSerializer()
    model = ModelsRegistryConfigSerializer()


class PromptTemplateSerializer(serializers.Serializer):
    input_variables = serializers.ListField(child=serializers.CharField(), allow_empty=True)
    template = serializers.CharField()


class ChatPromptTemplateSerializer(serializers.Serializer):
    messages = serializers.ListField(
        child=serializers.ListField(child=serializers.CharField(), min_length=2, max_length=2)
    )

    def validate_messages(self, value):
        allowed_roles = {"system", "human", "placeholder", "assistant"}
        for role, content in value:
            if role not in allowed_roles:
                raise serializers.ValidationError(f"Invalid role: {role}")
            if not isinstance(content, str):
                raise serializers.ValidationError("Content must be a string.")
        return value


class AgentConfigSerializer(serializers.Serializer):
    agent_class = serializers.CharField()
    llm = LLMConfigSerializer()
    repositories = RepositoriesConfigSerializer()
    retrievers = RetrieversConfigSerializer()
    injector = serializers.CharField()
    registry = RegistryConfigSerializer()
    prompt_template = PromptTemplateSerializer(required=False, allow_null=True)
    chat_prompt_template = ChatPromptTemplateSerializer(required=False, allow_null=True)
    function_tools = serializers.ListField(child=serializers.CharField(), required=False, allow_null=True)
    llm_tools = LLMToolConfigSerializer(many=True, required=False, allow_null=True)
    agent_tools = AgentToolConfigSerializer(many=True, required=False, allow_null=True)
    agent_callback_handler = CallbackHandlerConfigSerializer(required=False, allow_null=True)

    def validate(self, attrs):
        prompt = attrs.get("prompt_template")
        chat_prompt = attrs.get("chat_prompt_template")

        if (prompt is None and chat_prompt is None) or (prompt is not None and chat_prompt is not None):
            raise serializers.ValidationError(
                "Exactly one of 'prompt_template' or 'chat_prompt_template' must be provided."
            )
        return attrs


class AgentConfigurationModelSerializer(serializers.ModelSerializer):
    config = AgentConfigSerializer()
    dataset = serializers.PrimaryKeyRelatedField(queryset=DataSet.objects.all())

    class Meta:
        model = AgentConfiguration
        fields = ["id", "name", "config", "dataset", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class AgentConfigurationDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgentConfiguration
        fields = ["id", "name", "dataset", "created_at", "updated_at"]
