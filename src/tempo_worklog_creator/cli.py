import json
import logging
import os
from datetime import datetime, date

import click
from click import Context
from dotenv import load_dotenv

from tempo_worklog_creator.io_util import converter
from tempo_worklog_creator.time_span import TimeSpan
from tempo_worklog_creator.worklog_creator import WorkLogCreator

load_dotenv()

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
def delete(ctx: Context, start: str, end: str):
    """
    Delete worklog entries from START to END dates (inclusive).
    Dates must be given in isoformat YYYY-MM-DD.
    """
    ctx.ensure_object(dict)
    time_span = TimeSpan.from_start_and_end(
        start=converter.structure(start, datetime), end=converter.structure(end, datetime)
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
    Dates must be given in isoformat YYYY-MM-DD.
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

    Dates must be given in isoformat YYYY-MM-DD.
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
        descriptions=descriptions
    )
