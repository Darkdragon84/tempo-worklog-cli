from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import date, datetime, time, timedelta

from typing_extensions import Self, TypeIs

from tempo_worklog_cli.constants import (
    DAILY_WORKLOAD,
    DAY_START,
    LUNCH_BREAK_END,
    LUNCH_BREAK_START,
)
from tempo_worklog_cli.util.io_util import SaveLoad


class TimeSpanError(ValueError):
    pass


def _is_date(obj: object) -> TypeIs[date]:
    return type(obj) is date  # datetime is a subtype of date!


@dataclass(frozen=True)
class TimeSpan(SaveLoad):
    start: datetime
    duration: timedelta

    def __post_init__(self) -> None:
        object.__setattr__(self, "start", self.start.replace(microsecond=0))
        object.__setattr__(
            self, "duration", self.duration - timedelta(microseconds=self.duration.microseconds)
        )

    @classmethod
    def from_start_and_end(cls, start: datetime | date, end: datetime | date) -> Self:
        if _is_date(start):
            start = datetime.combine(start, time(0, 0))
        if _is_date(end):
            end = datetime.combine(end, time(23, 59))
        if end <= start:
            raise ValueError(f"end time {end} must be greater than start time {start}")
        return cls(start=start, duration=end - start)

    @property
    def end(self) -> datetime:
        return self.start + self.duration

    @property
    def dates(self) -> list[date]:
        return [self.start.date() + timedelta(days=d) for d in range(self.duration.days + 1)]

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
        """
        return overlapping part between `self` and `other`
        :param other:
        :return:
           - overlap if non-zero, None otherwise
        """
        return self.intersection(other)

    def subtract(self, other: TimeSpan) -> tuple[()] | tuple[TimeSpan] | tuple[TimeSpan, TimeSpan]:
        """
        subtract other TimeSpan from self

        Remove overlapping part between `self` and `other` from `self`.
        :param other:
        :return:
            - empty tuple if `other` completely covers `self`
            - 2 tuple (part_before_other, part_after_other) If `other` is completely contained in
            `self`
            - single element tuple otherwise
        """
        overlap = self & other
        if not overlap:
            return (replace(self),)

        spans = []
        if self.start < overlap.start:
            spans.append(TimeSpan.from_start_and_end(start=self.start, end=overlap.start))
        if overlap.end < self.end:
            spans.append(TimeSpan.from_start_and_end(start=overlap.end, end=self.end))

        return tuple(spans)

    def __sub__(self, other: TimeSpan) -> tuple[()] | tuple[TimeSpan] | tuple[TimeSpan, TimeSpan]:
        return self.subtract(other)


FULL_DAY = TimeSpan(start=DAY_START, duration=DAILY_WORKLOAD)
MORNING = TimeSpan.from_start_and_end(start=DAY_START, end=LUNCH_BREAK_START)
AFTERNOON = TimeSpan(start=LUNCH_BREAK_END, duration=DAILY_WORKLOAD - MORNING.duration)
