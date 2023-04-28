import os
import logging
from typing import Mapping, Tuple

from pycognaize.common.utils import directory_summary_hash
from pycognaize.login import Login
from pycognaize.common import utils
from pycognaize.common.enums import EnvConfigEnum, HASH_FILE
from pycognaize.common.exceptions import AuthenthicationError
from pycognaize.common.lazy_dict import LazyDocumentDict


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
    def get_by_id(cls, snapshot_id: str) -> 'Snapshot':
        """Returns the Snapshot Object"""
        login_instance = Login()
        if login_instance.logged_in:
            snapshot_dir = login_instance.snapshot_root
            snapshot_path = os.path.join(snapshot_dir, snapshot_id)
            return cls(path=snapshot_path)
        else:
            snapshot_dir = os.environ[EnvConfigEnum.SNAPSHOT_PATH.value]
            snapshot_id = os.environ[EnvConfigEnum.SNAPSHOT_ID.value]
            snapshot_path = os.path.join(snapshot_dir, snapshot_id)
            return cls(path=snapshot_path)

    @classmethod
    def download(cls, snapshot_id: str, destination_dir: str) -> \
            Tuple['Snapshot', str]:
        """Downloads snapshot to specified destination"""
        login_instance = Login()

        if login_instance.logged_in:
            snapshot_path = os.path.join(login_instance.snapshot_root,
                                         snapshot_id)
            ci = utils.cloud_interface_login(login_instance)
            ci.copy_dir(snapshot_path, destination_dir)

            summary_hash = directory_summary_hash(destination_dir)
            with open(os.path.join(destination_dir, HASH_FILE), 'w') as f:
                f.write(summary_hash)

            logging.info(f"Snapshot {snapshot_id} downloaded to "
                         f"{destination_dir}. To use the snapshot, check our "
                         f"documentation at: ",
                         "http://pycognaize-docs.com."
                         "s3-website.us-east-2.amazonaws.com")

            return cls(path=snapshot_path), \
                os.path.join(destination_dir, snapshot_id),
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
