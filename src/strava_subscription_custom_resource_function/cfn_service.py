from strava_subscription_custom_resource_function import http_client


def send_successful_response(
    url: str,
    logical_resource_id: str,
    physical_resource_id: str,
    stack_id: str,
    request_id: str,
    data: dict = {},
):
    http_client.request(
        "PUT",
        url,
        body={
            "Status": "SUCCESS",
            "Reason": "Everything worked.",
            "LogicalResourceId": logical_resource_id,
            "PhysicalResourceId": physical_resource_id,
            "StackId": stack_id,
            "RequestId": request_id,
            "Data": data,
        },
    )


def send_failed_response(
    url: str,
    logical_resource_id: str,
    physical_resource_id: str,
    stack_id: str,
    request_id: str,
    reason: str,
):
    http_client.request(
        "PUT",
        url,
        body={
            "Status": "FAILED",
            "Reason": reason,
            "LogicalResourceId": logical_resource_id,
            "PhysicalResourceId": physical_resource_id,
            "StackId": stack_id,
            "RequestId": request_id,
        },
    )
