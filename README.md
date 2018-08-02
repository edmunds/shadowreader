# ShadowReader

<a href="https://travis-ci.com/edmunds/shadowreader"><img alt="Build Status" src="https://travis-ci.com/edmunds/shadowreader.svg?branch=master"></a>
<a href="http://www.serverless.com"><img alt="Serverless" src="http://public.serverless.com/badges/v3.svg"></a>

<p align="center">
  <img src="https://ysawa0.github.io/sr-assets/logo.png" alt="ShadowReader Logo" width="50%" height="50%"/>
</p>

ShadowReader has the ability to replay production traffic to a destination of your choice by collecting traffic patterns from access logs. It is built on AWS Lambda, S3 and Elastic Load Balancers.

<p align="center">
  <img src="https://ysawa0.github.io/sr-assets/example1.png" alt="Example1" width="75%" height="75%"/>
</p>

In the chart above, the blue line is the request rate of ShadowReader while in orange is the load on the production website.

ShadowReader mimics real user traffic by replaying URLs from production at the same rate as the live website. Being serverless, it is more efficient cost and performance wise than traditional distributed load tests and in practice has scaled beyond 50,000 requests / minute.

Support for replaying logs from two types of load balancers:

- Application Load Balancer
- Classic Load Balancer
- (Support for other types of load balancers planned)

# Quick start

## 1. serverless.yml set up

Copy the contents of `shadowreader/serverless.example.yml` and use it to create new file `shadowreader/serverless.yml`. Then update the variables listed below.

Both `serverless.yml` and `shadowreader.yml` must be configured before deployment via the [Serverless framework](https://serverless.com/).

```
# Required. This is your project name. It is to ensure that the S3 bucket used by ShadowReader has unique naming.
custom:
  my_project_name: my-unique-project-name
```

```
# Required.
# "test_params" variable is a JSON that specifies the parameters for the load test.
# All values except "identifier" must be properly configured.
# Values below are examples

orchestrator-past:
  handler: functions/orchestrator_past.lambda_handler
  events:
    - schedule: rate(1 minute)
  environment:
    test_params: '{
                    "base_url": "http://www.mywebsite.com",
                    "rate": 100,
                    "replay_start_time": "2018-4-2-15-40",
                    "loop_duration": 60,
                    "identifier": "oss"
                }'
    timezone: US/Pacific

  # "base_url" - Here, you can specify the base URL which will prefix the URIs collected from ELB logs.
  #              It should not end with a "/"
  # "rate" - A percentage value at which ShadowReader will perform the load test.
  #          It accepts a float value larger than 0
  # "replay_start_time" - ShadowReader replays traffic from certain time periods for its load tests.
  #                       This is the starting time for the replay period.
  #                       If ShadowReader has not collected data for this time period,
  #                       no requests will be sent in the load test.
  # "loop_duration" - This is an integer value, denominated in minutes.
  #                   It is how long the replay period will be, starting from the time specified in "replay_start_time"
  #                   For example, if "replay_start_time" = "2018-1-1-10-0" and "loop_duration" = 60,
  #                   then it will replay traffic from 2018-1-1-10-0 to 2018-1-1-11-0
  # "identifier" - This is an identifier that is used when tagging CloudWatch metrics. Editing it is optional.
  # "timezone" - Timezone the replay_start_time is in. Accepts pytz timezone names like "US/Pacific" or "UTC"
```

```
# Optional. If you are testing inside a VPC, these must be set to give ShadowReader VPC access.
vpc:
  securityGroupIds:
    - sg-your-security-group-id
  subnetIds:
    - subnet-your-subnet-1
    - subnet-your-subnet-2
```

## 2. shadowreader.yml set up

Copy the contents of `shadowreader/shadowreader.example.yml` and use it to create file `shadowreader/shadowreader.yml`

```
# Required. This variable must be set according to where your ELB logs are being written to.
# See screenshots below for help in finding this.
environment:
    access_logs_bucket: AWSLogs/123456789/elasticloadbalancing
```

### Enabling ELB logs

Click on your ELB in the AWS console then scroll to the `attributes` section

<p align="center">
  <img src="https://ysawa0.github.io/sr-assets/elb-how-1.png" alt="elb-how-to-1" width="75%" height="75%"/>
</p>

<p align="center">
  <img src="https://ysawa0.github.io/sr-assets/elb-how-2.png" alt="elb-how-to-2" width="75%" height="75%"/>
</p>

### Finding your access_logs_bucket and path

<p align="center">
  <img src="https://ysawa0.github.io/sr-assets/elb-how-3.png" alt="elb-how-to-3" width="75%" height="75%"/>
</p>

## 3. Install the Serverless framework

```sh
# Install the serverless cli
npm install -g serverless

# In-depth guide for installing Serverless framework:
# https://serverless.com/framework/docs/getting-started/

# Install the Serverless plugin which will pack necessary Python libraries
serverless plugin install -n serverless-python-requirements
```

## 4. Deploy to AWS

```
# Deploy ShadowReader to your AWS account
serverless deploy --stage dev --region region_of_your_choice
```

```
You may run into this error while deploying:

  File "/usr/local/Cellar/python/3.6.4_4/Frameworks/Python.framework/Versions/3.6/lib/python3.6/distutils/command/install.py", line 248, in finalize_options
    "must supply either home or prefix/exec-prefix -- not both")
  distutils.errors.DistutilsOptionError: must supply either home or prefix/exec-prefix -- not both

This is due to the way Homebrew installs Python. Run this command from the base project directory to fix it.

echo '[install]\nprefix=' > shadowreader/setup.cfg

See here for more details: https://stackoverflow.com/questions/24257803/distutilsoptionerror-must-supply-either-home-or-prefix-exec-prefix-not-both
```

## How it works

<p align="center">
  <img src="https://ysawa0.github.io/sr-assets/how-it-works.png" alt="how-it-works" width="90%" height="90%"/>
</p>

## Usage example

ShadowReader can be used for performance testing applications.

For monitoring results, the recommended way is to create CloudWatch dashboards that display metrics such as RequestCount, TargetResponseTime and CPU/MEM Utilization

By comparing status codes and latency between the original request and replayed request, its possible to detect defects before they are shipped to production.

## Contributing

Please see the [contributing guide](CONTRIBUTING.md) for more specifics.

## Contact

Please use the [Issues](https://github.com/edmunds/shadowreader/issues) page or contact
[Yuki Sawa](https://github.com/ysawa0) – ysawa@edmunds.com

## License

Distributed under the Apache License 2.0. See [`LICENSE`](LICENSE) for more information.
