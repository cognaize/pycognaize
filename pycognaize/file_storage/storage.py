from pathlib import Path
from typing import Iterable, Union

from cloudpathlib import AnyPath

from pycognaize.file_storage.path_type_checker import (
    get_path_from_string
)


class Storage:

    def __init__(self, *args, **kwargs):
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

    @staticmethod
    def is_s3_path(path: Union[str, Path]) -> bool:
        return str(path).startswith('s3://')

    @staticmethod
    def get_path_from_string(path: str) -> Path:
        return get_path_from_string(path)

    @staticmethod
    def is_dir(path: Union[str, Path]) -> bool:
        return AnyPath(path).is_dir()

    @staticmethod
    def is_file(path: Union[str, Path]) -> bool:
        return AnyPath(path).is_file()

    @staticmethod
    def _list_dir(path: Union[str, Path]) -> Iterable[Path]:
        yield from AnyPath(path).iterdir()

    @staticmethod
    def _list_dir_recursive(path: Union[str, Path]):
        yield from AnyPath(path).rglob('*')

    @staticmethod
    def open(path: Union[str, Path], *args, **kwargs):
        return AnyPath(path).open(*args, **kwargs)
