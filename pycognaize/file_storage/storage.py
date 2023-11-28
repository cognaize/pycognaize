from abc import ABC, abstractmethod
from pathlib import Path
from typing import Iterable, Union

from pycognaize.file_storage.path_type_checker \
    import (
        is_local_path,
        is_s3_path,
        get_path_from_string
    )


class Storage(ABC):

    @abstractmethod
    def __init__(self, config=None):
        pass

    @abstractmethod
    def is_dir(self, path: Union[str, Path]) -> bool:
        pass

    @abstractmethod
    def is_file(self, path: Union[str, Path]) -> bool:
        pass

    @abstractmethod
    def _list_dir(self, path: Union[str, Path]) -> Iterable[Path]:
        pass

    @abstractmethod
    def _list_dir_recursive(self, path: Union[str, Path]):
        pass

    def list_dir(
            self,
            path: Union[str, Path],
            recursive=False,
            include_files=True,
            exclude_folders=False
    ) -> Iterable[Path]:
        if isinstance(path, str):
            path = get_path_from_string(path)

        if not path.is_dir():
            raise NotADirectoryError()

        if recursive:
            list_dir = self._list_dir_recursive(path)
        else:
            list_dir = self._list_dir(path)

        for file_path in list_dir:
            if not include_files and file_path.is_file():
                continue
            if exclude_folders and file_path.is_dir():
                continue
            yield file_path

    @abstractmethod
    def open(self, path: Union[str, Path], *args, **kwargs):
        pass

    def is_local_path(self, path: Union[str, Path]) -> bool:
        return is_local_path(path)

    def is_s3_path(self, path: Union[str, Path]) -> bool:
        return is_s3_path(path)

    def get_path_from_string(self, path: str) -> Path:
        return get_path_from_string(path)
