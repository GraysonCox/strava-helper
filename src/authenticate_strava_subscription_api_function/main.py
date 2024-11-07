import json
import os


VERIFY_TOKEN = os.environ["VERIFY_TOKEN"]


def lambda_handler(event, _) -> dict:
    if event.get("queryStringParameters", {}).get("hub.verify_token") != VERIFY_TOKEN:
        return {"statusCode": 401, "body": "Unauthorized"}

    if "hub.challenge" not in event["queryStringParameters"]:
        return {"statusCode": 400, "body": "Unauthorized"}

    return {
        "statusCode": 200,
        "body": json.dumps(
            {"hub.challenge": event["queryStringParameters"]["hub.challenge"]}
        ),
    }
