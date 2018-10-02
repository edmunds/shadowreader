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
from libs import s3


def main(**kwargs):
    """ Take the time the master lambda was invoked at and subtract 6 minutes from it.
        Then generate the key for the s3 object which holds access logs from that timestamp
    """
    lambda_start_time = kwargs.get("lambda_start_time", None)
    app = kwargs.get("app_name", "")
    lambda_start_time = lambda_start_time.to_utc()
    lambda_start_time = lambda_start_time.set_seconds_to_zero().add_timedelta(
        minutes=-6
    )

    s3_parsed_data_key = s3._generate_s3_key(mytime=lambda_start_time, app_name=app)
    return s3_parsed_data_key
