from datetime import date, timedelta, datetime
from typing import Type, TypeVar

import pytest

from tempo_worklog_cli.util.serialization import converter

T = TypeVar("T", date, datetime, timedelta)


@pytest.mark.parametrize(
    "string, cls, expected",
    [
        # date
        ("2000-01-01", date, date(year=2000, month=1, day=1)),
        ("2023-09-11", date, date(year=2023, month=9, day=11)),
        ("today", date, date.today()),
        ("today-3", date, date.today() + timedelta(days=-3)),
        ("today+7", date, date.today() + timedelta(weeks=1)),
        ("week-start", date, date.today() + timedelta(days=-date.today().weekday())),
        ("week-end", date, date.today() + timedelta(days=4 - date.today().weekday())),
        # same as week-end
        ("week-start+4", date, date.today() + timedelta(days=4 - date.today().weekday())),
        # same as week-start
        ("week-end-4", date, date.today() + timedelta(days=-date.today().weekday())),
        # datetime
        ("2000-01-01T13:45:00", datetime, datetime(year=2000, month=1, day=1, hour=13, minute=45)),
        ("2023-10-31T00:00:00", datetime, datetime(year=2023, month=10, day=31)),
        # pure isotime is converted to datetime on 0001-01-01
        ("18:00:00", datetime, datetime(year=1, month=1, day=1, hour=18)),
        ("15:32:18", datetime, datetime(year=1, month=1, day=1, hour=15, minute=32, second=18)),
        # timedelta
        ("0T00:00:01", timedelta, timedelta(seconds=1)),
        ("1T00:00:01", timedelta, timedelta(days=1, seconds=1)),
        ("0T12:34:56", timedelta, timedelta(hours=12, minutes=34, seconds=56)),
        ("7T12:30:00", timedelta, timedelta(weeks=1, hours=12, minutes=30)),
    ],
)
def test_structuring(string: str, cls: Type[T], expected: T):
    assert converter.structure(string, cls) == expected


@pytest.mark.parametrize(
    "obj, expected",
    [
        # date
        (date(year=2000, month=1, day=1), "2000-01-01"),
        (date(year=2023, month=9, day=11), "2023-09-11"),
        # datetime
        (
            datetime(year=1999, month=12, day=31, hour=23, minute=59, second=59),
            "1999-12-31T23:59:59",
        ),
        (datetime(year=1895, month=1, day=1), "1895-01-01T00:00:00"),
        (datetime(year=2000, month=1, day=1, hour=13, minute=45), "2000-01-01T13:45:00"),
        # timedelta
        (timedelta(seconds=1), "0T00:00:01"),
        (timedelta(days=1, seconds=1), "1T00:00:01"),
        (timedelta(hours=12, minutes=34, seconds=56), "0T12:34:56"),
        (timedelta(weeks=1, hours=12, minutes=30), "7T12:30:00"),
    ],
)
def test_unstructuring(obj: T, expected: str):
    assert converter.unstructure(obj) == expected


@pytest.mark.parametrize(
    "obj",
    [
        date(year=2000, month=1, day=1),
        datetime(year=2023, month=10, day=14, hour=12),
        datetime(year=2023, month=10, day=14, hour=12, minute=34, second=57),
        timedelta(days=1, hours=2, minutes=3),
        timedelta(seconds=3),
    ],
)
def test_round_trip_serialization(obj: T):
    assert converter.structure(converter.unstructure(obj), type(obj)) == obj
