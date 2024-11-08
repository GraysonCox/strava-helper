import json
import pytest
from typing import Optional
from unittest.mock import MagicMock, call, patch

from src.strava_subscription_custom_resource_function import main
from src.strava_subscription_custom_resource_function.main import lambda_handler


def __event(request_type: str, physical_resource_id: Optional[str] = None) -> dict:
    event = {
        "RequestType": request_type,
        "StackId": "some-stack",
        "RequestId": "some-request",
        "LogicalResourceId": "StravaSubscription",
        "ResponseURL": "some-url.com",
        "ResourceProperties": {
            "ClientId": "12345",
            "ClientSecret": "some-secret",
            "CallbackUrl": "the-callback-url.com",
            "VerifyToken": "some-token",
            "StravaSubscriptionsUrl": "the-strava-url.com",
        },
    }
    if physical_resource_id:
        event["PhysicalResourceId"] = physical_resource_id
    return event


def __mock_http_response(status: int, data: dict) -> MagicMock:
    mock_response = MagicMock()
    mock_response.status = status
    mock_response.data = json.dumps(data).encode("utf-8")
    return mock_response


@pytest.fixture
def mock_http():
    with patch.object(main, "HTTP") as mock:
        yield mock


@pytest.mark.parametrize("http_response_code", [200, 201, 202, 203, 204, 299])
def test_create_subscription_success(mock_http, http_response_code):
    event = __event("Create")
    mock_http.request.side_effect = [
        __mock_http_response(http_response_code, {"id": 420}),
        __mock_http_response(http_response_code, {}),
    ]

    lambda_handler(event, {})

    mock_http.request.assert_has_calls(
        [
            call(
                "POST",
                event["ResourceProperties"]["StravaSubscriptionsUrl"],
                body=json.dumps(
                    {
                        "client_id": event["ResourceProperties"]["ClientId"],
                        "client_secret": event["ResourceProperties"]["ClientSecret"],
                        "callback_url": event["ResourceProperties"]["CallbackUrl"],
                        "verify_token": event["ResourceProperties"]["VerifyToken"],
                    }
                ),
                headers={
                    "Content-Type": "application/json",
                },
            ),
            call(
                "PUT",
                event["ResponseURL"],
                body=json.dumps(
                    {
                        "Status": "SUCCESS",
                        "Reason": "Everything worked.",
                        "PhysicalResourceId": str(420),
                        "StackId": event["StackId"],
                        "RequestId": event["RequestId"],
                        "LogicalResourceId": event["LogicalResourceId"],
                        "Data": {"SubscriptionId": str(420)},
                    }
                ).encode("utf-8"),
            ),
        ]
    )


@pytest.mark.parametrize("http_response_code", [100, 300, 400])
def test_create_subscription_failure(mock_http, http_response_code):
    event = __event("Create")
    mock_http.request.side_effect = [
        __mock_http_response(http_response_code, {"message": "Something went wrong."}),
        __mock_http_response(200, {}),
    ]

    lambda_handler(event, {})

    mock_http.request.assert_has_calls(
        [
            call(
                "POST",
                event["ResourceProperties"]["StravaSubscriptionsUrl"],
                body=json.dumps(
                    {
                        "client_id": event["ResourceProperties"]["ClientId"],
                        "client_secret": event["ResourceProperties"]["ClientSecret"],
                        "callback_url": event["ResourceProperties"]["CallbackUrl"],
                        "verify_token": event["ResourceProperties"]["VerifyToken"],
                    }
                ),
                headers={
                    "Content-Type": "application/json",
                },
            ),
            call(
                "PUT",
                event["ResponseURL"],
                body=json.dumps(
                    {
                        "Status": "FAILED",
                        "Reason": f"Request failed: {http_response_code} - "
                        + json.dumps({"message": "Something went wrong."}),
                        "PhysicalResourceId": "N/A",
                        "StackId": event["StackId"],
                        "RequestId": event["RequestId"],
                        "LogicalResourceId": event["LogicalResourceId"],
                        "Data": {},
                    }
                ).encode("utf-8"),
            ),
        ]
    )


