# ShadowReader

<a href="https://travis-ci.com/edmunds/shadowreader"><img alt="Build Status" src="https://travis-ci.com/edmunds/shadowreader.svg?branch=master"></a>
<a href="http://www.serverless.com"><img alt="Serverless" src="http://public.serverless.com/badges/v3.svg"></a>
<a href="https://github.com/ambv/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>

<p align="center">
  <img src="https://ysawa0.github.io/sr-assets/logo.png" alt="ShadowReader Logo" width="50%" height="50%"/>
</p>

ShadowReader has the ability to replay production traffic to a destination of your choice by collecting traffic patterns from access logs. It is built on AWS Lambda, S3 and Elastic Load Balancers.

<p align="center">
  <img src="https://ysawa0.github.io/sr-assets/example1.png" alt="Example1" width="75%" height="75%"/>
</p>

In the chart above, the blue line is the request rate of ShadowReader while in orange is the load on the production website.

ShadowReader mimics real user traffic by replaying URLs from production at the same rate as the live website. Being serverless, it is more efficient cost and performance wise than traditional distributed load tests and in practice has scaled beyond 50,000 requests / minute.

Support for replaying logs from these load balancers:

- [Application Load Balancer](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/introduction.html)
- [Classic Load Balancer](https://docs.aws.amazon.com/elasticloadbalancing/latest/classic/introduction.html)
- (Support for other types of load balancers planned)

# Quick start

```
git clone https://github.com/edmunds/shadowreader.git
cd shadowreader/shadowreader
```

## 1. Deploy ShadowReader and collect access logs

Copy `serverless.example.yml` to `serverless.yml`.

```
cp serverless.example.yml serverless.yml
```

(Both `serverless.yml` and `shadowreader.yml` must be configured before deployment via the [Serverless framework](https://serverless.com/).)

Update `my_project_name` in `serverless.yml`. This is your project name.
It is to ensure that the S3 bucket used by ShadowReader has unique naming (S3 bucket names must be globally unique).

```
custom:
  my_project_name: my-unique-project-name
```

Copy `shadowreader.example.yml` to `shadowreader.yml`

```
cp serverless.example.yml serverless.yml
```

ShadowReader must read/parse your access logs stored on S3 before it can replay it for a load test.

`access_logs_bucket` in `serverless.yml` must point to the S3 bucket and path with your ELB logs.

Once SR is deployed to your AWS account, it will start ingesting the logs in this bucket in real-time.

```
# See screenshots below for help in finding this.
environment:
    access_logs_bucket: AWSLogs/123456789/elasticloadbalancing
```

## Enabling ELB logs

By enabling ELB logs, AWS will start writing your access logs to a S3 bucket in real-time.

ShadowReader has the ability to read these logs and replay it once ingested.

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

### The `producer` section controls the type of load balancer logs to parse.

If you are parsing Application Load Balancer logs, enter "alb"

If you are parsing Classic Load Balancer logs, enter "elb"

```
# Required
# Default is alb
plugins:
  producer: alb
```

## 3. Install the Serverless framework

Guide for installing Serverless framework:
https://serverless.com/framework/docs/getting-started/

```sh
# Install the serverless cli
npm install -g serverless
# Install the Serverless plugin which will pack necessary Python libraries
serverless plugin install -n serverless-python-requirements
```

## 3.5 Set up virtual env

```sh
python3 -m venv ~/.virtualenvs/sr-env
source ~/.virtualenvs/sr-env/bin/activate
```

## 4. Deploy to AWS

```
# Deploy ShadowReader to your AWS account
serverless deploy --stage dev --region region_of_your_choice
```

You may run into this error:

```
File "/usr/local/Cellar/python/3.6.4_4/Frameworks/Python.framework/Versions/3.6/lib/python3.6/distutils/command/install.py", line 248, in finalize_options
  "must supply either home or prefix/exec-prefix -- not both")
distutils.errors.DistutilsOptionError: must supply either home or prefix/exec-prefix -- not both
```

This happens with Brew installed Python.
Run this to fix it.

```
(while inside the shadowreader folder)
echo '[install]\nprefix=' > setup.cfg
```

More details here:

https://stackoverflow.com/questions/24257803/distutilsoptionerror-must-supply-either-home-or-prefix-exec-prefix-not-both

https://github.com/UnitedIncome/serverless-python-requirements#applebeersnake-mac-brew-installed-python-notes

## 5. Start a load test

Once SR has parsed some incoming access logs, you can start a load test to replay the logs that were just collected.
Open `serverless.yml` and edit these values:

```
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
                    "replay_start_time": "2018-08-06T13:30",
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
  #                   For example, if "replay_start_time" = "2018-08-06T13:30" and "loop_duration" = 60,
  #                   then it will replay access logs from 2018-08-06T13:30 to 2018-08-06T14:30
  #                   (ie. replay traffic from 2018-08-06 1:30PM to 2:30PM)
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

Now redeploy ShadowReader with the new config to start the load test:

```
serverless deploy --stage dev --region region_of_your_choice
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

## Contact/Support

Please use the [Issues](https://github.com/edmunds/shadowreader/issues) page or contact/email
[Yuki Sawa](https://github.com/ysawa0) – ysawa@edmunds.com

## License

Distributed under the Apache License 2.0. See [`LICENSE`](LICENSE) for more information.
