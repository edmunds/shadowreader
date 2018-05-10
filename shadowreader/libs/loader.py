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

import math
import random

from utils.conf import sr_plugins
"""
Functions for generating and transforming load test data to load to be used for consumer_slave
"""


def loader_main(*, load: list, rate: float, min_load: int, base_url: str,
                filters: dict):
    num_original_reqs = len(load)

    num_targeted_reqs = _calculate_target_load(
        num_original_reqs, rate=rate, min_load=min_load)

    print(f'rate: {num_targeted_reqs} / {num_original_reqs} = {rate}%')

    load = _loader(load, num_targeted_reqs, num_original_reqs)

    try:
        # If apply_filter key exists, set to True and there is a filter plugin
        if ('apply_filter' in filters and filters['apply_filter']
                and sr_plugins.exists('load_filter')):
            filter_plugin = sr_plugins.load('load_filter')
            load = filter_plugin.main(load=load, filters=filters)

    except Exception as e:
        print(type(e), e)
        print('# load:', len(load))
        print('filters:', filters)
        raise Exception(
            f'Error applying filters in filter_load(): {type(e)}, {e}')

    if sr_plugins.exists('loader_middleware'):
        midware = sr_plugins.load('loader_middleware')
        midware_input = {
            'load': load,
            'rate': rate,
            'base_url': base_url,
            'filters': filters,
        }
        load = midware.main(**midware_input)

    return load


def _loader(uris_data, target, original):
    if target > original:
        load = _loader(uris_data, target - original, original)
        target = original
    else:
        load = []
    if not isinstance(uris_data, list):
        print('loader data:', type(uris_data))
        print('loader keys:', uris_data.keys())
    load += random.sample(uris_data, target)
    return load


def _calculate_target_load(num_reqs: int, rate: float = 100,
                           min_load: int = 0):
    """ Given the rate and number of URLs in data set, calculate how many URLs to send in this load"""
    try:
        target_num_reqs = num_reqs * (rate / 100)
        if target_num_reqs < min_load:
            target_num_reqs = min_load + (0.5 - random.random()) * 50
        return math.ceil(target_num_reqs)
    except ArithmeticError as e:
        print(
            f'{type(e)}, {e}: int({num_reqs} * ({rate}/100)), {min_load}+(0.5 - random.random())*50'
        )
        raise ArithmeticError(
            f'{type(e)}, {e}: int({num_reqs} * ({rate}/100)), {min_load}+(0.5 - random.random())*50'
        )
