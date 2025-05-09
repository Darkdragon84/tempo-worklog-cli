from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass, replace
from datetime import date, datetime, time, timedelta
from itertools import combinations
from typing import Any

from jira import JIRA

from tempo_worklog_cli.constants import (
    ACCOUNT_ID,
    AUTHOR_ACCOUNT_ID,
    DESCRIPTION,
    ID,
    ISSUE,
    ISSUE_ID,
    START_DATE,
    START_TIME,
    TEMPO_WORKLOG_ID,
    TIME_SPENT_SECONDS,
)
from tempo_worklog_cli.time_span import TimeSpan
from tempo_worklog_cli.util.io_util import SaveLoad


@dataclass(frozen=True)
class WorkLog(SaveLoad):
    issue: str  # str-int (like e.g. PP-1)
    time_span: TimeSpan
    description: str
    worklog_id: int | None = None

    def as_tempo_dict(self, jira: JIRA) -> dict[str, Any]:
        """
        dict representation for TEMPO API
        """
        return {
            AUTHOR_ACCOUNT_ID: jira.myself()[ACCOUNT_ID],
            ISSUE_ID: jira.issue(self.issue).id,
            START_DATE: self.time_span.start.date().isoformat(),
            START_TIME: self.time_span.start.time().isoformat(),
            TIME_SPENT_SECONDS: int(self.time_span.duration.total_seconds()),
            DESCRIPTION: self.description,
            TEMPO_WORKLOG_ID: self.worklog_id,
        }

    @classmethod
    def from_tempo_dict(cls, log_dict: dict[str, Any], jira: JIRA):
        """
        create from TEMPO API dict representation
        """
        return cls(
            issue=jira.issue(log_dict[ISSUE][ID]).key,
            time_span=TimeSpan(
                start=datetime.combine(
                    date.fromisoformat(log_dict[START_DATE]),
                    time.fromisoformat(log_dict[START_TIME]),
                ),
                duration=timedelta(seconds=log_dict[TIME_SPENT_SECONDS]),
            ),
            description=log_dict[DESCRIPTION],
            worklog_id=log_dict.get(TEMPO_WORKLOG_ID),
        )


@dataclass
class WorkLogSequence(SaveLoad):
    start_date: date
    day_to_logs: dict[int, list[WorkLog]]

    @classmethod
    def from_worklogs(cls, work_logs: list[WorkLog]):
        start_date = min([log.time_span.start.date() for log in work_logs])
        day_to_logs = defaultdict(list)
        for log in work_logs:
            day = (log.time_span.start.date() - start_date).days
            time_span = replace(
                log.time_span, start=log.time_span.start.replace(year=1, month=1, day=1)
            )
            day_to_logs[day].append(replace(log, time_span=time_span))
        return cls(start_date=start_date, day_to_logs=day_to_logs)

    @property
    def worklogs(self) -> list[WorkLog]:
        return [
            replace(
                log,
                time_span=replace(
                    log.time_span,
                    start=datetime.combine(
                        self.start_date + timedelta(days=day), log.time_span.start.time()
                    ),
                ),
            )
            for day, logs in self.day_to_logs.items()
            for log in logs
        ]


def overlapping(logs: Iterable[WorkLog]) -> list[tuple[WorkLog, WorkLog]]:
    """
    return pairs of overlapping WorkLogs from a given iterable of WorkLogs
    :param logs:
    :return:
    """
    return [(log1, log2) for log1, log2 in combinations(logs, 2) if log1.time_span & log2.time_span]
