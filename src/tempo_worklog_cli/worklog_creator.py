from __future__ import annotations

import logging
import os
import warnings
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from datetime import date, timedelta
from pathlib import Path
from typing import Iterable, Callable, TypeVar, Any, Iterator

from jira import JIRA, Issue
from tempoapiclient.client_v4 import Tempo

from tempo_worklog_cli.constants import (
    ACCOUNT_ID,
    HOLIDAYS_ISSUE,
    TEMPO_WORKLOG_ID,
    ISSUE_ID,
)
from tempo_worklog_creator.time_span import TimeSpan, FULL_DAY, MORNING, AFTERNOON
from tempo_worklog_creator.util.io_util import load_yaml
from tempo_worklog_creator.util.serialization import converter
from tempo_worklog_creator.work_log import WorkLog, WorkLogSequence

T = TypeVar("T")


class WorkLogCreator:
    def __init__(
        self,
        url: str,
        user: str,
        jira_token: str,
        tempo_token: str,
        num_threads: int = os.cpu_count(),
    ) -> None:
        self._url = url
        self._user = user

        self._jira = JIRA(self._url, basic_auth=(self._user, jira_token))
        self._user_id = self._jira.myself()[ACCOUNT_ID]

        self._tempo = Tempo(auth_token=tempo_token)
        self._num_threads = num_threads
        self.logger = logging.getLogger(self.__class__.__name__)

    @property
    def user(self) -> str:
        return self._user

    @property
    def user_id(self) -> str:
        return self._user_id

    @property
    def tempo(self) -> Tempo:
        return self._tempo

    @property
    def jira(self) -> JIRA:
        return self._jira

    def jira_issue(self, issue: str | int) -> Issue:
        """
        get unique JIRA integer id from issue identifier (
        """
        return self._jira.issue(issue)

    def _adapt_existing_logs(self, work_log: WorkLog):
        """
        fetch all existing logs, that overlap with `work_log` and cut away the overlaps from the
        existing logs or delete them

        :param work_log:
        :return:
        """
        for log in self.get_worklogs(work_log.time_span):
            adapted_spans = log.time_span - work_log.time_span
            # new_log covers log completely
            if not adapted_spans:
                self.logger.warning("deleting %s", log)
                self.delete_log(log.worklog_id)
                continue

            # new_log cuts log in the middle
            if len(adapted_spans) == 2:
                span1, span2 = adapted_spans

                self.logger.info(f"splitting {log} into {span1} and {span2}")
                log1 = replace(log, time_span=span1)
                log2 = replace(log, time_span=span2)
                self.update_log(log1)
                self.create_log(log2)
                continue

            adapted_span = adapted_spans[0]
            # no overlap (this shouldn't happen though)
            if adapted_span == log.time_span:
                continue

            self.logger.info(f"adapting {log} to {adapted_span}")
            log = replace(log, time_span=adapted_span)
            self.update_log(log)

    def get_worklogs(self, time_span: TimeSpan) -> list[WorkLog]:
        """
        get all worklogs that overlap with `time_span`.

        :param time_span:
        :return:
        """
        # this gets all logs on all DAYS that have an overlap with `time_span`
        worklogs = [
            WorkLog.from_tempo_dict(log, self.jira)
            for log in self._tempo.get_worklogs(time_span.start, time_span.end)
        ]
        # filter out logs that actually overlap with time_spane
        worklogs = [worklog for worklog in worklogs if worklog.time_span & time_span]
        return worklogs

    def create_log(self, work_log: WorkLog, skip_weekend: bool = True) -> WorkLog | None:
        """
        create new work log entry

        :param work_log:
        :param skip_weekend: whether to create the log if its start or end date fall on a weekend
        :return:
        """
        if work_log.time_span.start.weekday() > 4 or work_log.time_span.end.weekday() > 4:
            self.logger.warning(f"%s is on a weekend", work_log.time_span)
            if skip_weekend:
                return

        self._adapt_existing_logs(work_log)
        new_log = None
        data = work_log.as_tempo_dict(self.jira)
        data.pop(TEMPO_WORKLOG_ID, None)  # payload can't contain existing worklog id
        try:
            new_log = WorkLog.from_tempo_dict(self._tempo.post("worklogs", data=data), self.jira)
            self.logger.info(f"created {new_log}")
        except (Exception, SystemExit) as e:
            self.logger.error(e)
            self.logger.error(f"payload: {data}")
        return new_log

    def _batch_perform_action(self, fun: Callable[[T], Any], data: Iterable[T]) -> Iterator[Any]:
        with ThreadPoolExecutor(max_workers=self._num_threads) as pool:
            results = pool.map(fun, data)
        return results

    def create_logs(self, worklogs: Iterable[WorkLog]):
        """
        create a batch of worklogs asynchronously
        :param worklogs:
        :return:
        """
        return [
            log for log in self._batch_perform_action(self.create_log, worklogs) if log is not None
        ]

    def update_log(self, work_log: WorkLog) -> WorkLog | None:
        """
        update an existing work log with new data in `work_log`. `work_log.worklog_id` must contain
        the id of an existing work log that is to be updated.

        :param work_log: work log to be updated with new data
        :return:
        """

        if work_log.worklog_id is None:
            raise ValueError(f"{work_log} has no work log id.")

        data = work_log.as_tempo_dict(self.jira)
        worklog_id = data.pop(TEMPO_WORKLOG_ID)  # payload can't contain existing worklog id
        data.pop(ISSUE_ID, None)  # payload can't contain issue id (must remain fixed)

        updated_log = None
        try:
            updated_log = WorkLog.from_tempo_dict(
                self._tempo.put(f"worklogs/{worklog_id}", data=data), self.jira
            )
            self.logger.info(f"updated {updated_log}")
        except (Exception, SystemExit) as e:
            self.logger.error(e)
            self.logger.error(f"payload: {data}")
        return updated_log

    def delete_log(self, work_log_id: int):
        """
        delete a work log by its id

        :param work_log_id:
        :return:
        """
        try:
            log = WorkLog.from_tempo_dict(self._tempo.get(f"worklogs/{work_log_id}"), self.jira)
            self._tempo.delete(f"worklogs/{work_log_id}")
            self.logger.info(f"deleted {log}")
        except (Exception, SystemExit) as e:
            self.logger.error(e)
            self.logger.error(f"work_log_id: {work_log_id}")

    def delete_logs(self, time_span: TimeSpan):
        """
        delete all logs overlapping with a time span.
        :param time_span:
        :return:
        """
        worklog_ids = [log.worklog_id for log in self.get_worklogs(time_span)]
        self._batch_perform_action(self.delete_log, worklog_ids)

    def _create_log_collection(
        self,
        start_date: date,
        end_date: date,
        issue: str,
        time_spans: TimeSpan | Iterable[TimeSpan],
        descriptions: str | Iterable[str],
    ) -> list[WorkLog]:
        """
        add multiple entries `start_date` to `end_date`. If `time_spans` and `descriptions` are
        iterables, they must both be of length `(end_date - start_date).days + 1`, i.e. must have
        an entry for each day. If they are single elements, the same entry will be created for
        every day.

        :param start_date: day of first entry
        :param end_date: day of last entry
        :param issue: name of the issue
        :param time_spans: time span for each entry. if single element, all entries will have
                           the same time span
        :param descriptions: description for each entry. if single element, all entries will have
                             the same description
        :return: list of created WorkLogs
        """
        duration = end_date - start_date
        if isinstance(descriptions, str):
            descriptions = [descriptions] * (duration.days + 1)
        if isinstance(time_spans, TimeSpan):
            time_spans = [time_spans]

        if duration.days + 1 != len(descriptions):
            warnings.warn(f"got {len(descriptions)} descriptions for {duration.days + 1} days.")

        worklogs = []
        for i, description in zip(range(duration.days + 1), descriptions):
            day = start_date + timedelta(days=i)
            # don't add entries for weekends
            if day.weekday() > 4:
                continue

            worklogs += [
                WorkLog(
                    issue=issue,
                    time_span=time_span.change_date(day),
                    description=description,
                )
                for time_span in time_spans
            ]

        return self.create_logs(worklogs)

    def create_holidays(self, start_date: date, end_date: date) -> list[WorkLog]:
        """
        creates holiday entries for 7.7h for each day from `start_date` to `end_date` without
        lunch break

        :param start_date:
        :param end_date:
        :return:
        """
        return self._create_log_collection(
            start_date=start_date,
            end_date=end_date,
            issue=HOLIDAYS_ISSUE,
            time_spans=FULL_DAY,
            descriptions="holidays",
        )

    def create_workdays(
        self, start_date: date, end_date: date, issue: str, descriptions: str | Iterable[str]
    ) -> list[WorkLog]:
        """
        creates full workdays for the same issue for every day from `start_date` to `end_date`,
        inserting a lunch break from 13:00 to 14:00.
        If description is a single string, it will be used for all created entries. If it is an
        iterable it has to contain as many different entries as work logs that will be created:
        2 * ((end_date - start_date).days + 1)

        :param start_date:
        :param end_date:
        :param issue:
        :param descriptions:
        :return:
        """
        return self._create_log_collection(
            start_date=start_date,
            end_date=end_date,
            issue=issue,
            time_spans=[MORNING, AFTERNOON],
            descriptions=descriptions,
        )

    def create_logs_from_yaml(self, filepath: Path | str):
        """
        loads logs from a yaml file and creates them.
        Supported yaml formats:
          - dict representation of WorkLogSequence
          - list of dict representation of WorkLog

        :param filepath:
        :return:
        """
        filepath = Path(filepath)
        if not filepath.is_file():
            raise FileNotFoundError(f"{filepath} not found")

        data = load_yaml(filepath)
        try:
            if isinstance(data, dict):
                sequence = WorkLogSequence.from_dict(data)
                worklogs = sequence.worklogs
            elif isinstance(data, list):
                worklogs = converter.structure(data, list[WorkLog])
            else:
                raise ValueError(f"data format in {filepath} not supported.")
            self.create_logs(worklogs)
        except Exception as e:
            self.logger.exception("log creation failed: %s", e, exc_info=True)
