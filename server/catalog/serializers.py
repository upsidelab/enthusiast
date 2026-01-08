from rest_framework import serializers
from utils.serializers import ParentDataContextSerializerMixin

from sync.document.registry import DocumentSourcePluginRegistry
from sync.product.registry import ProductSourcePluginRegistry

from .models import DataSet, Document, DocumentSource, Product, ProductSource
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

    class Meta:
        model = DocumentSource
        fields = ["id", "plugin_name", "config", "data_set_id", "corrupted"]


class SyncResponseSerializer(serializers.Serializer):
    task_id = serializers.CharField()
