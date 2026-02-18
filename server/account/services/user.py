import logging
from typing import Optional, Type

from django.contrib.auth import get_user_model
from django.db import models
from guardian.shortcuts import assign_perm, remove_perm

from catalog.utils import AdminRole, BaseRole, UserRole

User = get_user_model()
logger = logging.getLogger(__name__)


class UserService:
    @staticmethod
    def _create_user_base(email, password=None, **extra_fields):
        if not email:
            raise ValueError("The email field must be set")

        from django.contrib.auth.base_user import BaseUserManager

        manager = BaseUserManager()
        email = manager.normalize_email(email)
        user = User(email=email, **extra_fields)

        if extra_fields.get("is_service_account", False):
            user.set_unusable_password()
        else:
            if password:
                user.set_password(password)

        user.save()
        return user

    @staticmethod
    def create_user(
        username=None,
        email=None,
        password=None,
        role: Type[BaseRole] = UserRole,
        is_staff: bool = False,
        is_superuser: bool = False,
        **extra_fields,
    ) -> User:
        extra_fields.setdefault("is_staff", is_staff)
        extra_fields.setdefault("is_superuser", is_superuser)

        user = UserService._create_user_base(email, password, **extra_fields)
        UserService.assign_role(user, role)

        return user

    @staticmethod
    def create_superuser(
        username=None, email=None, password=None, role: Type[BaseRole] = AdminRole, **extra_fields
    ) -> User:
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        user = UserService._create_user_base(email, password, **extra_fields)

        UserService.assign_role(user, role)

        return user

    @staticmethod
    def create_service_account(email, role: Optional[Type[BaseRole]] = None, **extra_fields) -> User:
        extra_fields.setdefault("is_service_account", True)

        user = UserService._create_user_base(email, password=None, **extra_fields)

        if role is None:
            if not extra_fields.get("is_staff", False):
                role = AdminRole
            else:
                role = UserRole

        if role is not None:
            UserService.assign_role(user, role)

        return user

    @staticmethod
    def assign_role(user: User, role: Type[BaseRole], obj: Optional[models.Model] = None) -> None:
        try:
            role.assign(user, obj)
        except Exception as e:
            logger.error(f"Failed to assign {role.__name__} role to user {user.id}: {str(e)}", exc_info=True)
            raise

    @staticmethod
    def assign_permission(user: User, permission: str, obj: Optional[models.Model] = None) -> None:
        try:
            assign_perm(permission, user, obj)
        except Exception as e:
            logger.error(f"Failed to assign permission '{permission}' to user {user.id}: {str(e)}", exc_info=True)
            raise

    @staticmethod
    def remove_permission(user: User, permission: str, obj: Optional[models.Model] = None) -> None:
        try:
            remove_perm(permission, user, obj)
        except Exception as e:
            logger.error(f"Failed to remove permission '{permission}' from user {user.id}: {str(e)}", exc_info=True)
            raise

    @staticmethod
    def assign_role_to_object(user: User, role: Type[BaseRole], obj: models.Model) -> None:
        UserService.assign_role(user, role, obj)
