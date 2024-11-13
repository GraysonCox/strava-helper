import os

from strava_subscription_custom_resource_function import http_client


def create_subscription(client_id: str, client_secret: str) -> int:
    response = http_client.request(
        "POST",
        f"{os.environ['STRAVA_API_URL']}/push_subscriptions",
        body={
            "client_id": client_id,
            "client_secret": client_secret,
            "callback_url": os.environ["API_CALLBACK_URL"],
            "verify_token": os.environ["STRAVA_VERIFY_TOKEN"],
        },
        headers={
            "Content-Type": "application/json",
        },
    )
    return response["id"]


def delete_subscription(
    subscription_id: int, client_id: str, client_secret: str
) -> None:
    http_client.request(
        "DELETE",
        f"{os.environ['STRAVA_API_URL']}/push_subscriptions/{subscription_id}",
        fields={
            "client_id": client_id,
            "client_secret": client_secret,
        },
    )
