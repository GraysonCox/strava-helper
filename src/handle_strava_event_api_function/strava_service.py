import json
import os
from typing import Optional
import urllib3


HTTP = urllib3.PoolManager()


def __send_http_request(
    method: str, url: str, body: Optional[dict] = None, headers: Optional[dict] = None
):
    response = HTTP.request(
        method, url, body=json.dumps(body) if body else None, headers=headers
    )

    if response.status not in range(200, 300):
        raise Exception(
            f"Request failed: {response.status} - {response.data.decode('utf-8')}"
        )

    return json.loads(response.data.decode("utf-8"))


def get_auth_token() -> str:
    response = __send_http_request(
        "POST",
        f"{os.environ['STRAVA_API_URL']}/oauth/token",
        body={
            "client_id": os.environ["STRAVA_CLIENT_ID"],
            "client_secret": os.environ["STRAVA_CLIENT_SECRET"],
            "grant_type": "refresh_token",
            "refresh_token": os.environ["STRAVA_REFRESH_TOKEN"],
        },
        headers={
            "Content-Type": "application/json",
        },
    )
    return response["access_token"]


def get_activity(activity_id: int, auth_token: str) -> dict:
    return __send_http_request(
        "GET",
        f"{os.environ['STRAVA_API_URL']}/activities/{activity_id}",
        headers={
            "Authorization": f"Bearer {auth_token}",
        },
    )


def update_activity(activity: dict, auth_token: str) -> dict:
    return __send_http_request(
        "PUT",
        f"{os.environ['STRAVA_API_URL']}/activities/{activity['id']}",
        body={
            "commute": activity["commute"],
            "trainer": activity["trainer"],
            "hide_from_home": activity["hide_from_home"],
            "description": activity["description"],
            "name": activity["name"],
            "type": activity["type"],
            "sport_type": activity["sport_type"],
            "gear_id": activity["gear_id"],
        },
        headers={
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json",
        },
    )
