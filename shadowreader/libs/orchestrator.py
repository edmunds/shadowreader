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
from pprint import pprint
from typing import Tuple
from os import getenv

import boto3
from pytz import timezone

from classes.app import App
from classes.mytime import MyTime
from libs.validate import validate_test_params, validate_timezone
from utils.conf import sr_plugins, env_vars


def init_apps_from_test_params(event: dict = None) -> Tuple[list, dict]:
    apps_to_test, test_params, overrides, tzinfo = _get_env_vars(event)

    _validate_params(
        apps=apps_to_test, test_params=test_params, overrides=overrides, tzinfo=tzinfo
    )

    validate_timezone(tzinfo)

    validate_test_params(test_params, tzinfo)

    apps = _init_app_objs(apps_to_test, test_params, tzinfo)
    override_apps = _init_overrides(overrides, tzinfo)

    apps = _merge_app_dicts_to_list(apps, override_apps)
    apps = _filter_out_apps_w_rate_zero(apps)

    return apps, test_params


def _validate_params(**kwargs):
    if sr_plugins.exists("test_params_validator"):
        validator = sr_plugins.load("test_params_validator")
        validator.main(**kwargs)


def _get_env_vars(event: dict):
    defaults = _check_for_defaults(event)
    env_vars = {}
    env_vars_to_get = ["apps_to_test", "test_params", "overrides"]

    for e in env_vars_to_get:
        if defaults:
            env_var = defaults[e]
        else:
            env_var = getenv(e, "{}")
            env_var = json.loads(env_var)

        env_vars[e] = env_var

    if defaults:
        tzinfo = getenv("timezone", defaults["timezone"])
    else:
        tzinfo = getenv("timezone", "UTC")

    return (
        env_vars["apps_to_test"],
        env_vars["test_params"],
        env_vars["overrides"],
        tzinfo,
    )


def _check_for_defaults(event):
    if isinstance(event, dict) and "apps_to_test" in event:
        return event
    else:
        return None


def _init_app_objs(apps_to_test: list, test_params: dict, tzinfo: timezone):
    apps = {}

    for app_name in apps_to_test:
        app = _init_app_obj_from_params(app_name, test_params, tzinfo)
        apps[app_name] = app

    return apps


def _init_app_obj_from_params(app_name: str, params: dict, tzinfo: timezone) -> App:
    """
    "rate": 50,
    "loop_duration": 60,
    "replay_start_time": "2018-3-26-12-30",
    "base_url": "https://www.my-website.com",
    "identifier": "qa",
    "env_to_test": "qa"
    """
    rate = params["rate"]
    if "baseline" in params:
        baseline = params["baseline"]
    else:
        baseline = 0

    loop_duration = params["loop_duration"]

    replay_start_time = params["replay_start_time"]
    replay_start_time = MyTime.set_to_replay_start_time_env_var(
        replay_start_time, tzinfo=tzinfo
    )

    base_url = params["base_url"]

    identifier = params["identifier"] if "identifier" in params else ""

    return App(
        name=app_name,
        replay_start_time=replay_start_time,
        loop_duration=loop_duration,
        base_url=base_url,
        rate=rate,
        baseline=baseline,
        identifier=identifier,
    )


def _init_overrides(overrides: dict, tzinfo: timezone) -> dict:
    apps = {}
    for override in overrides:
        app_name = override["app"]
        app = _init_app_obj_from_params(app_name, override, tzinfo)
        apps[app_name] = app
    return apps


def _merge_app_dicts_to_list(apps: dict, override_apps: dict) -> list:
    for app, params in override_apps.items():
        if app in apps:
            apps[app] = params

    return list(apps.values())


def _filter_out_apps_w_rate_zero(apps: list) -> list:
    return [app for app in apps if app.rate > 0]


def init_filters():
    """ Initialize filters that will filter out certain requests from load test replay """
    defaults = '{"app": "*", "uri": "*", "status": [200, 300, 400, 500], "apply_filter": false}'
    filters = json.loads(getenv("filters", defaults))
    return filters


def choose_projection_rate(projection, steps):
    size = len(projection)
    step = steps % size
    rate = projection[step]
    # multiple rate by 100 as rate is a number between 0 to 1, so must convert to percentage value
    return rate * 100


def advance_app_timestamp(app, step):
    if app.loop_duration == 0:  # If loop duration is 0, then don't advance timestamp
        return app

    try:
        app.cur_timestamp = app.cur_timestamp + (step % app.loop_duration) * 60
    except ArithmeticError as e:
        raise ArithmeticError(
            f"{type(e)}, {e}: app.cur_timestamp = {app.cur_timestamp} + ({step} % {app.loop_duration}) * 60"
        )
    return app


def invoke_func(event, func):
    cl = boto3.client("lambda", region_name=env_vars["region"])
    args = json.dumps(event)
    resp = cl.invoke_async(FunctionName=func, InvokeArgs=args)
    return resp


def generate_step_from_mytime(mytime) -> int:
    mytime = mytime.set_seconds_to_zero()
    m = mytime.epoch % 1508201100
    step = m // 60
    return step


def print_to_logs(consumer_event, apps):
    if consumer_event and apps:
        msg = "\n".join([x.name for x in apps])
        print(f"Invoke consumer-master-past for: {len(apps)} apps\n{msg}")
        print("Sample consumer_event:")
        pprint(consumer_event)
