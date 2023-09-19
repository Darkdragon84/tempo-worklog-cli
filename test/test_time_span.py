import pytest
from tempo_worklog_creator.time_span import TimeSpan
from datetime import datetime, time, timedelta


@pytest.mark.parametrize(
    "span1, span2",
    [
        (
            TimeSpan(start=datetime(2000, 1, 1, 10), end=datetime(2000, 1, 1, 11)),
            TimeSpan(start=datetime(2000, 1, 1, 10), end=datetime(2000, 1, 1, 11)),
        ),
        (
            TimeSpan(start=datetime(2000, 1, 1, 10), end=timedelta(hours=1)),
            TimeSpan(start=datetime(2000, 1, 1, 10), end=timedelta(hours=1)),
        ),
        (
            TimeSpan(start=datetime(2000, 1, 1, 10), end=timedelta(hours=1)),
            TimeSpan(start=datetime(2000, 1, 1, 10), end=datetime(2000, 1, 1, 11)),
        ),
        (
            TimeSpan(start=datetime(2000, 1, 1, 10), end=timedelta(hours=1)),
            TimeSpan(start=datetime(2000, 1, 1, 10), end=timedelta(minutes=60)),
        ),
        (
            TimeSpan(start=time(10), end=timedelta(hours=1)),
            TimeSpan(start=time(10), end=timedelta(minutes=60)),
        ),
    ],
)
def test_equality(span1, span2):
    assert span1 == span2


@pytest.mark.parametrize(
    "span1, span2, difference",
    [
        (
            TimeSpan(start=datetime(1, 1, 1, 10), end=datetime(1, 1, 1, 11)),
            TimeSpan(start=datetime(1, 1, 1, 10), end=datetime(1, 1, 1, 11)),
            (),
        ),
        (
            TimeSpan(start=datetime(1, 1, 1, 10), end=datetime(1, 1, 1, 11)),
            TimeSpan(start=datetime(1, 1, 1, 9), end=datetime(1, 1, 1, 11)),
            (),
        ),
        (
            TimeSpan(start=datetime(1, 1, 1, 10), end=datetime(1, 1, 1, 11)),
            TimeSpan(start=datetime(1, 1, 1, 10), end=datetime(1, 1, 1, 12)),
            (),
        ),
        (
            TimeSpan(start=datetime(1, 1, 1, 10), end=datetime(1, 1, 1, 12)),
            TimeSpan(start=datetime(1, 1, 1, 11), end=datetime(1, 1, 1, 13)),
            (TimeSpan(start=datetime(1, 1, 1, 10), end=datetime(1, 1, 1, 11)),),
        ),
        (
            TimeSpan(start=datetime(1, 1, 1, 10), end=datetime(1, 1, 1, 12)),
            TimeSpan(start=datetime(1, 1, 1, 11), end=datetime(1, 1, 1, 12)),
            (TimeSpan(start=datetime(1, 1, 1, 10), end=datetime(1, 1, 1, 11)),),
        ),
        (
            TimeSpan(start=datetime(1, 1, 1, 10), end=datetime(1, 1, 1, 12)),
            TimeSpan(start=datetime(1, 1, 1, 9), end=datetime(1, 1, 1, 11)),
            (TimeSpan(start=datetime(1, 1, 1, 11), end=datetime(1, 1, 1, 12)),),
        ),
        (
            TimeSpan(start=datetime(1, 1, 1, 10), end=datetime(1, 1, 1, 12)),
            TimeSpan(start=datetime(1, 1, 1, 10), end=datetime(1, 1, 1, 11)),
            (TimeSpan(start=datetime(1, 1, 1, 11), end=datetime(1, 1, 1, 12)),),
        ),
        (
            TimeSpan(start=datetime(1, 1, 1, 10), end=datetime(1, 1, 1, 12)),
            TimeSpan(start=datetime(1, 1, 1, 10, 30), end=datetime(1, 1, 1, 11, 30)),
            (
                TimeSpan(start=datetime(1, 1, 1, 10), end=datetime(1, 1, 1, 10, 30)),
                TimeSpan(start=datetime(1, 1, 1, 11, 30), end=datetime(1, 1, 1, 12)),
            ),
        ),
    ],
)
def test_subtract(span1, span2, difference):
    actual_difference = span1 - span2
    assert actual_difference == difference
