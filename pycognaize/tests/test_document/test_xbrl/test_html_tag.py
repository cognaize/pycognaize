import json
import os
import unittest
from copy import deepcopy

from pycognaize.common.enums import IqFieldKeyEnum, XBRLCellEnum
from pycognaize.common.utils import empty_keys
from pycognaize.document.html_info import HTML
from pycognaize.document.tag.html_tag import HTMLTag, HTMLTableTag, HTMLCell
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

        self.html_tag_dict_1 = deepcopy(self.data['output_fields']['v_other_operating_expenses_operating_is__current']
                                        [0]['tags'][0])
        self.html_tag_dict_2 = deepcopy(self.data['output_fields']['v_other_operating_expenses_operating_is__previous']
                                        [0]['tags'][0])
        self.html_tag_dict_3 = deepcopy(self.data['output_fields']['v_other_operating_expenses_operating_is__tr'][0]
                                        ['tags'][0])
        self.html_tag_dict_4 = deepcopy(self.data['output_fields']['v_cash_at_bank_and_in_hand_bs__tr'][0]['tags'][0])
        # self.html_cell_dict1 = deepcopy(self.data['input_fields']["table"][0])

        self.html_tag_1 = HTMLTag.construct_from_raw(self.html_tag_dict_1, html=self.html)
        self.html_tag_2 = HTMLTag.construct_from_raw(self.html_tag_dict_2, html=self.html)
        self.html_tag_3 = HTMLTag.construct_from_raw(self.html_tag_dict_3, html=self.html)

        self.html_tag_4 = HTMLTag.construct_from_raw(self.html_tag_dict_4, html=self.html)

        self.cell = HTMLCell(
            row_index=2,
            col_index=1,
            col_span=2,
            row_span=1,
            html_id="68db2b0f-15c2-472d-bb7e-1a44cd804159",
            xpath="/html/body/div[1]/table/tr[1]/td[1]",
            raw_value="Three months",
            is_bold=True,
            left_indentation=None
        )

    def test_col_span(self):
        self.assertEqual(self.cell.col_span, 2)

    def test_row_span(self):
        self.assertEqual(self.cell.row_span, 1)

    def test_html_id(self):
        self.assertEqual(self.cell.html_id, "68db2b0f-15c2-472d-bb7e-1a44cd804159")

    def test_xpath(self):
        self.assertEqual(self.cell.xpath, "/html/body/div[1]/table/tr[1]/td[1]")

    def test_is_bold(self):
        self.assertTrue(self.cell.is_bold)

    def test_left_indentation(self):
        self.assertIsNone(self.cell.left_indentation)

    def test_value(self):
        self.assertEqual(self.tbl_tag.value, '')

    def test_ocr_value(self):
        self.assertEqual(self.tbl_tag.ocr_value, '')

    def test_html(self):
        self.assertTrue(isinstance(self.tbl_tag.html, HTML))

    def test_extract_value(self):
        self.assertEqual(HTMLTableTag._extract_value(self.html_tag_1), '6481')
        self.assertEqual(HTMLTableTag._extract_value(self.html_tag_2), '3689')
        self.assertEqual(HTMLTableTag._extract_value(self.html_tag_3), 'Operating costs')
        self.assertEqual(HTMLTableTag._extract_value(self.html_tag_4), 'Cash at bank')
        self.assertNotEqual(HTMLTableTag._extract_value(self.html_tag_4), 'Another sentence')

        # This case can work if we'll not have HTMLTag, because HTMLTag can't be created without raw_value
        self.assertEqual(HTMLTableTag._extract_value(None), '')

    def test_raw_value(self):
        self.assertEqual(self.html_tag_1.raw_value, '6481')
        self.assertEqual(self.html_tag_2.raw_value, '3689')
        self.assertEqual(self.html_tag_3.raw_value, 'Operating costs')
        self.assertEqual(self.html_tag_4.raw_value, 'Cash at bank')
        self.assertEqual(self.cell.raw_value, "Three months")

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
        self.assertEqual(self.cell.row_index, 2)

    def test_col_index(self):
        self.assertEqual(self.html_tag_1.col_index, 1)
        self.assertEqual(self.html_tag_2.col_index, 2)
        self.assertEqual(self.html_tag_3.col_index, 0)
        self.assertEqual(self.html_tag_4.col_index, -1)
        self.assertEqual(self.cell.col_index, 1)

    def test_is_table(self):
        self.assertFalse(self.html_tag_1.is_table)
        self.assertFalse(self.html_tag_2.is_table)
        self.assertFalse(self.html_tag_3.is_table)
        self.assertFalse(self.html_tag_4.is_table)
        self.assertTrue(self.tbl_tag.is_table)

    def test__row_index_with_table(self):
        raw_df = self.tbl_tag.raw_df
        self.assertEqual(raw_df[self.html_tag_1.col_index][self.html_tag_1.row_index].raw_value,
                         self.html_tag_1.raw_ocr_value)
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
        self.assertEqual(field_dict_1.keys(), self.html_tag_dict_1.keys())

        self.assertEqual(field_dict_1[XBRLCellEnum.source.value].keys(),
                         self.html_tag_dict_1[XBRLCellEnum.source.value].keys())

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

        self.assertEqual(self.cell.to_dict(),  {'1:2': {'colspan': 2,
                                                        'rowspan': 1,
                                                        'id': '68db2b0f-15c2-472d-bb7e-1a44cd804159',
                                                        'xpath': '/html/body/div[1]/table/tr[1]/td[1]',
                                                        'value':
                                                        'Three months',
                                                        'leftIndentation': None,
                                                        'isBold': True}})

    def test_df(self):
        self.assertEqual(self.tbl_tag.df.at[4, 1], '$6,481')


if __name__ == '__main__':
    unittest.main()
