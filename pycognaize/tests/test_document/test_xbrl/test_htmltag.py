import unittest

import pandas as pd

from pycognaize.common.enums import XBRLTableTagEnum, XBRLCellEnum, IqDataTypesEnum, XBRLTagEnum, ID, IqRecipeEnum
from pycognaize.document.html_info import HTML
from pycognaize.document.tag.html_tag import HTMLTableTag, HTMLCell, HTMLTag, TDTag


class TestHTMLTag(unittest.TestCase):

    def setUp(self):
        self.html_id = ['html_id']
        self.xpath = 'xpath'
        self.tag_id = ''
        self.html_tag = HTMLTag(html_id=self.html_id, xpath=self.xpath)

    def test__html_id(self):
        self.assertEqual(self.html_tag.html_id, self.html_id)

    def test__xpath(self):
        self.assertEqual(self.html_tag.xpath, self.xpath)

    def test__construct_from_raw(self):
        raw = {IqDataTypesEnum.table.value: {XBRLTagEnum.anchor_id.value: self.html_id,
                                             XBRLTagEnum.xpath.value: self.xpath,
                                             XBRLTagEnum.tag_id.value: self.tag_id}}
        html = HTML(self.xpath)
        html_tag = HTMLTag.construct_from_raw(raw=raw, html=html)
        self.assertIsInstance(html_tag, HTMLTag)
        self.assertEqual(html_tag.html_id, self.html_id)
        self.assertEqual(html_tag.xpath, self.xpath)


class TestHTMLTableTag(unittest.TestCase):
    def setUp(self):
        self.tag_id = 'test tabletag _id'
        self.ocr_value = ''
        self.value = ''
        self.is_table = True
        self.xpath = '/html/body/table[1]'
        self.title = 'Test Table'
        self.html_id = ['table_1']
        self.source_ids = []
        self.cell_data = {
            '1:1': {
                XBRLCellEnum.id.value: 'cell_1', XBRLCellEnum.xpath.value: '/html/body/table[1]/tr[1]/td[1]',
                XBRLCellEnum.row_index.value: 1, XBRLCellEnum.col_index.value: 1,
                XBRLCellEnum.col_span.value: 1, XBRLCellEnum.row_span.value: 1,
                XBRLCellEnum.raw_value.value: 'Cell 1', XBRLCellEnum.is_bold.value: False,
                XBRLCellEnum.left_indentation.value: None},
            '1:2': {
                XBRLCellEnum.id.value: 'cell_2', XBRLCellEnum.xpath.value: '/html/body/table[1]/tr[1]/td[2]',
                XBRLCellEnum.row_index.value: 1, XBRLCellEnum.col_index.value: 2,
                XBRLCellEnum.col_span.value: 1, XBRLCellEnum.row_span.value: 1,
                XBRLCellEnum.raw_value.value: 'Cell 2', XBRLCellEnum.is_bold.value: True,
                XBRLCellEnum.left_indentation.value: 2}}

        self.html = HTML(self.xpath)
        self.table = HTMLTableTag(self.tag_id, self.ocr_value, self.value, self.xpath, self.title, self.html_id,
                                  self.cell_data, self.html, self.source_ids)

    def test__title(self):
        self.assertEqual(self.table.title, self.title)

    def test__cell_data(self):
        self.assertDictEqual(self.table.cell_data, self.cell_data)

    def test__cells(self):
        cells = self.table.cells
        self.assertIsInstance(cells[(1, 1)], HTMLCell)
        self.assertEqual(cells[(1, 1)].raw_value, 'Cell 1')
        self.assertEqual(cells[(1, 2)].raw_value, 'Cell 2')
        self.assertEqual(cells[(1, 2)].is_bold, True)

    def test__df(self):
        self.assertIsInstance(self.table.df, pd.DataFrame)

    def test__populate_cells(self):
        self.table._populate_cells()
        self.assertEqual(len(self.table.cells), 2)
        self.assertIsInstance(self.table.cells[(1, 1)], HTMLCell)
        self.assertEqual(self.table.cells[(1, 1)].is_bold, False)

    def test__construct_from_raw(self):
        raw = {XBRLTableTagEnum._id.value: 'test tabletag _id',
               XBRLTableTagEnum.source.value: 'ids: []',
               XBRLTableTagEnum.ocr_value.value: '',
               XBRLTableTagEnum.value.value: '',
               XBRLTableTagEnum.table.value: {
                   XBRLTableTagEnum.xpath.value: "/path/to/table",
                   XBRLTableTagEnum.title.value: "Table Title",
                   XBRLTableTagEnum.anchor_id.value: "table-1",
                   XBRLTableTagEnum.cells.value: {"1:1": {"colspan": 1, "rowspan": 1, "id": ["test cell id"],
                                                          "xpath": "/html/body/div[47]/table/tr[1]/td[0]",
                                                          "leftIndentation": "0", "value": ""}}}}

        table = self.table.construct_from_raw(raw, self.html)
        self.assertIsInstance(table, HTMLTableTag)
        self.assertEqual(table.xpath, "/path/to/table")
        self.assertEqual(table.title, "Table Title")
        self.assertEqual(table.html_id, "table-1")
        self.assertEqual(table.cell_data, {"1:1": {"colspan": 1, "rowspan": 1, "id": ["test cell id"],
                                                   "xpath": "/html/body/div[47]/table/tr[1]/td[0]",
                                                   "leftIndentation": "0", "value": "", 'isBold': False}})
        self.assertIs(table.html, self.html)

    def test__construct_from_raw_to_dict(self):
        raw = {XBRLTableTagEnum._id.value: 'test tabletag _id',
               XBRLTableTagEnum.ocr_value.value: '',
               XBRLTableTagEnum.value.value: '',
               XBRLTableTagEnum.is_table.value: True,
               XBRLTableTagEnum.table.value: {
                   XBRLTableTagEnum.xpath.value: "/path/to/table",
                   XBRLTableTagEnum.title.value: "Table Title",
                   XBRLTableTagEnum.anchor_id.value: "table-id",
                   XBRLTableTagEnum.cells.value: {"1:1": {"colspan": 1, "rowspan": 1, "id": ["test cell id"],
                                                          "xpath": "/html/body/div[47]/table/tr[1]/td[]",
                                                          "leftIndentation": "0", "value": ""}}},
               XBRLTableTagEnum.source.value: 'ids: []'}
        table = HTMLTableTag.construct_from_raw(raw, self.html_id)
        self.assertEqual(table.to_dict(), raw)


