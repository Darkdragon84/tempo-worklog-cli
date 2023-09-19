import os
from dataclasses import replace
from datetime import date, datetime

from dotenv import load_dotenv

from tempo_worklog_creator.time_span import TimeSpan
from tempo_worklog_creator.work_log import WorkLog
from tempo_worklog_creator.worklog_creator import WorkLogCreator

load_dotenv()

URL = os.getenv("URL")
USER = os.getenv("USER_EMAIL")
JIRA_TOKEN = os.getenv("JIRA_TOKEN")
TEMPO_TOKEN = os.getenv("TEMPO_TOKEN")


def main():
    log_creator = WorkLogCreator(url=URL, user=USER, jira_token=JIRA_TOKEN, tempo_token=TEMPO_TOKEN)
    full_week = TimeSpan(datetime(2023, 9, 18), datetime(2023, 9, 22, 23))
    log_creator.delete_logs(full_week)

    log_creator.create_workdays(date(2023, 9, 18), date(2023, 9, 22), "CORE-140", "implement and test vanilla MCTS")
    log_creator.create_workweek_default_meetings(date(2023, 9, 18))
    # log_creator.delete_logs(time_span=TimeSpan(datetime(2023, 9, 18, 1), datetime(2023, 9, 18, 23)))
    # span1 = TimeSpan(datetime(2023, 9, 18, 11), datetime(2023, 9, 18, 14))
    # span2 = TimeSpan(datetime(2023, 9, 18, 12), datetime(2023, 9, 18, 13))
    # log1 = WorkLog("639b25aaf7f0ee492fcf3b7a", issue_id="10138", time_span=span1, description="test")
    # log2 = replace(log1, time_span=span2, description="party crasher")
    # log1 = log_creator.create_log(log1)
    # log2 = log_creator.create_log(log2)

    # log_id = log_creator.create_log(log).worklog_id
    # log_creator.delete_log(log_id)
    # log_creator.tempo.delete(f"worklogs/{log_id}")
    # log_creator.create_workweek_default_meetings(date(year=2023, month=9, day=18))
    # today_p_3 = today + timedelta(days=3)
    # log_creator.create_workdays(mon, fri, "RES-109", "parity retreat 2023")
    # log_creator.create_holidays(date(year=2023, month=8, day=14), date(year=2023, month=8, day=15))
    # log_creator.create_log()


if __name__ == "__main__":
    main()
