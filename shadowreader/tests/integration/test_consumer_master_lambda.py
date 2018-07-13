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

from functions import consumer_master_past


def test_consumer_master_past_lambda_handler():
    test_app = 'test-app1'
    identifier = 'qa'

    event = {
        'app': test_app,
        'child_lambda_past': 'sr-local-pytest',
        'cur_timestamp': 1525371600,
        'identifier': identifier,
        'base_url': 'http://shadowreader.example.com',
        'filters': {
            'app': '',
            'apply_filter': True,
            'status': [],
            'type': 'exclude',
            'uri': '',
            'user_agent': ['Apache-HttpClient', 'node-fetch', 'Jmeter']
        },
        'headers': {
            'User-Agent':
            'sr_local_pytest'
        },
        'parent_lambda': 'sr-local-pytest',
        'rate': 1,
        'baseline': 0,
    }
    res = consumer_master_past.lambda_handler(event, {})
    assert res == test_app
