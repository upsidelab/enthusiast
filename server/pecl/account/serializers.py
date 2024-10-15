from rest_framework import serializers


class CustomUserSerializer(serializers.Serializer):
    email = serializers.EmailField()
