from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src import app as application_module

client = TestClient(application_module.app)
_original_activities = deepcopy(application_module.activities)

@pytest.fixture(autouse=True)
def reset_activities():
    application_module.activities.clear()
    application_module.activities.update(deepcopy(_original_activities))
    yield


def test_get_activities_returns_all_activities():
    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data


def test_signup_for_activity_adds_participant():
    email = "test.student@mergington.edu"
    response = client.post(
        "/activities/Chess%20Club/signup",
        params={"email": email},
    )

    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for Chess Club"

    activities = client.get("/activities").json()
    assert email in activities["Chess Club"]["participants"]


def test_signup_duplicate_returns_400():
    email = "duplicate.student@mergington.edu"
    first_response = client.post(
        "/activities/Programming%20Class/signup",
        params={"email": email},
    )
    assert first_response.status_code == 200

    second_response = client.post(
        "/activities/Programming%20Class/signup",
        params={"email": email},
    )
    assert second_response.status_code == 400
    assert second_response.json()["detail"] == "Student already signed up for this activity"


def test_remove_participant_from_activity():
    email = "michael@mergington.edu"
    response = client.delete(
        "/activities/Chess%20Club/participants",
        params={"email": email},
    )

    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from Chess Club"

    activities = client.get("/activities").json()
    assert email not in activities["Chess Club"]["participants"]


def test_remove_nonexistent_participant_returns_404():
    response = client.delete(
        "/activities/Gym%20Class/participants",
        params={"email": "missing.student@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found for this activity"
