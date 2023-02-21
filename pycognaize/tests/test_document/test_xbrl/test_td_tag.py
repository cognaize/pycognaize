import json
import os
import unittest
from copy import deepcopy

from pycognaize.common.enums import IqFieldKeyEnum, XBRLCellEnum
from pycognaize.common.utils import empty_keys

from pycognaize.document.html_info import HTML

from pycognaize.document.tag.html_tag import TDTag, HTMLTableTag
from pycognaize.tests.resources import RESOURCE_FOLDER

class TestTDTag(unittest.TestCase):

    # set expected constants
    SNAPSHOT_PATH = os.path.join(RESOURCE_FOLDER, 'xbrl_snapshot')
    SNAPSHOT_ID = '63fd387178232c6001119a41a'
    snap_storage_path = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.snap_storage_path = os.path.join(cls.SNAPSHOT_PATH,
                                             cls.SNAPSHOT_ID)

    def setUp(self) -> None:
        with open(self.snap_storage_path + '/document.json') as document_json:
            self.data = json.load(document_json)

        self.html = HTML(path=RESOURCE_FOLDER, document_id=self.SNAPSHOT_ID)

        table_field = deepcopy(self.data['input_fields']['table'][0])
        self.raw_tbl_tag = table_field[IqFieldKeyEnum.tags.value][0]
        self.tbl_tag = HTMLTableTag.construct_from_raw(self.raw_tbl_tag,
                                                       html=self.html)

        self.td_tag_dict_1 = deepcopy(self.data['output_fields']['v_other_operating_expenses_operating_is__current'][0]['tags'][0])
        self.td_tag_dict_2 = deepcopy(self.data['output_fields']['v_other_operating_expenses_operating_is__previous'][0]['tags'][0])
        self.td_tag_dict_3 = deepcopy(self.data['output_fields']['v_other_operating_expenses_operating_is__tr'][0]['tags'][0])

        self.td_tag_1 = TDTag.construct_from_raw(self.td_tag_dict_1, html=self.html)
        self.td_tag_2 = TDTag.construct_from_raw(self.td_tag_dict_2, html=self.html)
        self.td_tag_3 = TDTag.construct_from_raw(self.td_tag_dict_3, html=self.html)

    def test_raw_value(self):
        self.assertEqual(self.td_tag_1.raw_value, '6481')
        self.assertEqual(self.td_tag_2.raw_value, '3689')
        self.assertEqual(self.td_tag_3.raw_value, 'Operating costs')

    def test_raw_ocr_value(self):
        self.assertEqual(self.td_tag_1.raw_ocr_value, '$6,481')
        self.assertEqual(self.td_tag_2.raw_ocr_value, '$3,689')
        self.assertEqual(self.td_tag_3.raw_ocr_value, 'Operating costs')

    def test_row_index(self):
        self.assertEqual(self.td_tag_1.row_index, 4)
        self.assertEqual(self.td_tag_2.row_index, 4)
        self.assertEqual(self.td_tag_3.row_index, 4)

    def test_col_index(self):
        self.assertEqual(self.td_tag_1.col_index, 1)
        self.assertEqual(self.td_tag_2.col_index, 2)
        self.assertEqual(self.td_tag_3.col_index, 0)

    def test_is_table(self):
        self.assertFalse(self.td_tag_1.is_table)
        self.assertFalse(self.td_tag_2.is_table)
        self.assertFalse(self.td_tag_3.is_table)

    def test__row_index_with_table(self):
        raw_df = self.tbl_tag.raw_df
        self.assertEqual(raw_df[self.td_tag_1.col_index][self.td_tag_1.row_index].raw_value, self.td_tag_1.raw_ocr_value)
        self.assertEqual(
            raw_df[self.td_tag_2.col_index][self.td_tag_2.row_index].raw_value,
            self.td_tag_2.raw_ocr_value)
        self.assertEqual(
            raw_df[self.td_tag_3.col_index][self.td_tag_3.row_index].raw_value,
            self.td_tag_3.raw_ocr_value)

    def test__tag_id_matching_with_table_tag_id(self):
        raw_df = self.tbl_tag.raw_df
        self.assertEqual(raw_df[self.td_tag_1.col_index][self.td_tag_1.row_index].tag_id, self.td_tag_1.tag_id)
        self.assertEqual(raw_df[self.td_tag_2.col_index][self.td_tag_2.row_index].tag_id, self.td_tag_2.tag_id)
        self.assertEqual(raw_df[self.td_tag_3.col_index][self.td_tag_3.row_index].tag_id, self.td_tag_3.tag_id)

    def test__to_dict(self):
        field_dict_1 = self.td_tag_1.to_dict()
        self.assertEqual(field_dict_1.keys(), self.td_tag_dict_1.keys())

        self.assertEqual(field_dict_1[XBRLCellEnum.source.value].keys(), self.td_tag_dict_1[XBRLCellEnum.source.value].keys())

        cleaned_td_tag_dict_1 = empty_keys(obj=deepcopy(self.td_tag_dict_1), keys=['_id'])
        cleaned_field_dict_1 = empty_keys(obj=deepcopy(field_dict_1), keys=['_id'])
        self.assertDictEqual(cleaned_field_dict_1, cleaned_td_tag_dict_1)

        field_dict_2 = self.td_tag_2.to_dict()
        cleaned_td_tag_dict_2 = empty_keys(obj=deepcopy(self.td_tag_dict_2),
                                           keys=['_id'])
        cleaned_field_dict_2 = empty_keys(obj=deepcopy(field_dict_2),
                                        keys=['_id'])
        self.assertDictEqual(cleaned_field_dict_2, cleaned_td_tag_dict_2)

        field_dict_3 = self.td_tag_3.to_dict()
        cleaned_td_tag_dict_3 = empty_keys(obj=deepcopy(self.td_tag_dict_3),
                                           keys=['_id'])
        cleaned_field_dict_3 = empty_keys(obj=deepcopy(field_dict_3),
                                          keys=['_id'])
        self.assertDictEqual(cleaned_field_dict_3, cleaned_td_tag_dict_3)

if __name__ == '__main__':
    unittest.main()
