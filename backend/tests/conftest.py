import os
os.environ["NINJA_SKIP_REGISTRY"] = "1"
import pytest
from django.test import Client
from ninja.testing import TestClient
from sensors.api import api
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

@pytest.fixture
def client(db):
    """
    Django Client for testing auth endpoints.
    """    
    return Client()

@pytest.fixture
def auth_client(db, user):
    """
    Authenticated Ninja Client with DB access for testing Ninja endpoints.
    """
    client = TestClient(api)
    refresh = RefreshToken.for_user(user)
    client.headers["Authorization"] = f"Bearer {refresh.access_token}"
    return client

@pytest.fixture
def user(db):
    """
    Creates a test user.
    """
    User = get_user_model()
    return User.objects.create_user(username="testuser", password="pass")

@pytest.fixture
def other_user(db):
    """
    Creates another user, separate from the test user.
    """
    User = get_user_model()
    return User.objects.create_user(username="otheruser", password="pass")