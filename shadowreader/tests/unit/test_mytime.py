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

from datetime import datetime

import pytest
from pytz import timezone

from classes.mytime import MyTime


def test_mytime_init():
    t = MyTime(year=2018, month=4, day=5, hour=8, minute=10, second=1, microsecond=1)
    assert t.year == 2018 and t.month == 4 and t.day == 5
    assert t.hour == 8 and t.minute == 10
    assert t.second == 1 and t.microsecond == 1


def test_mytime_comparison_equals():
    a = MyTime(dt=datetime(2018, 1, 29, 17, 9, 0))
    b = MyTime(dt=datetime(2018, 1, 29, 17, 9, 0))
    assert a == b


def test_mytime_comparison_greater_than():
    a = MyTime(dt=datetime(2018, 1, 29, 17, 9, 10))
    b = MyTime(dt=datetime(2018, 1, 29, 17, 9, 0))
    assert a > b


def test_mytime_comparison_greater_than_or_equals():
    a = MyTime(dt=datetime(2018, 1, 29, 17, 9, 10))
    b = MyTime(dt=datetime(2018, 1, 29, 17, 9, 10))
    assert a >= b


def test_mytime_comparison_less_than():
    a = MyTime(dt=datetime(2018, 1, 29, 17, 9, 1))
    b = MyTime(dt=datetime(2018, 1, 29, 17, 9, 10))
    assert a < b


def test_mytime_comparison_less_than_or_equals():
    a = MyTime(dt=datetime(2018, 1, 29, 17, 9, 10))
    b = MyTime(dt=datetime(2018, 1, 29, 17, 9, 10))
    assert a <= b


def test_set_seconds_to_zero():
    x = MyTime(year=2018, month=1, day=2, hour=0, tzinfo=timezone("US/Pacific"))
    x_new = x.set_seconds_to_zero()
    assert x_new.second == 0
    assert str(x_new.tzinfo) == "US/Pacific"
    assert x.epoch == x_new.epoch


def test_obj_creation_and_comparison_from_epoch():
    time_before = 1517314953
    time_after = 1517320293
    before = MyTime(epoch=time_before)
    after = MyTime(epoch=time_after)
    print(before, after)
    assert before < after


def test_epoch_variable_exists():
    mytime = MyTime(epoch=1514851200)
    print("mytime", mytime)
    assert mytime.epoch == 1514851200


def test_pst_to_utc_conversion():
    m = MyTime(year=2018, month=1, day=1, hour=8)
    m = m.to_pst()
    m_in_pst = MyTime(year=2018, month=1, day=1, hour=0, tzinfo=timezone("US/Pacific"))
    print(f"m: {m}, pst: {m_in_pst}")
    assert m.epoch == m_in_pst.epoch


def test_creation_of_pst_mytime():
    m1 = MyTime(year=2018, month=1, day=2, hour=0, tzinfo=timezone("US/Pacific"))
    m2 = MyTime(year=2018, month=1, day=2, hour=8)  # same time in UTC
    assert m1.epoch == m2.epoch


def test_init_from_replay_start_time():
    replay_start_time = (
        "2018-2-5-18-15"
    )  # epoch time for 2018-2-5, 6:15PM PST is 1517883300
    mytime = MyTime.set_to_replay_start_time_env_var(
        replay_start_time, timezone("US/Pacific")
    )
    assert mytime.epoch == 1517883300


def test_init_from_replay_start_time_w_isoformat():
    # Test that ISO 8601 formatted times are parsed correctly
    # Test for Thursday, August 2, 2018 12:30:00 AM GMT-07:00 DST
    replay_start_times = [
        "2018-08-02T00:30",
        "2018-08-02T00:30:40",
        "2018-08-02T00:30:40.873460",
        "2018-08-02T00:30:40.873460-07:00",
        "2018-08-02T00:30:40.873Z",
        "2018-08-02T00:30:40.873+10:00",
    ]
    for t in replay_start_times:
        mytime = MyTime.set_to_replay_start_time_env_var(t, timezone("US/Pacific"))
        assert mytime.epoch == 1533195000


def test_strip_timezone_from_isoformat():
    # Test that ISO 8601 formatted times with timezone
    # have the timezone part removed
    times = ["2018-08-03T08:30:00.00011+10:00" "2018-08-03T13:52:19.235608-07:00"]
    for time in times:
        time_stripped = MyTime._strip_timezone_from_isoformat(time)
        assert time[:-6] == time_stripped


def test_add_timedelta():
    mytime = MyTime(
        year=2018, month=4, day=5, hour=8, minute=0, tzinfo=timezone("US/Pacific")
    )
    mytime_plus_65_mins = mytime.add_timedelta(minutes=65)
    assert (mytime.epoch + 60 * 65) == mytime_plus_65_mins.epoch
    assert str(mytime_plus_65_mins.tzinfo) == "US/Pacific"


def test_invalid_initializtion():
    with pytest.raises(ValueError):
        MyTime(
            year=2018,
            month=4,
            day=5,
            hour=8,
            minute=0,
            tzinfo=timezone("US/Pacific"),
            epoch=12345,
        )
    with pytest.raises(ValueError):
        MyTime(
            year=2018,
            month=4,
            day=5,
            hour=8,
            minute=0,
            tzinfo=timezone("US/Pacific"),
            dt=datetime.now(),
        )
    with pytest.raises(ValueError):
        MyTime(
            year=2018,
            month=4,
            day=5,
            hour=8,
            minute=0,
            tzinfo=timezone("US/Pacific"),
            dt=datetime.now(),
            epoch=1234,
        )
    with pytest.raises(ValueError):
        MyTime(dt=datetime.now(), epoch=1234)


def test_from_epoch():
    t = MyTime.from_epoch(epoch=1523321265, tzinfo="US/Pacific")
    assert t.hour == 17 and t.minute == 47 and t.second == 45
    assert t.year == 2018 and t.month == 4 and t.day == 9
    assert str(t.tzinfo) == "US/Pacific"
