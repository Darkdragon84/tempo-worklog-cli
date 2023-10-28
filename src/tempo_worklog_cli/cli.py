import logging
import os
from datetime import date
from pathlib import Path

import click
from click import Context
from dotenv import load_dotenv

from tempo_worklog_cli.time_span import TimeSpan
from tempo_worklog_cli.util.serialization import converter
from tempo_worklog_cli.worklog_creator import WorkLogCreator

DOTENV_PATH = Path("~/.tempo/.env").expanduser()
load_dotenv(DOTENV_PATH)

JIRA = os.environ["JIRA_TOKEN"]
TEMPO = os.environ["TEMPO_TOKEN"]
URL = os.environ["URL"]
USER = os.environ["USER_EMAIL"]

LOG_CREATOR = "log_creator"


@click.group()
@click.option(
    "--loglevel", "-l", default="info", help="one of (debug, info, warning, error, critical)"
)
@click.pass_context
def cli(ctx: Context, loglevel: str):
    """
    Tempo timesheets command line interface for (batch) creating and deleting work log entries
    from arguments or yaml files.
    """
    level = logging.getLevelName(loglevel.upper())
    logging.basicConfig(level=level, format="%(asctime)s|%(name)s|%(levelname)s: %(message)s")
    ctx.ensure_object(dict)
    ctx.obj[LOG_CREATOR] = WorkLogCreator(url=URL, user=USER, jira_token=JIRA, tempo_token=TEMPO)


@cli.command()
@click.argument("start")
@click.argument("end")
@click.pass_context
def get(ctx: Context, start: str, end: str):
    """
    Get and display worklog entries from START to END dates (inclusive).

    Dates must be given in isoformat YYYY-MM-DD or follow the pattern

      today|week-start|week-end[+/-DAYS]

    where week-start and week-end are the dates of the current week's MON and FRI respectively
    and the
    group [+/-DAYS] with DAYS an integer is optional.

    \b
    Examples:
             today: today
           today-1: yesterday
           today+2: the day after tomorrow
      week-start-7: last week's MON
        week-end-1: this week's THU
        week-end+3: next week's MON
    """
    ctx.ensure_object(dict)
    time_span = TimeSpan.from_start_and_end(
        start=converter.structure(start, date), end=converter.structure(end, date)
    )
    logs = ctx.obj[LOG_CREATOR].get_logs(time_span=time_span)
    for log in logs:
        click.echo(log)


@cli.command()
@click.argument("start")
@click.argument("end")
@click.pass_context
def delete(ctx: Context, start: str, end: str):
    """
    Delete worklog entries from START to END dates (inclusive).

    Dates must be given in isoformat YYYY-MM-DD or follow the pattern

      today|week-start|week-end[+/-DAYS]

    where week-start and week-end are the dates of the current week's MON and FRI respectively
    and the
    group [+/-DAYS] with DAYS an integer is optional.

    \b
    Examples:
             today: today
           today-1: yesterday
           today+2: the day after tomorrow
      week-start-7: last week's MON
        week-end-1: this week's THU
        week-end+3: next week's MON
    """
    ctx.ensure_object(dict)
    time_span = TimeSpan.from_start_and_end(
        start=converter.structure(start, date), end=converter.structure(end, date)
    )
    ctx.obj[LOG_CREATOR].delete_logs(time_span=time_span)


@cli.group()
@click.pass_context
def create(ctx: Context):
    """
    Create worklog entries.
    """
    pass


@create.command()
@click.argument("filename", type=click.Path(exists=True))
@click.pass_context
def from_yaml(ctx: Context, filename: str):
    """
    Create worklog entries from yaml file at FILENAME.

    Supported yaml formats:
      - dict representation of WorkLogSequence
      - list of dict representation of WorkLog
    """
    ctx.ensure_object(dict)
    ctx.obj[LOG_CREATOR].create_logs_from_yaml(filename)


@create.command()
@click.argument("start")
@click.argument("end")
@click.pass_context
def holidays(ctx: Context, start: str, end: str):
    """
    Create holiday entries from START to END dates (inclusive) for 7.7h each day.
    Weekend days are skipped.

    Dates must be given in isoformat YYYY-MM-DD or follow the pattern

      today|week-start|week-end[+/-DAYS]

    where week-start and week-end are the dates of the current week's MON and FRI respectively
    and the
    group [+/-DAYS] with DAYS an integer is optional.

    \b
    Examples:
             today: today
           today-1: yesterday
           today+2: the day after tomorrow
      week-start-7: last week's MON
        week-end-1: this week's THU
        week-end+3: next week's MON
    """
    ctx.ensure_object(dict)
    ctx.obj[LOG_CREATOR].create_holidays(
        start_date=converter.structure(start, date), end_date=converter.structure(end, date)
    )


@create.command()
@click.argument("start")
@click.argument("end")
@click.argument("issue")
@click.argument("descriptions", nargs=-1)
@click.pass_context
def workdays(ctx: Context, start: str, end: str, issue: str, descriptions: str):
    """
    Create workdays batch from START to END dates (inclusive) for ISSUE:
     - one in the morning from 09:00 - 13:00
     - one in the afternoon from 14:00 - 17:42
    giving a total of 7.7h work hours per day.
    Weekend days are skipped.

    DESCRIPTIONS can be either a single string that is used for all entries, or a sequence of
    strings for each entry. The number of entries in DESCRIPTIONS must match the number of
    worklog entries that are created (two per day).

    Dates must be given in isoformat YYYY-MM-DD or follow the pattern

      today|week-start|week-end[+/-DAYS]

    where week-start and week-end are the dates of the current week's MON and FRI respectively
    and the
    group [+/-DAYS] with DAYS an integer is optional.

    \b
    Examples:
             today: today
           today-1: yesterday
           today+2: the day after tomorrow
      week-start-7: last week's MON
        week-end-1: this week's THU
        week-end+3: next week's MON
    """
    # if descriptions empty, turn into no-op
    if not descriptions:
        ctx.obj[LOG_CREATOR].logger.warning("descriptions empty, not creating any worklogs")
        return

    if len(descriptions) == 1:
        descriptions = descriptions[0]

    ctx.ensure_object(dict)
    ctx.obj[LOG_CREATOR].create_workdays(
        start_date=converter.structure(start, date),
        end_date=converter.structure(end, date),
        issue=issue,
        descriptions=descriptions,
    )
