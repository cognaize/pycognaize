import os
from pathlib import Path
from typing import Iterable, Union

from pycognaize.file_storage.storage import Storage


class LocalStorage(Storage):
    def __init__(self, config=None):
        pass

    def is_dir(self, path: Union[str, Path]) -> bool:
        path = Path(path)
        return path.is_dir()

    def is_file(self, path: Union[str, Path]) -> bool:
        path = Path(path)
        return path.is_file()

    def _list_dir_recursive(self, path: Union[str, Path]) -> Iterable[Path]:
        for root, directories, files in os.walk(path):
            for file in files:
                yield Path(os.path.join(root, file))
            for directory in directories:
                yield Path(os.path.join(root, directory))

    def _list_dir(self, path: Union[str, Path]):
        path = Path(path)

        yield from path.iterdir()

    def open(self, path: Union[str, Path], *args, **kwargs):
        path = Path(path)
        return path.open(*args, **kwargs)
