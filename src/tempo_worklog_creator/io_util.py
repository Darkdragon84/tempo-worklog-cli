from pathlib import Path
from typing import Any

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
