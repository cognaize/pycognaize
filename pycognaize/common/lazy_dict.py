"""Defines LazyDocumentDict, used for lazy loading the documents
in the snapshot
"""
import logging
import os
from collections.abc import Mapping
from typing import Optional

from bson import json_util

from pycognaize.common.enums import StorageEnum
from pycognaize.common.utils import join_path
from pycognaize.document import Document
from pycognaize.file_storage import get_storage
from pycognaize.login import Login


class LazyDocumentDict(Mapping):
    """Contains documents included in the snapshot"""
    document_filename = StorageEnum.doc_file.value

    def __init__(self, doc_path: str,
                 data_path: str):
        login_instance = Login()

        if login_instance.logged_in:
            self._storage_config = {
                'aws_access_key_id': login_instance.aws_access_key,
                'aws_session_token': login_instance.aws_session_token,
                'aws_secret_access_key': login_instance.aws_secret_access_key
            }

        else:
            self._storage_config = None

        self._doc_path = doc_path
        self._data_path = data_path
        storage = get_storage(self._doc_path, config=self._storage_config)

        ids = []

        for directory in storage.list_dir(doc_path, include_files=False):
            if storage.is_file(directory / self.document_filename):
                ids.append(directory.name)

        self._ids = sorted(ids)

    @property
    def doc_path(self) -> str:
        """Path of the document's JSON"""
        return self._doc_path

    @property
    def data_path(self) -> str:
        """Path of the document's OCR and page images"""
        return self._data_path

    def __getitem__(self, doc_id) -> Optional[Document]:
        """The Document object, retrieved from provided path

        Note: Path can be both local and remote
        """

        storage = get_storage(self.doc_path, config=self._storage_config)
        path = join_path(
            storage.is_s3_path(self.doc_path),
            self.doc_path,
            doc_id,
            f"{self.document_filename}"
        )
        try:
            with storage.open(path, 'r', encoding='utf8') as f:
                doc_dict = json_util.loads(f.read())
            return Document.from_dict(raw=doc_dict,
                                      data_path=os.path.join(self.data_path,
                                                             doc_id))
        except FileNotFoundError:
            logging.error(f'Document at path {path} is not found.')
        except Exception as e:
            logging.error(f'Failed reading document {doc_id}: {e}')

    def __iter__(self):
        return iter(self._ids)

    def __len__(self):
        return len(self._ids)
