from typing import Literal, Optional, Type

from django.contrib.auth import get_user_model
from django.db import models
from drf_yasg import openapi
from guardian.decorators import permission_required_or_403
from guardian.shortcuts import assign_perm
from pydantic import BaseModel
from pydantic import ValidationError as PydanticValidationError
from rest_framework import serializers
from rest_framework.exceptions import APIException
from utils.serializers import BasePydanticModelField

from sync.base import SourcePluginRegistry

User = get_user_model()


def get_model_permission(model: Type[models.Model], action: Literal["view", "change", "delete", "add"]) -> str:
    app_label = model._meta.app_label
    model_name = model._meta.model_name
    return f"{app_label}.{action}_{model_name}"


class ModelPermissions:
    """
    Helper class to access all permissions (built-in and custom) for a model.

    Usage:
        perms = ModelPermissions(DataSet)
        # Built-in permissions:
        # perms.view -> "catalog.view_dataset"
        # perms.add -> "catalog.add_dataset"
        # perms.change -> "catalog.change_dataset"
        # perms.delete -> "catalog.delete_dataset"
        # Custom permissions (from Meta.permissions):
        # perms.manage_dataset_users -> "catalog.manage_dataset_users"
    """

    def __init__(self, model: Type[models.Model]):
        self.model = model
        app_label = model._meta.app_label

        # Built-in permissions
        self.view = get_model_permission(model, "view")
        self.add = get_model_permission(model, "add")
        self.change = get_model_permission(model, "change")
        self.delete = get_model_permission(model, "delete")

        # Custom permissions from Meta.permissions
        custom_permissions = getattr(model._meta, "permissions", [])
        for codename, _ in custom_permissions:
            setattr(self, codename, f"{app_label}.{codename}")

    def get_custom_permission(self, codename: str) -> str:
        """Get a custom permission string for the model (for dynamic access)."""
        app_label = self.model._meta.app_label
        return f"{app_label}.{codename}"


def is_builtin_permission_action(action: str) -> bool:
    return action in ["view", "change", "delete", "add"]


def build_permission_string(model: Type[models.Model], action: str) -> str:
    app_label = model._meta.app_label

    if is_builtin_permission_action(action):
        model_name = model._meta.model_name
        return f"{app_label}.{action}_{model_name}"
    else:
        return f"{app_label}.{action}"


def permission_required_with_global_perms(perm, *args, **kwargs):
    kwargs.setdefault("accept_global_perms", True)
    return permission_required_or_403(perm, *args, **kwargs)


class BaseRole:
    PERMISSIONS: dict[str, list[str]] = {}

    @classmethod
    def _get_model_by_string(cls, model_string: str) -> Type[models.Model]:
        from django.apps import apps

        app_label, model_name = model_string.split(".")
        return apps.get_model(app_label, model_name)

    @classmethod
    def get_permissions_for_model(cls, model: Type[models.Model]) -> list[str]:
        model_string = f"{model._meta.app_label}.{model.__name__}"

        role_permissions = cls.PERMISSIONS.get(model_string, [])

        if not role_permissions:
            return []

        permissions = []
        for action in role_permissions:
            permissions.append(build_permission_string(model, action))

        return permissions

    @classmethod
    def assign(cls, user: User, obj: Optional[models.Model] = None) -> None:
        from django.contrib.auth.models import Permission
        from django.contrib.contenttypes.models import ContentType

        if obj is None:
            for model_string, _ in cls.PERMISSIONS.items():
                model = cls._get_model_by_string(model_string)
                permissions = cls.get_permissions_for_model(model)

                for perm in permissions:
                    try:
                        assign_perm(perm, user)
                    except Permission.DoesNotExist:
                        codename = perm.split(".")[-1]
                        content_type = ContentType.objects.get_for_model(model)
                        Permission.objects.get_or_create(
                            codename=codename,
                            content_type=content_type,
                            defaults={"name": f"Can {codename.replace('_', ' ')}"},
                        )
                        assign_perm(perm, user)
        else:
            model = type(obj)
            permissions = cls.get_permissions_for_model(model)

            for perm in permissions:
                try:
                    assign_perm(perm, user, obj)
                except Permission.DoesNotExist:
                    codename = perm.split(".")[-1]
                    content_type = ContentType.objects.get_for_model(model)
                    Permission.objects.get_or_create(
                        codename=codename,
                        content_type=content_type,
                        defaults={"name": f"Can {codename.replace('_', ' ')}"},
                    )
                    assign_perm(perm, user, obj)


class AdminRole(BaseRole):
    PERMISSIONS = {
        "catalog.DataSet": [
            "view",
            "change",
            "delete",
            "add",
            "manage_dataset_users",
        ],
        "account.User": [
            "view",
            "change",
            "delete",
            "add",
        ],
    }


class UserRole(BaseRole):
    PERMISSIONS = {
        "catalog.DataSet": [
            "view",
        ],
    }


class PydanticModelField(BasePydanticModelField):
    def __init__(self, *, config_field_name: str, plugin_registry_class: Type[SourcePluginRegistry], **kwargs):
        self.config_field_name = config_field_name
        self.plugin_registry_class = plugin_registry_class
        super().__init__(**kwargs)

    def to_internal_value(self, data):
        plugin_name = self.context.get("plugin_name")
        try:
            class_obj = self.plugin_registry_class().get_plugin_class_by_name(plugin_name)
        except Exception as e:
            raise APIException(f"Error loading plugin: {str(e)}")

        try:
            schema = getattr(class_obj, self.config_field_name)
        except KeyError:
            raise serializers.ValidationError(f"Unknown schema for field: {self.config_field_name}")

        if not schema:
            return {}

        try:
            return schema(**data).model_dump()
        except PydanticValidationError as e:
            raise serializers.ValidationError(self._format_pydantic_errors(e))

    def to_representation(self, value):
        if isinstance(value, BaseModel):
            return value.model_dump()
        return value

    class Meta:
        swagger_schema_fields = {"type": openapi.TYPE_OBJECT}
