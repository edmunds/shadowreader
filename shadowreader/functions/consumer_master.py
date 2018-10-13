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

import traceback
from collections import ChainMap

from libs import s3
from libs.lambda_init import init_lambda, init_consumer_master
from libs.loader import loader_main
from libs.master import invoke_slave_lambdas
from utils.conf import sr_plugins


def emit_metrics(
    base_metric: dict, num_reqs_pre_filter_val: int, num_reqs_after_filter: int
):
    """ Generate dicts to pass to metric emitter plugin """
    num_reqs_pre_filter = {
        "name": "num_requests_pre_filter",
        "val": num_reqs_pre_filter_val,
    }
    num_reqs_pre_filter = ChainMap(num_reqs_pre_filter, base_metric)

    num_reqs_pre_filter_all = {
        "app": "all",
        "name": "num_requests_pre_filter",
        "val": num_reqs_pre_filter_val,
    }
    num_reqs_pre_filter_all = ChainMap(num_reqs_pre_filter_all, base_metric)

    num_reqs = {"name": "num_requests", "val": num_reqs_after_filter}
    num_reqs = ChainMap(num_reqs, base_metric)

    num_reqs_all = {"app": "all", "name": "num_requests", "val": num_reqs_after_filter}
    num_reqs_all = ChainMap(num_reqs_all, base_metric)

    metrics = [num_reqs_pre_filter, num_reqs_pre_filter_all, num_reqs, num_reqs_all]

    if sr_plugins.exists("metrics"):
        metric_emitter = sr_plugins.load("metrics")
        for metric in metrics:
            metric_emitter.main(metric)


def lambda_handler(event, context):
    """
    Example event passed from orchestrator Lambda
        consumer_event = {
        'app': app.name,
        'env_to_test': app.env_to_test,
        'cur_timestamp': app.cur_timestamp,
        'rate': app.rate,
        'parent_lambda': lambda_name,
        'child_lambda': consumer_master_lambda_name,
        'headers': headers,
    }
    """
    try:
        mytime, lambda_name, env_vars = init_lambda(context)
        stage = env_vars["stage"]

        app, identifier, cur_timestamp, rate, headers, filters, base_url, baseline = init_consumer_master(
            event
        )

        parsed_data_bucket = env_vars["parsed_data_bucket"]

        replay_mode = sr_plugins.load("replay_mode")
        kwargs = {
            "lambda_start_time": mytime,
            "app_name": app,
            "app_cur_timestamp": cur_timestamp,
        }
        s3_parsed_data_key = replay_mode.main(**kwargs)

        print(f"s3://{parsed_data_bucket}/{s3_parsed_data_key}")

        # Fetch from S3 the URLs to send for this load test
        load = s3.fetch_from_s3(key=s3_parsed_data_key, bucket=parsed_data_bucket)

        num_reqs_pre_filter = len(load)

        # Transform the URLs based on the test params and filters
        load = loader_main(
            load=load, rate=rate, baseline=baseline, base_url=base_url, filters=filters
        )

        num_reqs_after_filter = len(load)

        # Init base metric dict
        base_metric = {
            "stage": stage,
            "lambda_name": lambda_name,
            "app": app,
            "identifier": identifier,
            "mytime": mytime,
        }

        emit_metrics(base_metric, num_reqs_pre_filter, num_reqs_after_filter)

        invoke_slave_lambdas(
            load=load,
            app=app,
            identifier=identifier,
            parent_lambda=lambda_name,
            headers=headers,
        )

    except Exception as e:
        trace = traceback.format_exc()
        raise Exception(trace)

    return app
