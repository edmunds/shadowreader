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
"""
import random


def calculate_total_expected_execution_time(load_size: int) -> float:
    """ Total time consumer-master should buffer out slave invocations for"""
    if load_size < 500:
        total_expected_execution_time = 70
    else:
        total_expected_execution_time = random.randint(50, 70)
    return total_expected_execution_time


def calculate_delay_per_req(num_total_requests: int,
                            total_expected_execution_time: float) -> float:
    """ Calculate the delay to insert between each request sent by slave lambda """
    delay_per_req = total_expected_execution_time / num_total_requests
    delay_per_req = round(delay_per_req, 3)
    return delay_per_req


def calculate_delays_between_slaves(load_chunks, delay_per_req):
    """ Calculate amount of delay to insert between slave invocations"""
    delays = []
    for chunk in load_chunks:
        num_reqs = len(chunk)
        delay_for_this_slave = delay_per_req * num_reqs
        delays.append(delay_for_this_slave)
    return delays


def make_delays_random(delays):
    delays = [delay * random.uniform(0.85, 1.15) for delay in delays]
    delays = [round(delay, 3) for delay in delays]
    return delays
