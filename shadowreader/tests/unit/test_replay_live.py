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

from plugins import replay_live
from classes.mytime import MyTime


def test_main():
    app_name = "myELB"
    lambda_start_time = MyTime(
        year=2018,
        month=10,
        day=1,
        hour=10,
        minute=31,
        second=31,
        tzinfo="Europe/Zurich",
    )
    s3_parsed_data_key = replay_live.main(
        lambda_start_time=lambda_start_time, app_name=app_name
    )
    assert s3_parsed_data_key == "myELB/2018/10/01/08/1538382300"


if __name__ == "__main__":
    test_main()
