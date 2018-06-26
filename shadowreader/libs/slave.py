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

import random
import time
from typing import Callable

from requests_futures.sessions import FuturesSession

from utils.conf import sr_plugins, sr_config

timeouts = sr_config["timeouts"]


def send_requests_slave(load: list, delay: float, random_delay: bool, headers: dict):
    """
    Start sending out requests, given load (URLs), delay (delay to insert between requests) and headers (User-Agent
    for the requests)
    """
    if len(load) == 0:
        return 0, 0, 0  # return futs, timeouts, exceptions

    if sr_plugins.exists("circuit_breaker"):
        cb = sr_plugins.load("circuit_breaker")
        first_url = load[0]["url"]
        cb.main(url=first_url)

    session = FuturesSession(max_workers=5)

    if sr_plugins.exists("slave_headers"):
        slave_headers = sr_plugins.load("slave_headers")
    else:
        slave_headers = None

    futs = _send_futs_slave(
        session,
        load,
        delay=delay,
        random_delay=random_delay,
        headers=headers,
        slave_headers=slave_headers,
    )
    futs, timeouts, exceptions = _collect_futs_slave(futs)

    return futs, timeouts, exceptions


def _send_futs_slave(
        session,
        load: list,
        delay: float,
        random_delay: bool,
        headers: dict,
        slave_headers: Callable[[dict, dict], dict] = None,
):
    """ Start load testing by sending requests to the specified URLs """
    futs = []
    for l in load:
        _do_sleep(delay, random_delay)

        if slave_headers:
            headers = slave_headers.main(load=l, headers=headers)

        init_timeout = timeouts["init_timeout"]
        resp_timeout = timeouts["resp_timeout"]
        redirects = True
        if "req_method" in l:
            req_method = l["req_method"].lower()
            if req_method == "get" or req_method == "post":
                fut = _send_request(
                    session,
                    req_method,
                    l["url"],
                    headers,
                    init_timeout,
                    resp_timeout,
                    redirects,
                )
            else:
                # Other request methods not supported currently
                fut = None
        else:
            fut = _send_request(
                session, "get", l["url"], headers, init_timeout, resp_timeout, redirects
            )

        if fut:
            futs.append({"live": l, "fut": fut})

    return futs


def _send_request(
        session, req_method, url, headers, init_timeout, resp_timeout, redirects
):
    fut = session.request(
        req_method,
        url,
        headers=headers,
        timeout=(init_timeout, resp_timeout),
        allow_redirects=redirects,
    )
    return fut


def _do_sleep(delay, random_delay):
    if delay > 0:
        if random_delay:
            time.sleep(delay * random.random() * 2)
        else:
            time.sleep(delay)


def _collect_futs_slave(futs):
    timeouts, exceptions = 0, 0
    errs = []
    for i, fut in enumerate(futs):
        try:
            r = fut["fut"].result()

        except IOError as e:
            errs.append(f"{type(e)}, {e}")
            # print(type(e), e)
            timeouts += 1

        except Exception as e:
            errs.append(f"{type(e)}, {e}")
            # print(type(e), e)
            exceptions += 1

    if errs:
        err = random.sample(errs, 1)
        print(err)
    return futs, timeouts, exceptions
