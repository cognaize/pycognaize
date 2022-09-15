import json
import os
from typing import Mapping
from glob import glob

from pycognaize.common.enums import EnvConfigEnum
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
    def _snapshot_path(cls) -> str:
        """Identify and return the snapshot path"""
        AWS_credentials_files = glob("/tmp/cognaize_aws_access_*.json")
        if AWS_credentials_files:
            credentials_file = json.load(open(AWS_credentials_files[0]))
            set_credentials(credentials_file['credentials'])
            snapshot_dir = credentials_file['snapshotRoot']
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


def set_credentials(credentials):
    """Set AWS credentials as ENV variables"""
    os.environ['AWS_ACCESS_KEY'] = credentials['AccessKeyId']
    os.environ['AWS_SECRET_ACCESS_KEY'] = credentials['SecretAccessKey']
    os.environ['AWS_SESSION_TOKEN'] = credentials['SessionToken']
