# Set up

This document describes how to set up Shadow Reader for replaying past access logs.

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
cp shadowreader.example.yml shadowreader.yml
```

ShadowReader must read/parse your access logs stored on S3 before it can replay it for a load test.

`access_logs_bucket` in `shadowreader.yml` must point to the S3 bucket and path with your ELB logs.

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
                    "replay_start_time": "2018-08-06T01:00",
                    "replay_end_time": "2018-08-06T02:00",
                    "identifier": "oss"
                }'
    timezone: US/Pacific

  # "base_url" - Here, you can specify the base URL which will prefix the URIs collected from ELB logs.
  #              It should not end with a "/"
  # "rate" - A percentage value at which ShadowReader will perform the load test.
  #          It accepts a float value larger than 0
  # "replay_start_time" - ShadowReader replays traffic from a certain time window for its load tests.
  #                       This is the starting time for the replay period.
  #                       If ShadowReader has not collected data for this time period,
  #                       no requests will be sent in the load test.
  # "replay_end_time" - This is the end time for the replay time window.
  #                     In the sample test_params above, the load test will replay traffic from
  #                     2018-08-06 1AM to 2018-08-06 2AM
  #                     The time windows are specified in ISO 8601 format.
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

## Usage example

ShadowReader can be used for performance testing applications.

For monitoring results, the recommended way is to create CloudWatch dashboards that display metrics such as RequestCount, TargetResponseTime and CPU/MEM Utilization

By comparing status codes and latency between the original request and replayed request, its possible to detect defects before they are shipped to production.
