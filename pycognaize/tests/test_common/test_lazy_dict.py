import json
import os
import shutil
import tempfile
import unittest
import uuid

from pycognaize.common.enums import EnvConfigEnum
from pycognaize.common.lazy_dict import LazyDocumentDict
from pycognaize.document import Document
from pycognaize.tests.resources import RESOURCE_FOLDER


class TestLazyDict(unittest.TestCase):
    ORIGINAL_SNAPSHOT_PATH = os.environ.get(EnvConfigEnum.SNAPSHOT_PATH.value)
    SNAPSHOT_PATH = os.path.join(tempfile.gettempdir(), str(uuid.uuid4()))

    @classmethod
    def setUpClass(cls) -> None:
        os.environ[EnvConfigEnum.SNAPSHOT_PATH.value] = cls.SNAPSHOT_PATH

        cls.path = 'sample_folder_path'
        cls.snap_storage_path = os.path.join(cls.SNAPSHOT_PATH, cls.path)

        # load resource data
        with open(RESOURCE_FOLDER +
                  '/snapshots/60f554497883ab0013d9d906/document.json')as document_json:
            cls.data = json.load(document_json)
        cls.snap_path = os.path.join(cls.SNAPSHOT_PATH, 'sample_snapshot_1', str(cls.data['metadata']['document_id']))

        if os.path.exists(cls.snap_path):
            shutil.rmtree(cls.snap_path)
        shutil.copytree(RESOURCE_FOLDER + '/snapshots/', cls.snap_path)

    def setUp(self) -> None:
        self.document = Document.from_dict(self.data, data_path=self.snap_path)
        self.docs = LazyDocumentDict(doc_path=self.snap_path, data_path=self.snap_path)

    def test_doc_path(self):
        self.assertEqual(self.docs.doc_path, self.snap_path)

    def test_data_path(self):
        self.assertEqual(self.docs.data_path, self.snap_path)

    def test___getitem__(self):
        doc_from_getitem = self.docs.__getitem__(self.document.id)
        self.assertIsInstance(doc_from_getitem, Document)
        self.assertTrue(doc_from_getitem.id, self.document.id)

    def test___iter__(self):
        doc_list = sorted(
            ['60f554497883ab0013d9d906', '60b76b3d6f3f980019105dac',
             '60f53e967883ab0013d9c6f9', '60f5260c7883ab0013d9c184',
             '60215310dbf28200120e6afa', '62eb8e6b28d7ca0012ec8288'])
        for i, value in enumerate(self.docs):
            self.assertEqual(doc_list[i], value)

    def test___len__(self):
        self.assertEqual(self.docs.__len__(), 6)
