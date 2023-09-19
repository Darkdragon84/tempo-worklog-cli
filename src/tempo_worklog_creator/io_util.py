from pathlib import Path
from typing import Union, Any

from cattrs import Converter
from ruamel.yaml import YAML

yaml = YAML(typ="safe")
yaml.default_flow_style = False  # disable flow style for consistent YAML format

converter = Converter(forbid_extra_keys=True)


class SaveLoad:
    def to_dict(self) -> dict[str, Any]:
        return converter.unstructure(self)

    @classmethod
    def from_dict(cls, dct: dict[str, Any]):
        return converter.structure(dct, cls)

    @classmethod
    def from_yaml(cls, filepath: Union[Path, str]):
        filepath = Path(filepath)
        with filepath.open("r") as file:
            return cls.from_dict(yaml.load(file))

    def to_yaml(self, filepath: Union[Path, str]):
        filepath = Path(filepath)
        with filepath.open("w") as file:
            yaml.dump(self.to_dict(), file)
