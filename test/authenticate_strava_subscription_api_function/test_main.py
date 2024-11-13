import json
import os
import pytest
from unittest.mock import patch
from faker import Faker

from src.authenticate_strava_subscription_api_function.main import lambda_handler


FAKER = Faker()


@pytest.fixture(autouse=True)
def the_verify_token():
    return FAKER.name()


@pytest.fixture(autouse=True)
def mock_os_environ(the_verify_token):
    env_vars = {"VERIFY_TOKEN": the_verify_token}
    with patch.dict(os.environ, env_vars) as mock:
        yield mock


def test_authenticate_successfully(the_verify_token):
    event = {
        "queryStringParameters": {
            "hub.mode": "subscribe",
            "hub.verify_token": the_verify_token,
            "hub.challenge": FAKER.name(),
        }
    }

    result = lambda_handler(event, {})

    assert result == {
        "statusCode": 200,
        "body": json.dumps(
            {"hub.challenge": event["queryStringParameters"]["hub.challenge"]}
        ),
    }


@pytest.mark.parametrize(
    "given_query_string_parameter_names",
    [
        ["hub.mode", "hub.verify_token"],
        ["hub.mode", "hub.challenge"],
        ["hub.verify_token", "hub.challenge"],
    ],
)
def test_fail_when_missing_required_fields(given_query_string_parameter_names):
    event = {
        "queryStringParameters": dict(
            (p, FAKER.name()) for p in given_query_string_parameter_names
        )
    }

    result = lambda_handler(event, {})

    assert result == {"statusCode": 400, "body": "Bad request"}


def test_fail_when_verify_token_is_wrong():
    event = {
        "queryStringParameters": {
            "hub.mode": "subscribe",
            "hub.verify_token": FAKER.name(),
            "hub.challenge": FAKER.name(),
        }
    }

    result = lambda_handler(event, {})

    assert result == {"statusCode": 401, "body": "Unauthorized"}


def test_fail_when_mode_is_not_subscribe(the_verify_token):
    event = {
        "queryStringParameters": {
            "hub.mode": FAKER.name(),
            "hub.verify_token": the_verify_token,
            "hub.challenge": FAKER.name(),
        }
    }

    result = lambda_handler(event, {})

    assert result == {"statusCode": 400, "body": "Bad request"}


def test_fail_when_event_is_missing_query_parameters():
    result = lambda_handler({}, {})

    assert result == {"statusCode": 400, "body": "Bad request"}
