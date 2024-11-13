import json
import os
import pytest
from unittest.mock import patch, MagicMock
from faker import Faker

from src.handle_strava_event_api_function import strava_service


FAKER = Faker()


def __mock_http_response(status: int, data: dict) -> MagicMock:
    mock_response = MagicMock()
    mock_response.status = status
    mock_response.data = json.dumps(data).encode("utf-8")
    return mock_response


@pytest.fixture(autouse=True)
def mock_os_environ():
    env_vars = {
        "STRAVA_API_URL": f"https://{FAKER.name()}",
        "STRAVA_CLIENT_ID": str(1),
        "STRAVA_CLIENT_SECRET": FAKER.name(),
        "STRAVA_REFRESH_TOKEN": FAKER.name(),
    }
    with patch.dict(os.environ, env_vars, clear=True) as mock:
        yield mock


@pytest.fixture
def mock_http():
    with patch.object(strava_service, "HTTP") as mock:
        yield mock


@pytest.mark.parametrize("http_response_code", [200, 201, 202, 203, 204, 299])
def test_get_auth_token_succeeds(mock_os_environ, mock_http, http_response_code):
    the_auth_token = FAKER.name()
    mock_http.request.return_value = __mock_http_response(
        http_response_code, {"access_token": the_auth_token}
    )

    result = strava_service.get_auth_token()

    mock_http.request.assert_called_once_with(
        "POST",
        f"{mock_os_environ['STRAVA_API_URL']}/oauth/token",
        body=json.dumps(
            {
                "client_id": mock_os_environ["STRAVA_CLIENT_ID"],
                "client_secret": mock_os_environ["STRAVA_CLIENT_SECRET"],
                "grant_type": "refresh_token",
                "refresh_token": mock_os_environ["STRAVA_REFRESH_TOKEN"],
            }
        ),
        headers={
            "Content-Type": "application/json",
        },
    )
    assert result == the_auth_token
