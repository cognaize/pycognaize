import json
import unittest
from pycognaize.document.html_info import HTML

from pycognaize.common.enums import IqFieldKeyEnum, ID
from pycognaize.document.page import create_dummy_page
from pycognaize.tests.resources import RESOURCE_FOLDER
from pycognaize.document.field.span_field import SpanField

class TestSpanField(unittest.TestCase):

    def setUp(self):
        table_key = 'table'
        with open(RESOURCE_FOLDER + '/snapshots/60b76b3d6f3f980019105dac/document.json') as document_json:
            self.data = json.load(document_json)

        self.html = HTML(path=(
            RESOURCE_FOLDER + '/snapshots/60b76b3d6f3f980019105dac'),
                         document_id='60b76b3d6f3f980019105dac')

        # add groupKey value to test in test_to_dict
        self.data["input_fields"][table_key][0]['groupKey'] = 'test_group_key'
        self.raw_span_1 = self.data['input_fields'][table_key][0]
        self.pages_1 = {1: create_dummy_page(page_n=1)}
        self.pages_2 = {1: create_dummy_page(page_n=1),
                        2: create_dummy_page(page_n=2)}
        self.span_field_1 = SpanField.construct_from_raw(raw=self.raw_span_1, pages=self.pages_1, html=self.html)
        self.span_field_2=SpanField(name='table')

    def test_construct_from_raw(self):
        self.assertEqual(self.span_field_1.name, "table")

    def test_to_dict(self):
        res_dict = self.span_field_1.to_dict()

        field_dict_keys = [IqFieldKeyEnum.name.value, IqFieldKeyEnum.data_type.value, ID,
                        IqFieldKeyEnum.tags.value, IqFieldKeyEnum.group_key.value,
                        IqFieldKeyEnum.value.value]

        self.assertEqual(sorted(res_dict.keys()), sorted(field_dict_keys))

        for key in res_dict:
            if key in [IqFieldKeyEnum.name.value, IqFieldKeyEnum.data_type.value]:
                self.assertEqual(res_dict[key], self.raw_span_1[key])

        self.assertEqual(res_dict[ID], str(self.raw_span_1[ID]))

    def test_order_tags(self):
        with self.assertRaises(NotImplementedError):
            self.span_field_2.order_tags()

    def test_repr(self):
        self.assertEqual(repr(self.span_field_2), f"<{self.span_field_2.__class__.__name__}: {self.span_field_2.name}>")

    def test_str(self):
        self.assertEqual(str(self.span_field_2), f"<{self.span_field_2.__class__.__name__}: {self.span_field_2.name}>")