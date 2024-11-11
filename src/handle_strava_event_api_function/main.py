import json
import logging

from handle_strava_event_api_function import strava_service


LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


def __successful_response() -> dict:
    return {"statusCode": 200, "body": json.dumps({"status": "success"})}


def __failed_response() -> dict:
    return {"statusCode": 400, "body": json.dumps({"status": "failed"})}


def lambda_handler(event: dict, _) -> dict:
    try:
        LOGGER.info("Recieved Strava event: %s", event["body"])

        strava_event = json.loads(event["body"])

        if any(
            [
                strava_event["aspect_type"] != "create",
                strava_event["object_type"] != "activity",
            ]
        ):
            return __successful_response()

        auth_token = strava_service.get_auth_token()
        activity = strava_service.get_activity(strava_event["object_id"], auth_token)

        if not activity["commute"]:
            return __successful_response()

        LOGGER.info("The event is a commute activity and will now be hidden.")
        activity["hide_from_home"] = True
        activity["description"] = (
            "This commute was automatically hidden by my shitty AWS project."
        )
        strava_service.update_activity(activity, auth_token)

        return __successful_response()
    except Exception:
        LOGGER.exception("There was a failure.")
        return __failed_response()
