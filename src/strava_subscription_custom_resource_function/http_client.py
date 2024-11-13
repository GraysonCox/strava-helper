import json
import urllib3
from typing import Optional


HTTP = urllib3.PoolManager()


def request(
    method: str,
    url: str,
    fields: Optional[dict] = None,
    body: Optional[dict] = None,
    headers: Optional[dict] = None,
):
    response = HTTP.request(
        method,
        url,
        fields=fields if fields else None,
        body=json.dumps(body) if body else None,
        headers=headers,
    )

    if response.status not in range(200, 300):
        raise Exception(
            f"Request failed: {response.status} - {response.data.decode('utf-8')}"
        )

    return json.loads(response.data.decode("utf-8"))
