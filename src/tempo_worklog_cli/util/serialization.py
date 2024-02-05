import re
from datetime import datetime, time, timedelta, date
from typing import Type

from cattrs import Converter

converter = Converter(forbid_extra_keys=True)

TODAY = "today"
WEEK_START = "week-start"
WEEK_END = "week-end"

DAY_REGEX = re.compile(rf"({TODAY}|{WEEK_START}|{WEEK_END})([+-]\d+)?")
TIME_DELTA_REGEX = re.compile(r"(?:(\d)+d)?(?:(\d{1,2})h)?(?:(\d{1,2})m)?(?:(\d{1,2})s)?")


def unstructure_datetime(dt: datetime) -> str:
    """
    unstructure to isoformat <year>-<month>-<day>T<hour>:<minute>:<second>
    """
    if dt.date() == datetime.min.date():
        dt = dt.time()
    return dt.isoformat()


def structure_datetime(dt: str | datetime, _: Type[datetime] = datetime) -> datetime:
    """
    structure from isoformat <year>-<month>-<day>T<hour>:<minute>:<second>
    """
    # yaml structures full datetime entries automatically
    if isinstance(dt, datetime):
        return dt

    try:
        return datetime.fromisoformat(dt)
    except ValueError:
        pass

    try:
        # try if only time is given and prepend min. date
        return datetime.combine(datetime.min.date(), time.fromisoformat(dt))
    except ValueError:
        raise ValueError(f"could not convert {dt} to datetime")


def unstructure_timedelta(td: timedelta) -> str:
    """
    unstructure to isoformat <days>T<hours>:<minutes>:<seconds>
    """
    return f"{td.days}T{str(timedelta(seconds=td.seconds)):>08}"


def structure_timedelta(td_str: str, _: Type[timedelta] = timedelta) -> timedelta:
    """
    structure from <days>T<hours>:<minutes>:<seconds> isoformat or special pattern

        [<days>d][<hours>h][<minutes>m][<seconds>s]

    where each group is optional, but at least one must be given

    Examples:

        >>> structure_timedelta("2T02:30:00", timedelta)
        datetime.timedelta(days=2, seconds=9000)
        >>> structure_timedelta("1h", timedelta)
        datetime.timedelta(seconds=3600)
        >>> structure_timedelta("1d30m", timedelta)
        datetime.timedelta(days=1, seconds=1800)
    """
    td_match_groups = TIME_DELTA_REGEX.match(td_str).groups()
    if any(td_match_groups):
        (days, hours, minutes, seconds) = td_match_groups
        return timedelta(
            days=int(days or 0),
            hours=int(hours or 0),
            minutes=int(minutes or 0),
            seconds=int(seconds or 0),
        )

    try:
        d_str, t_str = td_str.split("T")
        days = int(d_str)
    except ValueError:
        t_str = td_str
        days = 0

    try:
        t = time.fromisoformat(t_str)
        return timedelta(days=days, hours=t.hour, minutes=t.minute, seconds=t.second)
    except ValueError:
        raise ValueError(f"could not convert '{td_str}' to timedelta")


def unstructure_date(d: date) -> str:
    """
    unstructure to isoformat YYYY-MM-DD
    """
    return d.isoformat()


def structure_date(date_str: str, _: Type[date] = date) -> date:
    """
    unstructure from isoformat YYYY-MM-DD or special form

      today|week-start|week-end[+/-DAYS]

    where week-start and week-end are the dates of the current week's MON and FRI respectively
    and the
    group [+/-DAYS] with DAYS an integer is optional.

    Examples:
             today: today
           today-1: yesterday
           today+2: the day after tomorrow
      week-start-7: last week's MON
        week-end-1: this week's THU
        week-end+3: next week's MON

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
