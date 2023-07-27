import copy
import json
import unittest
from copy import deepcopy

from pycognaize.document.page import create_dummy_page
from pycognaize.document.tag.span_tag import SpanTag
from pycognaize.tests.resources import RESOURCE_FOLDER
from pycognaize import Snapshot


class TestSpanTag(unittest.TestCase):

    def setUp(self):
        self.page = create_dummy_page()

        with open(
                RESOURCE_FOLDER + '/snapshots/64b1621a44acf9001017db4f/document.json') as document_json:
            self.data = json.load(document_json)

        snapshot = Snapshot(RESOURCE_FOLDER + '/snapshots')
        doc = snapshot.documents['64b1621a44acf9001017db4f']

        self.ext_tag_dict_1 = deepcopy(
            self.data['output_fields']['test_text_span__text_span'][0]['tags'][
                0])
        self.ext_tag_dict_2 = deepcopy(
            self.data['output_fields']['test_text_span__text_span'][0]['tags'][
                1])
        self.ext_tag_dict_3 = deepcopy(
            self.data['output_fields']['test_text_span__text_span'][1]['tags'][
                0])
        self.ext_tag_dict_4 = deepcopy(
            self.data['output_fields']['test_text_span__text_span'][1]['tags'][
                1])
        self.ext_tag_dict_5 = deepcopy(
            self.data['output_fields']['test_text_span__text_span'][2]['tags'][
                0])
        self.ext_tag_dict_6 = deepcopy(
            self.data['output_fields']['test_text_span__text_span'][2]['tags'][
                1])
        self.ext_tag_dict_7 = deepcopy(
            self.data['output_fields']['test_text_span__text_span'][2]['tags'][
                2])
        self.ext_tag_dict_8 = deepcopy(
            self.data['output_fields']['test_text_span__text_span'][2]['tags'][
                3])

        self.ext_tag_1 = SpanTag.construct_from_raw(self.ext_tag_dict_1,
                                                          page=create_dummy_page(
                                                              self.ext_tag_dict_1[
                                                                  'page']))
        self.ext_tag_2 = SpanTag.construct_from_raw(self.ext_tag_dict_2,
                                                          page=create_dummy_page(
                                                              self.ext_tag_dict_2[
                                                                  'page']))
        self.ext_tag_3 = SpanTag.construct_from_raw(self.ext_tag_dict_3,
                                                          page=create_dummy_page(
                                                              self.ext_tag_dict_3[
                                                                  'page']))
        self.ext_tag_4 = SpanTag.construct_from_raw(self.ext_tag_dict_4,
                                                          page=create_dummy_page(
                                                              self.ext_tag_dict_4[
                                                                  'page']))
        self.ext_tag_5 = SpanTag.construct_from_raw(self.ext_tag_dict_5,
                                                          page=create_dummy_page(
                                                              self.ext_tag_dict_5[
                                                                  'page']))
        self.ext_tag_6 = SpanTag.construct_from_raw(self.ext_tag_dict_6,
                                                          page=create_dummy_page(
                                                              self.ext_tag_dict_6[
                                                                  'page']))
        self.ext_tag_7 = SpanTag.construct_from_raw(self.ext_tag_dict_7,
                                                          page=create_dummy_page(
                                                              self.ext_tag_dict_7[
                                                                  'page']))
        self.ext_tag_8 = SpanTag.construct_from_raw(self.ext_tag_dict_8,
                                                          page=create_dummy_page(
                                                              self.ext_tag_dict_8[
                                                                  'page']))

        self.invalid_span_ext_tag = SpanTag(left=11.1, right=13.1,
                                                  top=10, bottom=13,
                                                  page=copy.deepcopy(
                                                      self.page),
                                                  raw_value='100.1%',
                                                  raw_ocr_value=None)

    def test_raw_value(self):
        self.assertEqual(self.ext_tag_1.raw_value, self.ext_tag_dict_1['value'])
        self.assertEqual(self.ext_tag_2.raw_value, self.ext_tag_dict_2['value'])

    def test_raw_ocr_value(self):
        self.assertNotEqual(self.ext_tag_3.raw_ocr_value, '145. ')
        self.assertIsNone(self.invalid_span_ext_tag.raw_ocr_value)

    def test_coordinates(self):
        self.assertAlmostEqual(str(self.ext_tag_1.top), self.ext_tag_dict_1['top'][:-1])
        self.assertNotEqual(str(self.ext_tag_1.bottom), '42.02')

    def test__construct_from_raw(self):
        SpanTag.construct_from_raw(raw=self.ext_tag_dict_2,
                                         page=self.page)

    def test_to_dict(self):
        invalid_field = deepcopy(self.ext_tag_1)
        invalid_field._bottom = 'INVALID STRING TYPE'
        with self.assertRaises(TypeError):
            invalid_field.to_dict()

    def test___contains__(self):
        self.assertFalse(self.ext_tag_2 in self.ext_tag_1)
        self.assertFalse(self.ext_tag_6 in self.ext_tag_8)
        self.assertFalse(self.ext_tag_5 in self.ext_tag_2)
        with self.assertRaises(NotImplementedError):
            self.ext_tag_5.__contains__('5')


if __name__ == '__main__':
    unittest.main()
