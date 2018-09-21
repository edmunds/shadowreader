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

import gzip
import re
import boto3

from libs.s3 import (
    put_on_s3,
    _generate_key_prefix_base_on_time,
    delete_tmp_file,
    fetch_file_names_on_s3,
)
from classes.mytime import MyTime
from typing import Tuple, Match
from collections import defaultdict

s3cl = boto3.client("s3")
elb_regex = r"(?P<type>[\S]+) (?P<timestamp>[\S]+) (?P<elb>[\S]+) (?P<client>[\S]+) (?P<target>[\S]+) (?P<request_processing_time>[\S]+) (?P<target_processing_time>[\S]+) (?P<response_processing_time>[\S]+) (?P<elb_status_code>[\S]+) (?P<target_status_code>[\S]+) (?P<received_bytes>[\S]+) (?P<sent_bytes>[\S]+) \"(?P<request>.*)\" \"(?P<user_agent>.*)\" (?P<ssl_cipher>[\S]+) (?P<ssl_protocol>[\S]+) (?P<target_group_arn>[\S]+) \"(?P<trace_id>[\S]+)\" \"(?P<domain_name>[\S]+)\" \"(?P<chosen_cert_arn>[\S]+)\""
regex = re.compile(elb_regex)


def _download_file(bucket: str, key: str) -> str:
    """ download file, unzip it then return the contents """
    tmp_file_name = f"/tmp/logs"

    try:
        with open(tmp_file_name, "wb") as data:
            s3cl.download_fileobj(bucket, key, data)
    except Exception as e:
        print(type(e).__name__, e)
        f = open(tmp_file_name, "w")
        f.write("")
        f.close()
    try:
        with gzip.open(tmp_file_name, mode="rt") as f:
            x = f.read()
            return x
    except Exception as e:
        print(type(e).__name__, e, key)
        return ""


def _parse_line(line: Match[str]) -> dict:
    """ Parse the a line in the ELB logs for various attributes"""
    request = line.group("request")
    request = request.split()
    req_method = request[0]  # GET, POST, PUT, etc.
    url = request[1]
    x = url.split("/")[3:]
    uri = f'/{"/".join(x)}'

    timestamp = line.group("timestamp")  # timestamp in ISO format
    timestamp = MyTime._try_isoformat(timestamp, tzinfo="UTC").dt

    res = {
        "url": url,
        "uri": uri,
        "req_method": req_method,
        "timestamp": timestamp,
        "user_agent": line.group("user_agent"),
    }
    return res


def _batch_lines_by_timestamp(lines: list, payload: dict, app: str) -> dict:
    for line in lines:
        epoch = line["timestamp"].timestamp()
        mytime = MyTime.from_epoch(epoch=epoch, tzinfo="UTC").set_seconds_to_zero()
        mytime = mytime.epoch

        payload[app][mytime].append(line)
    return payload


def _filter_payload_for_get_requests(payload: dict, app: str) -> dict:
    for timestamp, val in payload[app].items():
        payload[app][timestamp] = list(filter(lambda x: x["req_method"] == "GET", val))
    return payload


def _count_num_of_lines_in_payload(payload: dict) -> int:
    len_all_lines = [len(lines) for timestamp, lines in payload.items()]
    total_num_lines = sum(len_all_lines)
    return total_num_lines


def _generate_s3_key(mytime: MyTime, elb_logs_path: str) -> str:
    date_prefix = _generate_key_prefix_base_on_time(
        mytime=mytime.to_utc(), time_format="%Y/%m/%d"
    )
    elb_logs_path = f"{elb_logs_path}/{date_prefix}"

    return elb_logs_path


def _download_and_parse_s3_data(files: list, elb_logs_bucket: str, app: str) -> dict:
    lines = []
    for f in files:
        data = _download_file(elb_logs_bucket, f["Key"])
        delete_tmp_file()
        lines += data.splitlines()

    lines = _regex_match_and_parse_logs(lines)

    payload = {app: defaultdict(list)}

    payload = _batch_lines_by_timestamp(lines, payload, app)

    payload = _filter_payload_for_get_requests(payload, app)

    num_lines = _count_num_of_lines_in_payload(payload[app])

    print(f"# lines produced: {num_lines}")
    return payload


def _regex_match_and_parse_logs(lines):
    lines = [regex.match(line) for line in lines]
    lines = sorted(lines, key=lambda x: x.group("timestamp"))
    lines = [_parse_line(line) for line in lines]
    return lines


def _deduce_bucket_n_path(bucket_w_logs: str) -> Tuple[str, str]:
    if bucket_w_logs.endswith("/"):
        bucket_w_logs = bucket_w_logs[:-1]

    regex = "^(?P<bucket>[^\/]+)\/(?P<path>.*)"
    match = re.match(regex, bucket_w_logs)
    elb_logs_bucket = match.group("bucket")
    elb_logs_path = match.group("path")
    return elb_logs_bucket, elb_logs_path


def _put_payload_on_s3(
    *, payload: dict, elb_name: str, bucket: str, testing: dict = None
) -> list:
    if testing and not "put_file":
        put_file = False
    else:
        put_file = True

    ddb_items = []
    for timestamp, lines in payload.items():
        mytime = MyTime.from_epoch(epoch=int(timestamp), tzinfo="UTC")
        s3_key = put_on_s3(lines, mytime, elb_name, bucket, put_file=put_file)
        ddb_item = {
            "timestamp": mytime.epoch,
            "s3_key": s3_key,
            "app": elb_name,
            "num_uris": len(lines),
        }
        ddb_items.append(ddb_item)
    return ddb_items


def main(
    *,
    mytime: MyTime,
    bucket_w_logs: str,
    apps: list,
    parsed_data_bucket: str,
    testing: dict = None,
) -> Tuple[list, str]:

    mytime = mytime.to_utc()
    if apps:
        app = identifier = apps[0]
    else:
        app = identifier = "myELB"

    elb_logs_bucket, elb_logs_path = _deduce_bucket_n_path(bucket_w_logs)

    key_prefix = _generate_s3_key(mytime, elb_logs_path)
    print(f"key s3://{elb_logs_bucket}/{key_prefix}")

    files, start_time = fetch_file_names_on_s3(
        bucket=elb_logs_bucket, key_prefix=key_prefix, mytime=mytime, time_offset=1
    )

    print("# files:", len(files))
    """
    Example payload = {'myELB': {1525529400: {..}, 1525529460: {...}}}
    """
    payload = _download_and_parse_s3_data(files, elb_logs_bucket, apps[0])

    ddb_items = _put_payload_on_s3(
        payload=payload[app],
        bucket=parsed_data_bucket,
        elb_name=identifier,
        testing=testing,
    )

    return ddb_items, identifier


if __name__ == "__main__":
    pass
