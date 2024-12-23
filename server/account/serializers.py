from rest_framework import serializers

from account.models import User

from .services import ServiceAccountNameService


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


class CreateServiceAccountSerializer(serializers.Serializer):
    name = serializers.CharField()
    datasets = serializers.ListField(
        child=serializers.IntegerField(), required=False
    )

    def create(self, validated_data):
        service = ServiceAccountNameService()
        name = validated_data.get('name')
        email = service.generate_service_account_email(name)
        dataset_ids = validated_data.get('datasets', [])
        user = User.objects.create_service_account(email=email)
        user.data_sets.add(*dataset_ids)
        return user

class ServiceAccountSerializer(serializers.ModelSerializer):
    data_sets = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'date_joined', 'data_sets']

    def get_data_sets(self, obj):
        return list(obj.data_sets.values_list('name', flat=True))
