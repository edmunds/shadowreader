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

from libs import cloudwatch as cw
from classes.mytime import MyTime


def test_put_metric():
    mytime = MyTime()
    resp = cw._put_metric(
        namespace="sr",
        metric_name="pytest",
        dimensions=[],
        timestamp=mytime.epoch,
        val=1,
        storage_resolution=60,
    )
    status_code = resp["ResponseMetadata"]["HTTPStatusCode"]
    assert status_code == 200


def test_put_lambda_metric_w_app_and_env_to_test():
    mytime = MyTime()
    resp = cw.put_lambda_metric_w_app_and_env_to_test(
        "pytest",
        stage="local",
        lambda_name="pytest",
        app="pytest",
        identifier="local",
        mytime=mytime,
        val=1,
    )
    status_code = resp["ResponseMetadata"]["HTTPStatusCode"]
    assert status_code == 200
