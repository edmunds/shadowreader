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
import os
import boto3
import json
from utils.conf import env_vars
from classes.mytime import MyTime
from botocore.exceptions import ClientError


aws_region = env_vars["region"]

s3 = boto3.client("s3", region_name=aws_region)
s3res = boto3.resource("s3", region_name=aws_region)


def put_on_s3(
    data: list, mytime: MyTime, app_name: str, bucket: str, put_file: bool = True
) -> str:
    key = _generate_s3_key(mytime, app_name)
    if put_file:
        _put_on_s3(data, key=key, bucket=bucket)
    return key


def _put_on_s3(data, key: str, bucket: str) -> dict:
    with open("/tmp/mydata", "w") as f:
        f.write(json.dumps(data, default=str))

    resp = _put_file("/tmp/mydata", key, bucket=bucket)
    return resp


def _generate_s3_key(mytime: MyTime, app_name: str) -> str:
    prefix = _generate_key_prefix_base_on_time(mytime=mytime, time_format="%Y/%m/%d/%H")
    key = f"{app_name}/{prefix}/{mytime.epoch}"
    return key


def _generate_key_prefix_base_on_time(*, mytime, time_format):
    prefix = mytime.dt.strftime(time_format)
    return prefix


def _put_file(myfile, key, bucket):
    # print(f'PUT s3://{bucket}/{key}')
    resp = s3res.meta.client.upload_file(myfile, bucket, key)
    return resp


def fetch_from_s3(*, key: str, bucket: str) -> list:
    s3_data = _download_parsed_file(bucket=bucket, key=key)
    delete_tmp_file()
    return json.loads(s3_data)


def _download_parsed_file(*, bucket: str, key: str) -> str:
    """
    :param key: ex: "my-app/parsed_urls"
    :param bucket: ex: sr-my-parsed-data
    """
    tmp_file_name = f"/tmp/logs"
    try:
        with open(tmp_file_name, "wb") as data:
            s3.download_fileobj(bucket, key, data)
    except ClientError as e:
        #  If no URLs were found, then return an empty list/load
        if (
            e.args[0]
            == "An error occurred (404) when calling the HeadObject operation: Not Found"
        ):
            print(f"URL data was not found at s3://{bucket}/{key}")
            return "[]"
        #  Otherwise raise error
        else:
            raise ValueError(
                f"{e}, Error downloading file from S3, for s3://{bucket}/{key}"
            ) from None

    except Exception as e:
        raise ValueError(
            f"{e}, Error downloading file from S3, for s3://{bucket}/{key}"
        ) from None

    try:
        with open(tmp_file_name, mode="rt") as f:
            s3_data = f.read()
    except Exception as e:
        raise ValueError(
            f"{e}, Error downloading file from S3, for s3://{bucket}/{key}"
        ) from None

    return s3_data


""" OSS CODE """


def fetch_logs_on_s3_alb(bucket, key_prefix, mytime, time_offset):
    files = _list_folder_contents(bucket, key_prefix)
    print("# files pre filter:", len(files))

    start_time = mytime.add_timedelta(minutes=-time_offset)
    end_time = mytime.add_timedelta(minutes=time_offset)

    files_filtered = _filter_files_on_time(files, start_time, end_time)

    return files_filtered, start_time


def fetch_file_names_on_s3(
    bucket: str, key_prefix: str, mytime: MyTime, time_offset: int
):
    files = _list_folder_contents(bucket, key_prefix)

    print("# files pre filter:", len(files))

    start_time = mytime.add_timedelta(minutes=-time_offset)
    end_time = mytime

    files_filtered = _filter_files_on_time(files, start_time, end_time)

    return files_filtered, start_time


def _list_folder_contents(bucket, key_prefix):
    paginator = s3.get_paginator("list_objects")
    iterator = paginator.paginate(Bucket=bucket, Prefix=key_prefix)

    files = []
    for page in iterator:
        files += page["Contents"]

    return files


def _filter_files_on_time(files: list, start_time: MyTime, end_time: MyTime) -> list:
    """
    :param files: List of files on S3
    :param start_time: Time the file's timestamp should be after
    :param end_time:  Time the file's timestamp should be before
    :return: List of files in S3 filtered by timestamp
    """
    filtered = []
    for f in files:
        timestamp = f["LastModified"]
        if start_time.dt <= timestamp < end_time.dt:
            filtered.append(f)
    return filtered


def delete_tmp_file():
    os.remove("/tmp/logs")


def put_payload_on_s3(*, payload: dict, bucket: str, mytime: MyTime):
    mytime = mytime.add_timedelta(minutes=-1)
    ddb_items = []
    for app, data in payload.items():
        s3_key = put_on_s3(data, mytime, app, bucket)
        ddb_item = {
            "timestamp": mytime.epoch,
            "s3_key": s3_key,
            "app": app,
            "num_uris": len(data),
        }
        ddb_items.append(ddb_item)
    return ddb_items
