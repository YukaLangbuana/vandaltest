import time
import json
import requests
from threading import Thread
from queue import Queue


def stress_test(
    method: str,
    endpoint: str,
    params: dict = {},
    data: dict = {},
    headers: dict = {},
    duration: int = 5,
    vus: int = 1000,
    expidite_shutdown: bool = True,
    expidite_shutdown_timeout: int = 30,
):
    """
    Stress Testing is a type of load testing used to
    determine the limits of the system. The purpose of this
    test is to verify the stability and reliability of the
    system under extreme conditions.
    """

    if type(data) is not dict:
        raise TypeError(f"data must be a dict, not {type(data)}")

    responses = Queue()
    threads = []
    test_is_running = True

    def request_thread(method, endpoint, params, data, headers, list_to_append):
        while test_is_running:
            response = requests.request(
                method, endpoint, params=params, data=json.dumps(data), headers=headers
            )
            list_to_append.put(response)

    start = time.time()
    while time.time() - start < duration:
        new_vu = 0
        if time.time() - start < duration / 8:
            new_vu = int(vus / 8) - len(threads)
        elif time.time() - start < duration / 4:
            new_vu = int(vus / 4) - len(threads)
        elif time.time() - start < duration / 2:
            new_vu = int(vus / 2) - len(threads)
        elif time.time() - start < duration:
            new_vu = int(vus) - len(threads)

        for _ in range(new_vu):
            thread = Thread(
                target=request_thread,
                args=("POST", endpoint, params, data, headers, responses),
            )
            thread.start()
            threads.append(thread)
        time.sleep(0.1)
    test_is_running = False
    for thread in threads:
        if expidite_shutdown:
            thread.join(timeout=int(vus / expidite_shutdown_timeout))
        else:
            thread.join()
    return None
