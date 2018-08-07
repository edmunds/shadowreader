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

from libs import loader


def test_loader():
    data = list(range(1, 100))
    target = 9999
    original = len(data)
    load = loader._loader(uris_data=data, target=target, original=original)
    print(load, len(load))
    assert len(load) == target


def test_calculate_target_load():
    target_num_reqs = loader._calculate_target_load(
        num_reqs=1234, rate=52.5, baseline=0
    )

    assert target_num_reqs == 648


def test_calculate_target_load_w_baseline():
    min_load = 2000
    target_num_reqs = loader._calculate_target_load(
        num_reqs=1234, rate=52.5, baseline=min_load
    )

    assert target_num_reqs == 1050
