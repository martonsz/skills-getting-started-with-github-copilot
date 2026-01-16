import sys
from copy import deepcopy
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Ensure src is on the path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT / "src"))

import app  # noqa: E402


@pytest.fixture(autouse=True)
def reset_data():
    """Reset the in-memory activities between tests."""
    original = deepcopy(app.activities)
    yield
    app.activities.clear()
    app.activities.update(deepcopy(original))


@pytest.fixture
def client():
    return TestClient(app.app)


def test_get_activities_returns_data(client):
    response = client.get("/activities")
    assert response.status_code == 200
    body = response.json()
    assert "Chess Club" in body
    assert "Programming Class" in body


def test_signup_adds_participant(client):
    activity_name = "Science Club"
    email = "new.student@mergington.edu"

    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    assert response.status_code == 200
    assert email in app.activities[activity_name]["participants"]


def test_signup_rejects_duplicate(client):
    activity_name = "Chess Club"
    email = app.activities[activity_name]["participants"][0]

    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    assert response.status_code == 400
    body = response.json()
    assert body["detail"] == "Student already signed up for this activity"


def test_delete_removes_participant(client):
    activity_name = "Gym Class"
    email = app.activities[activity_name]["participants"][0]

    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    assert response.status_code == 200
    assert email not in app.activities[activity_name]["participants"]


def test_delete_missing_participant_returns_404(client):
    activity_name = "Drama Club"
    email = "absent@mergington.edu"

    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    assert response.status_code == 404
    body = response.json()
    assert body["detail"] == "Student not found in this activity"
