from rest_framework import serializers


class CustomUserSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    email = serializers.EmailField()
    is_staff = serializers.BooleanField()