class TestHTMLCell(unittest.TestCase):
    def test__construct_from_raw(self):
        row_without_isbold = {
            XBRLCellEnum.source.value: {
                XBRLCellEnum.html_id.value: ["id1", "id2"], XBRLCellEnum.xpath.value: "//table/tr[1]/td[1]",
                XBRLCellEnum.row_index.value: 1, XBRLCellEnum.col_index.value: 1,
                XBRLCellEnum.col_span.value: 2, XBRLCellEnum.row_span.value: 1},
            XBRLCellEnum.raw_value.value: "cell value"}

        cell = HTMLCell.construct_from_raw(row_without_isbold)
        self.assertEqual(cell.html_id, ["id1", "id2"])
        self.assertEqual(cell.xpath, "//table/tr[1]/td[1]")
        self.assertEqual(cell.row_index, 1)
        self.assertEqual(cell.col_index, 1)
        self.assertEqual(cell.col_span, 2)
        self.assertEqual(cell.row_span, 1)
        self.assertEqual(cell.raw_value, "cell value")
        self.assertEqual(cell.is_bold, False)
        self.assertEqual(cell.left_indentation, None)

    def test__to_dict(self):
        cell = HTMLCell(
            html_id=["id1", "id2"], xpath="//table/tr[1]/td[1]", row_index=1, col_index=1,
            col_span=2, row_span=1, raw_value="cell value", is_bold=True, left_indentation="10px")
        cell_dict = cell.to_dict()
        self.assertEqual(cell_dict[XBRLCellEnum.row_index.value], 1)
        self.assertEqual(cell_dict[XBRLCellEnum.col_index.value], 1)
        self.assertEqual(cell_dict[XBRLCellEnum.col_span.value], 2)
        self.assertEqual(cell_dict[XBRLCellEnum.row_span.value], 1)
        self.assertEqual(cell_dict[XBRLCellEnum.raw_value.value], "cell value")
        self.assertEqual(cell_dict[XBRLCellEnum.html_id.value], ["id1", "id2"])
        self.assertEqual(cell_dict[XBRLCellEnum.xpath.value], "//table/tr[1]/td[1]")
        self.assertEqual(cell_dict[XBRLCellEnum.is_bold.value], True)
        self.assertEqual(cell_dict[XBRLCellEnum.left_indentation.value], "10px")


