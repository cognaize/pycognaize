import json
import os
import unittest
from copy import deepcopy

from pycognaize.common.enums import IqFieldKeyEnum, XBRLCellEnum
from pycognaize.common.utils import empty_keys
from pycognaize.document.html_info import HTML
from pycognaize.document.tag.html_tag import HTMLTag, HTMLTableTag
from pycognaize.tests.resources import RESOURCE_FOLDER


class TestHTMLTag(unittest.TestCase):

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

        self.html_tag_dict_1 = deepcopy(self.data['output_fields']['v_other_operating_expenses_operating_is__current'][0]['tags'][0])
        self.html_tag_dict_2 = deepcopy(self.data['output_fields']['v_other_operating_expenses_operating_is__previous'][0]['tags'][0])
        self.html_tag_dict_3 = deepcopy(self.data['output_fields']['v_other_operating_expenses_operating_is__tr'][0]['tags'][0])
        self.html_tag_dict_4 = deepcopy(self.data['output_fields']['v_cash_at_bank_and_in_hand_bs__tr'][0]['tags'][0])
        self.html_tag_dict_5 = self.html_tag_dict_1["source"]

        self.html_tag_1 = HTMLTag.construct_from_raw(self.html_tag_dict_1, html=self.html)
        self.html_tag_2 = HTMLTag.construct_from_raw(self.html_tag_dict_2, html=self.html)
        self.html_tag_3 = HTMLTag.construct_from_raw(self.html_tag_dict_3, html=self.html)

        self.html_tag_4 = HTMLTag.construct_from_raw(self.html_tag_dict_4, html=self.html)
        # self.html_tag_5 = HTMLCell.construct_from_raw(self.html_tag_dict_5)

    # def test_construct_from_raw(self.html_tag_dict_5):
    #     source_data = self.html_tag_dict_5[XBRLCellEnum.source.value]

    def test_value(self):
        self.assertEqual(self.tbl_tag.value, '')

    def test_ocr_value(self):
        self.assertEqual(self.tbl_tag.ocr_value, '')

    def test_html(self):
        self.assertTrue(isinstance(self.tbl_tag.html, HTML))

    def test_raw_value(self):
        self.assertEqual(self.html_tag_1.raw_value, '6481')
        self.assertEqual(self.html_tag_2.raw_value, '3689')
        self.assertEqual(self.html_tag_3.raw_value, 'Operating costs')
        self.assertEqual(self.html_tag_4.raw_value, 'Cash at bank')

    def test_raw_ocr_value(self):
        self.assertEqual(self.html_tag_1.raw_ocr_value, '$6,481')
        self.assertEqual(self.html_tag_2.raw_ocr_value, '$3,689')
        self.assertEqual(self.html_tag_3.raw_ocr_value, 'Operating costs')
        self.assertEqual(self.html_tag_4.raw_ocr_value, 'Cash at bank')

    def test_row_index(self):
        self.assertEqual(self.html_tag_1.row_index, 4)
        self.assertEqual(self.html_tag_2.row_index, 4)
        self.assertEqual(self.html_tag_3.row_index, 4)
        self.assertEqual(self.html_tag_4.row_index, 0)

    def test_col_index(self):
        self.assertEqual(self.html_tag_1.col_index, 1)
        self.assertEqual(self.html_tag_2.col_index, 2)
        self.assertEqual(self.html_tag_3.col_index, 0)
        self.assertEqual(self.html_tag_4.col_index, -1)

    def test_is_table(self):
        self.assertFalse(self.html_tag_1.is_table)
        self.assertFalse(self.html_tag_2.is_table)
        self.assertFalse(self.html_tag_3.is_table)
        self.assertFalse(self.html_tag_4.is_table)
        self.assertTrue(self.tbl_tag.is_table)

    def test__row_index_with_table(self):
        raw_df = self.tbl_tag.raw_df
        self.assertEqual(raw_df[self.html_tag_1.col_index][self.html_tag_1.row_index].raw_value, self.html_tag_1.raw_ocr_value)
        self.assertEqual(
            raw_df[self.html_tag_2.col_index][self.html_tag_2.row_index].raw_value,
            self.html_tag_2.raw_ocr_value)
        self.assertEqual(
            raw_df[self.html_tag_3.col_index][self.html_tag_3.row_index].raw_value,
            self.html_tag_3.raw_ocr_value)

    def test__tag_id_matching_with_table_tag_id(self):
        raw_df = self.tbl_tag.raw_df
        self.assertEqual(raw_df[self.html_tag_1.col_index][self.html_tag_1.row_index].tag_id, self.html_tag_1.tag_id)
        self.assertEqual(raw_df[self.html_tag_2.col_index][self.html_tag_2.row_index].tag_id, self.html_tag_2.tag_id)
        self.assertEqual(raw_df[self.html_tag_3.col_index][self.html_tag_3.row_index].tag_id, self.html_tag_3.tag_id)

    def test__to_dict(self):
        field_dict_1 = self.html_tag_1.to_dict()
        # field_dict_1["colspan"] = 1
        # field_dict_1["rowspan"] = 2
        # field_dict_1["html_id"] = "63fd387178232c6001119a41a"
        self.assertEqual(field_dict_1.keys(), self.html_tag_dict_1.keys())

        self.assertEqual(field_dict_1[XBRLCellEnum.source.value].keys(), self.html_tag_dict_1[XBRLCellEnum.source.value].keys())

        cleaned_html_tag_dict_1 = empty_keys(obj=deepcopy(self.html_tag_dict_1), keys=['_id'])
        cleaned_field_dict_1 = empty_keys(obj=deepcopy(field_dict_1), keys=['_id'])
        self.assertDictEqual(cleaned_field_dict_1, cleaned_html_tag_dict_1)

        field_dict_2 = self.html_tag_2.to_dict()
        cleaned_html_tag_dict_2 = empty_keys(obj=deepcopy(self.html_tag_dict_2),
                                             keys=['_id'])
        cleaned_field_dict_2 = empty_keys(obj=deepcopy(field_dict_2),
                                          keys=['_id'])
        self.assertDictEqual(cleaned_field_dict_2, cleaned_html_tag_dict_2)

        field_dict_3 = self.html_tag_3.to_dict()
        cleaned_html_tag_dict_3 = empty_keys(obj=deepcopy(self.html_tag_dict_3),
                                             keys=['_id'])
        cleaned_field_dict_3 = empty_keys(obj=deepcopy(field_dict_3),
                                          keys=['_id'])
        self.assertDictEqual(cleaned_field_dict_3, cleaned_html_tag_dict_3)

        field_dict_4 = self.html_tag_4.to_dict()
        cleaned_html_tag_dict_4 = empty_keys(obj=deepcopy(self.html_tag_dict_4),
                                             keys=['_id'])
        cleaned_field_dict_4 = empty_keys(obj=deepcopy(field_dict_4),
                                          keys=['_id'])
        self.assertDictEqual(cleaned_field_dict_4, cleaned_html_tag_dict_4)

    def test_df(self):
        self.assertEqual(self.tbl_tag.df.at[4,1],'$6,481')

if __name__ == '__main__':
    unittest.main()
