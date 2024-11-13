import logging

from strava_subscription_custom_resource_function import cfn_service, strava_service

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


def __create_subscription(event) -> dict:
    LOGGER.info("Creating subscription ...")

    subscription_id = strava_service.create_subscription(
        event["ResourceProperties"]["ClientId"],
        event["ResourceProperties"]["ClientSecret"],
    )

    return {"SubscriptionId": str(subscription_id)}


def __delete_subscription(event) -> None:
    if not event["PhysicalResourceId"].isdigit():
        LOGGER.info(
            "Deletion was requested, but the subscription already doesn't exist."
        )
        return

    LOGGER.info("Deleting subscription %s ...", event["PhysicalResourceId"])
    strava_service.delete_subscription(
        event["Data"]["SubscriptionId"],
        event["ResourceProperties"]["ClientId"],
        event["ResourceProperties"]["ClientSecret"],
    )


def lambda_handler(event, _):
    try:
        LOGGER.info("Recieved event with request type %s.", event["RequestType"])

        request_type = event["RequestType"]
        if request_type == "Create":
            cfn_outputs = __create_subscription(event)
        elif request_type == "Update":
            __delete_subscription(event)
            cfn_outputs = __create_subscription(event)
        elif request_type == "Delete":
            __delete_subscription(event)
            cfn_outputs = {}
        else:
            cfn_outputs = {}

        cfn_service.send_successful_response(
            event["ResponseURL"],
            logical_resource_id=event["LogicalResourceId"],
            physical_resource_id=cfn_outputs.get("SubscriptionId", "N/A"),
            stack_id=event["StackId"],
            request_id=event["RequestId"],
            data=cfn_outputs,
        )

    except Exception as e:
        LOGGER.exception("There was a failure.")
        cfn_service.send_failed_response(
            event["ResponseURL"],
            logical_resource_id=event["LogicalResourceId"],
            physical_resource_id="N/A",
            stack_id=event["StackId"],
            request_id=event["RequestId"],
            reason=str(e),
        )
