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

from classes.mytime import MyTime


class App:
    """ Data structure which holds info about the load test currently being run for a certain app """

    def __init__(
        self,
        *,
        name: str,
        replay_start_time: MyTime,
        loop_duration: int,
        rate: int,
        baseline: int,
        base_url: str,
        identifier: str = "",
    ):
        """
        :param name: name of application being tested
        :param replay_start_time: The time the replay should start at
        :param loop_duration: duration of each replay. denominated in minutes.
                    ex: 60 (this would loop 60 mins of traffic)
        :param cur_timestamp: The time slice currently being replayed
        """
        self.name = name
        self.replay_start_time = replay_start_time
        self.loop_duration = int(loop_duration)

        if self.loop_duration == 0:
            self.loop_duration = 1

        self.base_url = self._validate_base_url(base_url)
        if identifier:
            self.identifier = identifier
        else:
            self.identifier = base_url

        self.rate = rate
        self.baseline = baseline

        self.cur_timestamp = replay_start_time.epoch
        self.cur_timestamp_pst = str(
            replay_start_time.to_pst()
        )  # Formatted time slice in PST

    def __repr__(self):
        L = [
            f'name="{self.name}"',
            f"replay_start_time={self.replay_start_time}",
            f"loop_duration={self.loop_duration}",
            f'base_url="{self.base_url}"',
            f'identifier="{self.identifier}"',
            f"rate={self.rate}",
            f"cur_timestamp={self.cur_timestamp}",
            f"baseline={self.baseline}",
        ]
        s = f'{self.__class__.__qualname__}({", ".join(map(str, L))})'
        return s

    def __str__(self):
        return self.__repr__()

    def __eq__(self, other):
        if not self._is_valid_operand(other):
            return NotImplemented

        res = (
            self.name == other.name
            and self.replay_start_time == other.replay_start_time
            and self.loop_duration == other.loop_duration
            and self.rate == other.rate
            and self.base_url == other.base_url
            and self.identifier == other.identifier
            and self.cur_timestamp == other.cur_timestamp
        )

        return res

    def _is_valid_operand(self, other):
        return (
            hasattr(other, "name")
            and hasattr(other, "replay_start_time")
            and hasattr(other, "loop_duration")
            and hasattr(other, "rate")
            and hasattr(other, "base_url")
            and hasattr(other, "identifier")
            and hasattr(other, "cur_timestamp")
        )

    def _validate_base_url(self, base_url):
        # If base_url ends with a "/", remove it
        if base_url.endswith("/"):
            base_url = base_url[:-1]

        # If base_url does not specify http or https, prefix it with https://
        if not (base_url.startswith("http://") or base_url.startswith("https://")):
            base_url = f"http://{base_url}"
        return base_url
