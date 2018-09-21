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

from plugins import clb


def test_clb_log_parsing():
    logs = [
        '2018-09-20T04:16:05.071375Z test-ELB 123.25.61.210:63407 123.123.15.138:902 0.000051 0.01047 0.00003 200 200 0 788 "GET https://sr.example.com:443/api/v1/asdf/sets/590045a1e4b1234599/abcdef/test123=zxc&zxc=abc&year=2018&type= HTTP/1.1" "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/603.3.8 (KHTML, like Gecko) Version/10.1.2 Safari/603.3.8" XXX-RSA-ZZZ-XXX-SHA256 TLSv1.2',
        '2018-09-20T04:16:05.924891Z test-ELB 123.255.254.192:19012 123.123.15.107:9051 0.00004 0.010085 0.000021 200 200 0 101 "GET http://sr.example.com:80/api/health/check HTTP/1.1" "Amazon-Route53-Health-Check-Service (ref 124-124-124-123-8f0e211dca04; report http://amzn.to/1vsZADi)" - -',
        '2018-09-20T04:16:06.473998Z qa-test-ELB 123.17.138.195:49928 123.123.15.107:9991 0.000063 0.012962 0.000023 200 200 0 861 "GET https://sr.example.com:443/example/abc/123419845935e4dc/test/xxx-search?xxx=1234&xxx=123&xxx=&xxx=&zzz=&xxx= HTTP/1.1" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36" XXX-RSA-ZZZ-XXX-SHA256 TLSv1.2',
        '2018-09-21T04:16:06.473998Z qa-test-ELB 123.17.138.195:49928 123.123.15.107:9991 0.000063 0.012962 0.000023 200 200 0 861 "GET https://sr.example.com:443/ HTTP/1.1" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36" XXX-RSA-ZZZ-XXX-SHA256 TLSv1.2',
    ]
    logs = clb._regex_match_and_parse_logs(logs)

    assert (
        logs[0]["uri"]
        == "/api/v1/asdf/sets/590045a1e4b1234599/abcdef/test123=zxc&zxc=abc&year=2018&type="
    )
    assert logs[1]["uri"] == "/api/health/check"
    assert (
        logs[2]["uri"]
        == "/example/abc/123419845935e4dc/test/xxx-search?xxx=1234&xxx=123&xxx=&xxx=&zzz=&xxx="
    )
    assert logs[3]["uri"] == "/"

    assert logs[0]["req_method"] == "GET"
    assert logs[0]["timestamp"].timestamp() == 1537416960.0
    assert logs[0]["timestamp"] < logs[3]["timestamp"]
    assert (
        logs[0]["user_agent"]
        == "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/603.3.8 (KHTML, like Gecko) Version/10.1.2 Safari/603.3.8"
    )


if __name__ == "__main__":
    test_clb_log_parsing()
