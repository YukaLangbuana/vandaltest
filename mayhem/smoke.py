import time
import json
import requests
import pandas as pd
from datetime import datetime


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

    responses = {}
    start = time.time()
    while time.time() - start < duration:
        response = requests.request(
            method, endpoint, params=params, data=json.dumps(data), headers=headers
        )
        responses[datetime.now()] = {
            "status_code": response.status_code,
            "response_time": response.elapsed.total_seconds(),
            "response_size": len(response.content),
        }
    
    result = pd.DataFrame.from_dict(responses, orient="index")
    return result