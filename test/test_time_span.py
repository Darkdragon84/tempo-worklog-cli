from datetime import datetime, timedelta

import pytest

from tempo_worklog_creator.time_span import TimeSpan


@pytest.mark.parametrize(
    "span1, span2",
    [
        (
            TimeSpan(start=datetime(2000, 1, 1, 10), end=datetime(2000, 1, 1, 11)),
            TimeSpan(start=datetime(2000, 1, 1, 10), end=datetime(2000, 1, 1, 11)),
        ),
        (
            TimeSpan.from_start_and_delta(start=datetime(2000, 1, 1, 10), delta=timedelta(hours=1)),
            TimeSpan.from_start_and_delta(start=datetime(2000, 1, 1, 10), delta=timedelta(hours=1)),
        ),
        (
            TimeSpan.from_start_and_delta(start=datetime(2000, 1, 1, 10), delta=timedelta(hours=1)),
            TimeSpan(start=datetime(2000, 1, 1, 10), end=datetime(2000, 1, 1, 11)),
        ),
        (
            TimeSpan.from_start_and_delta(start=datetime(2000, 1, 1, 10), delta=timedelta(hours=1)),
            TimeSpan.from_start_and_delta(
                start=datetime(2000, 1, 1, 10), delta=timedelta(minutes=60)
            ),
        ),
    ],
)
def test_equality(span1, span2):
    assert span1 == span2


@pytest.mark.parametrize(
    "span1, span2, intersection",
    [
        (
            TimeSpan(start=datetime(1, 1, 1, 10), end=datetime(1, 1, 1, 11)),
            TimeSpan(start=datetime(1, 1, 1, 10), end=datetime(1, 1, 1, 11)),
            TimeSpan(start=datetime(1, 1, 1, 10), end=datetime(1, 1, 1, 11)),
        ),
        (
            TimeSpan(start=datetime(1, 1, 1, 10), end=datetime(1, 1, 1, 11)),
            TimeSpan(start=datetime(1, 1, 1, 11), end=datetime(1, 1, 1, 12)),
            None,
        ),
        (
            TimeSpan(start=datetime(1, 1, 1, 10), end=datetime(1, 1, 1, 12)),
            TimeSpan(start=datetime(1, 1, 1, 11), end=datetime(1, 1, 1, 13)),
            TimeSpan(start=datetime(1, 1, 1, 11), end=datetime(1, 1, 1, 12)),
        ),
        (
            TimeSpan(start=datetime(1, 1, 1, 10), end=datetime(1, 1, 1, 13)),
            TimeSpan(start=datetime(1, 1, 1, 11), end=datetime(1, 1, 1, 12)),
            TimeSpan(start=datetime(1, 1, 1, 11), end=datetime(1, 1, 1, 12)),
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
def test_subtract(span1: TimeSpan, span2: TimeSpan, difference: TimeSpan):
    actual_difference = span1 - span2
    assert actual_difference == difference
