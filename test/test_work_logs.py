from datetime import datetime, timedelta

import pytest

from tempo_worklog_creator.time_span import TimeSpan
from tempo_worklog_creator.work_log import WorkLog, WorkLogSequence


@pytest.mark.parametrize('worklogs', [
    ([
        WorkLog("PP-1", TimeSpan(datetime(1, 1, 1, 10, 30), timedelta(minutes=30)), "test"),
        WorkLog("CORE-2", TimeSpan(datetime(1, 1, 3, 12), timedelta(hours=1)), "test2"),
    ]),
])
def test_work_log_sequence(worklogs: list[WorkLog]):
    seq = WorkLogSequence.from_worklogs(worklogs)
    assert seq.worklogs == worklogs
