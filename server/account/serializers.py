from rest_framework import serializers


class AccountSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    email = serializers.EmailField()
    is_staff = serializers.BooleanField()


class UserSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    email = serializers.EmailField()
    is_active = serializers.BooleanField()
    is_staff = serializers.BooleanField()
    password = serializers.CharField(write_only=True)


class UserUpdateSerializer(serializers.Serializer):
    email = serializers.EmailField()
    is_active = serializers.BooleanField()
    is_staff = serializers.BooleanField()


class UserUpdatePasswordSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True)
