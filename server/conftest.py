import tempfile

import pytest
from django.test import override_settings
from model_bakery import baker
from rest_framework.test import APIClient

from account.models import User
from account.services import UserService
from agent.models import Conversation
from catalog.models import DataSet, DocumentSource, ProductSource
from catalog.utils import AdminRole, UserRole


@pytest.fixture
def user():
    return baker.make(User)


@pytest.fixture
def admin_user():
    """Create admin user with AdminRole permissions."""
    user = baker.make(User, is_staff=True)
    UserService.assign_role(user, AdminRole)
    return user


@pytest.fixture
def api_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def admin_api_client(admin_user):
    client = APIClient()
    client.force_authenticate(user=admin_user)
    return client


@pytest.fixture
def user_with_view_permission(data_set):
    user = baker.make(User, is_staff=True)
    UserService.assign_role(user, UserRole, data_set)
    return user


@pytest.fixture
def api_client_with_view_permission(user_with_view_permission):
    client = APIClient()
    client.force_authenticate(user=user_with_view_permission)
    return client


@pytest.fixture
def user_with_change_permission(data_set):
    user = baker.make(User, is_staff=True)
    UserService.assign_role(user, AdminRole, data_set)
    return user


@pytest.fixture
def api_client_with_change_permission(user_with_change_permission):
    client = APIClient()
    client.force_authenticate(user=user_with_change_permission)
    return client


@pytest.fixture
def user_with_manage_permission(data_set):
    user = baker.make(User, is_staff=True)
    UserService.assign_role(user, AdminRole, data_set)
    return user


@pytest.fixture
def api_client_with_manage_permission(user_with_manage_permission):
    client = APIClient()
    client.force_authenticate(user=user_with_manage_permission)
    return client


@pytest.fixture
def user_with_user_view_permission():
    user = baker.make(User, is_staff=True)
    from account.models import User as UserModel
    from catalog.utils import get_model_permission

    UserService.assign_permission(user, get_model_permission(UserModel, "view"))
    return user


@pytest.fixture
def api_client_with_user_view_permission(user_with_user_view_permission):
    client = APIClient()
    client.force_authenticate(user=user_with_user_view_permission)
    return client


@pytest.fixture
def user_with_user_add_permission():
    user = baker.make(User, is_staff=True)
    UserService.assign_role(user, AdminRole)
    return user


@pytest.fixture
def api_client_with_user_add_permission(user_with_user_add_permission):
    client = APIClient()
    client.force_authenticate(user=user_with_user_add_permission)
    return client


@pytest.fixture
def user_with_user_change_permission():
    user = baker.make(User, is_staff=True)
    UserService.assign_role(user, AdminRole)
    return user


@pytest.fixture
def api_client_with_user_change_permission(user_with_user_change_permission):
    client = APIClient()
    client.force_authenticate(user=user_with_user_change_permission)
    return client


@pytest.fixture
def data_set():
    return baker.make(DataSet)


@pytest.fixture
def document_source(data_set):
    return baker.make(DocumentSource, data_set=data_set)


@pytest.fixture
def product_source(data_set):
    return baker.make(ProductSource, data_set=data_set)


@pytest.fixture
def conversation(user, data_set):
    return baker.make(Conversation, user=user, data_set=data_set)


@pytest.fixture(autouse=True)
def temp_media_root():
    tmp_dir = tempfile.mkdtemp()
    with override_settings(DEFAULT_FILE_STORAGE="django.core.files.storage.FileSystemStorage", MEDIA_ROOT=tmp_dir):
        yield
