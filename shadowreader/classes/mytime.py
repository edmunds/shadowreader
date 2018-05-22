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
"""

from datetime import datetime, timedelta
from functools import total_ordering
from typing import Union

from pytz import timezone, utc

from classes.exceptions import InvalidLambdaEnvVarError

pst = timezone('US/Pacific')


@total_ordering
class MyTime:
    """
    Wrapper around datetime to make passing around timestamps easier
    If tzinfo is not set, it defaults to UTC
    Example initializations:
    MyTime() => get the current time in UTC
    MyTime(epoch=1517366269) => tzinfo always set to UTC if using epoch arg
    MyTime(year=2018, month=1, day=1, hour=1, minute=1) => tzinfo set to UTC by default
    MyTime(year=2018, month=1, day=1, hour=1, minute=1, tzinfo=pytz.timezone('US/Pacific')) => tzinfo set to PST
    """

    # TODO: Raise errors when incompatible args set
    def __init__(self,
                 *,
                 dt: datetime = None,
                 year=0,
                 month=0,
                 day=0,
                 hour=0,
                 minute=0,
                 second=0,
                 microsecond=0,
                 epoch=0,
                 tzinfo: Union[timezone, str] = None):

        res = self._check_params_valid(dt, year, month, day, hour, minute,
                                       second, microsecond, epoch, tzinfo)
        if not res:
            raise ValueError(
                'Invalid combination of parameters passed to MyTime initialization'
            )

        tzinfo = self._convert_to_timezone_obj(tzinfo)

        # If tzinfo was not set, set it to either UTC or the tzinfo in dt
        if not tzinfo:
            # Check if dt passed in and get tzinfo from dt if it exists, else set to UTC
            if dt and dt.tzinfo:
                tzinfo = dt.tzinfo
            else:
                tzinfo = utc

        if not any([dt, year, month, day, hour, minute, second, epoch]):
            self.dt = datetime.now(utc)

        elif dt:
            if tzinfo == utc:
                self.dt = dt
            else:
                # Have to use localize() method to set tzinfo instead of passing it in datetime.__new__
                # Unfortunately using the tzinfo argument of the standard datetime constructors
                # does not work with pytz for many timezones
                self.dt = tzinfo.localize(
                    datetime(dt.year, dt.month, dt.day, dt.hour, dt.minute,
                             dt.second, dt.microsecond))

        elif epoch:
            self.dt = datetime.utcfromtimestamp(epoch)
            self.dt = self.dt.replace(tzinfo=utc)

        # If year, month, day, hour, minute, second, microsecond args were set
        else:
            if not all([year, month, day]):
                raise ValueError(
                    f'year, month, day must all be set: {year}, {month}, {day}'
                )
            if tzinfo == utc:
                self.dt = datetime(
                    year,
                    month,
                    day,
                    hour,
                    minute,
                    second,
                    microsecond,
                    tzinfo=tzinfo)
            else:
                dt = datetime(year, month, day, hour, minute, second,
                              microsecond)
                self.dt = tzinfo.localize(dt)

        self._set_variables()

    @classmethod
    def from_epoch(cls, *, epoch, tzinfo) -> 'MyTime':
        tzinfo = cls._convert_to_timezone_obj(tzinfo)

        dt = datetime.utcfromtimestamp(epoch)
        dt = dt.replace(tzinfo=utc)
        dt = dt.astimezone(tzinfo)

        return cls(
            year=dt.year,
            month=dt.month,
            day=dt.day,
            hour=dt.hour,
            minute=dt.minute,
            second=dt.second,
            microsecond=dt.microsecond,
            tzinfo=tzinfo)

    @staticmethod
    def _convert_to_timezone_obj(tzinfo):
        if isinstance(tzinfo, str):
            tzinfo = timezone(tzinfo)
        return tzinfo

    @staticmethod
    def _check_params_valid(dt, year, month, day, hour, minute, second,
                            microsecond, epoch, tzinfo) -> bool:
        # TODO: Implement fully
        if dt and any(
            [year, month, day, hour, minute, second, microsecond, epoch]):
            return False
        if epoch and any(
            [year, month, day, hour, minute, second, microsecond, dt, tzinfo]):
            return False
        return True

    def _set_variables(self):
        """ Update class vars based on internal datetime object """
        self.epoch = self.dt.timestamp()
        self.epoch = int(self.epoch)
        self.year = self.dt.year
        self.month = self.dt.month
        self.day = self.dt.day
        self.hour = self.dt.hour
        self.minute = self.dt.minute
        self.second = self.dt.second
        self.microsecond = self.dt.microsecond
        self.tzinfo = self.dt.tzinfo

    def set_seconds_to_zero(self):
        """ Return a new object where the second and microsecond vals are set to 0 """
        return MyTime(
            year=self.year,
            month=self.month,
            day=self.day,
            hour=self.hour,
            minute=self.minute,
            second=0,
            microsecond=0,
            tzinfo=self.tzinfo)

    def format_to_str_for_es_index(self) -> str:
        date_format = '%Y.%m.%d'
        return self.dt.strftime(date_format)

    def to_pst(self) -> 'MyTime':
        dt = self.dt.astimezone(timezone('US/Pacific'))
        return MyTime(dt=dt, tzinfo=timezone('US/Pacific'))

    def to_utc(self) -> 'MyTime':
        dt = self.dt.astimezone(utc)
        return MyTime(dt=dt)

    def add_timedelta(self, days=0, hours=0, minutes=0, seconds=0) -> 'MyTime':
        dt = self.dt + timedelta(
            days=days, hours=hours, minutes=minutes, seconds=seconds)
        return MyTime(dt=dt, tzinfo=self.tzinfo)

    def __repr__(self):
        tzinfo = f'timezone("{self.tzinfo}")'
        L = [
            f'year={self.year}', f'month={self.month}', f'day={self.day}',
            f'hour={self.hour}', f'minute={self.minute}',
            f'second={self.second}', f'tzinfo={tzinfo}', f'epoch={self.epoch}'
        ]

        s = f'{self.__class__.__qualname__}({", ".join(map(str, L))})'
        return s

    def __str__(self):
        s = self.dt.strftime('%Y-%m-%d %H:%M:%S')
        return f'{s} {self.tzinfo}'

    def __eq__(self, other):
        if not self._is_valid_operand(other):
            return NotImplemented
        return self.dt == other.dt

    def __lt__(self, other):
        if not self._is_valid_operand(other):
            return NotImplemented

        return self.dt < other.dt

    @staticmethod
    def _is_valid_operand(other):
        return hasattr(other, "dt") and hasattr(other, "epoch")

    @staticmethod
    def set_to_replay_start_time_env_var(lambda_env_var, tzinfo) -> 'MyTime':
        replay_start_time = list(map(int, lambda_env_var.split('-')))

        if len(replay_start_time) != 5:
            raise InvalidLambdaEnvVarError(
                f'replay_start_time value was not valid: {lambda_env_var}')

        kwargs = {
            'year': replay_start_time[0],
            'month': replay_start_time[1],
            'day': replay_start_time[2],
            'hour': replay_start_time[3],
            'minute': replay_start_time[4],
            'tzinfo': tzinfo
        }
        return MyTime(**kwargs)
