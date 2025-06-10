from rest_framework import serializers

from .models import DataSet, Document, DocumentSource, Product, ProductSource


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
            "system_message",
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


class ProductSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSource
        fields = ["id", "plugin_name", "config", "data_set_id"]


class DocumentSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentSource
        fields = ["id", "plugin_name", "config", "data_set_id"]
