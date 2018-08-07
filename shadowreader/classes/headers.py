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

from classes.app import App


class Headers:
    def __init__(self, *, shadowreader_type: str, stage: str, app: App, step: int):
        """
        Class for generating Headers such as the user-agent for load test requests
        :param shadowreader_type: Type of Shadowreader testing. Ex: "past", "synthetic", "capacity"
        :param stage: The stage that this SR run is deployed in. Ex: "dev", "prod"
        :param app: Name of app being tested
        :param step: The step in this loop iteration
        """
        self.sr_type = shadowreader_type
        self.stage = stage
        self.app = app
        self.step = step
        self.identifier = app.identifier

        self.headers = self.generate_headers(self._generate_base_user_agent())

    def generate_headers(self, base_user_agent: str) -> dict:
        """
        Generate a Dict with User-Agent for load tests
        """
        headers = {"x-request-id": self._generate_user_agent(base_user_agent)}

        return headers

    def _generate_user_agent(self, user_agent: str) -> str:
        if self.sr_type == "past":
            user_agent += self._generate_user_agent_for_past_sr_type()
        elif self.sr_type == "syn":
            user_agent += self._generate_user_agent_for_synthetic()
        elif self.sr_type == "capacity":
            pass  # TODO: Add more details to this type of user-agent
        else:
            raise NotImplementedError(
                f"Implement _generate_user_agent() for other SR types. sr_type: {self.sr_type}"
            )
        return user_agent

    def _generate_base_user_agent(self) -> str:
        """ Generate base_user_agent, an example is: 'sr_dev_past_qa' """
        base_user_agent = f"sr_{self.stage}_{self.sr_type}_{self.identifier}"
        return base_user_agent

    def _generate_user_agent_for_past_sr_type(self) -> str:
        """
        Append to the base user agent info about the currently running test.
        Ex user-agent: _myapp_
        """
        loop_iteration = self._calculate_loop_iteration()

        replay_start_time = self._format_app_time_to_str()

        user_agent_suffix = f"_{self.app.name}_{replay_start_time}_{self.app.loop_duration}m_{loop_iteration}"

        return user_agent_suffix

    def _generate_user_agent_for_synthetic(self) -> str:
        """
        Append to the base user agent info about the currently running test.
        Ex user-agent: _myapp_
        """
        user_agent_suffix = f"_{self.app.name}"

        return user_agent_suffix

    def _calculate_loop_iteration(self) -> int:
        """ Find out which loop iteration this replay run is"""
        loop_iteration = self.step // self.app.loop_duration
        return loop_iteration

    def _format_app_time_to_str(self) -> str:
        mytime = self.app.replay_start_time
        date_format = "%m-%d-%Y-%H-%M"
        return mytime.dt.strftime(date_format)
