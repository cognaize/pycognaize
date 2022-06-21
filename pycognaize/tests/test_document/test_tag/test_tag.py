import unittest
from copy import deepcopy

from pycognaize.document.page import create_dummy_page
from pycognaize.document.tag import ExtractionTag


class TestTag(unittest.TestCase):

    def setUp(self):
        self.page = create_dummy_page(page_n=1)
        self.invalid_page = create_dummy_page(page_n=3)

        self.valid_arguments_tag = ExtractionTag(left=11.1, right=13.1, top=10, bottom=13,
                                                 page=create_dummy_page(page_n=1),
                                                 raw_value='100.1', raw_ocr_value='110.1'
                                                 )

        self.valid_arguments_tag_otherpage = ExtractionTag(left=11.1, right=13.1, top=10, bottom=13,
                                                           page=create_dummy_page(page_n=2),
                                                           raw_value='100.1', raw_ocr_value='110.1'
                                                           )
        self.valid_arguments_tag_samepage = ExtractionTag(left=10, right=13.1, top=11, bottom=13,
                                                          page=create_dummy_page(page_n=1),
                                                          raw_value='100.1', raw_ocr_value='110.1'
                                                          )
        self.intersection_true_tag = ExtractionTag(left=11.1, right=12.2, top=9.9, bottom=12,
                                                   page=create_dummy_page(page_n=1),
                                                   raw_value='100.1', raw_ocr_value='110.1'
                                                   )
        self.intersection_false_tag = ExtractionTag(left=14.1, right=15.1, top=13.9, bottom=14,
                                                    page=create_dummy_page(page_n=1),
                                                    raw_value='100.1', raw_ocr_value='110.1'
                                                    )
        self.contains_true_tag = ExtractionTag(left=11.1, right=12.2, top=10.1, bottom=12,
                                               page=create_dummy_page(page_n=1),
                                               raw_value='100.1', raw_ocr_value='110.1'
                                               )
        self.contains_true_tag_otherpage = ExtractionTag(left=11.1, right=12.2, top=10.1, bottom=12,
                                                         page=create_dummy_page(page_n=2),
                                                         raw_value='100.1', raw_ocr_value='110.1'
                                                         )
        self.contains_false_tag = deepcopy(self.intersection_true_tag)
        self.and_tag = deepcopy(self.intersection_true_tag)
        self.or_tag = deepcopy(self.intersection_true_tag)
        self.add_tag = deepcopy(self.intersection_true_tag)
        self.iou_tag = deepcopy(self.intersection_true_tag)
        self.is_in_rectangle = deepcopy(self.intersection_true_tag)
        self.invalid_tag_to_transform = deepcopy(self.valid_arguments_tag)
        self.invalid_left = deepcopy(self.invalid_tag_to_transform)
        self.invalid_right = deepcopy(self.invalid_tag_to_transform)
        self.invalid_top = deepcopy(self.invalid_tag_to_transform)
        self.invalid_bottom = deepcopy(self.invalid_tag_to_transform)

    def test__parse_coordinates(self):
        self.invalid_tag_to_transform._left = 10
        self.invalid_tag_to_transform._right = "18.9"
        self.invalid_tag_to_transform._top = "10"
        self.invalid_tag_to_transform._bottom = "-15"
        self.invalid_tag_to_transform._parse_coordinates()
        self.assertEqual(self.invalid_tag_to_transform.left, 10)
        self.assertEqual(self.invalid_tag_to_transform._right, 18.9)
        self.assertEqual(self.invalid_tag_to_transform._top, 10)
        self.assertEqual(self.invalid_tag_to_transform._bottom, -15)

        self.invalid_left._left = "10s"
        with self.assertRaises(ValueError):
            self.invalid_left._parse_coordinates()
        self.invalid_left._left = ["10s"]
        with self.assertRaises(TypeError):
            self.invalid_left._parse_coordinates()
        self.invalid_right._right = "text"
        with self.assertRaises(ValueError):
            self.invalid_right._parse_coordinates()
        self.invalid_right._right = ["text"]
        with self.assertRaises(TypeError):
            self.invalid_right._parse_coordinates()
        self.invalid_top._top = "25.12.2020"
        with self.assertRaises(ValueError):
            self.invalid_top._parse_coordinates()
        self.invalid_top._top = 7, 8
        with self.assertRaises(TypeError):
            self.invalid_top._parse_coordinates()
        self.invalid_bottom._bottom = ""
        with self.assertRaises(ValueError):
            self.invalid_bottom._parse_coordinates()
        self.invalid_bottom._bottom = (5, 4, 8)
        with self.assertRaises(TypeError):
            self.invalid_bottom._parse_coordinates()

    def test__validate_types (self):
        # TODO: "left, right, top, bottom" coordinates are numbers (_parse_coordinates ensures it), it will be better to avoid double type checking

        self.invalid_left._left = ["10s"]
        with self.assertRaises(TypeError):
            self.invalid_left._validate_types ()
        self.invalid_right._right = "text"
        with self.assertRaises(TypeError):
            self.invalid_right._validate_types ()
        self.invalid_top._top = 7, 8
        with self.assertRaises(TypeError):
            self.invalid_top._validate_types()
        self.invalid_bottom._bottom = (5, 4, 8)
        with self.assertRaises(TypeError):
            self.invalid_bottom._validate_types()

    def test__validate_coords(self):
        self.invalid_right._right = 10
        with self.assertRaises(ValueError):
            self.invalid_right._validate_coords()
        self.invalid_top._top = 14
        with self.assertRaises(ValueError):
            self.invalid_top._validate_coords()
        self.invalid_right._left = self.invalid_right._right
        with self.assertRaises(ValueError):
            self.invalid_right._validate_coords()
        self.invalid_top._bottom = self.invalid_top._top
        with self.assertRaises(ValueError):
            self.invalid_top._validate_coords()

    # def test__validate_ranges(self):
    #     self.invalid_left._left = -150
    #     with self.assertLogs() as captured:
    #         self.invalid_left._validate_ranges()
    #     self.assertEqual(len(captured.records), 1)
    #     self.assertEqual(self.invalid_left._left, 0)
    #
    #     self.invalid_right._right = 150
    #     with self.assertLogs() as captured:
    #         self.invalid_right._validate_ranges()
    #     self.assertEqual(len(captured.records), 1)
    #     self.assertEqual(self.invalid_right._right, 100)
    #
    #     self.invalid_top._top = 150
    #     with self.assertLogs() as captured:
    #         self.invalid_top._validate_ranges()
    #     self.assertEqual(len(captured.records), 1)
    #     self.assertEqual(self.invalid_top._top, 100)
    #
    #     self.invalid_bottom._bottom = -150
    #     with self.assertLogs() as captured:
    #         self.invalid_bottom._validate_ranges()
    #     self.assertEqual(len(captured.records), 1)
    #     self.assertEqual(self.invalid_bottom._bottom, 0)

    def test_left(self):
        self.assertEqual(self.valid_arguments_tag.left, 11.1)

    def test_right(self):
        self.assertEqual(self.valid_arguments_tag.right, 13.1)

    def test_top(self):
        self.assertEqual(self.valid_arguments_tag.top, 10)

    def test_bottom(self):
        self.assertEqual(self.valid_arguments_tag.bottom, 13)

    def test_page(self):
        self.assertTrue(self.valid_arguments_tag.page, self.page)

    def test_width(self):
        self.assertEqual(self.valid_arguments_tag.width, 2)

    def test_height(self):
        self.assertEqual(self.valid_arguments_tag.height, 3)

    def test_area(self):
        self.assertEqual(self.valid_arguments_tag.area, 6.0)

    def test_xcenter(self):
        self.assertEqual(self.valid_arguments_tag.xcenter, 12.1)

    def test_ycenter(self):
        self.assertEqual(self.valid_arguments_tag.ycenter, 11.5)

    def test_center(self):
        self.assertEqual(self.valid_arguments_tag.center, (12.1, 11.5))

    def test_intersects(self):
        self.assertTrue(self.valid_arguments_tag.intersects(self.intersection_true_tag))
        self.assertFalse(self.valid_arguments_tag.intersects(self.intersection_false_tag))
        with self.assertRaises(NotImplementedError):
            self.valid_arguments_tag.intersects(0)

    def test_hshift(self):
        shifted = self.valid_arguments_tag.hshift(0.1)
        shifted_1 = self.valid_arguments_tag.hshift(-1)
        self.assertEqual(shifted.left, 11.2)
        self.assertEqual(shifted.right, 13.2)
        self.assertEqual(shifted_1.left, 10.1)
        self.assertEqual(shifted_1.right, 12.1)

    def test_vshift(self):
        shifted = self.valid_arguments_tag.vshift(0.1)
        shifted_1 = self.valid_arguments_tag.vshift(-1)
        self.assertEqual(shifted.top, 10.1)
        self.assertEqual(shifted.bottom, 13.1)
        self.assertEqual(shifted_1.top, 9)
        self.assertEqual(shifted_1.bottom, 12)

    def test_shift(self):
        shifted = self.valid_arguments_tag.shift(1, 2)
        shifted_1 = self.valid_arguments_tag.shift(-1, -2)
        self.assertEqual(shifted.left, 12.1)
        self.assertEqual(shifted.right, 14.1)
        self.assertEqual(shifted_1.top, 8)
        self.assertEqual(shifted_1.bottom, 11)

    def test___contains__(self):
        self.assertTrue(self.contains_true_tag in self.valid_arguments_tag)
        self.assertFalse(self.contains_false_tag in self.valid_arguments_tag)
        with self.assertRaises(NotImplementedError):
            0 in self.valid_arguments_tag

    def test___and__(self):
        self.assertEqual(round(self.valid_arguments_tag & self.and_tag, 2), 2.2)
        self.assertEqual(self.valid_arguments_tag & self.intersection_false_tag, 0)
        with self.assertRaises(NotImplementedError):
            self.valid_arguments_tag & "wrong type"

    def test___or__(self):
        self.assertEqual(round(self.valid_arguments_tag | self.or_tag, 2), 6.11)
        self.assertEqual(round(self.valid_arguments_tag | self.intersection_false_tag, 2), 6.1)
        self.assertEqual(self.valid_arguments_tag | self.valid_arguments_tag_otherpage, 0)
        with self.assertRaises(NotImplementedError):
            self.valid_arguments_tag | 0

    def test_iou(self):
        self.assertEqual(round(self.valid_arguments_tag.iou(self.iou_tag), 2), 0.36)
        self.assertEqual(self.valid_arguments_tag.iou(self.valid_arguments_tag_otherpage), 0)
        with self.assertRaises(NotImplementedError):
            self.valid_arguments_tag.iou("String")

    def test___add__(self):
        add_tag = self.valid_arguments_tag + self.add_tag
        self.assertEqual(add_tag.left, 11.1)
        self.assertEqual(add_tag.right, 13.1)
        self.assertEqual(add_tag.top, 9.9)
        self.assertEqual(add_tag.bottom, 13)
        with self.assertRaises(ValueError):
            self.valid_arguments_tag + self.valid_arguments_tag_otherpage

    def test___radd__(self):
        radd_tag = self.valid_arguments_tag + self.add_tag
        self.assertEqual(radd_tag.left, 11.1)
        self.assertEqual(radd_tag.right, 13.1)
        self.assertEqual(radd_tag.top, 9.9)
        self.assertEqual(radd_tag.bottom, 13)

    def test_is_in_rectangle(self):
        self.assertTrue(round(self.valid_arguments_tag.is_in_rectangle(self.is_in_rectangle, 0.36), 2))
        self.assertFalse(round(self.valid_arguments_tag.is_in_rectangle(self.is_in_rectangle, 0.37), 2))
        with self.assertRaises(ValueError):
            self.valid_arguments_tag.is_in_rectangle(self.is_in_rectangle, 1.1)
        self.assertTrue(round(self.valid_arguments_tag.is_in_rectangle(self.valid_arguments_tag, 1), 2))
        self.assertFalse(round(self.valid_arguments_tag.is_in_rectangle(self.valid_arguments_tag_otherpage, 1), 2))
        with self.assertRaises(NotImplementedError):
            self.valid_arguments_tag.is_in_rectangle("text", 1)

    def test_get_top_left(self):
        self.assertEqual(self.valid_arguments_tag.get_top_left(), (10, 11.1))

    def test_get_width_height(self):
        self.assertEqual(self.valid_arguments_tag.get_width_height(), (2, 3))

    def test_distance(self):
        with self.assertRaises(ValueError):
            self.valid_arguments_tag.distance(self.valid_arguments_tag_otherpage)
        self.assertEqual(self.valid_arguments_tag.distance(self.valid_arguments_tag), 0)
        self.assertTrue(round(self.valid_arguments_tag.distance(self.valid_arguments_tag_samepage), 2), 0.23)


if __name__ == '__main__':
    unittest.main()
