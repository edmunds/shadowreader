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

import json

from classes.headers import Headers
from libs import lambda_init
from libs.orchestrator import invoke_func
from libs.orchestrator import (
    init_filters,
    advance_app_timestamp,
    init_apps_from_test_params,
    generate_step_from_mytime,
    print_to_logs,
)
from utils.conf import sr_plugins, sr_config, exception_handler


@exception_handler
def lambda_handler(event, context):
    """
    First gather the necessary test params, init App objects, filters and compute the current step
    After,
    then send (app, env_to_test, cur_timestamp, rate) to consumer-master
    consumer-master will then fetch data set (set of URLs) from S3, then pass it to multiple consumer-workers
    each consumer-worker will then send out requests to test environment (each worker handles up to 100 requests)
    """

    mytime, lambda_name, env_vars = lambda_init.init_lambda(context)
    stage = env_vars["stage"]
    consumer_master_past_lambda = env_vars["consumer_master_past_name"]

    apps, test_params = init_apps_from_test_params(event)
    filters = init_filters()

    step = generate_step_from_mytime(mytime)

    print("step:", step)
    for app in apps:
        advance_app_timestamp(app, step)

    consumer_event = {}

    # Invoke the consumer-master lambda for each app in apps
    for app in apps:
        headers = Headers(
            shadowreader_type="past", stage=stage, app=app, step=step
        ).headers

        consumer_event = {
            "app": app.name,
            "identifier": app.identifier,
            "base_url": app.base_url,
            "cur_timestamp": app.cur_timestamp,
            "rate": app.rate,
            "baseline": app.baseline,
            "parent_lambda": lambda_name,
            "child_lambda": consumer_master_past_lambda,
            "headers": headers,
            "filters": filters,
        }
        invoke_func(consumer_event, func=consumer_master_past_lambda)

    if apps and consumer_event:
        print_to_logs(consumer_event, apps)

    # Collect metrics and put metrics into CW
    metrics = []
    for app in apps:
        # This is the timestamp (in epoch time) that is being replayed
        # by the load test.
        metric = {
            "name": "replayed_timestamp",
            "stage": stage,
            "lambda_name": lambda_name,
            "app": app.name,
            "identifier": app.identifier,
            "mytime": mytime,
            "val": app.cur_timestamp,
        }
        metrics.append(metric)

    if sr_plugins.exists("metrics"):
        metric_emitter = sr_plugins.load("metrics")
        for metric in metrics:
            metric_emitter.main(metric)

    cur_params = {"apps": apps, "filters": filters, "test_params": test_params}

    if sr_plugins.exists("test_params_emitter"):
        params_emitter = sr_plugins.load("test_params_emitter")
        params_emitter.main(
            cur_params,
            lambda_name,
            mytime,
            stage,
            env_vars,
            sr_config,
            sr_plugins._sr_plugins,
        )

    return json.dumps(cur_params, default=str), json.dumps(consumer_event, default=str)
