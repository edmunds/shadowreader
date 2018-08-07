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

from os import getenv
import json

from classes.mytime import MyTime

from libs import zipper

from utils.conf import sr_plugins, env_vars

"""
    Core functions for Shadowreader Lambdas
    Used for initializing Lambdas, getting Env vars, checking if a Lambda invocation is a retry, etc
"""


def init_lambda(context, print_time=True):
    """
    context arg is the Lambda context passed from AWS Lambda invocation
    example context:
    {'aws_request_id': '210989ca-07b8-11e8-ad31-3fca2d187dd7',
    'client_context': None,
    'function_name': 'my-lambda-func',
    'function_version': '$LATEST',
    'identity': <__main__.CognitoIdentity object at 0x7f457190a438>,
    'log_stream_name': '2018/02/02/[$LATEST]1f110e1c49234b3b97c32511d7e9af78',
     'memory_limit_in_mb': '256'}
    """
    mytime = get_and_print_current_time(print_time)
    stage = env_vars["stage"]

    try:
        lambda_name = context.function_name
    except AttributeError as e:
        lambda_name = f"sr-{stage}-error-getting-context.function_name"

    return mytime, lambda_name, env_vars


def init_env_vars_apis():
    # TODO: Init other Env vars
    env_vars_to_get = ["region", "stage", "synthetic_data_table"]

    env_vars = {}
    for env_var in env_vars_to_get:
        env_vars[env_var] = getenv(env_var, "")

    for env_var, val in env_vars.items():
        if not val:
            msg = f"Invalid Lambda environment variable detected. env_var: {env_var}, env_var val: {val}"
            raise ValueError(msg)

    return env_vars


def get_and_print_current_time(print_time):
    mytime = MyTime()
    if print_time:
        print(f"Start time: {mytime}")
    return mytime


def init_consumer_master(event: dict):
    try:
        app = event["app"]
        identifier = event["identifier"]
        base_url = event["base_url"]
        cur_timestamp = event["cur_timestamp"]
        rate = float(event["rate"])
        headers = event["headers"]
        filters = event["filters"]
        baseline = event["baseline"]
    except Exception as e:
        raise ValueError(
            f"{type(e)}, {e}, error getting orchestration data from Lambda event json"
        )

    return app, identifier, cur_timestamp, rate, headers, filters, base_url, baseline


def init_consumer_slave(event: dict):
    payload = event["payload"]
    event = zipper.decompress(data=payload)
    event = json.loads(event)

    try:
        app = event["app"]
        load = event["load"]
        identifier = event["identifier"]
        delay_random = event["delay_random"]
        delay_per_req = event["delay_per_req"]
        headers = event["headers"]
    except KeyError as e:
        raise ValueError(
            f"{type(e)}, {e}, error getting event json passed from consumer-master"
        )
    return app, load, identifier, delay_random, delay_per_req, headers


def init_producer(lambda_event: dict = None) -> list:
    if lambda_event and "apps_to_parse" in lambda_event:
        apps = lambda_event["apps_to_parse"]
    else:
        apps = getenv("apps_to_parse", "[]")
        apps = json.loads(apps)

    if sr_plugins.exists("test_params_validator"):
        validator = sr_plugins.load("test_params_validator")
        validator.main(apps=apps)

    return apps
