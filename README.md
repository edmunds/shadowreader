# ShadowReader

<a href="https://travis-ci.com/edmunds/shadowreader"><img alt="Build Status" src="https://travis-ci.com/edmunds/shadowreader.svg?branch=master"></a>
<a href="http://www.serverless.com"><img alt="Serverless" src="http://public.serverless.com/badges/v3.svg"></a>
<a href="https://github.com/ambv/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>

<p align="center">
  <img src="https://raw.githubusercontent.com/edmunds/shadowreader/master/docs/imgs/logo.png" alt="ShadowReader Logo" width="50%" height="50%"/>
</p>

ShadowReader has the ability to replay production traffic to a destination of your choice by collecting traffic patterns from access logs. It is built on AWS Lambda, S3 and Elastic Load Balancers.

<!-- <p align="center">
  <img src="https://github.com/edmunds/shadowreader/blob/master/docs/imgs/example1.png?raw=true" alt="shadow-reader-example1" width="75%" height="75%"/>
</p> -->
<p align="center">
  <img src="https://github.com/edmunds/shadowreader/blob/master/docs/imgs/load-test-animation.gif?raw=true" alt="shadow-reader-animation" width="90%" height="90%"/>
</p>
In the chart above, the blue line is the request rate of ShadowReader while in orange is the load on the production website.

ShadowReader mimics real user traffic by replaying URLs from production at the same rate as the live website. Being serverless, it is more efficient cost and performance wise than traditional distributed load tests and in practice has scaled beyond 50,000 requests / minute.

Support for replaying logs from these load balancers:

