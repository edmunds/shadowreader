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

from libs import delay, master


def test_calculate_delay_per_req():
    num_total_requests = 2231
    total_expected_execution_time = 60

    delay_per_req = delay.calculate_delay_per_req(
        num_total_requests, total_expected_execution_time
    )
    assert delay_per_req == 0.027


def test_calculate_total_expected_excecution_time():
    delay1 = delay.calculate_total_expected_execution_time(load_size=100)
    assert delay1 == 70

    delay2 = delay.calculate_total_expected_execution_time(load_size=1000)
    assert 50 <= delay2 <= 70


def test_calculate_delay_between_slaves():
    load = [1] * 1234
    load_chunks, load_size = master._generate_chunked_load(load=load, chunk_max=100)
    delay_per_req = delay.calculate_delay_per_req(
        num_total_requests=len(load), total_expected_execution_time=65
    )
    delays = delay.calculate_delays_between_slaves(load_chunks, delay_per_req)
    from pprint import pprint

    pprint(load_chunks)
    pprint(delays)

    print(sum(delays))
    assert int(sum(delays)) == 65


def test_calculate_delay_between_slaves_random():
    load = [1] * 1234
    load_chunks, load_size = master._generate_chunked_load(load=load, chunk_max=100)
    delay_per_req = delay.calculate_delay_per_req(
        num_total_requests=len(load), total_expected_execution_time=65
    )
    delays = delay.calculate_delays_between_slaves(load_chunks, delay_per_req)
    delays_rand = delay.make_delays_random(delays)

    assert delays[0] != delays_rand[0] and len(delays) == len(delays_rand)
