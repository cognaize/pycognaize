import json
import os
import unittest
from copy import deepcopy

from pycognaize.common.enums import (
    IqFieldKeyEnum, XBRLCellEnum, XBRLTableTagEnum
)
from pycognaize.document.html_info import HTML
from pycognaize.document.tag.html_tag import HTMLCell
from pycognaize.tests.resources import RESOURCE_FOLDER


class TestHTMLCell(unittest.TestCase):
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

        table_field = deepcopy(self.data['input_fields']['table'][0])
        self.raw_tbl_tag = table_field[IqFieldKeyEnum.tags.value][0]
        self.raw = table_field[IqFieldKeyEnum.tags.value][0]
        table_raw_data = self.raw[XBRLTableTagEnum.table.value]
        cell_data = table_raw_data[XBRLTableTagEnum.cells.value]
        cell_dict = cell_data["1:1"]
        self.html_cell = HTMLCell(html_id=cell_dict[XBRLCellEnum.id.value],
                                  xpath=cell_dict[XBRLCellEnum.xpath.value],
                                  row_index=1,
                                  col_index=1,
                                  col_span=cell_dict[
                                      XBRLCellEnum.col_span.value],
                                  row_span=cell_dict[
                                      XBRLCellEnum.row_span.value],
                                  raw_value=cell_dict[
                                      XBRLCellEnum.raw_value.value],
                                  is_bold=False,
                                  left_indentation=cell_dict[
                                      XBRLCellEnum.left_indentation.value])

    def test_row_index(self):
        self.assertEqual(self.html_cell.row_index, 1)

    def test_col_index(self):
        self.assertEqual(self.html_cell.col_index, 1)

    def test_col_span(self):
        self.assertEqual(self.html_cell.col_span, 1)

    def test_row_span(self):
        self.assertEqual(self.html_cell.row_span, 1)

    def test_html_id(self):
        self.assertEqual(self.html_cell.html_id,
                         ["20a65cb6-01cb-40c1-8bdf-25771dc59f72"])

    def test_xpath(self):
        self.assertEqual(self.html_cell.xpath,
                         "/html/body/div[1]/table/tr[1]/td[0]")

    def test_raw_value(self):
        self.assertEqual(self.html_cell.raw_value, "")

    def test_is_bold(self):
        self.assertFalse(self.html_cell.is_bold)

    def test_left_indentation(self):
        self.assertEqual(self.html_cell.left_indentation, "0")

    def test_construct_from_raw(self):
        ...
        # html_cell_from_raw = self.html_cell.construct_from_raw(self.raw)

        # self.assertEqual(html_cell_from_raw.row_index, 1)
        # self.assertEqual(html_cell_from_raw.col_index, 1)
        # self.assertEqual(html_cell_from_raw.col_span, 1)
        # self.assertEqual(html_cell_from_raw.row_span, 1)
        # self.assertEqual(html_cell_from_raw.html_id, ["20a65cb6-01cb-40c1-8bdf-25771dc59f72"])
        # self.assertEqual(html_cell_from_raw.xpath, "/html/body/div[1]/table/tr[1]/td[0]")
        # self.assertEqual(html_cell_from_raw.raw_value, "")
        # self.assertFalse(html_cell_from_raw.is_bold)
        # self.assertEqual(html_cell_from_raw.left_indentation, "0")

    def test_to_dict(self):
        cell_dict = self.html_cell.to_dict()

        self.assertEqual(len(cell_dict), 1)
        self.assertEqual(cell_dict["1:1"]["value"], "")
        self.assertEqual(cell_dict["1:1"]["id"],
                         ['20a65cb6-01cb-40c1-8bdf-25771dc59f72'])
        self.assertEqual(cell_dict["1:1"]["xpath"],
                         "/html/body/div[1]/table/tr[1]/td[0]")


if __name__ == '__main__':
    unittest.main()