- [Application Load Balancer](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/introduction.html)
- [Classic Load Balancer](https://docs.aws.amazon.com/elasticloadbalancing/latest/classic/introduction.html)
- [Any logs stored locally, just provide a RegEx for the log format](docs/local_parser.md)
- (Support for other types of load balancers planned)

### Read about it
### [How we fixed a Node.js memory leak by using ShadowReader to replay production traffic into QA](http://technology.edmunds.com/2018/08/25/Investigating-a-Memory-Leak-and-Introducing-ShadowReader/)


## Documentation

To get started, see:

- [Batteries included demo for trying out live replay](#live-replay)
- [More in-depth guide for setting up past replay](docs/setup.md)
- [How to send load test metrics to CloudWatch](docs/cloudwatch-guide.md)
- [Parse locally stored logs](docs/local_parser.md)
- [Filter requests from replay](docs/filters.md)

## Trying Live Replay <a name="live-replay"/>

<p align="center">
  <img src="https://github.com/edmunds/shadowreader/blob/master/docs/imgs/live-replay2.png?raw=true" alt="shadow-reader-live-demo-results" width="80%" height="80%"/>
</p>

This guide will deploy all the necessary AWS resources to try out ShadowReader's live replay feature (replay requests as they come in).

This demo uses `us-east-1` AWS region. Substitute all references to `us-east-1` with a region of your choice.

## Deploy AWS resources for demo

The provided CloudFormation stack will deploy these AWS resources for the demo: A VPC, subnets, 2 ALBs and a S3 bucket.

One ALB comes preconfigured to send logs to S3.
This demo will walk you through in setting up ShadowReader to parse those logs then replay it to the 2nd ALB.

```
Deploy the stack:
curl https://raw.githubusercontent.com/edmunds/shadowreader/master/docs/demo-cf.yml --output demo-cf.yml
aws cloudformation deploy --stack-name sr-demo-resources  --template-file demo-cf.yml --region us-east-1
```

If you'd rather not deploy a new VPC and subnets, this CF will allow you to choose already existing VPC/Subnets.
```
curl https://raw.githubusercontent.com/edmunds/shadowreader/master/docs/demo-cf-choose.yml --output demo-cf-choose.yml
aws cloudformation deploy --stack-name sr-demo-resources  --template-file demo-cf-choose.yml --region us-east-1 --parameter-overrides subnet1=$SUBNET_ID1 subnet2=$SUBNET_ID2 vpcid=$VPCID
```

## Set up shadowreader.yml

Copy `shadowreader.example.yml` to `shadowreader.yml`

```
cp shadowreader.example.yml shadowreader.yml
```

Set `access_logs_bucket` in `shadowreader.yml` like below.

Replace AWS_ACCOUNT_ID with your account id (should be an integer like `123450493079`).
Replace AWS_REGION with the region you deployed the CloudFormation to.

```
environment:
    access_logs_bucket: sr-access-logs-$AWS_REGION-$AWS_ACCOUNT_ID/AWSLogs/$AWS_ACCOUNT_ID/elasticloadbalancing/$AWS_REGION/
```

Set `replay_mode` to `replay_live`

```
plugins:
  loader_middleware: loader_middleware
  replay_mode: replay_live
```

## Set up serverless.yml

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

Find out the DNS name for the ALB we will be load testing.

```
$ aws elbv2 describe-load-balancers --names SR-Demo-ALB-receiving --region us-east-1 | grep DNSName
>> "DNSName": "SR-Demo-ALB-receiving-123459376.us-east-1.elb.amazonaws.com",
```

Find `orchestrator-past` in `serverless.yml` and edit `base_url` to be `http://{DNSName}`.

```
orchestrator-past:
  handler: functions/orchestrator_past.lambda_handler
  events:
    - schedule: rate(1 minute)
  environment:
    test_params: '{
                    "base_url": "http://SR-Demo-ALB-receiving-123459376.us-east-1.elb.amazonaws.com",
                    "rate": 100,
                    "replay_start_time": "2018-08-06T01:00",
                    "replay_end_time": "2018-08-06T02:00",
                    "identifier": "oss"
                }'
    timezone: US/Pacific
```

## 3. Install the Serverless framework

```sh
npm install -g serverless
serverless plugin install -n serverless-python-requirements
```

A more detailed guide here:
https://serverless.com/framework/docs/getting-started/

## 3.5 Set up virtual env (optional)

```sh
python3 -m venv ~/.virtualenvs/sr-env
source ~/.virtualenvs/sr-env/bin/activate
```

## 4. Deploy to AWS

```
# Deploy ShadowReader to your AWS account
serverless deploy --stage dev --region us-east-1
```

If you installed Python using Brew, you may run into this error:

```
File "/usr/local/Cellar/python/3.6.4_4/Frameworks/Python.framework/Versions/3.6/lib/python3.6/distutils/command/install.py", line 248, in finalize_options
  "must supply either home or prefix/exec-prefix -- not both")
distutils.errors.DistutilsOptionError: must supply either home or prefix/exec-prefix -- not both
```

Run this to fix it.
[More details at StackOverflow](https://stackoverflow.com/questions/24257803/distutilsoptionerror-must-supply-either-home-or-prefix-exec-prefix-not-both)

```
(while in same directory as serverless.yml)
echo '[install]\nprefix=' > setup.cfg
```

## Start replaying traffic

Now we will start querying one ALB, which will generate access logs for ShadowReader to replay in real-time.

Find the DNSName for the ALB we will hit.

```
$ aws elbv2 describe-load-balancers --names SR-Demo-ALB-log-generator --region us-east-1 | grep DNSName
>> "DNSName": "SR-Demo-ALB-log-generator-1234567.us-east-1.elb.amazonaws.com"
```

Use [watch](https://linux.die.net/man/1/watch) to start sending requests to our ALB, this will generate access logs for ShadowReader to replay.

(`brew install watch` on mac)

```
watch -n 1 curl http://SR-Demo-ALB-log-generator-1234567.us-east-1.elb.amazonaws.com
```

You should now start seeing ALB logs being deposited to the `sr-access-logs` S3 bucket.

In about 8 minutes, requests sent to SR-Demo-ALB-log-generator will be replayed to SR-Demo-ALB-receiving

## See the results

Check the CloudWatch ` HTTP fixed response count` metrics for SR-Demo-ALB-receiving. It should be similar to the one for SR-Demo-ALB-log-generator.

<p align="center">
  <img src="https://github.com/edmunds/shadowreader/blob/master/docs/imgs/live-replay1.png?raw=true" alt="shadow-reader-live-demo-results" width="80%" height="80%"/>
</p>

## Next steps

To start replaying actual application traffic, try attaching an ECS service or EC2 server to log-generator ALB.


## Design

This diagram details the AWS components Shadow Reader uses and how they interact. More details in the above case study.

<p align="center">
  <img src="https://github.com/edmunds/shadowreader/blob/master/docs/imgs/shadow-reader-architecture.png?raw=true" alt="shadow-reader-design" width="90%" height="90%"/>
</p>

## Contributing and Deveploment

Please see the [contributing guide](CONTRIBUTING.md) for more specifics.

## Contact/Support

While ShadowReader has been productionalized at Edmunds, the open source version is still under active development and we greatly appreciate any feedback, suggestions, or comments!

Email me: ysawa@edmunds.com or contact me on Twitter: [@yukisww](https://twitter.com/yukisww)

or use the [Issues](https://github.com/edmunds/shadowreader/issues) page


## License

Distributed under the Apache License 2.0. See [`LICENSE`](LICENSE) for more information.
