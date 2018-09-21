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

from plugins import alb


def test_alb_log_parsing():
    logs = [
        'http 2018-09-17T23:55:00.505420Z app/test123/31b04dcf954789b6 123.123.123.123:34868 123.123.133.226:17073 0.000 0.392 0.000 200 200 1315 43765 "GET http://www.testsite.com:80/asda/asd12/12345/?zxcv=1&vsda=true HTTP/1.0" "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)" - - arn:aws:elasticloadbalancing:us-east-1:1234:targetgroup/sr-demo/0bc8356a792940a6 "Root=1-1123-asd1asd" "-" "-" 0 2018-09-17T23:55:00.109000Z "forward" "-"',
        'http 2018-09-17T23:55:00.439945Z app/test123/31b04dcf954789b6 123.123.123.123:34936 123.123.132.81:17073 0.000 0.117 0.000 200 200 1590 39859 "GET http://www.testsite.com:80/zxcv/asda/24567/testme/test2 HTTP/1.0" "Mozilla/5.0 (Linux; Android 6.0.1; SM-T800 Build/MMB29K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.91 Safari/537.36" - - arn:aws:elasticloadbalancing:us-east-1:12345:targetgroup/sr-demo/0bc8356a792940a6 "Root=1-5ba03e123124" "-" "-" 0 2018-09-17T23:55:00.319000Z "forward" "-"',
        'http 2018-09-18T00:15:00.391912Z app/SR-Demo-ALB/010d1e7cd31d5139 18.123.123.123:60138 - -1 -1 -1 200 - 245 192 "GET http://sr-demo-alb.elb.amazonaws.com:80/ HTTP/1.1" "python-requests/2.19.1" - - - "Root=1-5ba04384-d6fd7b802a5ec138a8cd9620" "-" "-" 0 2018-09-18T00:15:00.391000Z "fixed-response" "-"',
        'http 2018-09-20T03:44:57.659531Z app/SR-Demo-ALB/010d1e7cd31d5139 123.123.248.213:42460 - -1 -1 -1 503 - 245 353 "GET http://sr-demo-alb-123.us-test-2.elb.amazonaws.com:80/test1234/abcd HTTP/1.1" "python-requests/2.19.1" - - arn:aws:elasticloadbalancing:us-east-2:1234:targetgroup/SrDemoTargetGroup/1234 "Root=1-124-124" "-" "-" 0 2018-09-20T03:44:57.659000Z "forward" "-"',
    ]
    logs = alb._regex_match_and_parse_logs(logs)

    assert logs[0]["uri"] == "/zxcv/asda/24567/testme/test2"
    assert logs[1]["uri"] == "/asda/asd12/12345/?zxcv=1&vsda=true"
    assert logs[2]["uri"] == "/"
    assert logs[3]["uri"] == "/test1234/abcd"

    assert logs[0]["req_method"] == "GET"
    assert logs[0]["timestamp"].timestamp() == 1537228500.0
    assert logs[0]["timestamp"] < logs[3]["timestamp"]
    assert (
        logs[0]["user_agent"]
        == "Mozilla/5.0 (Linux; Android 6.0.1; SM-T800 Build/MMB29K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.91 Safari/537.36"
    )


if __name__ == "__main__":
    test_alb_log_parsing()
