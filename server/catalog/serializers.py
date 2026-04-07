from rest_framework import serializers
from utils.serializers import ParentDataContextSerializerMixin

from agent.core.registries.embeddings.embedding_provider_registry import EmbeddingProviderRegistry
from sync.document.registry import DocumentSourcePluginRegistry
from sync.product.registry import ProductSourcePluginRegistry

from .models import DataSet, Document, DocumentSource, ECommerceIntegration, Product, ProductSource
from .utils import PydanticModelField


class DataSetSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataSet
        fields = [
            "id",
            "name",
            "language_model_provider",
            "language_model",
            "embedding_provider",
            "embedding_model",
            "embedding_vector_dimensions",
        ]

class DataSetCreateSerializer(DataSetSerializer):
    preconfigure_agents = serializers.BooleanField(write_only=True, required=False, default=False)

    class Meta(DataSetSerializer.Meta):
        fields = DataSetSerializer.Meta.fields + ["preconfigure_agents"]

    def validate(self, data):
        """Validate that embedding_vector_dimensions satisfies provider constraints."""
        embedding_provider = data.get("embedding_provider")
        embedding_model = data.get("embedding_model")
        embedding_vector_dimensions = data.get("embedding_vector_dimensions")

        if embedding_provider and embedding_model and embedding_vector_dimensions is not None:
            try:
                provider_class = EmbeddingProviderRegistry().provider_class_by_name(embedding_provider)
            except Exception:
                provider_class = None

            if provider_class is not None:
                constraints = provider_class.vector_size_constraints()
                allowed_sizes = constraints.get(embedding_model)
                if allowed_sizes and embedding_vector_dimensions not in allowed_sizes:
                    raise serializers.ValidationError(
                        {
                            "embedding_vector_dimensions": (
                                f"Model '{embedding_model}' only supports vector sizes: "
                                f"{allowed_sizes}. Got {embedding_vector_dimensions}."
                            )
                        }
                    )

        return data


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["name", "slug", "sku", "description", "categories", "properties"]


class DocumentSerializer(serializers.ModelSerializer):
    is_indexed = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = ["url", "title", "content", "is_indexed"]

    def get_is_indexed(self, obj):
        return obj.chunks_count > 0


class ProductSourceConfigSerializer(serializers.Serializer):
    configuration_args = PydanticModelField(
        config_field_name="CONFIGURATION_ARGS",
        plugin_registry_class=ProductSourcePluginRegistry,
        allow_null=True,
        default=None,
    )


class DocumentSourceConfigSerializer(serializers.Serializer):
    configuration_args = PydanticModelField(
        config_field_name="CONFIGURATION_ARGS",
        plugin_registry_class=DocumentSourcePluginRegistry,
        allow_null=True,
        default=None,
    )


class ProductSourceSerializer(ParentDataContextSerializerMixin, serializers.ModelSerializer):
    context_keys_to_propagate = ["plugin_name"]

    config = ProductSourceConfigSerializer()
    task_id = serializers.CharField(read_only=True, required=False, allow_null=True)

    class Meta:
        model = ProductSource
        fields = ["id", "plugin_name", "config", "data_set_id", "corrupted", "task_id"]


class DocumentSourceSerializer(ParentDataContextSerializerMixin, serializers.ModelSerializer):
    context_keys_to_propagate = ["plugin_name"]

    config = DocumentSourceConfigSerializer()
    task_id = serializers.CharField(read_only=True, required=False, allow_null=True)

    class Meta:
        model = DocumentSource
        fields = ["id", "plugin_name", "config", "data_set_id", "corrupted", "task_id"]


class ECommerceIntegrationSerializer(ParentDataContextSerializerMixin, serializers.ModelSerializer):
    context_keys_to_propagate = ["plugin_name"]

    task_id = serializers.CharField(read_only=True, required=False, allow_null=True)

    class Meta:
        model = ECommerceIntegration
        fields = ["id", "plugin_name", "config", "data_set_id", "task_id"]


class SyncResponseSerializer(serializers.Serializer):
    task_id = serializers.CharField()
