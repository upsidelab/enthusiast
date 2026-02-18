from rest_framework import serializers

from account.models import User

from .services import ServiceAccountNameService, UserService


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


class CreateUpdateServiceAccountSerializer(serializers.Serializer):
    name = serializers.CharField(write_only=True)
    is_active = serializers.BooleanField(default=True)
    is_staff = serializers.BooleanField(default=False)
    data_set_ids = serializers.ListField(child=serializers.IntegerField(), required=False)

    def create(self, validated_data):
        email = self._build_service_account_email(validated_data.get("name"))
        is_active = validated_data.get("is_active")
        is_staff = validated_data.get("is_staff")
        dataset_ids = validated_data.get("data_set_ids", [])
        service_account = UserService.create_service_account(email=email, is_active=is_active, is_staff=is_staff)
        service_account.data_sets.add(*dataset_ids)
        return service_account

    def update(self, instance, validated_data):
        instance.email = self._build_service_account_email(validated_data.get("name"))
        instance.is_active = validated_data.get("is_active")
        instance.is_staff = validated_data.get("is_staff")
        instance.save()
        data_set_ids = validated_data.get("data_set_ids", [])
        instance.data_sets.set(data_set_ids)
        return instance

    def _build_service_account_email(self, name):
        service = ServiceAccountNameService()
        return service.generate_service_account_email(name)


class ServiceAccountSerializer(serializers.ModelSerializer):
    data_set_ids = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "email", "date_joined", "data_set_ids", "is_active", "is_staff"]

    def get_data_set_ids(self, obj):
        return list(obj.data_sets.values_list("id", flat=True))


class TokenResponseSerializer(serializers.Serializer):
    token = serializers.CharField()


class AvailabilityResponseSerializer(serializers.Serializer):
    is_available = serializers.BooleanField()
