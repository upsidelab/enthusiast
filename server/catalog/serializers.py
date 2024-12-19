from rest_framework import serializers

from .models import DataSet, Document, DocumentSource, Product, ProductSource


class DataSetSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataSet
        fields = ['id', 'name', 'embedding_provider', 'embedding_model', 'embedding_vector_dimensions']


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['name', 'slug', 'sku', 'description', 'categories']


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['url', 'title', 'content']


class ProductSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSource
        fields = ['id', 'plugin_name', 'config', 'data_set_id']


class DocumentSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentSource
        fields = ['id', 'plugin_name', 'config', 'data_set_id']
