import pytest
from model_bakery import baker
from rest_framework.test import APIClient

from account.models import User
from catalog.models import DataSet


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
def data_set():
    return baker.make(DataSet)
