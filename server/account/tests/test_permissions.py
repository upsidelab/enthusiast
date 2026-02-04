import pytest
from rest_framework.test import APIRequestFactory

from account.models import User
from account.permissions import IsAdminUser, IsLimitedAdminUser

pytestmark = pytest.mark.django_db


class TestIsAdminUser:
    @pytest.fixture
    def permission(self):
        return IsAdminUser()

    @pytest.fixture
    def request_factory(self):
        return APIRequestFactory()

    def test_allows_full_admin_user(self, permission, request_factory):
        user = User.objects.create_user(
            email="admin@test.com", password="test123", is_staff=True, is_limited_admin=False
        )
        request = request_factory.get("/")
        request.user = user

        assert permission.has_permission(request, None) is True

    def test_denies_limited_admin_user(self, permission, request_factory):
        user = User.objects.create_user(
            email="limited@test.com", password="test123", is_staff=True, is_limited_admin=True
        )
        request = request_factory.get("/")
        request.user = user

        assert permission.has_permission(request, None) is False

    def test_denies_regular_user(self, permission, request_factory):
        user = User.objects.create_user(email="user@test.com", password="test123", is_staff=False)
        request = request_factory.get("/")
        request.user = user

        assert permission.has_permission(request, None) is False

    def test_denies_unauthenticated_user(self, permission, request_factory):
        request = request_factory.get("/")
        request.user = None

        assert permission.has_permission(request, None) is False

    def test_denies_staff_with_limited_admin_flag(self, permission, request_factory):
        user = User.objects.create_user(
            email="staff_limited@test.com", password="test123", is_staff=True, is_limited_admin=True
        )
        request = request_factory.get("/")
        request.user = user

        assert permission.has_permission(request, None) is False


class TestIsLimitedAdminUser:
    @pytest.fixture
    def permission(self):
        return IsLimitedAdminUser()

    @pytest.fixture
    def request_factory(self):
        return APIRequestFactory()

    def test_allows_full_admin_user(self, permission, request_factory):
        user = User.objects.create_user(
            email="admin@test.com", password="test123", is_staff=True, is_limited_admin=False
        )
        request = request_factory.get("/")
        request.user = user

        assert permission.has_permission(request, None) is True

    def test_allows_limited_admin_user(self, permission, request_factory):
        user = User.objects.create_user(
            email="limited@test.com", password="test123", is_staff=False, is_limited_admin=True
        )
        request = request_factory.get("/")
        request.user = user

        assert permission.has_permission(request, None) is True

    def test_allows_limited_admin_with_staff_flag(self, permission, request_factory):
        user = User.objects.create_user(
            email="limited_staff@test.com", password="test123", is_staff=True, is_limited_admin=True
        )
        request = request_factory.get("/")
        request.user = user

        assert permission.has_permission(request, None) is True

    def test_denies_regular_user(self, permission, request_factory):
        user = User.objects.create_user(
            email="user@test.com", password="test123", is_staff=False, is_limited_admin=False
        )
        request = request_factory.get("/")
        request.user = user

        assert permission.has_permission(request, None) is False

    def test_denies_unauthenticated_user(self, permission, request_factory):
        request = request_factory.get("/")
        request.user = None

        assert permission.has_permission(request, None) is False
