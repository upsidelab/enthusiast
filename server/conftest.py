import tempfile

import pytest
from django.test import override_settings
from model_bakery import baker
from rest_framework.test import APIClient

from account.models import User
from agent.models import Conversation
from catalog.models import DataSet, DocumentSource, ProductSource


@pytest.fixture
def user():
    return baker.make(User)


@pytest.fixture
def admin_user():
    return baker.make(User, is_staff=True)


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
def limited_admin_user():
    return baker.make(User, is_staff=True, is_limited_admin=True)


@pytest.fixture
def limited_admin_api_client(limited_admin_user):
    client = APIClient()
    client.force_authenticate(user=limited_admin_user)
    return client


@pytest.fixture
def limited_admin_with_dataset(limited_admin_user):
    data_set = baker.make(DataSet)
    data_set.users.add(limited_admin_user)
    return limited_admin_user, data_set


@pytest.fixture
def limited_admin_with_dataset_client(limited_admin_with_dataset):
    user, _ = limited_admin_with_dataset
    client = APIClient()
    client.force_authenticate(user=user)
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
