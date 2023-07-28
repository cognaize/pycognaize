import json
import os
import unittest
from copy import deepcopy

from pycognaize.document.html_info import HTML

from pycognaize.common.enums import IqDocumentKeysEnum, IqTagKeyEnum, \
    IqFieldKeyEnum, ID
from pycognaize.document.field import SpanField
from pycognaize.document.page import create_dummy_page
from pycognaize.tests.resources import RESOURCE_FOLDER


class TestSpanField(unittest.TestCase):

    def setUp(self):
        with open(RESOURCE_FOLDER +
                  '/snapshots/64b1621a44acf9001017db4f/document.json') \
                as document_json:
            self.data_with_group_key = json.load(document_json)

        self.html = HTML(path=(
                RESOURCE_FOLDER + '/snapshots/64b1621a44acf9001017db4f'),
            document_id='64b1621a44acf9001017db4f')
        # add groupKey value to test in test_to_dict
        self.raw_field_1 = self.data_with_group_key \
            ["output_fields"]["test_text_span__text_span"][0]
        self.raw_field_2 = \
            self.data_with_group_key["output_fields"][
                "test_text_span__text_span"][
                2]

        self.page_10 = {
            10: create_dummy_page(page_n=self.raw_field_1['tags'][0]['page'])}
        self.page_8 = {
            8: create_dummy_page(page_n=self.raw_field_2['tags'][0]['page'])}

        self.span_field_1 = SpanField.construct_from_raw(raw=self.raw_field_1,
                                                         pages=self.page_10,
                                                         html=self.html)
        self.span_field_2 = SpanField.construct_from_raw(raw=self.raw_field_2,
                                                         pages=self.page_8,
                                                         html=self.html)

    def test___repr__(self):
        self.assertEqual(self.span_field_1.name, self.raw_field_1['name'])
        self.assertEqual(self.span_field_2.name, self.raw_field_2['name'])

    def test__field_id(self):
        self.assertEqual(self.span_field_1._field_id, self.raw_field_1['_id'])
        self.assertEqual(self.span_field_2._field_id, self.raw_field_2['_id'])

    def test_value(self):
        self.assertIsInstance(self.span_field_1.value, str)
        self.assertEqual(self.span_field_1.value, self.raw_field_1['value'])
        self.assertEqual(self.span_field_2.value, self.raw_field_2['value'])

    def test__construct_from_raw(self):
        self.assertEqual(self.span_field_1.name, self.raw_field_1['name'])
        self.assertEqual(self.span_field_1.tags[0].raw_ocr_value,
                         self.raw_field_1['tags'][0]['ocrValue'])
        self.assertNotEqual(self.span_field_2.tags[0].top, '42.02')

    def test_to_dict(self):
        dict_1 = self.span_field_1.to_dict()
        self.check_keys(dict_1)

        dict_2 = self.span_field_2.to_dict()
        self.check_keys(dict_2)

        self.assertIsInstance(dict_1[IqDocumentKeysEnum.tags.value][0], dict)
        self.assertEqual(len(dict_2[IqDocumentKeysEnum.tags.value]), 4)

        invalid_field = deepcopy(self.span_field_2)
        invalid_field.tags[0]._right = 'string'
        with self.assertRaises(TypeError):
            invalid_field.to_dict()

    def test_group_key(self):
        self.assertEqual(self.span_field_1.group_key,
                         self.raw_field_1['groupKey'])
        self.assertEqual(self.span_field_2.group_key,
                         self.raw_field_2['groupKey'])

        with self.assertRaises(TypeError):
            self.span_field_1.group_key = 1
        with self.assertRaises(TypeError):
            self.span_field_1.group_key = True
        with self.assertRaises(TypeError):
            self.span_field_1.group_key = ['abc']

    def check_keys(self, test_dict):
        to_dict_keys = [IqFieldKeyEnum.name.value,
                        IqFieldKeyEnum.data_type.value, ID,
                        IqFieldKeyEnum.tags.value,
                        IqFieldKeyEnum.group_key.value,
                        IqFieldKeyEnum.value.value]
        self.assertEqual(sorted(test_dict.keys()), sorted(to_dict_keys))
