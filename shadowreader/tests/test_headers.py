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

from classes.app import App
from classes.headers import Headers
from classes.mytime import MyTime


def test_user_agent_generation_for_past_w_identifier():
    mytime = MyTime(epoch=1520020741)
    stage = 'local'
    step = 1234
    base_url = 'http://shadowreader.example.com'
    app = App(
            name='my-test-app',
            replay_start_time=mytime,
            loop_duration=60,
            base_url=base_url,
            identifier='qa-21',
            rate=100,
            baseline=0
    )
    headers = Headers(
            shadowreader_type='past', stage=stage, app=app, step=step).headers
    user_agent = headers['x-request-id']
    print(headers)
    assert user_agent == 'sr_local_past_qa-21_my-test-app_03-02-2018-19-59_60m_20'


def test_user_agent_generation_for_past():
    mytime = MyTime(epoch=1520020741)
    stage = 'local'
    step = 1234
    base_url = 'http://shadowreader.example.com'
    app = App(
            name='my-test-app',
            replay_start_time=mytime,
            loop_duration=60,
            base_url=base_url,
            rate=100,
            baseline=0
    )
    headers = Headers(
            shadowreader_type='past', stage=stage, app=app, step=step).headers
    user_agent = headers['x-request-id']
    print(headers)
    assert user_agent == f'sr_local_past_{base_url}_my-test-app_03-02-2018-19-59_60m_20'