class TestTDTag(unittest.TestCase):
    def setUp(self):
        self.td_id = 'test_td_id'
        self.html_id = ['1', '2', '3']
        self.xpath = "/xpath"
        self.raw_value = "raw_value"
        self.raw_ocr_value = "raw_ocr_value"
        self.is_table = False
        self.field_id = "field_id"
        self.tag_id = "tag_id"
        self.row_index = 0
        self.col_index = 1
        self.td_tag = TDTag(td_id=self.td_id, html_id=self.html_id, xpath=self.xpath, raw_value=self.raw_value,
                            raw_ocr_value=self.raw_ocr_value, is_table=self.is_table, field_id=self.field_id,
                            tag_id=self.tag_id, row_index=self.row_index, col_index=self.col_index)

    def test__td_tag_init(self):
        self.assertEqual(self.td_tag.html_id, self.html_id)
        self.assertEqual(self.td_tag.xpath, self.xpath)
        self.assertEqual(self.td_tag.raw_value, self.raw_value)
        self.assertEqual(self.td_tag.raw_ocr_value, self.raw_ocr_value)
        self.assertEqual(self.td_tag.field_id, self.field_id)
        self.assertEqual(self.td_tag.tag_id, self.tag_id)
        self.assertEqual(self.td_tag.row_index, self.row_index)
        self.assertEqual(self.td_tag.col_index, self.col_index)

    def test__td_tag_construct_from_raw(self):
        raw = {
            XBRLTagEnum.td_id.value: 'test_td_id',
            XBRLTagEnum.is_table.value: False,
            XBRLTagEnum.source.value: {
                XBRLTagEnum.ids.value: [1, 2, 3],
                XBRLTagEnum.xpath.value: "/xpath",
                XBRLTagEnum.row_index.value: 0,
                XBRLTagEnum.col_index.value: 1,
                IqRecipeEnum.field_id.value: "field_id",
                XBRLTagEnum.tag_id.value: "tag_id",
            },
            XBRLTagEnum.ocr_value.value: "raw_ocr_value",
            XBRLTagEnum.value.value: "raw_value"
        }
        html = HTML(self.xpath)
        td_tag = TDTag.construct_from_raw(raw, html)
        self.assertEqual(td_tag.html_id, [1, 2, 3])
        self.assertEqual(td_tag.xpath, "/xpath")
        self.assertEqual(td_tag.raw_value, "raw_value")
        self.assertEqual(td_tag.raw_ocr_value, "raw_ocr_value")
        self.assertEqual(td_tag.field_id, "field_id")
        self.assertEqual(td_tag.tag_id, "tag_id")
        self.assertEqual(td_tag.row_index, 0)
        self.assertEqual(td_tag.col_index, 1)

    def test__td_tag_to_dict(self):
        td_tag = TDTag(td_id='test td_id', html_id=['1', '2', '3'], xpath="/xpath", raw_value="raw_value",
                       raw_ocr_value="raw_ocr_value", is_table=False, field_id="field_id",
                       tag_id="tag_id", row_index=0, col_index=1)
        output_dict = td_tag.to_dict()
        expected_dict = {
            ID: output_dict[ID], XBRLTagEnum.ids.value: ['1', '2', '3'],
            XBRLTagEnum.xpath.value: "/xpath", XBRLTagEnum.value.value: "raw_value",
            XBRLTagEnum.ocr_value.value: "raw_ocr_value", IqRecipeEnum.field_id.value: "field_id",
            XBRLTagEnum.tag_id.value: "tag_id", XBRLTagEnum.row_index.value: 0, XBRLTagEnum.col_index.value: 1}
        self.assertDictEqual(output_dict, expected_dict)

    def test__td_tag_construct_from_raw_output(self):
        raw = {
            XBRLTagEnum.source.value: {
                XBRLTagEnum.ids.value: [1, 2, 3], XBRLTagEnum.xpath.value: "/xpath",
                XBRLTagEnum.row_index.value: 0, XBRLTagEnum.col_index.value: 1,
                IqRecipeEnum.field_id.value: "field_id", XBRLTagEnum.tag_id.value: "tag_id"},
            XBRLTagEnum.ocr_value.value: "raw_value", XBRLTagEnum.value.value: "value",
            XBRLTagEnum.td_id.value: 'test td_id',
            XBRLTagEnum.is_table.value: False}

        html = HTML(self.xpath)
        td_tag = TDTag.construct_from_raw(raw=raw, html=html)
        td_dict = td_tag.to_dict()
        expected_output = {
            ID: td_dict[ID], XBRLTagEnum.ids.value: [1, 2, 3],
            XBRLTagEnum.xpath.value: "/xpath", XBRLTagEnum.value.value: "value",
            XBRLTagEnum.ocr_value.value: "raw_value", IqRecipeEnum.field_id.value: "field_id",
            XBRLTagEnum.tag_id.value: "tag_id", XBRLTagEnum.row_index.value: 0,
            XBRLTagEnum.col_index.value: 1}
        self.assertDictEqual(td_dict, expected_output)


if __name__ == '__main__':
    unittest.main()
