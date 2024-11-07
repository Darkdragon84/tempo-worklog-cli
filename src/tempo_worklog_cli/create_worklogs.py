import logging
import os
from datetime import datetime, timedelta
from pathlib import Path

from dotenv import load_dotenv

from tempo_worklog_cli.time_span import TimeSpan
from tempo_worklog_cli.worklog_creator import WorkLogCreator

load_dotenv()

JIRA = os.environ["JIRA_TOKEN"]
TEMPO = os.environ["TEMPO_TOKEN"]
URL = os.environ["URL"]
USER = os.environ["USER_EMAIL"]

LOGS = Path("/home/valentin/Python/tempo-worklog-creator/src/data/logs.yaml")
WEEK = Path("/home/valentin/Python/tempo-worklog-creator/src/data/work_week.yaml")
REGULAR = Path("/home/valentin/Python/tempo-worklog-creator/src/data/regular_meetings.yaml")

logging.basicConfig(level=logging.INFO)


def main():
    log_creator = WorkLogCreator(url=URL, user=USER, jira_token=JIRA, tempo_token=TEMPO)
    this_week = TimeSpan(start=datetime(2023, 9, 25), duration=timedelta(days=5))
    # log_creator.delete_logs(this_week)
    # log_creator.create_holidays(this_week.start.date(), this_week.end.date())
    # log_creator.create_logs_from_yaml(REGULAR)
    log_creator.create_logs_from_yaml(LOGS)


if __name__ == "__main__":
    main()
