import json
import logging
import urllib3


LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)

HTTP = urllib3.PoolManager()

URL = 'https://www.strava.com'
CLIENT_ID = 117583
CLIENT_SECRET = 'eabc93844d322f6a48a78f11adffbd9d94b7ebc9'
REFRESH_TOKEN = '9eeb4aab45ca6a7ccff451c11bc6272875fe3eab'


def _get_access_token():
    data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'refresh_token',
        'refresh_token': REFRESH_TOKEN,
    }
    response = requests.post(f'{URL}/api/v3/oauth/token', data=data)
    print(response.json())
    return response.json()['access_token']


def _get_my_activities(access_token: str):
    response = requests.get(
        f'{URL}/api/v3/athlete/activities',
        headers={'Authorization': f'Bearer {access_token}'},
    )
    return response.json()


def main():
    access_token = _get_access_token()

    my_activities = _get_my_activities(access_token)

    my_commute_rides = [x for x in my_activities if x['sport_type'] == 'Ride' and x['commute']]

    for x in my_commute_rides:
        print(' - '.join([x['start_date'], x['name']]))


def lambda_handler(event, _) -> dict:
    body = json.loads(event["body"])
    LOGGER.info("Recieved Strava event: %s", body)
    return {"statusCode": 200, "body": json.dumps({"status": "success"})}import requests
