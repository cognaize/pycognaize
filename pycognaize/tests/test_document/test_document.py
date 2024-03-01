import json
import os
import shutil
import tempfile
import unittest
import uuid
from collections import OrderedDict
from copy import deepcopy

import bs4.element
import pandas as pd

import pycognaize
from pycognaize.common.enums import EnvConfigEnum, FieldTypeEnum
from pycognaize.document import Page, Document
from pycognaize.document.field.field import Field
from pycognaize.document.tag.html_tag import HTMLTag
from pycognaize.document.html_info import HTML
from pycognaize.tests.resources import RESOURCE_FOLDER


class TestDocument(unittest.TestCase):
    ORIGINAL_SNAPSHOT_PATH = os.environ.get(EnvConfigEnum.SNAPSHOT_PATH.value)
    SNAPSHOT_PATH = os.path.join(tempfile.gettempdir(), str(uuid.uuid4()))
    XBRL_SNAPSHOT_PATH = os.path.join(RESOURCE_FOLDER, 'snapshots')
    XBRL_SNAPSHOT_ID = '63dfb66b7861050010cd64b5'

    @classmethod
    def setUpClass(cls) -> None:
        os.environ[EnvConfigEnum.SNAPSHOT_PATH.value] = cls.SNAPSHOT_PATH

        cls.path = 'sample_folder_path'
        cls.snap_storage_path = os.path.join(cls.SNAPSHOT_PATH, cls.path)

        # load resource data
        with open(RESOURCE_FOLDER + '/snapshots/60f554497883ab0013d9d906/document.json', encoding="utf8") as document_json:
            cls.data = json.load(document_json)

        with open(RESOURCE_FOLDER + '/snapshots/5eb8ee1c6623f200192a0651/document.json', encoding="utf8") as document_json:
            cls.data2 = json.load(document_json)

        with open(os.path.join(cls.XBRL_SNAPSHOT_PATH, cls.XBRL_SNAPSHOT_ID, 'document.json')) as document_json:
            cls.data3 = json.load(document_json)

        cls.html = HTML(path=cls.XBRL_SNAPSHOT_PATH, document_id=cls.XBRL_SNAPSHOT_ID)

        cls.snap_path = os.path.join(cls.SNAPSHOT_PATH, 'sample_snapshot_1', str(cls.data['metadata']['document_id']))

        shutil.copytree(RESOURCE_FOLDER + '/snapshots/60f554497883ab0013d9d906/', cls.snap_path)

    def setUp(self) -> None:
        self.document = Document.from_dict(self.data, data_path=self.snap_path)
        self.xbrl_document = Document.from_dict(
            self.data3, data_path=os.path.join(self.XBRL_SNAPSHOT_PATH, self.XBRL_SNAPSHOT_ID)
        )
        self.Field = Field
        self.doc_src = self.data['metadata']['src']
        self.recipe_x = self.data['input_fields'].keys()
        self.recipe_y = self.data['output_fields'].keys()
        input_fields = next(iter(self.data2))
        table = next(iter(self.data2[input_fields]))
        self.data2[input_fields] = {
            table: self.data2[input_fields][table]
        }
        self.html_tag_dict = deepcopy(
            self.data3['output_fields']['v_lease_right_of_use_asset_bs__previous'][0]['tags'][0]
        )

        self.html_tag = HTMLTag.construct_from_raw(self.html_tag_dict, html=self.html)

        self.document2 = Document.from_dict(
            self.data2,
            data_path=RESOURCE_FOLDER + '/snapshots/5eb8ee1c6623f200192a0651')

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
        with self.assertRaises(TypeError):
            Document.from_dict(raw=[], data_path=self.snap_path)

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

    def test_get_tied_fields(self):
        tag = self.document.x['paragraph'][0].tags[0]
        table_tag = self.document2.x['table'][0].tags[0]
        tied_field_real = self.document.x['paragraph'][0]
        tied_field = list(self.document.get_tied_fields(tag).values())[0][0]
        first_tied_field = self.document.get_first_tied_field(tag)[1]
        first_tied_field_value = self.document.get_first_tied_field_value(tag)
        first_tied_field_fvalue = self.document.get_first_tied_field_value(
            tag=12.3)
        pname_tied_field = list(self.document.get_tied_fields(tag).items())[0]
        pname_tied_field = pname_tied_field[0], pname_tied_field[1][0]

        self.assertEqual(len(self.document.get_tied_fields(tag)), 2)
        self.assertEqual(len(self.document.get_tied_fields(
            tag, field_type=FieldTypeEnum.INPUT_FIELD.value)), 2)
        self.assertEqual(len(self.document.get_tied_fields(
            tag, field_type=FieldTypeEnum.INPUT_FIELD.value,
            pn_filter=lambda x: x == 'source_date')), 0)
        self.assertEqual(len(self.document.get_tied_fields(
            tag, field_type=FieldTypeEnum.OUTPUT_FIELD.value)), 0)
        with self.assertRaises(ValueError):
            self.document.get_tied_fields(
                tag, field_type='random_field_type')
        self.assertEqual(tied_field_real, tied_field)
        self.assertEqual(self.document.get_first_tied_field(tag),pname_tied_field)
        self.assertEqual(first_tied_field, tied_field_real)
        self.assertEqual(len(first_tied_field_value), 399)
        self.assertEqual(first_tied_field_fvalue, '')
        with self.assertRaises(AttributeError):
            self.document2.get_first_tied_field_value(table_tag)

    def test_get_tied_tags(self):
        # print(self.document.x['source_date'][0].tags[0])
        tag = self.document.x['paragraph'][0].tags[0]
        table_tag = self.document2.x['table'][0].tags[0]
        other_tag = self.document.x['ref'][0].tags[0]

        tied_tags = self.document.get_tied_tags(tag)
        self.assertEqual(len(tied_tags), 1)
        self.assertEqual(len(self.document.get_tied_tags(tag=tag, field_type=FieldTypeEnum.INPUT_FIELD.value)), 1)
        self.assertEqual(len(self.document.get_tied_tags(tag=tag, field_type=FieldTypeEnum.OUTPUT_FIELD.value)), 0)
        with self.assertRaises(ValueError):
            self.document.get_tied_tags(
                tag, field_type='random_field_type')
        self.assertEqual(len(self.document.get_tied_tags(
            tag, field_type=FieldTypeEnum.INPUT_FIELD.value,
            pn_filter=lambda x: x == 'source_date')), 0)
        tied_tags = list(self.document.get_tied_tags(
            tag, threshold=0.002).values())[0][0]
        self.assertEqual(tied_tags, tag)
        first_tied_tag = self.document.get_first_tied_tag(tag)[1]
        self.assertEqual(first_tied_tag, tag)
        first_tied_tag_value = self.document.get_first_tied_tag_value(tag)
        self.assertEqual(len(first_tied_tag_value), 399)
        with self.assertRaises(AttributeError):
            self.document2.get_first_tied_tag_value(table_tag)
        df_with_tied_field_values = (self.document2.
                                     get_df_with_tied_field_values(table_tag))
        self.assertIsInstance(df_with_tied_field_values, pd.DataFrame)

    def test_is_xbrl(self):
        is_xbrl = self.document.is_xbrl
        self.assertFalse(is_xbrl)

    def test_html(self):
        html = self.document.html
        self.assertIsInstance(html, pycognaize.document.html_info.HTML)

    def test_get_table_cell_overlap(self):
        snap_path = RESOURCE_FOLDER + '/snapshots/5eb8ee1c6623f200192a0651/document.json'
        with open(snap_path, encoding="utf8") as document_json:
            data = json.load(document_json)
        document = Document.from_dict(data, data_path=snap_path)

        self.assertFalse(document.get_table_cell_overlap(
            source_field='table', one_to_one=True))
        self.assertFalse(document.get_table_cell_overlap(
            source_field='table', one_to_one=False))
        self.assertEqual(len(document.get_table_cell_overlap(
            source_field='mmas_current_assets_v_1_4_1__'
                         'total_assets__current_value',
            one_to_one=True)), 1)
        self.assertEqual(len(document.get_table_cell_overlap(
            source_field='mmas_current_assets_v_1_4_1__'
                         'total_assets__current_value',
            one_to_one=False)), 2)
        self.assertFalse(document.get_table_cell_overlap(
            source_field='random_field',
            one_to_one=False))

    def test_load_page_images(self):
        self.assertIsNone(self.document.load_page_images())

    def test_find_html_elements(self):
        els = self.xbrl_document.find_html_elements(tag=self.html_tag)
        for e in els:
            self.assertIsInstance(e, bs4.element.Tag)

    @classmethod
    def tearDownClass(cls) -> None:

        shutil.rmtree(cls.SNAPSHOT_PATH)
        if cls.ORIGINAL_SNAPSHOT_PATH is not None:
            os.environ[EnvConfigEnum.SNAPSHOT_PATH.value] = cls.ORIGINAL_SNAPSHOT_PATH
        else:
            del os.environ[EnvConfigEnum.SNAPSHOT_PATH.value]
