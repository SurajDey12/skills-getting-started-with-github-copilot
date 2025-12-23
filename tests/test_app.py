"""
Tests for the Mergington High School API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    return TestClient(app)


def test_root_redirect(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.url.path == "/static/index.html"


def test_get_activities(client):
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Basketball" in data
    assert "description" in data["Basketball"]
    assert "participants" in data["Basketball"]


def test_signup_success(client):
    # Test successful signup
    response = client.post("/activities/Basketball/signup?email=test@mergington.edu")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "test@mergington.edu" in data["message"]

    # Verify the participant was added
    response = client.get("/activities")
    data = response.json()
    assert "test@mergington.edu" in data["Basketball"]["participants"]


def test_signup_activity_not_found(client):
    response = client.post("/activities/NonExistent/signup?email=test@mergington.edu")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Activity not found" in data["detail"]


def test_signup_already_signed_up(client):
    # First signup
    client.post("/activities/Tennis Club/signup?email=duplicate@mergington.edu")
    # Try again
    response = client.post("/activities/Tennis Club/signup?email=duplicate@mergington.edu")
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "already signed up" in data["detail"]


def test_unregister_success(client):
    # First signup
    client.post("/activities/Art Studio/signup?email=unregister@mergington.edu")
    # Then unregister
    response = client.delete("/activities/Art Studio/unregister?email=unregister@mergington.edu")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "unregister@mergington.edu" in data["message"]

    # Verify removed
    response = client.get("/activities")
    data = response.json()
    assert "unregister@mergington.edu" not in data["Art Studio"]["participants"]


def test_unregister_activity_not_found(client):
    response = client.delete("/activities/NonExistent/unregister?email=test@mergington.edu")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Activity not found" in data["detail"]


def test_unregister_not_signed_up(client):
    response = client.delete("/activities/Basketball/unregister?email=notsigned@mergington.edu")
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "not signed up" in data["detail"]