import json
import os
import unittest
from copy import deepcopy

from pycognaize.common.utils import empty_keys
from pycognaize.document.html_info import HTML

from pycognaize.common.enums import (IqFieldKeyEnum,
                                     IqTableTagEnum,
                                     IqTagKeyEnum)
from pycognaize.document.tag.html_tag import HTMLTableTag

from pycognaize.tests.resources import RESOURCE_FOLDER


class TestHTMLTableTag(unittest.TestCase):

    # set expected constants
    SNAPSHOT_PATH = os.path.join(RESOURCE_FOLDER, 'xbrl_snapshot')
    SNAPSHOT_ID = '63fd387178232c6001119a41a'
    snap_storage_path = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.snap_storage_path = os.path.join(cls.SNAPSHOT_PATH, cls.SNAPSHOT_ID)

    def setUp(self) -> None:
        with open(self.snap_storage_path + '/document.json') as document_json:
            self.data = json.load(document_json)

        table_field = deepcopy(self.data['input_fields']['table'][0])
        self.raw_tbl_tag = table_field[IqFieldKeyEnum.tags.value][0]

        self.html = HTML(path=RESOURCE_FOLDER, document_id=self.SNAPSHOT_ID)
        self.tbl_tag = HTMLTableTag.construct_from_raw(self.raw_tbl_tag,
                                                       html=self.html)

    def test_construct_from_raw(self):

        invalid_raw_table_tag = deepcopy(self.raw_tbl_tag)
        # pop table key
        invalid_raw_table_tag.pop("table")
        with self.assertRaises(KeyError):
            HTMLTableTag.construct_from_raw(invalid_raw_table_tag, self.html)

        invalid_raw_table_tag = deepcopy(self.raw_tbl_tag)
        # pop required key
        invalid_raw_table_tag["table"].pop('cells')
        with self.assertRaises(KeyError):
            HTMLTableTag.construct_from_raw(invalid_raw_table_tag, self.html)

        invalid_raw_table_tag = deepcopy(self.raw_tbl_tag)
        # pop required key
        invalid_raw_table_tag["table"]['cells']['2:1'].pop('value')
        with self.assertRaises(KeyError):
            HTMLTableTag.construct_from_raw(invalid_raw_table_tag, self.html)

        invalid_raw_table_tag = deepcopy(self.raw_tbl_tag)
        # change key separator
        invalid_raw_table_tag["table"]['cells']['4_1'] = \
        invalid_raw_table_tag["table"]['cells']['4:1']
        with self.assertRaises(IndexError):
            HTMLTableTag.construct_from_raw(invalid_raw_table_tag, self.html)

        invalid_raw_table_tag = deepcopy(self.raw_tbl_tag)
        # empty cells for testing build cells
        invalid_raw_table_tag["table"]['cells'] = {}
        with self.assertRaises(Exception):
            HTMLTableTag.construct_from_raw(invalid_raw_table_tag, self.html)

    def test_to_dict(self):
        ttd = self.tbl_tag.to_dict()
        self.assertIsInstance(ttd[IqTableTagEnum.table.value], dict)
        self.assertTrue(ttd[IqTagKeyEnum.is_table.value])
        self.assertIsInstance(
            ttd[IqTableTagEnum.table.value][IqTableTagEnum.cells.value], dict)
        self.assertEqual(
            ttd[IqTableTagEnum.table.value][IqTableTagEnum.cells.value]['3:5'][
                'value'], "$3,689")
        self.assertEqual(
            ttd[IqTableTagEnum.table.value][IqTableTagEnum.cells.value]['1:2'][
                'value'], '')
        self.assertEqual(
            ttd[IqTableTagEnum.table.value][IqTableTagEnum.cells.value][
                '4:1']['colspan'], 2)

        cleaned_ttd = empty_keys(deepcopy(ttd), keys=['_id'])
        cleaned_raw_ttd = empty_keys(deepcopy(self.raw_tbl_tag), keys=['_id'])
        self.assertDictEqual(cleaned_ttd, cleaned_raw_ttd)

    def test_cells(self):
        cells = self.tbl_tag.cells

        self.assertEqual(len(cells), 23)
        self.assertEqual(cells[2, 1].raw_value, "Three months")
        self.assertEqual(cells[2, 2].raw_value, "2023")
        self.assertEqual(cells[3, 4].raw_value, "(32654)")
        self.assertEqual(cells[5, 2].raw_value, "")

        self.assertEqual(cells[3, 3].html_id, ["ca93e995-162c-4422-8327-f4ce543a3be8"])
        self.assertEqual(cells[5, 3].xpath, "/html/body/div[1]/table/tr[3]/td[7]")

    def test_build_df(self):
        raw_df = self.tbl_tag._build_df()

        self.assertEqual(raw_df.shape, (5, 5))
        self.assertEqual(raw_df[1][1].raw_ocr_value, '2023')
        self.assertEqual(raw_df[2][1].html_id, ["ee6c660b-b270-4fef-ae4d-60fcf65b7c3a"])
        self.assertEqual(raw_df[2][1].row_index, 1)
        self.assertEqual(raw_df[2][1].col_index, 2)
        self.assertEqual(raw_df[2][0].raw_value, 'Three months')

    def test_df(self):
        df = self.tbl_tag.df

        self.assertEqual(df.shape, (5, 5))
        self.assertEqual(df[1][1], '2023')
        self.assertEqual(df[2][0], 'Three months')


if __name__ == '__main__':
    unittest.main()
