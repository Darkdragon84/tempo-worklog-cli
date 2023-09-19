from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, date, time, timedelta
from typing import Any

from tempo_worklog_creator.constants import (
    AUTHOR_ACCOUNT_ID,
    ISSUE_ID,
    START_DATE,
    START_TIME,
    TIME_SPENT_SECONDS,
    DESCRIPTION,
    AUTHOR,
    ACCOUNT_ID,
    ISSUE,
    ID,
    TEMPO_WORKLOG_ID,
)
from tempo_worklog_creator.time_span import TimeSpan


@dataclass
class WorkLog:
    account_id: str
    issue_id: int | str  # this is the integer id, not str-int (like e.g. PP-1)
    time_span: TimeSpan
    description: str
    worklog_id: int | None = None

    def as_dict(self) -> dict[str, Any]:
        """
        dict representation for TEMPO API
        """
        return {
            AUTHOR_ACCOUNT_ID: self.account_id,
            ISSUE_ID: self.issue_id,
            START_DATE: self.time_span.start.date().isoformat(),
            START_TIME: self.time_span.start.time().isoformat(),
            TIME_SPENT_SECONDS: int(self.time_span.duration.total_seconds()),
            DESCRIPTION: self.description,
            TEMPO_WORKLOG_ID: self.worklog_id
        }

    @classmethod
    def from_dict(cls, log_dict: dict[str, Any]):
        """
        create from TEMPO API dict representation
        """
        return cls(
            account_id=log_dict[AUTHOR][ACCOUNT_ID],
            issue_id=log_dict[ISSUE][ID],
            time_span=TimeSpan(
                start=datetime.combine(
                    date.fromisoformat(log_dict[START_DATE]),
                    time.fromisoformat(log_dict[START_TIME]),
                ),
                end=timedelta(seconds=log_dict[TIME_SPENT_SECONDS]),
            ),
            description=log_dict[DESCRIPTION],
            worklog_id=log_dict.get(TEMPO_WORKLOG_ID),
        )
