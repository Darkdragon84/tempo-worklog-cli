from __future__ import annotations

from datetime import timedelta, time

AUTHOR = "author"
ACCOUNT_ID = "accountId"
AUTHOR_ACCOUNT_ID = "authorAccountId"
ISSUE = "issue"
ID = "id"
ISSUE_ID = "issueId"
START_DATE = "startDate"
START_TIME = "startTime"
TIME_SPENT_SECONDS = "timeSpentSeconds"
DESCRIPTION = "description"
TEMPO_WORKLOG_ID = "tempoWorklogId"

COMPILER_STANDUP = "CORE-141"
DEV_MEETINGS = "PP-1"
COMPANY_MEETINGS = "PP-2"
HOLIDAYS_ISSUE = "PP-7"
JOINT_SEMINAR = "RES-123"

DAILY_WORKLOAD = timedelta(seconds=27720)  # 7.7h in seconds
DAY_START = time(hour=9)
LUNCH_BREAK_START = time(hour=13)
LUNCH_BREAK_END = time(hour=14)
