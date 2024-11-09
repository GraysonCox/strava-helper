import json
import pytest
import random
import string
from unittest.mock import patch

from src.handle_strava_event_api_function import main
from src.handle_strava_event_api_function.main import lambda_handler


def __random_string():
    return "".join(random.choice(string.ascii_letters) for _ in range(10))


def __event(aspect_type: str, object_type: str):
    strava_event = {
        "aspect_type": aspect_type,
        "event_time": 1516126040,
        "object_id": 123456789,
        "object_type": object_type,
        "owner_id": 1,
        "subscription_id": 12345,
    }
    return {"body": json.dumps(strava_event)}


@pytest.fixture
def mock_strava_service():
    with patch.object(main, "strava_service", autospec=True) as mock:
        yield mock


def test_hide_activity_that_should_be_hidden(mock_strava_service):
    given_event = __event("create", "activity")
    the_auth_token = __random_string()
    mock_strava_service.get_auth_token.return_value = the_auth_token
    mock_strava_service.get_activity.return_value = {
        "commute": True,
        "hide_from_home": False,
        "description": "",
    }

    result = lambda_handler(given_event, {})

    mock_strava_service.get_auth_token.assert_called_once()
    mock_strava_service.get_activity.assert_called_once_with(
        json.loads(given_event["body"])["object_id"], the_auth_token
    )
    mock_strava_service.update_activity.assert_called_once_with(
        {
            "commute": True,
            "hide_from_home": True,
            "description": "This commute was automatically hidden by my shitty AWS project.",
        },
        the_auth_token,
    )
    assert result == {"statusCode": 200, "body": json.dumps({"status": "success"})}


def test_fail_when_first_strava_service_call_fails(mock_strava_service):
    given_event = __event("create", "activity")
    mock_strava_service.get_auth_token.side_effect = Exception

    result = lambda_handler(given_event, {})

    assert result == {"statusCode": 400, "body": json.dumps({"status": "failed"})}


def test_fail_when_second_strava_service_call_fails(mock_strava_service):
    given_event = __event("create", "activity")
    mock_strava_service.get_auth_token.return_value = __random_string()
    mock_strava_service.get_activity.side_effect = Exception

    result = lambda_handler(given_event, {})

    assert result == {"statusCode": 400, "body": json.dumps({"status": "failed"})}


def test_fail_when_third_strava_service_call_fails(mock_strava_service):
    given_event = __event("create", "activity")
    mock_strava_service.get_auth_token.return_value = __random_string()
    mock_strava_service.get_activity.return_value = {
        "commute": True,
        "hide_from_home": False,
        "description": "",
    }
    mock_strava_service.update_activity.side_effect = Exception

    result = lambda_handler(given_event, {})

    assert result == {"statusCode": 400, "body": json.dumps({"status": "failed"})}


@pytest.mark.parametrize(
    "given_aspect_type, given_object_type, given_activity_is_commute",
    [
        ("create", "activity", False),
        ("create", "athlete", False),
        ("create", "athlete", True),
        ("update", "activity", False),
        ("update", "activity", True),
        ("update", "athlete", False),
        ("update", "athlete", True),
        ("delete", "activity", False),
        ("delete", "activity", True),
        ("delete", "athlete", False),
        ("delete", "athlete", True),
    ],
)
def test_do_nothing_as_desired(
    mock_strava_service,
    given_aspect_type: str,
    given_object_type: str,
    given_activity_is_commute: bool,
):
    given_event = __event(given_aspect_type, given_object_type)
    the_auth_token = __random_string()
    mock_strava_service.get_auth_token.return_value = the_auth_token
    mock_strava_service.get_activity.return_value = {
        "commute": given_activity_is_commute,
        "hide_from_home": False,
        "description": "",
    }

    result = lambda_handler(given_event, {})

    assert result == {"statusCode": 200, "body": json.dumps({"status": "success"})}
