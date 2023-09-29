from datetime import date
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from tempo_worklog_creator.time_span import TimeSpan


@pytest.mark.parametrize(
    "span1, span2",
    [
        (
            TimeSpan.from_start_and_end(
                start=datetime(2000, 1, 1, 10), end=datetime(2000, 1, 1, 11)
            ),
            TimeSpan.from_start_and_end(
                start=datetime(2000, 1, 1, 10), end=datetime(2000, 1, 1, 11)
            ),
        ),
        (
            TimeSpan(start=datetime(2000, 1, 1, 10), duration=timedelta(hours=1)),
            TimeSpan(start=datetime(2000, 1, 1, 10), duration=timedelta(hours=1)),
        ),
        (
            TimeSpan(start=datetime(2000, 1, 1, 10), duration=timedelta(hours=1)),
            TimeSpan.from_start_and_end(
                start=datetime(2000, 1, 1, 10), end=datetime(2000, 1, 1, 11)
            ),
        ),
        (
            TimeSpan(start=datetime(2000, 1, 1, 10), duration=timedelta(hours=1)),
            TimeSpan(start=datetime(2000, 1, 1, 10), duration=timedelta(minutes=60)),
        ),
    ],
)
def test_equality(span1, span2):
    assert span1 == span2


@pytest.mark.parametrize(
    "span1, span2, intersection",
    [
        (
            TimeSpan(start=datetime(1, 1, 1, 10), duration=timedelta(hours=1)),
            TimeSpan(start=datetime(1, 1, 1, 10), duration=timedelta(hours=1)),
            TimeSpan(start=datetime(1, 1, 1, 10), duration=timedelta(hours=1)),
        ),
        (
            TimeSpan(start=datetime(1, 1, 1, 10), duration=timedelta(hours=1)),
            TimeSpan(start=datetime(1, 1, 1, 11), duration=timedelta(hours=1)),
            None,
        ),
        (
            TimeSpan(start=datetime(1, 1, 1, 10), duration=timedelta(hours=2)),
            TimeSpan(start=datetime(1, 1, 1, 11), duration=timedelta(hours=2)),
            TimeSpan(start=datetime(1, 1, 1, 11), duration=timedelta(hours=1)),
        ),
        (
            TimeSpan(start=datetime(1, 1, 1, 10), duration=timedelta(hours=2)),
            TimeSpan(start=datetime(1, 1, 1, 11), duration=timedelta(hours=1)),
            TimeSpan(start=datetime(1, 1, 1, 11), duration=timedelta(hours=1)),
        ),
    ],
)
def test_intersection(span1: TimeSpan, span2: TimeSpan, intersection: TimeSpan):
    actual_intersection1 = span1 & span2
    actual_intersection2 = span2 & span1
    assert actual_intersection1 == actual_intersection2
    assert actual_intersection1 == intersection


@pytest.mark.parametrize(
    "span1, span2, difference",
    [
        (
            TimeSpan(start=datetime(1, 1, 1, 10), duration=timedelta(hours=1)),
            TimeSpan(start=datetime(1, 1, 1, 10), duration=timedelta(hours=1)),
            (),
        ),
        (
            TimeSpan(start=datetime(1, 1, 1, 10), duration=timedelta(hours=1)),
            TimeSpan(start=datetime(1, 1, 1, 9), duration=timedelta(hours=2)),
            (),
        ),
        (
            TimeSpan(start=datetime(1, 1, 1, 10), duration=timedelta(hours=1)),
            TimeSpan(start=datetime(1, 1, 1, 10), duration=timedelta(hours=2)),
            (),
        ),
        (
            TimeSpan(start=datetime(1, 1, 1, 10), duration=timedelta(hours=2)),
            TimeSpan(start=datetime(1, 1, 1, 11), duration=timedelta(hours=2)),
            (TimeSpan(start=datetime(1, 1, 1, 10), duration=timedelta(hours=1)),),
        ),
        (
            TimeSpan(start=datetime(1, 1, 1, 10), duration=timedelta(hours=2)),
            TimeSpan(start=datetime(1, 1, 1, 11), duration=timedelta(hours=1)),
            (TimeSpan(start=datetime(1, 1, 1, 10), duration=timedelta(hours=1)),),
        ),
        (
            TimeSpan(start=datetime(1, 1, 1, 10), duration=timedelta(hours=2)),
            TimeSpan(start=datetime(1, 1, 1, 9), duration=timedelta(hours=2)),
            (TimeSpan(start=datetime(1, 1, 1, 11), duration=timedelta(hours=1)),),
        ),
        (
            TimeSpan(start=datetime(1, 1, 1, 10), duration=timedelta(hours=2)),
            TimeSpan(start=datetime(1, 1, 1, 10), duration=timedelta(hours=1)),
            (TimeSpan(start=datetime(1, 1, 1, 11), duration=timedelta(hours=1)),),
        ),
        (
            TimeSpan(start=datetime(1, 1, 1, 10), duration=timedelta(hours=2)),
            TimeSpan(start=datetime(1, 1, 1, 10, 30), duration=timedelta(hours=1)),
            (
                TimeSpan(start=datetime(1, 1, 1, 10), duration=timedelta(minutes=30)),
                TimeSpan(start=datetime(1, 1, 1, 11, 30), duration=timedelta(minutes=30)),
            ),
        ),
    ],
)
def test_subtract(span1: TimeSpan, span2: TimeSpan, difference: TimeSpan):
    actual_difference = span1 - span2
    assert actual_difference == difference


@pytest.mark.parametrize(
    "time_span",
    [
        TimeSpan(start=datetime(1, 1, 1), duration=timedelta(seconds=1)),
        TimeSpan(
            start=datetime(1, 2, 3, 4, 5), duration=timedelta(days=2, hours=1, microseconds=14)
        ),  # microseconds will be truncated
        TimeSpan(start=datetime(1984, 11, 16, 19, 45), duration=timedelta(minutes=42)),
    ],
)
def test_serialization(time_span: TimeSpan, tmp_path: Path):
    file_path = tmp_path / "time_span.yaml"
    dct = time_span.to_dict()
    time_span2 = TimeSpan.from_dict(dct)
    assert time_span2 == time_span

    time_span.to_yaml(file_path)
    time_span3 = TimeSpan.from_yaml(file_path)
    assert time_span3 == time_span


@pytest.mark.parametrize(
    "time_span, new_date, expected",
    [
        (
            TimeSpan(start=datetime(1, 1, 1), duration=timedelta(days=1)),
            date(1, 2, 3),
            TimeSpan(start=datetime(1, 2, 3), duration=timedelta(days=1)),
        ),
        (
            TimeSpan(start=datetime(1999, 10, 12, 13, 12), duration=timedelta(hours=1)),
            date(2023, 1, 31),
            TimeSpan(start=datetime(2023, 1, 31, 13, 12), duration=timedelta(hours=1)),
        ),
    ],
)
def test_change_date(time_span: TimeSpan, new_date: date, expected: TimeSpan):
    actual = time_span.change_date(new_date)
    assert actual == expected
