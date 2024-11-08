import json
import os
import logging
import urllib3


LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)

HTTP = urllib3.PoolManager()

URL = "https://www.strava.com"
CLIENT_ID = 117583
CLIENT_SECRET = "eabc93844d322f6a48a78f11adffbd9d94b7ebc9"
REFRESH_TOKEN = "9eeb4aab45ca6a7ccff451c11bc6272875fe3eab"


def _get_access_token():
    data = {
        "client_id": os.environ["STRAVA_CLIENT_ID"],
        "client_secret": os.environ["STRAVA_CLIENT_SECRET"],
        "grant_type": "refresh_token",
        "refresh_token": os.environ["STRAVA_REFRESH_TOKEN"],
    }
    response = HTTP.request(
        "POST", f"{os.environ['STRAVA_API_URL']}/oauth/token", data=data
    )
    print(response.json())
    return response.json()["access_token"]


def _get_my_activities(access_token: str):
    response = requests.get(
        f"{URL}/athlete/activities",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    return response.json()


def main():
    access_token = _get_access_token()

    my_activities = _get_my_activities(access_token)

    my_commute_rides = [
        x for x in my_activities if x["sport_type"] == "Ride" and x["commute"]
    ]

    for x in my_commute_rides:
        print(" - ".join([x["start_date"], x["name"]]))


def lambda_handler(event, _) -> dict:
    body = json.loads(event["body"])
    LOGGER.info("Recieved Strava event: %s", body)
    return {"statusCode": 200, "body": json.dumps({"status": "success"})}
