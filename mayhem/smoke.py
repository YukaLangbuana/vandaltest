import time
import json
import requests
import numpy as np


def smoke_test(
    method: str,
    endpoint: str,
    params: dict = {},
    data: dict = {},
    headers: dict = {},
    duration: int = 5,
    vus: int = 1,
):
    """
    Smoke test is a test to verify that your system
    can handle minimal load, without any problems.
    """

    if type(data) is not dict:
        raise TypeError(f"data must be a dict, not {type(data)}")

    responses = []
    start = time.time()
    while time.time() - start < duration:
        response = requests.request(
            method, endpoint, params=params, data=json.dumps(data), headers=headers
        )
        responses.append(response)
    end = time.time()
    return {
        "time": {
            "start": start,
            "end": end,
            "duration": end - start,
        },
        "data_received": {
            "size": sum([len(response.content) for response in responses]),
        },
        "http_duration": {
            "avg": np.mean(
                [response.elapsed.total_seconds() for response in responses]
            ),
            "min": np.min([response.elapsed.total_seconds() for response in responses]),
            "max": np.max([response.elapsed.total_seconds() for response in responses]),
        },
        "successful_requests": {
            "count": len(
                [response for response in responses if response.status_code == 200]
            ),
            "percentage": len(
                [response for response in responses if response.status_code == 200]
            )
            / len(responses),
        },
        "failed_requests": {
            "count": len(
                [response for response in responses if response.status_code != 200]
            ),
            "percentage": len(
                [response for response in responses if response.status_code != 200]
            )
            / len(responses),
        },
        "iterations": len(responses),
        "vus": vus,
        "raw_responses": responses,
    }
