import time
import json
import requests
import pandas as pd
from threading import Thread
from datetime import datetime
from multiprocessing import Manager


def load_test(
    method: str,
    endpoint: str,
    params: dict = {},
    data: dict = {},
    headers: dict = {},
    duration: int = 5,
    vus: int = 5,
    expidite_shutdown: bool = True,
    expidite_shutdown_timeout: int = 30,
):
    """
    Load Testing is a type of Performance Testing used
    to determine a system's behavior under both normal
    and peak conditions. Load Testing is used to ensure
    that the application performs satisfactorily when many
    users access it at the same time.
    """

    if type(data) is not dict:
        raise TypeError(f"data must be a dict, not {type(data)}")

    responses = Manager().dict()
    threads = []
    test_is_running = True

    def request_thread(method, endpoint, params, data, headers, list_to_append):
        while test_is_running:
            response = requests.request(
                method, endpoint, params=params, data=json.dumps(data), headers=headers
            )
            responses[datetime.now()] = {
                "status_code": response.status_code,
                "#VUS": len(threads),
                "response_time": response.elapsed.total_seconds(),
                "response_size": len(response.content),
            }

    start = time.time()
    for _ in range(vus):
        thread = Thread(
            target=request_thread,
            args=("POST", endpoint, params, data, headers, responses),
        )
        thread.start()
        threads.append(thread)

    while time.time() - start < duration:
        time.sleep(0.1)

    test_is_running = False
    for thread in threads:
        if expidite_shutdown:
            thread.join(timeout=int(vus / expidite_shutdown_timeout))
        else:
            thread.join()
    
    result = pd.DataFrame.from_dict(responses, orient="index")
    return result
