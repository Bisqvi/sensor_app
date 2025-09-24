import os
os.environ["NINJA_SKIP_REGISTRY"] = "1"
import pytest
from sensors.api import api
from ninja.testing import TestClient
from django.contrib.auth import get_user_model

@pytest.fixture
def client(db):
    """
    Ninja TestClient with DB access.
    """
    return TestClient(api)

@pytest.fixture
def user(db):
    """
    Creates a test user.
    """
    User = get_user_model()
    return User.objects.create_user(username="testuser", password="pass")
