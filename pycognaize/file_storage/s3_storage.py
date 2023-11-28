from pathlib import Path
from typing import Union, Iterable

from cloudpathlib import CloudPath, S3Client

from pycognaize.file_storage.storage import Storage


class S3Storage(Storage):

    def __init__(self, config=None):
        if config is not None:
            client = S3Client(
                aws_access_key_id=config['aws_access_key_id'],
                aws_session_token=config['aws_session_token'],
                aws_secret_access_key=config['aws_secret_access_key']
            )

            client.set_as_default_client()

    def is_dir(self, path: Union[str, Path]) -> bool:
        path = CloudPath(path)

        return path.is_dir()

    def is_file(self, path: Union[str, Path]) -> bool:
        path = CloudPath(path)

        return path.is_file()

    def _list_dir(self, path: Union[str, Path]) -> Iterable[Path]:
        path = CloudPath(path)

        yield from path.iterdir()

    def _list_dir_recursive(self, path: Union[str, Path]):
        path = CloudPath(path)

        yield from path.rglob('*')

    def open(self, path: Union[str, Path], *args, **kwargs):
        path = CloudPath(path)

        return path.open(*args, **kwargs)
