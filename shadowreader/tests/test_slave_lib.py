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

from libs import slave

from requests_futures.sessions import FuturesSession


def test_send_requests_slave(monkeypatch):
    load = [{"url": "http://shadowreader.example.com", "req_method": "POST"}]
    headers = {"User-Agent": "sr_pytest"}

    fut = FuturesSession().get("http://www.example.com")
    monkeypatch.setattr("libs.slave._send_request", lambda a, b, c, d, e, f, g: fut)

    futs, timeouts, exceptions = slave.send_requests_slave(
        load=load, delay=0.1, random_delay=True, headers=headers
    )

    assert len(futs) == 1

    fut = futs[0]["fut"]
    assert fut.result().status_code == 200
