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
from classes.mytime import MyTime


def test_app_init():
    mytime = MyTime()
    base_url = 'http://qa-21-www.pytest.com'
    app = App(
        name='test',
        replay_start_time=mytime,
        loop_duration=60,
        base_url=base_url,
        rate=100)
    assert app.name == 'test' and app.loop_duration == 60 and app.base_url == base_url
    assert app.cur_timestamp == mytime.epoch and app.rate == 100 and app.identifier == base_url


def test_app_init_w_identifier():
    mytime = MyTime()
    base_url = 'http://qa-21-www.pytest.com'
    app = App(
        name='test',
        replay_start_time=mytime,
        loop_duration=60,
        base_url=base_url,
        rate=100,
        identifier='qa-21')
    assert app.name == 'test' and app.loop_duration == 60 and app.base_url == base_url
    assert app.cur_timestamp == mytime.epoch and app.rate == 100 and app.identifier == 'qa-21'


def test_app_str():
    mytime = MyTime(epoch=1522091259)
    base_url = 'http://qa-21-www.pytest.com'
    app = App(
        name='test',
        replay_start_time=mytime,
        loop_duration=60,
        base_url=base_url,
        rate=100,
        identifier='qa-21')
    s = 'App(name="test", ' \
        'replay_start_time=2018-03-26_19:07:39_UTC, loop_duration=60, base_url="http://qa-21-www.pytest.com", identifier="qa-21", rate=100, cur_timestamp=1522091259)'
    assert str(app) == s
