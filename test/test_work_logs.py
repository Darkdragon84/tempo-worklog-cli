from datetime import datetime, timedelta
from pathlib import Path

import pytest

from tempo_worklog_cli.time_span import TimeSpan
from tempo_worklog_cli.work_log import WorkLog, WorkLogSequence


@pytest.mark.parametrize(
    "worklog",
    [
        WorkLog("PP-1", TimeSpan(datetime(1, 1, 1, 10, 30), timedelta(minutes=30)), "test"),
        WorkLog("CORE-2", TimeSpan(datetime(1, 1, 3, 12), timedelta(hours=1)), "test2", 1784),
    ],
)
def test_worklog_serialization(worklog: WorkLog, tmp_path: Path):
    filepath = tmp_path / "work_log.yaml"
    dct = worklog.to_dict()
    worklog1 = WorkLog.from_dict(dct)
    assert worklog1 == worklog

    worklog.to_yaml(filepath)
    worklog2 = WorkLog.from_yaml(filepath)
    assert worklog2 == worklog


@pytest.mark.parametrize(
    "worklogs",
    [
        (
            [
                WorkLog("PP-1", TimeSpan(datetime(1, 1, 1, 10, 30), timedelta(minutes=30)), "test"),
                WorkLog(
                    "CORE-2", TimeSpan(datetime(1, 1, 3, 12), timedelta(hours=1)), "test2", 1784
                ),
            ]
        ),
    ],
)
def test_work_log_sequence(worklogs: list[WorkLog]):
    seq = WorkLogSequence.from_worklogs(worklogs)
    assert seq.worklogs == worklogs


@pytest.mark.parametrize(
    "sequence",
    [
        (
            WorkLogSequence.from_worklogs(
                [
                    WorkLog(
                        "PP-1", TimeSpan(datetime(1, 1, 1, 10, 30), timedelta(minutes=30)), "test"
                    ),
                    WorkLog(
                        "CORE-2", TimeSpan(datetime(1, 1, 3, 12), timedelta(hours=1)), "test2", 1784
                    ),
                ]
            )
        ),
    ],
)
def test_work_log_sequence_serialization(sequence: WorkLogSequence, tmp_path: Path):
    filepath = tmp_path / "sequence.yaml"
    dct = sequence.to_dict()
    sequence1 = WorkLogSequence.from_dict(dct)
    assert sequence1 == sequence

    sequence.to_yaml(filepath)
    sequence2 = WorkLogSequence.from_yaml(filepath)
    assert sequence2 == sequence
