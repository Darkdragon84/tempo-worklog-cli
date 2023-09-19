from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timedelta, date
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
    end: datetime

    def __post_init__(self) -> None:
        self.start = self.start.replace(microsecond=0)
        self.end = self.end.replace(microsecond=0)
        if self.end <= self.start:
            raise ValueError(f"end time {self.end} must be greater than start time {self.start}")

    @classmethod
    def from_start_and_delta(cls, start: datetime, delta: timedelta) -> Self:
        return cls(start=start, end=start + delta)

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


FULL_DAY = TimeSpan.from_start_and_delta(start=DAY_START, delta=DAILY_WORKLOAD)
MORNING = TimeSpan(start=DAY_START, end=LUNCH_BREAK_START)
AFTERNOON = TimeSpan.from_start_and_delta(
    start=LUNCH_BREAK_END, delta=DAILY_WORKLOAD - MORNING.duration
)


def unstructure_datetime(date_time: datetime) -> str:
    return date_time.isoformat()


def structure_datetime(date_time_str: str, _: Type[datetime]) -> datetime:
    return datetime.fromisoformat(date_time_str)


converter.register_unstructure_hook(datetime, unstructure_datetime)
converter.register_structure_hook(datetime, structure_datetime)
