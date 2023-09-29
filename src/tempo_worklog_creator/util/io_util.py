from datetime import date, datetime, timedelta, time
from pathlib import Path
from typing import Any, Type

from cattrs import Converter
from ruamel.yaml import YAML

yaml = YAML(typ="safe")
yaml.default_flow_style = False  # disable flow style for consistent YAML format

converter = Converter(forbid_extra_keys=True)


def load_yaml(filepath: Path | str) -> dict | list:
    filepath = Path(filepath)
    with filepath.open("r") as file:
        return yaml.load(file)


def save_yaml(obj, filepath: Path | str):
    filepath = Path(filepath)
    with filepath.open("w") as file:
        yaml.dump(obj, file)


class SaveLoad:
    def to_dict(self) -> dict[str, Any]:
        return converter.unstructure(self)

    @classmethod
    def from_dict(cls, dct: dict[str, Any]):
        return converter.structure(dct, cls)

    @classmethod
    def from_yaml(cls, filepath: Path | str):
        return cls.from_dict(load_yaml(filepath))

    def to_yaml(self, filepath: Path | str):
        save_yaml(self.to_dict(), filepath)


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


def structure_date(d_str: str, _: Type[date]) -> date:
    return date.fromisoformat(d_str)


converter.register_unstructure_hook(date, unstructure_date)
converter.register_unstructure_hook(datetime, unstructure_datetime)
converter.register_unstructure_hook(timedelta, unstructure_timedelta)

converter.register_structure_hook(date, structure_date)
converter.register_structure_hook(datetime, structure_datetime)
converter.register_structure_hook(timedelta, structure_timedelta)
