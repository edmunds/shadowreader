"""
Copyright 2018 Edmunds.com, Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import json
import math
import time
import random

import boto3

from utils.conf import env_vars
from libs import zipper
from libs.delay import (
    calculate_delay_per_req,
    calculate_total_expected_execution_time,
    calculate_delays_between_workers,
    make_delays_random,
)

cl = boto3.client("lambda", region_name=env_vars["region"])

consumer_worker_lambda = env_vars["consumer_worker_name"]


def invoke_worker_lambdas(
    *, load: list, app: str, identifier: str, parent_lambda: str, headers: dict
):
    print(f"Start invoking worker lambdas: {app}")
    if len(load) == 0:
        print(f"Load was empty, stopping worker invocations: {app}")
        return 0, 0, 0  # return futs, timeouts, exceptions to CW metrics

    load_chunks, chunk_size = _generate_chunked_load(load, chunk_max=100)

    delay_per_req = _calculate_delays(load_size=len(load))
    delays = calculate_delays_between_workers(load_chunks, delay_per_req)

    delay_random = True
    delays = make_delays_random(delays)

    print(f"chunk size: {chunk_size}, # chunks: {len(load_chunks)}")

    event = {
        "delay_per_req": delay_per_req,
        "delay_random": delay_random,
        "rate": 100,
        "app": app,
        "identifier": identifier,
        "parent_lambda": parent_lambda,
        "child_lambda": consumer_worker_lambda,
        "headers": headers,
    }

    _invoke_workers(event, load_chunks, delays)


def _invoke_workers(event, load_chunks, delays):
    print("chunks:", [len(ch) for ch in load_chunks])
    print("delays:", delays)
    print("delay total:", sum(delays))

    num_chunks = len(load_chunks)
    for i, chunk in enumerate(load_chunks):
        event["load"] = chunk
        event["worker_num"] = f"{i}/{num_chunks}"
        delay_for_this_worker = delays[i]

        _invoke_func_w_zip(event, consumer_worker_lambda)

        if i < num_chunks - 1:
            time.sleep(
                delay_for_this_worker
            )  # Sleep if this is not the last worker lambda to invoke


def _calculate_delays_for_workers(load_chunks, delay_per_req):
    delays = []
    for chunk in load_chunks:
        num_reqs = len(chunk)
        delay_for_this_worker = delay_per_req * num_reqs
        delays.append(delay_for_this_worker)
    return delays


def _generate_chunked_load(load: list, chunk_max: int):
    load_size = len(load)
    chunk_size = _calculate_chunk_size(load_size, chunk_max=chunk_max)

    load_chunks = _generate_chunks(
        load, chunk_size, smallest_chunk_size_ratio_allowed=0.8
    )

    return load_chunks, chunk_size


def _calculate_delays(load_size: int):
    """ Figure out how long master should run for and how long delays should be between requests """
    total_expected_execution_time = calculate_total_expected_execution_time(load_size)

    delay_per_req = calculate_delay_per_req(load_size, total_expected_execution_time)
    return delay_per_req


def _calculate_chunk_size(load_size: int, chunk_max: int) -> int:
    divisions = load_size / chunk_max
    divisions = math.ceil(divisions)
    size = math.floor(load_size / divisions)
    return size


def _generate_chunks(
    load: list, chunk_size: int, smallest_chunk_size_ratio_allowed: float
) -> list:
    """
    Given a load (list of URLs), batch them into chunks, each of size 'chunk_size',
    transforming the load into a list of lists
    """
    load_chunks = list(_make_chunks(load, chunk_size))
    """
    If the last chunk is much smaller than the others, then distribute the URLs
    in the last chunk to the rest of the chunks
    This is to ensure that the requests/URLs being sent is evenly distributed over 60 seconds
    """
    if len(load_chunks) > 2:
        if smallest_chunk_size_ratio_allowed > len(load_chunks[-1]) / chunk_size:
            load_chunks = _distribute_last_chunk(load_chunks)

    return load_chunks


def _distribute_last_chunk(chunks: list) -> list:
    last = chunks.pop()
    num_chunks = len(chunks)

    rand_chunk = random.randint(0, num_chunks - 1)
    chunks[rand_chunk] += last
    return chunks


def _make_chunks(load, size_of_each_chunk):
    for i in range(0, len(load), size_of_each_chunk):
        d = load[i : i + size_of_each_chunk]
        yield d


def _invoke_func_w_zip(payload: dict, func: str):
    payload = json.dumps(payload)
    payload = zipper.compress(
        data=payload
    )  # Need to compress payload due to 130KB limit on Lambda invoke API
    payload = {"payload": payload}
    resp = _invoke_func(payload, func)
    return resp


def _invoke_func(payload: dict, func: str):
    payload = json.dumps(payload)
    try:
        resp = cl.invoke(
            FunctionName=func, InvocationType="Event", LogType="None", Payload=payload
        )
    except Exception as e:
        raise e

    return resp
