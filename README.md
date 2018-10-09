# ShadowReader

<a href="https://travis-ci.com/edmunds/shadowreader"><img alt="Build Status" src="https://travis-ci.com/edmunds/shadowreader.svg?branch=master"></a>
<a href="http://www.serverless.com"><img alt="Serverless" src="http://public.serverless.com/badges/v3.svg"></a>
<a href="https://github.com/ambv/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>

<p align="center">
  <img src="https://ysawa0.github.io/sr-assets/logo.png" alt="ShadowReader Logo" width="50%" height="50%"/>
</p>

ShadowReader has the ability to replay production traffic to a destination of your choice by collecting traffic patterns from access logs. It is built on AWS Lambda, S3 and Elastic Load Balancers.

<p align="center">
  <img src="https://github.com/edmunds/shadowreader/blob/master/docs/imgs/example1.png?raw=true" alt="shadow-reader-example1" width="75%" height="75%"/>
</p>

In the chart above, the blue line is the request rate of ShadowReader while in orange is the load on the production website.

ShadowReader mimics real user traffic by replaying URLs from production at the same rate as the live website. Being serverless, it is more efficient cost and performance wise than traditional distributed load tests and in practice has scaled beyond 50,000 requests / minute.

Support for replaying logs from these load balancers:

- [Application Load Balancer](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/introduction.html)
- [Classic Load Balancer](https://docs.aws.amazon.com/elasticloadbalancing/latest/classic/introduction.html)
- (Support for other types of load balancers planned)

## Getting started

To get started, see:

1. [Batteries included demo for trying out live replay](docs/demo_live_replay.md)
2. [More in-depth guide for setting up past replay](docs/setup.md)

## Case study

[How we fixed a Node.js memory leak by using ShadowReader to replay production traffic into QA](http://technology.edmunds.com/2018/08/25/Investigating-a-Memory-Leak-and-Introducing-ShadowReader/)

## Design

This diagram details the AWS components Shadow Reader uses and how they interact. More details in the above case study.

<p align="center">
  <img src="https://github.com/edmunds/shadowreader/blob/master/docs/imgs/shadow-reader-architecture.png?raw=true" alt="shadow-reader-design" width="90%" height="90%"/>
</p>

## Contributing

Please see the [contributing guide](CONTRIBUTING.md) for more specifics.

## Contact/Support

Contact [Yuki Sawa](https://github.com/ysawa0) – ysawa@edmunds.com

or use the [Issues](https://github.com/edmunds/shadowreader/issues) page

## License

Distributed under the Apache License 2.0. See [`LICENSE`](LICENSE) for more information.
