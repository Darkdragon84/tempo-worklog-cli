from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timedelta, date, time
from typing import Type

from typing_extensions import Self

from tempo_worklog_creator.constants import (
    DAY_START,
    DAILY_WORKLOAD,
    LUNCH_BREAK_START,
    LUNCH_BREAK_END,
)
from tempo_worklog_creator.io_util import SaveLoad, converter


@dataclass
class TimeSpan(SaveLoad):
    start: datetime
    duration: timedelta

    def __post_init__(self) -> None:
        self.start = self.start.replace(microsecond=0)
        self.duration = self.duration - timedelta(microseconds=self.duration.microseconds)

    @classmethod
    def from_start_and_end(cls, start: datetime, end: datetime) -> Self:
        if end <= start:
            raise ValueError(f"end time {end} must be greater than start time {start}")
        return cls(start=start, duration=end - start)

    @property
    def end(self) -> datetime:
        return self.start + self.duration

    def change_date(self, new_date: date) -> TimeSpan:
        return TimeSpan(
            start=datetime.combine(date=new_date, time=self.start.time()),
            duration=self.duration,
        )

    def intersection(self, other: TimeSpan) -> TimeSpan | None:
        if self.start <= other.start < self.end or other.start <= self.start < other.end:
            return TimeSpan.from_start_and_end(
                start=max(self.start, other.start), end=min(self.end, other.end)
            )

    def __and__(self, other: TimeSpan) -> TimeSpan | None:
        return self.intersection(other)

    def subtract(self, other: TimeSpan) -> tuple[()] | tuple[TimeSpan] | tuple[TimeSpan, TimeSpan]:
        overlap = self & other
        if not overlap:
            return (replace(self),)

        spans = []
        if self.start < overlap.start:
            spans.append(TimeSpan.from_start_and_end(start=self.start, end=overlap.start))
        if overlap.end < self.end:
            spans.append(TimeSpan.from_start_and_end(start=overlap.end, end=self.end))

        return tuple(spans)

    def __sub__(self, other: TimeSpan) -> None | tuple[TimeSpan] | tuple[TimeSpan, TimeSpan]:
        return self.subtract(other)


FULL_DAY = TimeSpan(start=DAY_START, duration=DAILY_WORKLOAD)
MORNING = TimeSpan.from_start_and_end(start=DAY_START, end=LUNCH_BREAK_START)
AFTERNOON = TimeSpan(start=LUNCH_BREAK_END, duration=DAILY_WORKLOAD - MORNING.duration)
