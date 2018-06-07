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

from pytz import timezone

from classes.mytime import MyTime
from functions import orchestrator_past


def test_orchestrator_lambda_handler(monkeypatch):
    defaults = {
        'apps_to_test': ['test-app1'],
        'test_params':  {
            "rate":              100,
            "loop_duration":     1,
            "replay_start_time": "2018-3-20-17-06",
            "base_url":          "http://shadowreader.example.com",
            "identifier":        "qa",
            },
        "overrides":    [{
            "app":               "test-app1",
            "rate":              50,
            "loop_duration":     1,
            "replay_start_time": "2018-3-20-17-06",
            "base_url":          "http://shadowreader.example.com",
            "identifier":        "qa",
            }],
        'timezone':     'US/Pacific'
        }
    monkeypatch.setattr("utils.conf.sr_plugins.exists", lambda x: False)

    cur_params, consumer_event = orchestrator_past.lambda_handler(defaults, {})
    timestamp = consumer_event['cur_timestamp']
    mytime = MyTime.set_to_replay_start_time_env_var(defaults['test_params']['replay_start_time'],
                                                     timezone('US/Pacific'))
    from pprint import pprint
    pprint(cur_params)
    rate = cur_params['test_params']['rate']
    assert rate == 100 and timestamp == mytime.epoch
    assert consumer_event['app'] == defaults['apps_to_test'][0]
