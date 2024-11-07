import json
import logging


LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


def lambda_handler(event, _) -> dict:
    body = json.loads(event["body"])
    LOGGER.info("Recieved Strava event: %s", body)
    return {"statusCode": 200, "body": json.dumps({"status": "success"})}
