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

from functions import consumer_slave
import json
from libs import zipper
from libs.loader import loader_main

app = 'test-app'
myload = [{
    "status": "200",
    "request_uri": "/get?foo1=bar1",
    "http_true_client_ip": "102.250.174.10",
    "user_agent": "test-user-agent",
    "app": app
}, {
    "status": "200",
    "request_uri": "/get?foo1=bar2",
    "http_true_client_ip": "198.0.150.21",
    "user_agent": "test-user-agent",
    "app": app
}, {
    "status": "200",
    "request_uri": "/get?foo1=bar3",
    "http_true_client_ip": "162.197.49.3",
    "user_agent": "test-user-agent",
    "app": app
}, {
    "status": "200",
    "request_uri": "/get?foo1=bar4",
    "http_true_client_ip": "72.83.226.30",
    "user_agent": "test-user-agent",
    "app": app
}]


def test_consumer_slave_lambda_handler():
    load = loader_main(
        load=myload,
        rate=1,
        baseline=0,
        base_url='https://postman-echo.com',
        filters={})

    from pprint import pprint
    pprint(load)

    event = {
        'delay_per_req': 0.01,
        'delay_random': True,
        'load': load,
        'rate': 1,
        'app': 'pytest',
        'identifier': 'qa',
        'parent_lambda': 'pytest',
        'child_lambda': 'sr-dev-consumer-slave',
        'headers': {
            'User-Agent': 'sr-dev-pytest'
        },
    }

    event = json.dumps(event)
    event = zipper.compress(data=event)
    event = {'payload': event}
    num_reqs_val = consumer_slave.lambda_handler(event, '')
    assert num_reqs_val == 1
