from pathlib import Path, _posix_flavour
import json
import yaml

from typing import Dict, Any


class JPath(Path):
    # What about windows? Good question ...
    _flavour = _posix_flavour

    def mkdir_maybe(self):  # type: ignore
        self.mkdir(parents=True, exist_ok=True)
        return self

    def read_json(self) -> Dict[str, Any]:
        with self.open() as f:
            out: Dict[str, Any] = json.load(f)
            return out

    def write_json(self, indict) -> None:
        with self.open("w") as f:
            json.dump(indict, f)

    def read_yaml(self) -> Dict[str, Any]:
        with self.open() as f:
            out: Dict[str, Any] = yaml.load(f)
            return out

    def __len__(self) -> int:
        return len(str(self))

    def glob_list(self, val):  # type: ignore
        return list(self.glob(val))

    @classmethod
    def from_home(cls, path):  # type: ignore
        return cls.home() / path

    @property
    def str(self) -> str:
        return str(self)

    def prepend_name(self, prefix: str):  # type: ignore
        return self.with_name(prefix + self.name)

    # def append_name(self, postfix: str):  # type: ignore
    #     return self.with_name(self. + postfix)