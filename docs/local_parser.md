# Local Parser

ShadowReader can parse logs stored locally and push it to S3, so that it can be replayed by the load testing Lambdas.


The only requirements are that:
- Logs must be in a consistent format.
- You must supply a RegEx to instruct the script of the log format.
- You must supply the time format for the timestamps in the logs.

Below is an example of how to parse logs stored in the [default Nginx log format](https://docs.nginx.com/nginx/admin-guide/monitoring/logging/)
```
log_format combined '$remote_addr - $remote_user [$time_local] '
                    '"$request" $status $body_bytes_sent '
                    '"$http_referer" "$http_user_agent"';
```

## How to
First, save the below to a `logs.txt` file.
```
10.168.166.132 - - [15/Mar/2019:04:12:24 +0000] "GET / HTTP/1.1" 403 23 "-" "ELB-HealthChecker/2.0" "-"
10.168.168.78 - - [15/Mar/2019:04:12:31 +0000] "GET / HTTP/1.1" 403 23 "-" "ELB-HealthChecker/2.0" "-"
10.168.166.132 - - [15/Mar/2019:04:12:39 +0000] "GET / HTTP/1.1" 403 23 "-" "ELB-HealthChecker/2.0" "-"
10.168.168.78 - - [15/Mar/2019:04:12:46 +0000] "GET / HTTP/1.1" 403 23 "-" "ELB-HealthChecker/2.0" "-"
10.168.166.132 - - [15/Mar/2019:04:12:54 +0000] "GET / HTTP/1.1" 403 23 "-" "ELB-HealthChecker/2.0" "-"
10.168.168.78 - - [15/Mar/2019:04:13:01 +0000] "GET / HTTP/1.1" 403 23 "-" "ELB-HealthChecker/2.0" "-"
10.168.166.132 - - [15/Mar/2019:04:13:09 +0000] "GET / HTTP/1.1" 403 23 "-" "ELB-HealthChecker/2.0" "-"
10.168.168.78 - - [15/Mar/2019:04:13:16 +0000] "GET / HTTP/1.1" 403 23 "-" "ELB-HealthChecker/2.0" "-"
10.168.166.132 - - [15/Mar/2019:04:13:24 +0000] "GET / HTTP/1.1" 403 23 "-" "ELB-HealthChecker/2.0" "-"
10.168.168.78 - - [15/Mar/2019:04:13:31 +0000] "GET / HTTP/1.1" 403 23 "-" "ELB-HealthChecker/2.0" "-"
10.168.166.132 - - [15/Mar/2019:04:13:39 +0000] "GET / HTTP/1.1" 403 23 "-" "ELB-HealthChecker/2.0" "-"
10.168.168.78 - - [15/Mar/2019:04:13:46 +0000] "GET / HTTP/1.1" 403 23 "-" "ELB-HealthChecker/2.0" "-"
10.168.166.132 - - [15/Mar/2019:04:13:54 +0000] "GET / HTTP/1.1" 403 23 "-" "ELB-HealthChecker/2.0" "-"
10.168.168.78 - - [15/Mar/2019:04:14:01 +0000] "GET / HTTP/1.1" 403 23 "-" "ELB-HealthChecker/2.0" "-"
10.168.166.132 - - [15/Mar/2019:04:14:09 +0000] "GET / HTTP/1.1" 403 23 "-" "ELB-HealthChecker/2.0" "-"
10.168.168.78 - - [15/Mar/2019:04:14:16 +0000] "GET / HTTP/1.1" 403 23 "-" "ELB-HealthChecker/2.0" "-"
10.168.166.132 - - [15/Mar/2019:04:14:24 +0000] "GET / HTTP/1.1" 403 23 "-" "ELB-HealthChecker/2.0" "-"
10.168.168.78 - - [15/Mar/2019:04:14:31 +0000] "GET / HTTP/1.1" 403 23 "-" "ELB-HealthChecker/2.0" "-"
10.168.166.132 - - [15/Mar/2019:04:14:39 +0000] "GET / HTTP/1.1" 403 23 "-" "ELB-HealthChecker/2.0" "-"
10.168.168.78 - - [15/Mar/2019:04:14:46 +0000] "GET / HTTP/1.1" 403 23 "-" "ELB-HealthChecker/2.0" "-"
10.168.166.132 - - [15/Mar/2019:04:14:54 +0000] "GET / HTTP/1.1" 403 23 "-" "ELB-HealthChecker/2.0" "-"
10.168.168.78 - - [15/Mar/2019:04:15:01 +0000] "GET / HTTP/1.1" 403 23 "-" "ELB-HealthChecker/2.0" "-"
10.168.166.132 - - [15/Mar/2019:04:15:09 +0000] "GET / HTTP/1.1" 403 23 "-" "ELB-HealthChecker/2.0" "-"
10.168.168.78 - - [15/Mar/2019:04:15:16 +0000] "GET / HTTP/1.1" 403 23 "-" "ELB-HealthChecker/2.0" "-"
10.168.166.132 - - [15/Mar/2019:04:15:24 +0000] "GET / HTTP/1.1" 403 23 "-" "ELB-HealthChecker/2.0" "-"
10.168.168.78 - - [15/Mar/2019:04:15:31 +0000] "GET / HTTP/1.1" 403 23 "-" "ELB-HealthChecker/2.0" "-"
10.168.166.132 - - [15/Mar/2019:04:15:39 +0000] "GET / HTTP/1.1" 403 23 "-" "ELB-HealthChecker/2.0" "-"
10.168.168.78 - - [15/Mar/2019:04:15:46 +0000] "GET / HTTP/1.1" 403 23 "-" "ELB-HealthChecker/2.0" "-"
10.168.166.132 - - [15/Mar/2019:04:15:54 +0000] "GET / HTTP/1.1" 403 23 "-" "ELB-HealthChecker/2.0" "-"
10.168.168.78 - - [15/Mar/2019:04:16:01 +0000] "GET / HTTP/1.1" 403 23 "-" "ELB-HealthChecker/2.0" "-"
10.168.166.132 - - [15/Mar/2019:04:16:09 +0000] "GET / HTTP/1.1" 403 23 "-" "ELB-HealthChecker/2.0" "-"
```

Now run the local parser, `parser.py` via the terminal.
The RegEx capturing group for the timestamp field *must* be named `timestamp` in the RegEx provided.
There must be a RegEx capturing group named `uri` which captures the uri of the logged event.
The RegEx must be in the [Python format](https://docs.python.org/3/howto/regex.html).
```
:param file: Name of log file to parse.
:param app: Name of the application for the logs.
:param bucket: S3 bucket to store the parsed logs to, Ex: "my-bucket123"
:param timeformat: The format of the timestamp in the logs. Ex: 'DD/MMM/YYYY:HH:mm:ss ZZ'
                   Accepts the following tokens: https://pendulum.eustace.io/docs/#tokens
:param regex: Regex to use to parse the logs.
              Ex: '(?P<remote_addr>[\S]+) - (?P<remote_user>[\S]+) \[(?P<timestamp>.+)\] "(?P<req_method>.+) (?P<uri>.+) (?P<httpver>.+)" (?P<status>[\S]+) (?P<body_bytes_sent>[\S]+) "(?P<referer>[\S]+)" "(?P<user_agent>[\S]+)" "(?P<x_forwarded_for>[\S]+)"'
```
## Run the local parser
```
# inside the shadowreader directory
pip install -r requirements-local-parser.txt
```
```
python3 parser.py --file logs.txt --app app1 --bucket my-bucket \
--timeformat 'DD/MMM/YYYY:HH:mm:ss ZZ' \
--regex '(?P<remote_addr>[\S]+) - (?P<remote_user>[\S]+) \[(?P<timestamp>.+)\] "(?P<req_method>.+) (?P<uri>.+) (?P<httpver>.+)" (?P<status>[\S]+) (?P<body_bytes_sent>[\S]+) "(?P<referer>[\S]+)" "(?P<user_agent>[\S]+)" "(?P<x_forwarded_for>[\S]+)"'
```
**NOTE:** The S3 bucket set in `--bucket` must be the same as the name of the deployed `parsed_data_bucket` in `serverless.yml`

You should see an output like below.
```
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
```

Paste the test_params and apps_to_test into serverless.yml and follow the other guides to start the load test.
