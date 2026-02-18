from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, username=None, email=None, password=None, role=None, **extra_fields):
        from account.services.user import UserService

        return UserService.create_user(username=username, email=email, password=password, role=role, **extra_fields)

    def create_superuser(self, username=None, email=None, password=None, role=None, **extra_fields):
        from account.services.user import UserService

        return UserService.create_superuser(
            username=username, email=email, password=password, role=role, **extra_fields
        )

    def create_service_account(self, email, role=None, **extra_fields):
        from account.services.user import UserService

        return UserService.create_service_account(email=email, role=role, **extra_fields)


class User(AbstractUser):
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    email = models.EmailField(max_length=255, unique=True)
    username = None
    is_service_account = models.BooleanField(default=False)

    objects = UserManager()

    def __str__(self):
        return self.email

    def has_dataset_access(self, dataset):
        return self.is_staff or getattr(self, "data_sets").filter(pk=dataset.pk).exists()