@pytest.mark.parametrize("http_response_code", [200, 201, 202, 203, 204, 299])
def test_update_subscription_success(mock_http, http_response_code):
    event = __event("Update", physical_resource_id="420")
    mock_http.request.side_effect = [
        __mock_http_response(http_response_code, {}),
        __mock_http_response(http_response_code, {"id": 420}),
        __mock_http_response(http_response_code, {}),
    ]

    lambda_handler(event, {})

    mock_http.request.assert_has_calls(
        [
            call(
                "DELETE",
                f'{event["ResourceProperties"]["StravaSubscriptionsUrl"]}/420',
                fields={
                    "client_id": event["ResourceProperties"]["ClientId"],
                    "client_secret": event["ResourceProperties"]["ClientSecret"],
                },
            ),
            call(
                "POST",
                event["ResourceProperties"]["StravaSubscriptionsUrl"],
                body=json.dumps(
                    {
                        "client_id": event["ResourceProperties"]["ClientId"],
                        "client_secret": event["ResourceProperties"]["ClientSecret"],
                        "callback_url": event["ResourceProperties"]["CallbackUrl"],
                        "verify_token": event["ResourceProperties"]["VerifyToken"],
                    }
                ),
                headers={
                    "Content-Type": "application/json",
                },
            ),
            call(
                "PUT",
                event["ResponseURL"],
                body=json.dumps(
                    {
                        "Status": "SUCCESS",
                        "Reason": "Everything worked.",
                        "PhysicalResourceId": str(420),
                        "StackId": event["StackId"],
                        "RequestId": event["RequestId"],
                        "LogicalResourceId": event["LogicalResourceId"],
                        "Data": {"SubscriptionId": str(420)},
                    }
                ).encode("utf-8"),
            ),
        ]
    )


def test_update_subscription_failure():
    pass  # TODO


@pytest.mark.parametrize("http_response_code", [200, 201, 202, 203, 204, 299])
def test_delete_subscription_success(mock_http, http_response_code):
    event = __event("Delete", physical_resource_id="420")
    mock_http.request.side_effect = [
        __mock_http_response(http_response_code, {}),
        __mock_http_response(http_response_code, {}),
    ]

    lambda_handler(event, {})

    mock_http.request.assert_has_calls(
        [
            call(
                "DELETE",
                f'{event["ResourceProperties"]["StravaSubscriptionsUrl"]}/420',
                fields={
                    "client_id": event["ResourceProperties"]["ClientId"],
                    "client_secret": event["ResourceProperties"]["ClientSecret"],
                },
            ),
            call(
                "PUT",
                event["ResponseURL"],
                body=json.dumps(
                    {
                        "Status": "SUCCESS",
                        "Reason": "Everything worked.",
                        "PhysicalResourceId": "N/A",
                        "StackId": event["StackId"],
                        "RequestId": event["RequestId"],
                        "LogicalResourceId": event["LogicalResourceId"],
                        "Data": {},
                    }
                ).encode("utf-8"),
            ),
        ]
    )


def test_delete_subscription_when_subscription_does_not_exist(mock_http):
    event = __event("Delete", physical_resource_id="N/A")
    mock_http.request.side_effect = [
        __mock_http_response(200, {}),
    ]

    lambda_handler(event, {})

    mock_http.request.assert_has_calls(
        [
            call(
                "PUT",
                event["ResponseURL"],
                body=json.dumps(
                    {
                        "Status": "SUCCESS",
                        "Reason": "Everything worked.",
                        "PhysicalResourceId": "N/A",
                        "StackId": event["StackId"],
                        "RequestId": event["RequestId"],
                        "LogicalResourceId": event["LogicalResourceId"],
                        "Data": {},
                    }
                ).encode("utf-8"),
            ),
        ]
    )


@pytest.mark.parametrize("http_response_code", [100, 300, 400])
def test_delete_subscription_failure(mock_http, http_response_code):
    event = __event("Delete", physical_resource_id="420")
    mock_http.request.side_effect = [
        __mock_http_response(http_response_code, {"message": "Something went wrong."}),
        __mock_http_response(200, {}),
    ]

    lambda_handler(event, {})

    mock_http.request.assert_has_calls(
        [
            call(
                "DELETE",
                f'{event["ResourceProperties"]["StravaSubscriptionsUrl"]}/420',
                fields={
                    "client_id": event["ResourceProperties"]["ClientId"],
                    "client_secret": event["ResourceProperties"]["ClientSecret"],
                },
            ),
            call(
                "PUT",
                event["ResponseURL"],
                body=json.dumps(
                    {
                        "Status": "FAILED",
                        "Reason": f"Request failed: {http_response_code} - "
                        + json.dumps({"message": "Something went wrong."}),
                        "PhysicalResourceId": "N/A",
                        "StackId": event["StackId"],
                        "RequestId": event["RequestId"],
                        "LogicalResourceId": event["LogicalResourceId"],
                        "Data": {},
                    }
                ).encode("utf-8"),
            ),
        ]
    )
