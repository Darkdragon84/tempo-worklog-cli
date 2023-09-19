from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, time, timedelta, date

from tempo_worklog_creator.constants import (
    DAY_START,
    DAILY_WORKLOAD,
    LUNCH_BREAK_START,
    LUNCH_BREAK_END,
)


@dataclass
class TimeSpan:
    start: datetime | time
    end: datetime | time | timedelta

    def __post_init__(self) -> None:
        if isinstance(self.start, time):
            self.start = datetime.combine(date.min, self.start)
        if isinstance(self.end, time):
            self.end = datetime.combine(date.min, self.end)
        elif isinstance(self.end, timedelta):
            self.end = self.start + self.end
        self.start = self.start.replace(microsecond=0)
        self.end = self.end.replace(microsecond=0)
        if self.end <= self.start:
            raise ValueError(f"end time {self.end} must be greater than start time {self.start}")

    @property
    def duration(self) -> timedelta:
        return self.end - self.start

    def change_date(self, new_date: date | datetime) -> TimeSpan:
        if isinstance(new_date, datetime):
            new_date = new_date.date
        return TimeSpan(
            start=datetime.combine(date=new_date, time=self.start.time()),
            end=datetime.combine(date=new_date, time=self.end.time()),
        )

    def intersection(self, other: TimeSpan) -> TimeSpan | None:
        if self.start <= other.start < self.end or other.start <= self.start < other.end:
            return TimeSpan(start=max(self.start, other.start), end=min(self.end, other.end))

    def __and__(self, other: TimeSpan) -> TimeSpan | None:
        return self.intersection(other)

    def subtract(self, other: TimeSpan) -> tuple[()] | tuple[TimeSpan] | tuple[TimeSpan, TimeSpan]:
        overlap = self & other
        if not overlap:
            return (replace(self),)

        spans = []
        if self.start < overlap.start:
            spans.append(TimeSpan(start=self.start, end=overlap.start))
        if overlap.end < self.end:
            spans.append(TimeSpan(start=overlap.end, end=self.end))

        return tuple(spans)

    def __sub__(self, other: TimeSpan) -> None | tuple[TimeSpan] | tuple[TimeSpan, TimeSpan]:
        return self.subtract(other)


FULL_DAY = TimeSpan(start=DAY_START, end=DAILY_WORKLOAD)
MORNING = TimeSpan(start=DAY_START, end=LUNCH_BREAK_START)
AFTERNOON = TimeSpan(start=LUNCH_BREAK_END, end=DAILY_WORKLOAD - MORNING.duration)
