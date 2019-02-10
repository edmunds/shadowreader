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


from libs.lambda_init import init_lambda, init_producer
from utils.conf import sr_config, sr_plugins, exception_handler


def emit_metrics(metric: dict):
    """ Generate dicts to pass to metric emitter plugin """

    if sr_plugins.exists("metrics"):
        metric_emitter = sr_plugins.load("metrics")
        metric_emitter.main(metric)


@exception_handler
def lambda_handler(event, context):
    mytime, lambda_name, env_vars = init_lambda(context)

    apps = init_producer(event)

    print(f"apps_to_parse: {apps}, size: {len(apps)}")

    stage = env_vars["stage"]
    parsed_data_bucket = env_vars["parsed_data_bucket"]

    mytime = mytime.set_seconds_to_zero()

    access_logs_bucket = sr_config["access_logs_bucket"]

    producer = sr_plugins.load("producer")
    ddb_items, identifier = producer.main(
        mytime=mytime,
        bucket_w_logs=access_logs_bucket,
        apps=apps,
        parsed_data_bucket=parsed_data_bucket,
    )

    metric = {
        "name": "parsed_timestamp",
        "stage": stage,
        "lambda_name": lambda_name,
        "app": identifier,
        "identifier": "oss",
        "mytime": mytime,
        "val": mytime.epoch,
    }
    emit_metrics(metric)

    return identifier
