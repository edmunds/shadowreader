# Filters

ShadowReader can filter out certain requests from the replay.

An example filter:
```
filters: '{
                    "app": "",
                    "uri": "",
                    "status": [300, 400, 500],
                    "user_agent": ["Googlebot"],
                    "type": "exclude",
                    "apply_filter": true
          }'
```
This will exclude any requests that returned a 3XX, 4XX, or 5XX status code and any requests that contain "Googlebot" in the User-Agent.

To enable filtering, open `serverless.yml` and scroll to the section with the `orchestrator` settings and add a `filter` block.
```
functions:
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
      filters: '{
                          "app": "",
                          "uri": "",
                          "status": [300, 400, 500],
                          "user_agent": ["Googlebot"],
                          "type": "exclude",
                          "apply_filter": true
                }'
```

# Overview of filters
### **type**
Accepts either `"exclude"` or `"only"`.

If set to `exclude` then any requests that match any of the filters will be excluded.

If set to `only` then only requests that match the filters will be replayed.

### **apply_filter**
Accepts either `true` or `false`.

If `true` the filter will be applied. If `false` the filter will be not applied.

### **uri**
Filter URIs that match a provided Regex. Accepts Regex in Python format.

Ex:

`"uri": "^\/dont-replay-me.*"`

`"uri": "^(\/api\/v5\/wizard.*)|(\/dont-replay-me.*)"`


### **status**
Filter requests based on status code. Accepts a list of status codes. Accepted status codes are `200` `300` `400` and `500`. 

Ex:

`"status": [400]`  ==> Will filter all 4XX status code requests.

`"status": [400, 500]` ==> Will filter all 4XX and 5XX status code requests.

### **user_agent**
Filter basd on User-Agent header. Accepts list of strings.

Ex:

`"user_agent": ["Googlebot"]` ==> Filter requests with User-Agent that contain the string "Googlebot"

`"user_agent": ["Googlebot", "BotXYZ"]` ==> Filter request with User-Agent contain the string "Googlebot" or "BotXYZ"

The strings do not match exactly. ie: A request with User-Agent `BotXYZ 1.5` will be filtered by the above example.
