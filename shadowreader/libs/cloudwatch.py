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

import boto3

from classes.mytime import MyTime
from utils.conf import env_vars

region = env_vars['region']

# Create CloudWatch clients
cw = boto3.client('cloudwatch', region_name=region)


def put_lambda_metric_w_app_and_env_to_test(metric_name: str,
                                            sr_stage: str,
                                            lambda_name: str,
                                            app: str,
                                            identifier: str,
                                            mytime: MyTime,
                                            storage_resolution: int = 60,
                                            val: int = 0) -> dict:
    """ Put a custom CloudWatch metric in the "sr" namespace """
    dimensions = [{
        'Name': 'sr_stage',
        'Value': sr_stage
    }, {
        'Name': 'lambda',
        'Value': lambda_name
    }, {
        'Name': 'app',
        'Value': app
    }, {
        'Name': 'identifier',
        'Value': identifier
    }]
    timestamp = mytime.epoch
    namespace = 'sr'
    resp = _put_metric(namespace, metric_name, dimensions, timestamp, val,
                       storage_resolution)
    return resp


def _put_metric(namespace: str,
                metric_name: str,
                dimensions: list,
                timestamp: int,
                val: float,
                storage_resolution: int = 60):
    """ Put a custom CloudWatch metric """
    resp = cw.put_metric_data(
        Namespace=namespace,
        MetricData=[{
            'MetricName': metric_name,
            'Dimensions': dimensions,
            'Timestamp': int(timestamp),
            'Value': val,
            'Unit': 'Count',
            'StorageResolution': storage_resolution
        }])
    return resp
