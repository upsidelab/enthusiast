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


class LLMConfigSerializer(serializers.Serializer):
    llm_class = serializers.CharField()
    callbacks = serializers.ListField(child=serializers.CharField(), required=False, allow_null=True)


class AgentCallbackHandlerConfigSerializer(serializers.Serializer):
    handler_class = serializers.CharField()
    args = serializers.DictField(child=serializers.CharField(), required=False)


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


class AgentConfigSerializer(serializers.Serializer):
    prompt_template = serializers.CharField()
    agent_class = serializers.CharField()
    llm = LLMConfigSerializer()
    repositories = RepositoriesConfigSerializer()
    retrievers = RetrieversConfigSerializer()
    injector = serializers.CharField()
    registry = RegistryConfigSerializer()
    function_tools = serializers.ListField(child=serializers.CharField(), required=False, allow_null=True)
    llm_tools = LLMToolConfigSerializer(many=True, required=False, allow_null=True)
    agent_tools = AgentToolConfigSerializer(many=True, required=False, allow_null=True)
    agent_callback_handler = AgentCallbackHandlerConfigSerializer(required=False, allow_null=True)


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
