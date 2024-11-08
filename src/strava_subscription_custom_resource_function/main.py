import json
import logging
import urllib3


LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)

HTTP = urllib3.PoolManager()


def __create_subscription(event) -> dict:
    LOGGER.info("Creating subscription ...")

    url = event["ResourceProperties"]["StravaSubscriptionsUrl"]
    body = json.dumps(
        {
            "client_id": event["ResourceProperties"]["ClientId"],
            "client_secret": event["ResourceProperties"]["ClientSecret"],
            "callback_url": event["ResourceProperties"]["CallbackUrl"],
            "verify_token": event["ResourceProperties"]["VerifyToken"],
        }
    )
    response = HTTP.request(
        "POST",
        url,
        body=body,
        headers={
            "Content-Type": "application/json",
        },
    )

    if response.status not in range(200, 300):
        raise Exception(
            f"Request failed: {response.status} - {response.data.decode('utf-8')}"
        )

    return {"SubscriptionId": str(json.loads(response.data.decode("utf-8"))["id"])}


def __delete_subscription(event) -> None:
    if not event["PhysicalResourceId"].isdigit():
        LOGGER.info(
            "Deletion was requested, but the subscription already doesn't exist."
        )
        return

    LOGGER.info("Deleting subscription %s ...", event["PhysicalResourceId"])

    url = f"{event['ResourceProperties']['StravaSubscriptionsUrl']}/{event['PhysicalResourceId']}"
    query_parameters = {
        "client_id": event["ResourceProperties"]["ClientId"],
        "client_secret": event["ResourceProperties"]["ClientSecret"],
    }
    response = HTTP.request(
        "DELETE",
        url,
        fields=query_parameters,
    )

    if response.status not in range(200, 300):
        raise Exception(
            f"Request failed: {response.status} - {response.data.decode('utf-8')}"
        )


def __send_cfn_response(event, status, reason, data) -> None:
    LOGGER.info("Sending CloudFormation response with status %s ...", status)

    url = event["ResponseURL"]
    body = {
        "Status": status,
        "Reason": reason,
        "PhysicalResourceId": data.get("SubscriptionId", "N/A"),
        "StackId": event["StackId"],
        "RequestId": event["RequestId"],
        "LogicalResourceId": event["LogicalResourceId"],
        "Data": data,
    }
    encoded_body = json.dumps(body).encode("utf-8")
    response = HTTP.request(
        "PUT",
        url,
        body=encoded_body,
    )

    if response.status not in range(200, 300):
        raise Exception(
            f"Failed to send CloudFormation response: {response.status} - {response.data.decode('utf-8')}"
        )


def lambda_handler(event, _):
    try:
        LOGGER.info("Recieved event with request type %s.", event["RequestType"])

        request_type = event["RequestType"]
        if request_type == "Create":
            cfn_response_data = __create_subscription(event)
        elif request_type == "Update":
            __delete_subscription(event)
            cfn_response_data = __create_subscription(event)
        elif request_type == "Delete":
            __delete_subscription(event)
            cfn_response_data = {}
        else:
            cfn_response_data = {}

        __send_cfn_response(event, "SUCCESS", "Everything worked.", cfn_response_data)
    except Exception as e:
        LOGGER.exception("There was a failure.")
        __send_cfn_response(event, "FAILED", str(e), {})
