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

import math
import random

from utils.conf import sr_plugins

"""
Functions for generating and transforming load test data to load to be used for consumer_slave
"""


def loader_main(
    *, load: list, rate: float, baseline: int, base_url: str, filters: dict
) -> list:
    """ Given a target rate (an integer percentage value) and a list of URIs (load)
        Transform them to a list of URLs
        Optional filters can filter out certain requests based on its attributes
    """
    num_original_reqs = len(load)

    # Given a rate and original load size, calculate the target load size
    num_targeted_reqs = _calculate_target_load(
        num_original_reqs, rate=rate, baseline=baseline
    )

    # Increase of decrease the load by the calculated target load size
    if baseline:
        print(f"rate: target={num_targeted_reqs} / baseline={baseline} = {rate}%")
    else:
        print(f"rate: target={num_targeted_reqs} / orig={num_original_reqs} = {rate}%")

    try:
        # If apply_filter key exists, set to True and there is a filter plugin
        # Filter out certain URLs according to the test params
        if (
            "apply_filter" in filters
            and filters["apply_filter"]
            and sr_plugins.exists("load_filter")
        ):
            filter_plugin = sr_plugins.load("load_filter")
            load = filter_plugin.main(load=load, filters=filters)

    except Exception as e:
        print(type(e), e)
        print("# load:", len(load))
        print("filters:", filters)
        raise Exception(f"Error applying filters in filter_load(): {type(e)}, {e}")

    if len(load) == 0:
        return load

    print(f"load_after_filter={len(load)}")
    if num_targeted_reqs > len(load):
        ratio = math.ceil(num_targeted_reqs / len(load))
        load = load * ratio
        load = _loader(load, num_targeted_reqs, num_original_reqs)
    else:
        load = _loader(load, num_targeted_reqs, num_original_reqs)
    print(f"load_after_loader={len(load)}")

    # Pass in URIs to plugin to transform into URLs
    if sr_plugins.exists("loader_middleware"):
        midware = sr_plugins.load("loader_middleware")
        midware_input = {
            "load": load,
            "rate": rate,
            "base_url": base_url,
            "filters": filters,
            "baseline": baseline,
        }
        load = midware.main(**midware_input)

    print(f"load_after_transform={len(load)}")
    return load


def _loader(uris_data: list, target: int, original: int) -> list:
    """ Given a target load size, sample from the URIs list to generate the load required"""
    if target > original:
        load = _loader(uris_data, target - original, original)
        target = original
    else:
        load = []
    load += random.sample(uris_data, target)
    return load


def _calculate_target_load(num_reqs: int, rate: float = 100, baseline: int = 0) -> int:
    """ Given the rate and number of URLs in data set, calculate how many URLs to send in this load"""
    if baseline:
        target_num_reqs = baseline * (rate / 100)
    else:
        target_num_reqs = num_reqs * (rate / 100)
    return math.ceil(target_num_reqs)
