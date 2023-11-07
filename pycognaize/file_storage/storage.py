from abc import ABC, abstractmethod
from pathlib import Path
from typing import Iterable, Union

from cloudpathlib import CloudPath
from cloudpathlib.exceptions import InvalidPrefixError


def get_path_from_string(path: str) -> Path:
    try:
        return CloudPath(path)
    except InvalidPrefixError:
        return Path(path)


class Storage(ABC):
    @abstractmethod
    def is_dir(self, path: Union[str, Path]) -> bool:
        pass

    @abstractmethod
    def is_file(self, path: Union[str, Path]) -> bool:
        pass

    @abstractmethod
    def _list_dir(self, path: Union[str, Path]) -> Iterable[Path]:
        pass

    def list_dir(
            self,
            path: Union[str, Path],
            include_files=True,
            exclude_folders=True
    ) -> Iterable[Path]:
        if isinstance(path, str):
            path = get_path_from_string(path)

        if not path.is_dir():
            raise NotADirectoryError()

        for file_path in self._list_dir(path):
            if not include_files and file_path.is_file():
                continue
            if exclude_folders and file_path.is_dir():
                continue
            yield file_path

    @abstractmethod
    def open(self, path: Union[str, Path], *args, **kwargs):
        pass
