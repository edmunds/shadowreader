# Configuring ShadowReader to send load test metrics to CloudWatch

Open `shadowreader.yml` and set `metrics` to `cloudwatch` under `plugins`

```
plugins:
  metrics: cloudwatch
```

Now push your changes

```
serverless deploy --stage $your_stage --region $your_region
```

After a couple of minutes open up CloudWatch. A `shadowreader` namespace should display under Custom Namespaces in the Metrics section.

<p align="center">
  <img src="https://github.com/edmunds/shadowreader/blob/master/docs/imgs/cw-example1.png?raw=true" alt="shadow-reader-cloudwatch-example1" width="45%" height="45%"/>
</p>

## Available metrics

<p align="center">
  <img src="https://github.com/edmunds/shadowreader/blob/master/docs/imgs/cw-example2.png?raw=true" alt="shadow-reader-cloudwatch-example2" width="70%" height="70%"/>
</p>

- `parsed_timestamp` timestamp of the traffic logs that are being parsed.
- `replayed_timestamp` timestamp of the traffic logs that are being replayed.
- `num_requests` total number of requests being sent by the load test.

Metrics are sent every minute.
