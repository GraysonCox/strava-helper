import json
import os


def lambda_handler(event, _) -> dict:
    if "queryStringParameters" not in event:
        return {"statusCode": 400, "body": "Bad request"}

    if any(
        [
            "hub.mode" not in event["queryStringParameters"],
            "hub.verify_token" not in event["queryStringParameters"],
            "hub.challenge" not in event["queryStringParameters"],
        ]
    ):
        return {"statusCode": 400, "body": "Bad request"}

    if event["queryStringParameters"]["hub.mode"] != "subscribe":
        return {"statusCode": 400, "body": "Bad request"}

    if event["queryStringParameters"]["hub.verify_token"] != os.environ["VERIFY_TOKEN"]:
        return {"statusCode": 401, "body": "Unauthorized"}

    return {
        "statusCode": 200,
        "body": json.dumps(
            {"hub.challenge": event["queryStringParameters"]["hub.challenge"]}
        ),
    }
