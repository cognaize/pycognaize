import json
import os
import shutil
import tempfile
import unittest
import uuid
from copy import deepcopy
from typing import Dict

from bson import json_util

from pycognaize.common.enums import StorageEnum, EnvConfigEnum

from pycognaize.common.utils import load_bson_by_path
from pycognaize.common.exceptions import AuthenthicationError
from pycognaize.document.snapshot import Snapshot
from pycognaize.tests.resources import RESOURCE_FOLDER


class TestSnapshot(unittest.TestCase):

    @staticmethod
    def create_image_folder(images_folder_path):
        if os.path.exists(images_folder_path):
            shutil.rmtree(images_folder_path)
        shutil.copytree(os.path.join(RESOURCE_FOLDER, StorageEnum.image_folder.value), images_folder_path)

    @staticmethod
    def create_ocr_folder(ocr_folder_path):
        os.makedirs(ocr_folder_path, exist_ok=True)

        with open(os.path.join(RESOURCE_FOLDER, 'ocr.json'), 'r') as f:
            ocr_data = json.load(f)
        for page_ocr in ocr_data:
            page_n = page_ocr['page']['number']
            tmp_ocr_file = os.path.join(ocr_folder_path, f"page_{page_n}.json")
            with open(tmp_ocr_file, 'w') as f:
                json.dump(page_ocr, f)

    @staticmethod
    def create_document_json(document_dict: Dict, document_path: str):
        os.makedirs(os.path.dirname(document_path), exist_ok=True)
        with open(document_path, 'w') as f:
            f.write(json_util.dumps(document_dict))

    @classmethod
    def create_document(cls, document_dict: Dict, path: str):
        document_path = os.path.join(path, StorageEnum.doc_file.value)
        images_path = os.path.join(path, StorageEnum.image_folder.value)
        ocr_path = os.path.join(path, StorageEnum.ocr_folder.value)
        cls.create_document_json(document_dict=document_dict,
                                 document_path=document_path)
        cls.create_image_folder(images_folder_path=images_path)
        cls.create_ocr_folder(ocr_folder_path=ocr_path)

    @classmethod
    def setUpClass(cls) -> None:

        cls.ORIGINAL_SNAPSHOT_PATH = os.environ.get(EnvConfigEnum.SNAPSHOT_PATH.value)
        cls.SNAPSHOT_PATH = os.path.join(tempfile.gettempdir(), str(uuid.uuid4()))

        # load resource data
        cls.recipe_data = load_bson_by_path(os.path.join(RESOURCE_FOLDER, 'sample_recipe.bson'))
        cls.doc_data = load_bson_by_path(os.path.join(RESOURCE_FOLDER, 'snapshot_document.json'))

    def setUp(self) -> None:
        self.snapshot_id = 'sample_snapshot_1'
        os.environ[EnvConfigEnum.SNAPSHOT_PATH.value] = self.SNAPSHOT_PATH
        os.environ[EnvConfigEnum.SNAPSHOT_ID.value] = self.snapshot_id

        # local prepositioning
        doc_id = str(self.doc_data['metadata']['id'])
        self.snap_path = os.path.join(self.SNAPSHOT_PATH, self.snapshot_id)
        self.create_document(document_dict=self.doc_data,
                             path=os.path.join(self.snap_path, doc_id))
        self.doc_data_2 = deepcopy(self.doc_data)
        self.doc_data_2['metadata']['id'] = '5defa06ff91e70001dfdcb3a'
        self.snapshot = Snapshot.get()

    def test_documents(self):
        self.assertEqual(len(self.snapshot.documents), 1)

    def test_get(self):
        self.create_document(document_dict=self.doc_data_2,
                             path=os.path.join(self.snap_path,
                                               self.doc_data_2['metadata']['id']))
        snap = Snapshot.get()
        self.assertIsInstance(snap, Snapshot)
        self.assertEqual(len(snap.documents), 2)

        shutil.rmtree(os.path.join(self.SNAPSHOT_PATH, 'sample_snapshot_1'))

    def test_download(self):
        snapshot_id = '60cc8738efddad00005fc638'
        destination_dir = 's3://cognaize-elements/snapshots/'
        with self.assertRaises(AuthenthicationError):
            self.snapshot.download(snapshot_id, destination_dir)

    def test_get_by_id(self):
        snapshot_id = '61430b35d302800000303bd5'
        self.assertIsInstance(self.snapshot.get_by_id(snapshot_id), Snapshot)

    def tearDown(self) -> None:
        shutil.rmtree(self.SNAPSHOT_PATH)
        if self.ORIGINAL_SNAPSHOT_PATH is not None:
            os.environ[EnvConfigEnum.SNAPSHOT_PATH.value] = self.ORIGINAL_SNAPSHOT_PATH
        else:
            del os.environ[EnvConfigEnum.SNAPSHOT_PATH.value]
