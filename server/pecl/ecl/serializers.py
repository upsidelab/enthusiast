from rest_framework import serializers
from .models import Companies, RawDataSets, Contents


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Companies
        fields = ['id', 'code', 'name']


class RawDataSetSerializer(serializers.ModelSerializer):
    class Meta:
        model = RawDataSets
        fields = ['name', 'slug', 'sku', 'description', 'categories']


class ContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contents
        fields = ['url', 'title', 'content']
