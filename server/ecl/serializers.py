from rest_framework import serializers

from .models import DataSet, Document, Product


class DataSetSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataSet
        fields = ['id', 'code', 'name']


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['name', 'slug', 'sku', 'description', 'categories']


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['url', 'title', 'content']
