import json
import os
import shutil
import tempfile
import unittest
import uuid
from collections import defaultdict

from pycognaize.common.enums import EnvConfigEnum
from pycognaize.common.lazy_group_dict import LazyGroupDict
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
                  '/snapshots/62eb8e6b28d7ca0012ec8288/document.json')as document_json:
            cls.data = json.load(document_json)
        cls.snap_path = os.path.join(cls.SNAPSHOT_PATH, 'sample_snapshot_1', str(cls.data['metadata']['document_id']))

        if os.path.exists(cls.snap_path):
            shutil.rmtree(cls.snap_path)
        shutil.copytree(RESOURCE_FOLDER + '/snapshots/', cls.snap_path)

    def setUp(self) -> None:
        self.document = Document.from_dict(self.data, data_path=self.snap_path)
        self.groups = LazyGroupDict(self.document.y)

    def get_group(self, group_name: str) -> dict:
        """Get fields from document that the give group name"""
        groups = defaultdict(list)
        group_name = group_name
        for field_name in self.document.y.keys():
            for item in self.document.y[field_name]:
                if item.group_name == group_name:
                    groups[item.group_key].append(item)
        return groups

    def test_create_groups(self):
        # Test create groups by name
        total_assets = self.get_group('Total Assets')
        self.assertDictEqual(self.groups.groups['Total Assets'], total_assets)
        self.assertEqual(len(self.groups.groups['Total Assets']), 1)
        # Check Structure
        self.assertIsInstance(self.groups.groups, defaultdict)
        # Test create groups by name empty input
        with self.assertRaises(KeyError):
            self.assertEqual(self.groups[''], {})
        with self.assertRaises(KeyError):
            self.assertEqual(self.groups['Non-Existent Group'], {})
