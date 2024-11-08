import json
import logging

import strava_service


LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


def lambda_handler(event, _) -> dict:
    try:
        LOGGER.info("Recieved Strava event: %s", event["body"])

        strava_event = json.loads(event["body"])

        if strava_event["object_type"] != "activity":
            return {"statusCode": 200, "body": json.dumps({"status": "success"})}

        LOGGER.info("The event is a commute activity and will now be hidden.")
        auth_token = strava_service.get_auth_token()
        activity = strava_service.get_activity(strava_event["object_id"], auth_token)
        if not activity["commute"]:
            return {"statusCode": 200, "body": json.dumps({"status": "success"})}
        activity["hide_from_home"] = True
        activity["description"] = (
            "This commute was automatically hidden by my shitty AWS project."
        )
        strava_service.update_activity(activity, auth_token)

        return {"statusCode": 200, "body": json.dumps({"status": "success"})}
    except Exception:
        LOGGER.exception("There was a failure.")
        return {"statusCode": 400, "body": json.dumps({"status": "failed"})}
