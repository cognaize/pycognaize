import logging
import os
from typing import Mapping, Tuple

from pycognaize.common.enums import EnvConfigEnum, HASH_FILE
from pycognaize.common.exceptions import AuthenthicationError
from pycognaize.common.lazy_dict import LazyDocumentDict
from pycognaize.common.utils import directory_summary_hash
from pycognaize.document.snapshot_downloader import SnapshotDownloader
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
    def get_by_id(cls, snapshot_id: str) -> 'Snapshot':
        """Returns the Snapshot Object"""
        login_instance = Login()
        if login_instance.logged_in:
            snapshot_dir = login_instance.snapshot_root
            snapshot_path = snapshot_dir + "/" + snapshot_id
            return cls(path=snapshot_path)
        else:
            snapshot_dir = os.environ[EnvConfigEnum.SNAPSHOT_PATH.value]
            snapshot_id = os.environ[EnvConfigEnum.SNAPSHOT_ID.value]
            snapshot_path = os.path.join(snapshot_dir, snapshot_id)
            return cls(path=snapshot_path)

    @classmethod
    def download(cls, snapshot_id: str, destination_dir: str,
                 exclude_images: bool = False,
                 exclude_ocr: bool = False,
                 exclude_pdf: bool = False,
                 exclude_html: bool = False,
                 require_login: bool = True,
                 snapshot_root: str = None
                 ) -> Tuple['Snapshot', str]:
        """Downloads snapshot to specified destination"""
        if require_login:
            if snapshot_root is not None:
                raise ValueError("If the require_login is True, "
                                 "snapshot_root should not be"
                                 " provided")
            login_instance = Login()
            if not login_instance.logged_in:
                raise AuthenthicationError()
            snapshot_path = login_instance.snapshot_root + "/" + snapshot_id
        else:
            if snapshot_root is None:
                raise ValueError("If require_login is False, "
                                 "snapshot_root` should be "
                                 "provided")
            snapshot_path = snapshot_root + "/" + snapshot_id
        exclude = cls._get_exclude_patterns(
            exclude_images=exclude_images,
            exclude_ocr=exclude_ocr,
            exclude_pdf=exclude_pdf,
            exclude_html=exclude_html
        )
        downloader = SnapshotDownloader()
        downloader.download(snapshot_path, destination_dir, exclude)
        summary_hash = directory_summary_hash(destination_dir)
        with open(os.path.join(destination_dir, HASH_FILE), 'w') as f:
            f.write(summary_hash)
        logging.info(f"Snapshot {snapshot_id} downloaded to "
                     f"{destination_dir}. To use the snapshot, check our "
                     f"documentation at: "
                     "http://pycognaize-docs.com."
                     "s3-website.us-east-2.amazonaws.com")

        return cls(path=snapshot_path), \
            os.path.join(destination_dir, snapshot_id)

    @classmethod
    def _snapshot_path(cls) -> str:
        """Identify and return the snapshot path"""
        login_instance = Login()
        if login_instance.logged_in:
            snapshot_dir = login_instance.snapshot_root
            snapshot_id = os.environ[EnvConfigEnum.SNAPSHOT_ID.value]
            snapshot_path = snapshot_dir + "/" + snapshot_id
        else:
            snapshot_dir = os.environ[EnvConfigEnum.SNAPSHOT_PATH.value]
            snapshot_id = os.environ[EnvConfigEnum.SNAPSHOT_ID.value]
            snapshot_path = os.path.join(snapshot_dir, snapshot_id)
        return snapshot_path

    @classmethod
    def _get_exclude_patterns(
            cls,
            exclude_images,
            exclude_ocr,
            exclude_pdf,
            exclude_html
    ):
        exclude = []

        if exclude_images:
            exclude.append('*/images/*.jpeg')

        if exclude_ocr:
            exclude.append('*/data/*.json')

        if exclude_pdf:
            exclude.append('*.pdf')

        if exclude_html:
            exclude.append('*.html')

        return exclude

    @classmethod
    def get(cls) -> 'Snapshot':
        """Read the snapshot object from local storage and return it"""
        return cls(path=cls._snapshot_path())
