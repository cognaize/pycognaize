import json
import os
import shutil
import tempfile
import unittest
import uuid
from copy import deepcopy


from pycognaize.common.enums import StorageEnum, EnvConfigEnum, IqFieldKeyEnum, IqDocumentKeysEnum, ID
from pycognaize.document.field.table_field import TableField
from pycognaize.document.page import create_dummy_page
from pycognaize.document.tag import TableTag, ExtractionTag
from pycognaize.tests.resources import RESOURCE_FOLDER
from pycognaize.document.html_info import HTML
from pycognaize.document.tag.html_tag import HTMLTableTag
from pycognaize.document.page import Page


class TestTableField(unittest.TestCase):

    # set expected constants
    ORIGINAL_SNAPSHOT_PATH = os.environ.get(EnvConfigEnum.SNAPSHOT_PATH.value)
    SNAPSHOT_PATH = os.path.join(tempfile.gettempdir(), str(uuid.uuid4()))

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

    @classmethod
    def setUpClass(cls) -> None:

        # set expected constants
        cls.path = 'sample_folder_path'
        cls.snap_storage_path = os.path.join(cls.SNAPSHOT_PATH, cls.path)
        cls.images_folder_path = os.path.join(cls.snap_storage_path, StorageEnum.image_folder.value)
        cls.ocr_folder_path = os.path.join(cls.snap_storage_path, StorageEnum.ocr_folder.value)

        # set env variables
        os.environ[EnvConfigEnum.SNAPSHOT_PATH.value] = cls.SNAPSHOT_PATH

        cls.create_image_folder(cls.images_folder_path)
        cls.create_ocr_folder(cls.ocr_folder_path)

    def setUp(self):
        self.doc_id = '60b76b3d6f3f980019105dac'
        self.doc_id_2 = '646c8efb96bed200112575e8'
        table_key = 'table'

        with open(os.path.join(RESOURCE_FOLDER, 'snapshots', self.doc_id,
                               'document.json')) as document_json:
            self.data = json.load(document_json)

        # add groupKey value to test in test_to_dict
        self.data["input_fields"][table_key][0]['groupKey'] = 'test_group_key'
        self.raw_table_with_group_key = self.data['input_fields'][table_key][0]
        page_n = self.raw_table_with_group_key['tags'][0]['page']
        self.pages = {page_n: create_dummy_page(page_n=page_n,
                                                path=self.snap_storage_path)}

        self.html = HTML(path=os.path.join(RESOURCE_FOLDER, 'snapshots'),
                         document_id=self.doc_id_2)

        with open(os.path.join(RESOURCE_FOLDER, 'snapshots', self.doc_id_2,
                               'document.json')) as document_json:
            self.data = json.load(document_json)

        self.tbl_field = TableField.construct_from_raw(self.raw_table_with_group_key,
                                                       pages=self.pages)
        table_field = self.data['input_fields']['table'][0]
        self.raw_table_tag = table_field[IqFieldKeyEnum.tags.value][0]
        self.tbl_tag = HTMLTableTag.construct_from_raw(raw=self.raw_table_tag,
                                                       html=self.html)
        self.tbl_field_2 = TableField(name="", tag=self.tbl_tag)

        self.path = os.path.join(RESOURCE_FOLDER, 'snapshots', self.doc_id)
        self.ext_tag = ExtractionTag(left=11.1, right=13.1, top=10, bottom=13,
                                     page=Page(page_number=1,
                                               document_id='60b76b3d6f3f980019105dac',
                                               path=self.path),
                                     raw_value='04/14/2020',
                                     raw_ocr_value='04.14.2020')

    def test_get_table_title(self):
        title_1 = self.tbl_field_2.get_table_title(n_lines_above=15, margin=9)
        self.assertEqual(title_1, '\u200b (exact name of registrant as specified in its charter):usa truck inc.')
        title_2 = self.tbl_field.get_table_title(n_lines_above=15, margin=9)
        self.assertEqual(title_2, "")

    def test_get_table_title_from_pdf(self):
        self.title_3 = TableField._get_table_title_from_pdf(tag=self.ext_tag, n_lines_above=15, margin=9)
        # page_line = self.ext_tag.page.lines[0][0]["left"]
        # self.assertEqual(page_line, 0)
        self.assertEqual(self.title_3, "PXqCgvAxR liCnkCx GbCCuwYTzpXa kDGPWBMeg JK AI lfIpa dnN 8330 tFj PAO uac bSsrG lVjsII LmFpX CfzWC BTWzUXSe kJj oNdArPnsvK jkQdAkWA Nvr 2812 HFN DDXZs uEE 2624 gQS 9440")

    def test___repr__(self):
        self.assertEqual(repr(self.tbl_field),
                         f"<{self.tbl_field.__class__.__name__}:"
                         f" {self.raw_table_with_group_key[IqFieldKeyEnum.name.value]}>")

    def test___str__(self):
        self.assertEqual(str(self.tbl_field),
                         f"<{self.tbl_field.__class__.__name__}:"
                         f" {self.raw_table_with_group_key[IqFieldKeyEnum.name.value]}>")

    def test_construct_from_raw(self):
        self.assertEqual(self.tbl_field.name, "table")
        self.assertIsInstance(self.tbl_field.tags[0], TableTag)
        self.assertAlmostEqual(self.tbl_field.tags[0].bottom, 64.0998)

        invalid_table_tag = deepcopy(self.raw_table_with_group_key)
        # pop tags key
        invalid_table_tag.pop(IqDocumentKeysEnum.tags.value)
        with self.assertRaises(KeyError):
            TableField.construct_from_raw(invalid_table_tag, self.pages)

        invalid_table_tag = deepcopy(self.raw_table_with_group_key)
        # two tags
        invalid_table_tag[IqDocumentKeysEnum.tags.value].append(invalid_table_tag[IqDocumentKeysEnum.tags.value][0])
        with self.assertRaises(ValueError):
            TableField.construct_from_raw(invalid_table_tag, self.pages)

        with open(RESOURCE_FOLDER + '/xbrl_snapshot/63fd387178232c6001119a41a/document.json') as document_json:
            self.data_with_group_key = json.load(document_json)

        self.raw_tbl_field = self.data_with_group_key["input_fields"]["table"][0]
        self.raw_tbl_field = TableField.construct_from_raw(raw=self.raw_tbl_field, pages=None, html=self.html)

        # wrong page number
        # with self.assertRaises(KeyError):
        #     TableField.construct_from_raw(self.raw_table_with_group_key,
        #                                   {2: create_dummy_page(page_n=2, path=self.snap_storage_path)})

    def test_to_dict(self):
        res_dict = self.tbl_field.to_dict()

        to_dict_keys = [IqFieldKeyEnum.name.value, IqFieldKeyEnum.data_type.value, ID,
                        IqFieldKeyEnum.tags.value, IqFieldKeyEnum.group_key.value,
                        IqFieldKeyEnum.value.value
                        ]

        raw_table_field = deepcopy(self.raw_table_with_group_key)

        self.assertIsInstance(res_dict[IqFieldKeyEnum.tags.value][0], dict)
        self.assertEqual(sorted(res_dict.keys()), sorted(to_dict_keys))

        for key in res_dict:
            if key in [IqFieldKeyEnum.name.value, IqFieldKeyEnum.data_type.value]:
                self.assertEqual(res_dict[key], raw_table_field[key])

        self.assertEqual(res_dict[ID], str(raw_table_field[ID]))

    def test_group_key(self):
        self.tbl_field.group_key = 'abc123'
        self.assertEqual(self.tbl_field.group_key, 'abc123')

        self.tbl_field.group_key = 'ABCDEF'
        self.assertEqual(self.tbl_field.group_key, 'ABCDEF')

        with self.assertRaises(TypeError):
            self.tbl_field.group_key = 1
        with self.assertRaises(TypeError):
            self.tbl_field.group_key = True
        with self.assertRaises(TypeError):
            self.tbl_field.group_key = ['abc']

    @classmethod
    def tearDownClass(cls) -> None:

        shutil.rmtree(cls.SNAPSHOT_PATH)
        if cls.ORIGINAL_SNAPSHOT_PATH is not None:
            os.environ[EnvConfigEnum.SNAPSHOT_PATH.value] = cls.ORIGINAL_SNAPSHOT_PATH
        else:
            del os.environ[EnvConfigEnum.SNAPSHOT_PATH.value]
