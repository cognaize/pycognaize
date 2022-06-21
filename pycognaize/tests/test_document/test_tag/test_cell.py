import unittest

from pycognaize.common.enums import IqCellKeyEnum
from pycognaize.document.tag.cell import Cell


class TestCell(unittest.TestCase):

    def setUp(self):
        self.valid_cells = [
            dict(value="", left=1, right=20, top=3, bottom=28, row_span=2, col_span=2, top_row=1, left_col=1),
            dict(value="", left=10, right=22, top=3, bottom=28, row_span=2, col_span=-8, top_row=-1, left_col=10)
        ]

        self.cell_1 = Cell(value="Addition", left=8.2, right=19.5, top=6.5, bottom=20.5, row_span=5, col_span=7,
                           top_row=9, left_col=11)
        self.cell_2 = Cell(value="Date", left=8.03, right=10.5, top=7.5, bottom=10.5, row_span=5, col_span=7,
                           top_row=8, left_col=12)

    # def testCell(self):
        # with self.assertRaises(ValueError):
        #     # invalid row spam
        #     Cell(value="Date", left=8.03, right=10.5, top=7.5, bottom=10.5, row_span=-5, col_span=7,
        #          top_row=8, left_col=12)
        # with self.assertRaises(ValueError):
        #     # invalid coords (left>right)
        #     Cell(value="Date", left=12.03, right=10.5, top=99, bottom=10.5, row_span=-5, col_span=7,
        #          top_row=8, left_col=12)
        #
        # with self.assertRaises(ValueError):
        #     # invalid type
        #     Cell(value="Date", left="12.03", right=10.5, top="99", bottom=10.5, row_span=-5, col_span=7,
        #          top_row=8, left_col=None)

    def test_col_span(self):
        self.assertEqual(self.cell_1.col_span, 7)

    def test_value(self):
        self.assertEqual(self.cell_2.value, "Date")
        self.assertIsInstance(self.cell_2.value, str)

    def test_right(self):
        self.assertAlmostEqual(self.cell_2.right, 10.5)

    def test_row_span(self):
        self.assertIsInstance(self.cell_1.row_span, int)
        self.assertNotIsInstance(self.cell_1.row_span, str)

    def test_eq(self):
        self.assertNotEqual(self.cell_1, self.cell_2)
        self.assertEqual(self.cell_1, self.cell_1)
        self.assertEqual(self.cell_1, 'Addition')
        self.assertNotEqual(self.cell_2, 'Ddd')

    def test_area(self):
        self.cell_1._area = None
        self.assertAlmostEqual(self.cell_1.area, self.cell_1.width * self.cell_1.height)
        self.assertAlmostEqual(self.cell_1.area, 11.3 * 14.0)

    def test_width(self):
        self.cell_2._width = None
        self.assertAlmostEqual(self.cell_2.width, self.cell_2.right - self.cell_2.left)
        self.assertAlmostEqual(self.cell_2.width, 10.5 - 8.03)

    def test_height(self):
        self.cell_1._height = None
        self.assertAlmostEqual(self.cell_1.height, self.cell_1.bottom - self.cell_1.top)
        self.assertAlmostEqual(self.cell_1.height, 20.5 - 6.5)

    def test___repr__(self):
        self.assertEqual(
            self.cell_1.__repr__(),
            '<Cell: coords: (6.50000  , 19.50000 , 20.50000 ,'
            ' 8.20000  ) spans: (5  , 7  ) corner coords: (11 , 9  )'
            ' value: Addition>')
        self.assertEqual(
            self.cell_2.__repr__(),
            '<Cell: coords: (7.50000  , 10.50000 , 10.50000'
            ' , 8.03000  ) spans: (5  , 7  ) corner coords: (12 , 8  )'
            ' value: Date>')

    def test___str__(self):
        self.assertEqual(self.cell_1.__str__(), 'Left: 11, Top: 9')
        self.assertEqual(self.cell_2.__str__(), 'Left: 12, Top: 8')

    def test_to_dict(self):
        rtd_1 = self.cell_1.to_dict()
        rtd_2 = self.cell_2.to_dict()
        self.assertEqual(rtd_1[IqCellKeyEnum.height.value], 14)
        self.assertAlmostEqual(rtd_2[IqCellKeyEnum.width.value], 2.47)
        self.assertAlmostEqual(rtd_2[IqCellKeyEnum.left.value], 8.03)
        self.assertIsInstance(rtd_1[IqCellKeyEnum.row_span.value], (float, int))
