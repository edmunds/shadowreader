import json
from functools import reduce
from operator import add
from collections import defaultdict

import re
import click
import pendulum

from plugins.alb import _batch_lines_by_timestamp, _put_payload_on_s3

timestamp_field = "timestamp"


@click.command()
@click.option("--file", help="file to parse")
@click.option("--app", help="name of app")
@click.option("--bucket", help="name of app")
@click.option("--timeformat", help="name of app")
@click.option("--regex", help="name of app")
def main(file: str, app: str, bucket: str, timeformat: str, regex: str):
    # def main(file: str, app: str, bucket: str, regex: str, timeformat: str = ""):
    """
    Accepts input from CLI to parse locally stored logs
    Example:
    python3 parser.py --file logs --app app1 --bucket serverless-sr-deploys \
    --timeformat 'DD/MMM/YYYY:HH:mm:ss ZZ' \
    --regex '(?P<remote_addr>[\S]+) - (?P<remote_user>[\S]+) \[(?P<timestamp>.+)\] "(?P<req_method>.+) (?P<uri>.+) (?P<httpver>.+)" (?P<status>[\S]+) (?P<body_bytes_sent>[\S]+) "(?P<referer>[\S]+)" "(?P<user_agent>[\S]+)" "(?P<x_forwarded_for>[\S]+)"'

    :param file: Name of log file to parse
    :param app: Name of the application for the logs
    :param bucket: S3 bucket to store the parsed logs to
    :param timeformat: The format of the timestamp in the logs
                       Accepts the following tokens: https://pendulum.eustace.io/docs/#tokens
    :param regex: Regex to use to parse the logs
    """  # noqa: W605

    def parse_time(t):
        if timeformat:
            return pendulum.from_format(t, timeformat)
        else:
            return pendulum.parse(t)

    with open(file) as f:
        lines = f.readlines()

    regex = re.compile(regex)

    lines = [x.strip() for x in lines if x.strip()]
    lines = [regex.match(x) for x in lines if x]
    lines = [x.groupdict() for x in lines if x]

    tzinfo = pendulum.tz.local_timezone()
    if lines:
        first = lines[0]
        inst = parse_time(first[timestamp_field])
        tzinfo = inst.tzinfo

    for l in lines:
        l[timestamp_field] = parse_time(l[timestamp_field])

    payload = {app: defaultdict(list)}
    payload = _batch_lines_by_timestamp(lines, payload, app)

    parse_results = _put_payload_on_s3(
        payload=payload[app], bucket=bucket, elb_name=app, testing={}
    )

    print_stats(parse_results, tzinfo, app)


def print_stats(res: list, tzinfo, app: str):
    """
    Print the results of the parse
    :param res: Results of the parsing
    :param tzinfo: Timezone found in logs
    :param app: Name of application for the logs
    """
    mins_of_data = len(res)

    total_reqs = reduce(add, [x["num_uris"] for x in res])
    max_reqs = max([x["num_uris"] for x in res])
    min_reqs = min([x["num_uris"] for x in res])
    avg_reqs = total_reqs // mins_of_data

    first, last = res[0], res[-1]
    first, last = first["timestamp"], last["timestamp"]
    first = pendulum.from_timestamp(first, tzinfo)
    last = pendulum.from_timestamp(last, tzinfo)
    first, last = first.isoformat()[:16], last.isoformat()[:16]

    test_params = {
        "base_url": "http://$your_base_url",
        "rate": 100,
        "replay_start_time": first,
        "replay_end_time": last,
        "identifier": "oss",
    }

    dump = json.dumps(test_params, indent=2)
    click.echo(f"{mins_of_data} minutes of traffic data was uploaded to S3.")
    click.echo(f"Average requests/min: {avg_reqs}")
    click.echo(f"Max requests/min: {max_reqs}")
    click.echo(f"Min requests/min: {min_reqs}")
    click.echo(f"Timezone found in logs: {tzinfo.name}")
    click.echo(
        f"To load test with these results, use the below parameters for the orchestrator in serverless.yml"
    )
    click.echo(f"==========================================")
    click.echo(f"test_params: '{dump}'")
    click.echo(f"apps_to_test: '[\"{app}\"]'")
    click.echo(f"==========================================")

    """
    Output shoud look like:
    5 minutes of traffic data was uploaded to S3.
    Average requests/min: 6
    Max requests/min: 8
    Min requests/min: 2
    Timezone found in logs: +00:00
    To load test with these results, use the below parameters for the orchestrator in serverless.yml
    ==========================================
    test_params: {
      "base_url": "http://$your_base_url",
      "rate": 100,
      "replay_start_time": "2019-03-15T04:12",
      "replay_end_time": "2019-03-15T04:16",
      "identifier": "oss"
    }
    apps_to_test: ["app1"]
    ==========================================
    """


if __name__ == "__main__":
    main()
