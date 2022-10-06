import os
from typing import Mapping

from pycognaize.common import utils
from pycognaize.common.enums import EnvConfigEnum
from pycognaize.common.lazy_dict import LazyDocumentDict
from pycognaize.login import Login


class Snapshot:
    """A snapshot of annotated documents from one or more collections"""

    def __init__(self, path: str):
        self._path = path
        self._documents = LazyDocumentDict(doc_path=path, data_path=path)

    @property
    def documents(self) -> Mapping:
        """Mapping of document ids to documents
        :return Mapping:  LazyDocumentDict Object
        """
        return self._documents

    @staticmethod
    def download(destination_dir: str):
        """Downloads snapshot to specified destination"""
        login_instance = Login()
        snapshot_dir = login_instance.snapshot_root
        snapshot_id = os.environ[EnvConfigEnum.SNAPSHOT_ID.value]
        snapshot_path = os.path.join(snapshot_dir, snapshot_id)

        ci = utils.cloud_interface_login(login_instance)
        ci.copy_dir(snapshot_path, destination_dir)

    @classmethod
    def _snapshot_path(cls, remote_snapshot_root: str = None) -> str:
        """Identify and return the snapshot path"""
        if remote_snapshot_root:
            snapshot_dir = remote_snapshot_root
            snapshot_id = os.environ[EnvConfigEnum.SNAPSHOT_ID.value]
            snapshot_path = os.path.join(snapshot_dir, snapshot_id)
        else:
            snapshot_dir = os.environ[EnvConfigEnum.SNAPSHOT_PATH.value]
            snapshot_id = os.environ[EnvConfigEnum.SNAPSHOT_ID.value]
            snapshot_path = os.path.join(snapshot_dir, snapshot_id)
        return snapshot_path

    @classmethod
    def get(cls) -> 'Snapshot':
        """Read the snapshot object from local storage and return it"""
        login_instance = Login()
        if login_instance.logged_in:
            remote_snapshot_root = login_instance.snapshot_root
            return cls(path=cls._snapshot_path(
                       remote_snapshot_root=remote_snapshot_root))

        else:
            return cls(path=cls._snapshot_path())
