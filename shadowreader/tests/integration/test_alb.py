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

from classes.mytime import MyTime
from plugins import alb


def test_alb_producer():
    parsed_data_bucket = "sr-oss-dummy-data"
    apps = ["myELB"]

    mytime = MyTime(
        year=2018,
        month=6,
        day=21,
        hour=14,
        minute=7,
        second=0,
        microsecond=0,
        tzinfo="US/Pacific",
    )

    mytime = mytime.to_utc()
    access_logs_bucket = (
        "sr-oss-dummy-data/AWSLogs/123456789/elasticloadbalancing/us-east-1/"
    )
    testing = {"put_file": False}

    ddb_items, identifier = alb.main(
        mytime=mytime,
        bucket_w_logs=access_logs_bucket,
        apps=apps,
        parsed_data_bucket=parsed_data_bucket,
        testing=testing,
    )

    print("--ddb-items--")
    assert len(ddb_items) > 0
    return ddb_items == [
        {
            "app": "myELB",
            "num_uris": 5,
            "s3_key": "myELB/2018/05/06/06/1525589940",
            "timestamp": 1525589940,
        }
    ]


if __name__ == "__main__":
    d = test_alb_producer()
