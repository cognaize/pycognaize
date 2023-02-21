import os
from typing import Mapping

from pycognaize.common import utils
from pycognaize.common.exceptions import AuthenthicationError
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

    @classmethod
    def download(cls, snapshot_id: str, destination_dir: str):
        """Downloads snapshot to specified destination"""
        login_instance = Login()

        if login_instance.logged_in:
            snapshot_path = os.path.join(login_instance.snapshot_root,
                                         snapshot_id)
            ci = utils.cloud_interface_login(login_instance)
            ci.copy_dir(snapshot_path, destination_dir)
        else:
            raise AuthenthicationError()

    @classmethod
    def _snapshot_path(cls) -> str:
        """Identify and return the snapshot path"""
        login_instance = Login()
        if login_instance.logged_in:
            snapshot_dir = login_instance.snapshot_root
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
        return cls(path=cls._snapshot_path())
