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

import traceback
from collections import ChainMap

from libs import lambda_init
from libs.slave import send_requests_slave
from libs.lambda_init import init_consumer_slave

from utils.conf import sr_plugins


def emit_metrics(base_metric: dict, num_reqs_val: int, timeouts: int, exceptions: int):
    """ Generate dicts to pass to metric emitter plugin """

    # Put on CW the number of requests sent
    num_reqs = {"name": "num_requests", "val": num_reqs_val}
    num_reqs = ChainMap(num_reqs, base_metric)

    num_reqs_all = {"name": "num_requests", "val": num_reqs_val, "app": "all"}
    num_reqs_all = ChainMap(num_reqs_all, base_metric)

    metrics = [num_reqs, num_reqs_all]

    # Put on CW the number of requests that timed out or errored out
    if timeouts > 0:
        num_timeouts = {"name": "timeouts", "val": timeouts}
        num_timeouts = ChainMap(num_timeouts, base_metric)
        metrics.append(num_timeouts)

    if exceptions > 0:
        num_exceptions = {"name": "exceptions", "val": exceptions}
        num_exceptions = ChainMap(num_exceptions, base_metric)
        metrics.append(num_exceptions)

    if sr_plugins.exists("metrics"):
        metric_emitter = sr_plugins.load("metrics")
        for metric in metrics:
            metric_emitter.main(metric)


def lambda_handler(event, context):
    try:
        mytime, lambda_name, env_vars = lambda_init.init_lambda(
            context, print_time=False
        )
        stage = env_vars["stage"]

        app, load, identifier, delay_random, delay_per_req, headers = init_consumer_slave(
            event
        )

        # Send out requests
        futs, timeouts, exceptions = send_requests_slave(
            load, delay_per_req, delay_random, headers
        )

        num_reqs_val = len(load)

        # Init base metric dict
        base_metric = {
            "stage": stage,
            "lambda_name": lambda_name,
            "app": app,
            "identifier": identifier,
            "mytime": mytime,
            "resolution": 1,
        }

        emit_metrics(base_metric, num_reqs_val, timeouts, exceptions)

        msg = f"app: {app}, env: {identifier} # reqs: {num_reqs_val}, " f"# timeouts: {timeouts}, # exceptions: {exceptions}"
        print(msg)

    except Exception as e:
        trace = traceback.format_exc()
        raise Exception(trace)

    return num_reqs_val
