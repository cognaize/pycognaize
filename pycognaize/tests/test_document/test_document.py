import json
import os
import shutil
import tempfile
import unittest
import uuid
from collections import OrderedDict
from copy import deepcopy

from pycognaize.common.enums import EnvConfigEnum
from pycognaize.document import Page, Document
from pycognaize.document.field.field import Field
from pycognaize.tests.resources import RESOURCE_FOLDER


class TestDocument(unittest.TestCase):
    ORIGINAL_SNAPSHOT_PATH = os.environ.get(EnvConfigEnum.SNAPSHOT_PATH.value)
    SNAPSHOT_PATH = os.path.join(tempfile.gettempdir(), str(uuid.uuid4()))

    @classmethod
    def setUpClass(cls) -> None:
        os.environ[EnvConfigEnum.SNAPSHOT_PATH.value] = cls.SNAPSHOT_PATH

        cls.path = 'sample_folder_path'
        cls.snap_storage_path = os.path.join(cls.SNAPSHOT_PATH, cls.path)

        # load resource data
        with open(RESOURCE_FOLDER + '/snapshots/60f554497883ab0013d9d906/document.json') as document_json:
            cls.data = json.load(document_json)

        cls.snap_path = os.path.join(cls.SNAPSHOT_PATH, 'sample_snapshot_1', str(cls.data['metadata']['document_id']))

        shutil.copytree(RESOURCE_FOLDER + '/snapshots/60f554497883ab0013d9d906/', cls.snap_path)

    def setUp(self) -> None:
        self.document = Document.from_dict(self.data, data_path=self.snap_path)
        self.Field = Field
        self.doc_src = self.data['metadata']['src']
        self.recipe_x = self.data['input_fields'].keys()
        self.recipe_y = self.data['output_fields'].keys()

    def test_x(self):
        for k, v in self.document.x.items():
            self.assertIn(k, self.recipe_x)
            self.assertIsInstance(v, list)
            for i in v:
                self.assertIsInstance(i, self.Field)

    def test_y(self):
        for k, v in self.document.y.items():
            self.assertIn(k, self.recipe_y)
            self.assertIsInstance(v, list)
            for i in v:
                self.assertIsInstance(i, self.Field)

    def test_document_id(self):
        self.assertIsInstance(self.document.id, str)
        self.assertEqual(self.document.id, '60f554497883ab0013d9d906')

    def test_document_src(self):
        self.assertIsInstance(self.document.document_src, str)
        self.assertEqual(self.document.document_src, self.doc_src)

    def test_pages(self):
        pages = self.document.pages
        self.assertEqual(len(pages), 7)
        self.assertIsInstance(pages, dict)
        [self.assertIsInstance(p, Page) for p in pages.values()]

    def test_to_dict(self):
        result = self.document.to_dict()
        keys_list = [key for key in result.keys()]

        self.assertIsInstance(result, dict)
        self.assertIsInstance(result["input_fields"], dict)
        self.assertIsInstance(result["output_fields"], dict)
        # self.assertIsInstance(result["pages"], dict)
        self.assertIsInstance(result["metadata"], dict)
        self.assertListEqual(keys_list, ['input_fields', 'output_fields', 'metadata'])
        # self.assertEqual(len(keys_list), 4)
        self.assertCountEqual(keys_list, ["output_fields", "metadata", "input_fields"])
        # self.assertEqual(len(result["pages"]), len(self.data['pages']))
        self.assertEqual(result['metadata']['document_id'], "60f554497883ab0013d9d906")
        self.assertEqual(result['metadata']['src'], "6645954b30f92ce8b63b5dc1274ee829dcc322073d238955536ce497fc4149e3")
        self.assertIsInstance(result["input_fields"]["source_date"], list)
        self.assertEqual(result["input_fields"]['ref'][1]["groupKey"], "c154be31-5919-4176-a948-ce46912edfb4")
        self.assertEqual(result["input_fields"]["source_date"][0]["tags"][0]["ocrValue"], "12/12/2011")
        self.assertEqual(self.document.id, result['metadata']['document_id'])
        # self.assertDictEqual(result["pages"], OrderedDict({page_n: page.path
        #                      for page_n, page in self.document.pages.items()}))
        self.assertDictEqual(result["metadata"], OrderedDict(self.document.metadata))
        self.assertDictEqual(result["output_fields"], OrderedDict({name: [field.to_dict() for field in fields]
                                                                  for name, fields in self.document.y.items()}))

    def test_from_dict(self):
        document = Document.from_dict(self.data, data_path=self.snap_path)
        self.assertEqual(document.id, self.data['metadata']['document_id'])
        self.assertEqual(document.document_src, self.doc_src)
        self.assertEqual(len(self.document.pages), len(self.data['pages']))
        [self.assertIsInstance(p, Page) for p in document.pages.values()]
        [self.assertEqual(len(value), len(document.x[key])) for key, value in self.data['input_fields'].items()]
        [self.assertEqual(len(value), len(document.y[key])) for key, value in self.data['output_fields'].items()]

        invalid_document_dict = deepcopy(self.data)
        invalid_document_dict = invalid_document_dict.pop('metadata')
        with self.assertRaises(KeyError):
            Document.from_dict(invalid_document_dict, data_path=self.snap_path)

        invalid_document_dict = deepcopy(self.data)
        invalid_document_dict['metadata'] = None
        with self.assertRaises(TypeError):
            Document.from_dict(invalid_document_dict, data_path=self.snap_path)

        invalid_document_dict = deepcopy(self.data)
        invalid_document_dict['metadata'] = invalid_document_dict['metadata'].pop('src')
        with self.assertRaises(TypeError):
            Document.from_dict(invalid_document_dict, data_path=self.snap_path)

    def test_to_pdf(self):
        document = Document.from_dict(self.data, data_path=self.snap_path)
        input_fields = ['source_date', 'level', 'paragraph', 'ref']
        output_fields = []
        self.assertIsInstance(document.to_pdf(input_fields=input_fields, output_fields=output_fields), bytes)
        self.assertIsInstance(document.to_pdf(input_fields=[], output_fields=[]), bytes)

        invalid_input_fields = ['source_date', 'lvl', 'paragraph', 'ref']
        invalid_output_fields = ['invalid', 'output', 'fields']
        with self.assertRaises(ValueError):
            document.to_pdf(input_fields=invalid_input_fields)
        with self.assertRaises(ValueError):
            document.to_pdf(output_fields=invalid_output_fields)

        with self.assertRaises(ValueError):
            document.to_pdf(input_fields=input_fields, input_color='wrong_color')

        with self.assertRaises(ValueError):
            document.to_pdf(input_fields=input_fields, input_opacity=5)
        with self.assertRaises(TypeError):
            document.to_pdf(input_fields=input_fields, input_opacity='5')

    @classmethod
    def tearDownClass(cls) -> None:

        shutil.rmtree(cls.SNAPSHOT_PATH)
        if cls.ORIGINAL_SNAPSHOT_PATH is not None:
            os.environ[EnvConfigEnum.SNAPSHOT_PATH.value] = cls.ORIGINAL_SNAPSHOT_PATH
        else:
            del os.environ[EnvConfigEnum.SNAPSHOT_PATH.value]
