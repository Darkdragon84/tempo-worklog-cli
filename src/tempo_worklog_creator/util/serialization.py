from datetime import datetime, time, timedelta, date
from typing import Type
import re
from cattrs import Converter

converter = Converter(forbid_extra_keys=True)

TODAY = "today"
WEEK_START = "week-start"
WEEK_END = "week-end"

DAY_REGEX = re.compile(rf"({TODAY}|{WEEK_START}|{WEEK_END})([+-]\d+)?")


def unstructure_datetime(dt: datetime) -> str:
    if dt.date() == datetime.min.date():
        dt = dt.time()
    return dt.isoformat()


def structure_datetime(dt: str | datetime, _: Type[datetime]) -> datetime:
    # yaml structures full datetime entries automatically
    if isinstance(dt, datetime):
        return dt

    try:
        dt = datetime.fromisoformat(dt)
    except ValueError:
        dt = datetime.combine(datetime.min.date(), time.fromisoformat(dt))
    return dt


def unstructure_timedelta(td: timedelta) -> str:
    return f"{td.days}T{str(timedelta(seconds=td.seconds)):>08}"


def structure_timedelta(td_str: str, _: Type[timedelta]) -> timedelta:
    d_str, t_str = td_str.split("T")
    t = time.fromisoformat(t_str)
    return timedelta(days=int(d_str), hours=t.hour, minutes=t.minute, seconds=t.second)


def unstructure_date(d: date) -> str:
    return d.isoformat()


def structure_date(date_str: str, _: Type[date]) -> date:
    """
    if there is a match, i.e. m = DAY_REGEX.match(date_str) is not None, then
    m.group(0) is the entire match
    m.group(1) is the first capturing group, i.e. one of ("today", "week-start", "week-end")
    m.group(2) is the second capturing group (which is optional), i.e. ±X or None
    :param date_str:
    :param _:
    :return:
    """
    m = DAY_REGEX.match(date_str)
    if m is not None:
        today = date.today()
        if m.group(1) == TODAY:
            day = today
        elif m.group(1) == WEEK_START:
            day = date.today() - timedelta(days=today.weekday())
        elif m.group(1) == WEEK_END:
            day = date.today() + timedelta(days=4 - today.weekday())
        else:
            raise ValueError(f"'{m.group(0)}' not recognized")

        if m.group(2) is not None:
            day += timedelta(days=int(m.group(2)))
        return day
    return date.fromisoformat(date_str)


converter.register_unstructure_hook(date, unstructure_date)
converter.register_unstructure_hook(datetime, unstructure_datetime)
converter.register_unstructure_hook(timedelta, unstructure_timedelta)

converter.register_structure_hook(date, structure_date)
converter.register_structure_hook(datetime, structure_datetime)
converter.register_structure_hook(timedelta, structure_timedelta)
