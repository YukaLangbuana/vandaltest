import time
import json
import requests
from threading import Thread
from queue import Queue


def spike_test(
    method: str,
    endpoint: str,
    params: dict = {},
    data: dict = {},
    headers: dict = {},
    duration: int = 5,
    vus: int = 100,
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
    spike_threads = []
    test_is_running = True
    spike_is_running = False

    def request_thread(method, endpoint, params, data, headers, list_to_append):
        while test_is_running:
            response = requests.request(
                method, endpoint, params=params, data=json.dumps(data), headers=headers
            )
            list_to_append.put(response)

    def spike_thread(method, endpoint, params, data, headers, list_to_append):
        while spike_is_running:
            response = requests.request(
                method, endpoint, params=params, data=json.dumps(data), headers=headers
            )
            list_to_append.put(response)

    start = time.time()
    while time.time() - start < duration:

        if time.time() - start > duration / 8 and time.time() - start < duration / 2:
            spike_is_running = True
            new_vu = int(vus) - len(threads) - len(spike_threads)
            for _ in range(new_vu):
                s_thread = Thread(
                    target=spike_thread,
                    args=("POST", endpoint, params, data, headers, responses),
                )
                s_thread.start()
                spike_threads.append(s_thread)
        elif time.time() - start > duration / 2 and len(spike_threads) > 2:
            spike_is_running = False
            for s_thread in spike_threads:
                s_thread.join()

        new_vu = 2 - len(threads)
        for _ in range(new_vu):
            thread = Thread(
                target=request_thread,
                args=("POST", endpoint, params, data, headers, responses),
            )
            thread.start()
            threads.append(thread)

    test_is_running = False
    for thread in threads:
        if expidite_shutdown:
            thread.join(timeout=int(vus / expidite_shutdown_timeout))
        else:
            thread.join()
    return None
