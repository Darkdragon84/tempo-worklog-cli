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
def cli(ctx, loglevel: str):
    level = logging.getLevelName(loglevel.upper())
    logging.basicConfig(level=level, format="%(asctime)s|%(name)s|%(levelname)s: %(message)s")
    ctx.ensure_object(dict)
    ctx.obj[LOG_CREATOR] = WorkLogCreator(url=URL, user=USER, jira_token=JIRA, tempo_token=TEMPO)


@cli.command()
@click.argument("start")
@click.argument("end")
@click.pass_context
def delete(ctx: Context, start: str, end: str):
    ctx.ensure_object(dict)
    time_span = TimeSpan.from_start_and_end(
        start=converter.structure(start, datetime), end=converter.structure(end, datetime)
    )
    ctx.obj[LOG_CREATOR].delete_logs(time_span=time_span)


@cli.group()
@click.pass_context
def create(ctx: Context):
    pass


@create.command()
@click.argument("filename", type=click.Path(exists=True))
@click.pass_context
def from_yaml(ctx: Context, filename: str):
    ctx.ensure_object(dict)
    ctx.obj[LOG_CREATOR].create_logs_from_yaml(filename)


@create.command()
@click.argument("start")
@click.argument("end")
@click.pass_context
def holidays(ctx: Context, start: str, end: str):
    ctx.ensure_object(dict)
    ctx.obj[LOG_CREATOR].create_holidays(
        start_date=converter.structure(start, date), end_date=converter.structure(end, date)
    )


if __name__ == "__main__":
    cli(obj={})
