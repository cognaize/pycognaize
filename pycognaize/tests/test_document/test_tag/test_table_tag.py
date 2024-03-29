import json
import os
import unittest
from copy import deepcopy

from pycognaize.common.enums import IqTableTagEnum, IqTagKeyEnum, IqFieldKeyEnum
from pycognaize.document.tag.table_tag import TableTag
from pycognaize.document.page import create_dummy_page
from pycognaize.tests.resources import RESOURCE_FOLDER


class TestTable(unittest.TestCase):

    # set expected constants
    SNAPSHOT_PATH = os.path.join(RESOURCE_FOLDER, 'snapshots')
    SNAPSHOT_ID = '60b76b3d6f3f980019105dac'
    snap_storage_path = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.snap_storage_path = os.path.join(cls.SNAPSHOT_PATH, cls.SNAPSHOT_ID)

    def setUp(self) -> None:
        with open(self.snap_storage_path + '/document.json') as document_json:
            self.data = json.load(document_json)

        table_field = deepcopy(self.data['input_fields']['table'][0])
        self.raw_tbl_tag = table_field[IqFieldKeyEnum.tags.value][0]

        self.page = create_dummy_page(page_n=3, path=self.snap_storage_path)
        self.tbl_tag = TableTag.construct_from_raw(self.raw_tbl_tag, self.page)

    def test_construct_from_raw(self):

        invalid_raw_table_tag = deepcopy(self.raw_tbl_tag)
        # pop table key
        invalid_raw_table_tag.pop("table")
        with self.assertRaises(KeyError):
            TableTag.construct_from_raw(invalid_raw_table_tag, self.page)

        invalid_raw_table_tag = deepcopy(self.raw_tbl_tag)
        # top to None
        invalid_raw_table_tag["table"]['top'] = None
        with self.assertRaises(TypeError):
            TableTag.construct_from_raw(invalid_raw_table_tag, self.page)

        invalid_raw_table_tag = deepcopy(self.raw_tbl_tag)
        # pop required key
        invalid_raw_table_tag["table"].pop('cells')
        with self.assertRaises(KeyError):
            TableTag.construct_from_raw(invalid_raw_table_tag, self.page)

        invalid_raw_table_tag = deepcopy(self.raw_tbl_tag)
        # pop required key
        invalid_raw_table_tag["table"]['cells']['2:1'].pop('value')
        with self.assertRaises(KeyError):
            TableTag.construct_from_raw(invalid_raw_table_tag, self.page)

        invalid_raw_table_tag = deepcopy(self.raw_tbl_tag)
        # change key separator
        invalid_raw_table_tag["table"]['cells']['3_1'] = invalid_raw_table_tag["table"]['cells']['3:1']
        with self.assertRaises(IndexError):
            TableTag.construct_from_raw(invalid_raw_table_tag, self.page)

        invalid_raw_table_tag = deepcopy(self.raw_tbl_tag)
        # empty cells for testing build cells
        invalid_raw_table_tag["table"]['cells'] = {}
        with self.assertRaises(Exception):
            TableTag.construct_from_raw(invalid_raw_table_tag, self.page)

    def test_to_dict(self):
        ttd = self.tbl_tag.to_dict()
        self.assertIsInstance(ttd[IqTableTagEnum.table.value], dict)
        self.assertEqual(ttd[IqTagKeyEnum.page.value], 3)
        self.assertTrue(ttd[IqTagKeyEnum.is_table.value])
        self.assertEqual(ttd[IqTagKeyEnum.ocr_value.value], 'table on page 3')
        self.assertIsInstance(ttd[IqTableTagEnum.table.value][IqTableTagEnum.cells.value], dict)
        self.assertEqual(ttd[IqTableTagEnum.table.value][IqTableTagEnum.page.value],  3)
        self.assertEqual(ttd[IqTableTagEnum.table.value][IqTableTagEnum.height.value], "52.0998%")
        self.assertEqual(ttd[IqTableTagEnum.table.value][IqTableTagEnum.cells.value]['3:7']['top'], 22.9999)
        self.assertEqual(ttd[IqTableTagEnum.table.value][IqTableTagEnum.cells.value]['1:2']['value'], '')
        self.assertEqual(ttd[IqTableTagEnum.table.value][IqTableTagEnum.cells.value]['2:10']['rowspan'], 1)

    def test_cells(self):
        cells = self.tbl_tag.cells

        self.assertEqual(len(cells), 81)
        self.assertEqual(cells[(1, 1)].value, '')
        self.assertEqual(cells[(2, 6)].value, '11.6')
        self.assertEqual(cells[(3, 27)].value, '$ 420.9')

        self.assertAlmostEqual(cells[(1, 5)].bottom - cells[(1, 4)].top, cells[(2, 5)].bottom - cells[(2, 4)].top)
        self.assertEqual(cells[(2, 20)].right, cells[2, 21].right)
        self.assertEqual(cells[(3, 16)].left - cells[(3, 15)].left, 0)

    def test_build_df(self):
        df = self.tbl_tag._build_df()
        self.assertEqual(df.shape, (27, 3))
        self.assertEqual(df[0][1].page.page_number, 3)
        self.assertEqual(df[1][5].raw_ocr_value, '11.6')
        self.assertEqual(df[0][4].left, 8.6)
        self.assertTrue(df[0][0].bottom > df[0][0].top)
        self.assertTrue(df[0][0].right > df[0][0].left)

        width_height_tbl_tag = deepcopy(self.tbl_tag)

        width_height_tbl_tag.page._image_width = self.tbl_tag.page.image_height
        width_height_tbl_tag.page._image_height = self.tbl_tag.page.image_width
        df = width_height_tbl_tag._build_df()
        self.assertEqual(df.shape, (27, 3))
        self.assertEqual(df[0][1].page.page_number, 3)
        self.assertEqual(df[1][5].raw_ocr_value, '11.6')
        self.assertEqual(df[0][4].left, 8.6)
        self.assertTrue(df[0][0].bottom > df[0][0].top)
        self.assertTrue(df[0][0].right > df[0][0].left)

    def test_df(self):
        self.assertEqual(self.tbl_tag.df.shape, (27, 3))
        self.assertEqual(self.tbl_tag.df[2][3], '')

    def test_letters_2_num(self):
        self.assertEqual(self.tbl_tag.letter_2_num('AB'), 28)
        self.assertEqual(self.tbl_tag.letter_2_num('OF'), 396)
        self.assertEqual(self.tbl_tag.letter_2_num('AWS'), 1293)
        self.assertEqual(self.tbl_tag.letter_2_num('CDE'), 2137)

    def test_split_excel_letters_numbers(self):
        self.assertEqual(self.tbl_tag.split_excel_letters_numbers('ABs12310'), ('ABs', 12310))
        self.assertIsNone(self.tbl_tag.split_excel_letters_numbers('123ABs'))

    def test_getitem(self):
        self.assertAlmostEqual(self.tbl_tag[(1, 4)].right,
                                        61.800000000000004)

        self.assertAlmostEqual(self.tbl_tag[(1, 4)].left, 8.6)
        with self.assertRaises(TypeError) as context:  # clarify this
            self.tbl_tag[1]
        self.assertEqual("object of type 'int' has no len()",
                              str(context.exception))
        with self.assertRaises(ValueError) as context:
            self.tbl_tag[1, 1, 1]
        self.assertEqual("Invalid argument (1, 1, 1)",
                              str(context.exception))
        with self.assertRaises(IndexError) as context:
            self.tbl_tag[100, 100]
        self.assertEqual(
            "No cell with the following index in the table: (100, 100)",
            str(context.exception))
        with self.assertRaises(NotImplementedError) as context:
            self.tbl_tag[10:100, 1:2]
        self.assertEqual("Slice lookup not implemented",
                         str(context.exception))

    def test__extract_raw_ocr(self):
        raw_ocr_value = TableTag._extract_raw_ocr(self.tbl_tag.raw_df[1][1])

        self.assertEqual(raw_ocr_value, "BaJjUBzdGmf")
        self.assertEqual("", TableTag._extract_raw_ocr([]))

    def test_to_string(self):
        # df already has None check
        # none_df_tbl_tag = deepcopy(self.tbl_tag)
        # none_df_tbl_tag._df = None
        # none_df_tbl_tag._raw_df = None
        # self.assertEqual(none_df_tbl_tag.to_string(), "")
        self.assertEqual(len(self.tbl_tag.to_string()), 2634)

    def test_repr(self):
        self.assertEqual(repr(self.tbl_tag),
                         "<TableTag: left: 8.6, right: "
                         "92.69999999999999, top: 12.0, bottom: 64.0998>")

    # def test_vshift(self):
        # self.assertEqual(self.tbl_tag.hshift(10), )
