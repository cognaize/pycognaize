"""Defines LazyDocumentDict, used for lazy loading the documents
in the snapshot
"""
import logging
import os
from collections.abc import Mapping
from typing import Optional

from bson import json_util

from pycognaize.common.cloud_interface import get_cloud_interface
from pycognaize.common.enums import StorageEnum
from pycognaize.document import Document
from pycognaize.login import Login


class LazyDocumentDict(Mapping):
    """Contains documents included in the snapshot"""
    document_filename = StorageEnum.doc_file.value

    def __init__(self, doc_path: str,
                 data_path: str):
        self._login_instance = Login()
        self._doc_path = doc_path
        self._data_path = data_path
        ci = get_cloud_interface()
        self._ids = sorted([os.path.basename(os.path.dirname(i))
                            for i in ci.listdir(doc_path,
                                                include_files=False)
                            if ci.isfile(os.path.join(doc_path,
                                                      i, self.document_filename))])

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
        ci = get_cloud_interface()
        try:
            path = os.path.join(self.doc_path, doc_id,
                                f"{self.document_filename}")
            if ci.is_local_path(path):
                with open(path, 'r', encoding='utf8') as f:
                    doc_dict = json_util.loads(f.read())
            else:
                with ci.open(path, 'r') as f:
                    doc_dict = json_util.loads(f.read())
            return Document.from_dict(raw=doc_dict,
                                      data_path=os.path.join(self.data_path,
                                                             doc_id))
        except Exception as e:
            logging.error(f'Failed reading document {doc_id}: {e}')

    def __iter__(self):
        return iter(self._ids)

    def __len__(self):
        return len(self._ids)
