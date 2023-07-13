import json
import os.path
import unittest
from copy import deepcopy

from pycognaize.document import Document
from pycognaize.document.html_info import HTML

from pycognaize.common.enums import IqDocumentKeysEnum, IqTagKeyEnum, IqFieldKeyEnum, ID
from pycognaize.document.field import NumericField
from pycognaize.document.page import create_dummy_page
from pycognaize.tests.resources import RESOURCE_FOLDER
from pycognaize import Snapshot


class TestNumericField(unittest.TestCase):

    def setUp(self):
        with open(RESOURCE_FOLDER + '/snapshots/60f554497883ab0013d9d906/document.json') as document_json:
            self.data_with_group_key = json.load(document_json)
        with open(RESOURCE_FOLDER + '/snapshots/63d4486c0e3fe60011fe3a75/document.json') as document_json:
            self.data_with_scale = json.load(document_json)

        # add groupKey value to test in test_to_dict
        self.data_with_group_key["input_fields"]["ref"][0]['groupKey'] = 'test_group_key'
        self.raw_num_field_1 = self.data_with_group_key["input_fields"]["ref"][0]
        self.raw_num_field_2 = self.data_with_group_key["input_fields"]["ref"][1]
        self.data_with_scale_1 = self.data_with_scale['output_fields']['v_year_end_outstanding_shares_sup_is__current'][0]
        self.numeric_field_scale_1 = self.data_with_scale['output_fields']['v_year_end_outstanding_shares_sup_is__current'][0]['scale']
        self.data_with_scale_2 = self.data_with_scale['output_fields']['v_other_receivables_bs__current'][0]
        self.numeric_field_scale_2 = self.data_with_scale['output_fields']['v_other_receivables_bs__current'][0]['scale']
        self.numeric_field_value_3 = self.data_with_scale['output_fields']['v_other_receivables_bs__current'][0]['tags'][0]['ocrValue']

        self.pages_1 = {1: create_dummy_page(page_n=1)}
        self.pages_2 = {1: create_dummy_page(page_n=1),
                        2: create_dummy_page(page_n=2)}

        self.snapshot = Snapshot(RESOURCE_FOLDER + '/snapshots')
        self.document = self.snapshot.documents['63d4486c0e3fe60011fe3a75']
        # self.document = Document.from_dict(self.data_with_scale, data_path='/home/maria/Desktop/pycognaize/pycognaize/tests/resources/snapshots')

        self.html = HTML(path=(RESOURCE_FOLDER + '/snapshots/60f554497883ab0013d9d906'),
                         document_id='60f554497883ab0013d9d906')
        self.num_field_1 = NumericField.construct_from_raw(raw=self.raw_num_field_1, pages=self.pages_1, html=self.html)
        self.num_field_2 = NumericField.construct_from_raw(raw=self.raw_num_field_2, pages=self.pages_2, html=self.html)
        self.num_field_3 = NumericField(name='', value='5000')

    def test_convert_to_numeric(self):
        self.assertEqual(NumericField.convert_to_numeric("50000.00"), 50000)

        invalid_num_cases = ['1,830,390', '1 830 390', "1'830'390", '1,830,390.65 1,630,390.65', '']
        for case in invalid_num_cases:
            float_nan = NumericField.convert_to_numeric(case)
            self.assertNotEqual(float_nan, float_nan)

    def test__field_id(self):
        self.assertEqual(self.num_field_2._field_id, '60f55629c23c8f0000e05d1e')
        self.assertIsNone(self.num_field_3._field_id)

    def test_name(self):
        self.assertIsInstance(self.num_field_1.name, str)
        self.assertEqual(self.num_field_1.name, 'ref')
        self.assertEqual(self.num_field_2.name, 'ref')
        self.assertEqual(self.num_field_3.name, '')

    def test_value(self):
        self.assertIsInstance(self.num_field_1.value, float)
        # sum of two tags
        self.assertEqual(self.num_field_2.value, 101.0)
        self.assertEqual(self.num_field_3.value, 5000)

    def test__construct_from_raw(self):
        self.assertEqual(self.num_field_1.name, 'ref')
        self.assertNotEqual(self.num_field_2.tags[0].raw_ocr_value, 101.0)

        # invalid raw num
        invalid_raw_1 = deepcopy(self.raw_num_field_1)
        invalid_raw_1.pop(IqTagKeyEnum.value.value)
        invalid_raw_2 = deepcopy(self.raw_num_field_2)
        invalid_raw_2[IqDocumentKeysEnum.tags.value][0].pop(IqTagKeyEnum.page.value)

        self.assertEqual(self.document.y['v_year_end_outstanding_shares_sup_is__current'][0].scale, self.numeric_field_scale_1)
        self.assertEqual(self.document.y['v_other_receivables_bs__current'][0].scale, self.numeric_field_scale_2)
        self.assertEqual(self.document.y['v_other_receivables_bs__current'][0].raw_value, self.numeric_field_value_3 * self.numeric_field_scale_2)
        # with self.assertRaises(KeyError):
        #     NumericField.construct_from_raw(raw=invalid_raw_1, pages=self.pages_1)
        # with self.assertRaises(KeyError):
        #     NumericField.construct_from_raw(raw=invalid_raw_2, pages=self.pages_2)
        # with self.assertRaises(KeyError):
        #     # invalid page key
        #     NumericField.construct_from_raw(raw=self.raw_num_field_1,
        #                                     pages={4: create_dummy_page(page_n=1)})
        #
        # with self.assertRaises(KeyError):
        #     # one page for 2 tags
        #     NumericField.construct_from_raw(self.raw_num_field_2, {3: create_dummy_page(page_n=1)})
        #
        # with self.assertRaises(KeyError):
        #     # not corresponding page key
        #     NumericField.construct_from_raw(self.raw_num_field_2,
        #                                     {2: create_dummy_page(page_n=1),
        #                                      3: create_dummy_page(page_n=2)})

    def test___str__(self):
        self.assertEqual(str(self.num_field_1), '99.')
        self.assertEqual(str(self.num_field_2), '101.')

    def test___repr__(self):
        repr_str_1 = f"<{self.num_field_1.__class__.__name__}: {self.raw_num_field_1['name']}: 99.>"
        self.assertEqual(repr(self.num_field_1), repr_str_1)

        repr_str_2 = f"<{self.num_field_2.__class__.__name__}: {self.raw_num_field_2['name']}: 101.>"
        self.assertEqual(repr(self.num_field_2), repr_str_2)

    def test_to_dict(self):
        dict_1 = self.num_field_1.to_dict()
        self.check_keys(dict_1)

        dict_2 = self.num_field_2.to_dict()
        self.check_keys(dict_2)

        dict_3 = self.num_field_3.to_dict()

        self.assertIsInstance(dict_1[IqDocumentKeysEnum.tags.value][0], dict)
        self.assertEqual(len(dict_3[IqDocumentKeysEnum.tags.value]), 0)
        self.assertEqual(len(dict_2[IqDocumentKeysEnum.tags.value]), 1)

        invalid_field = deepcopy(self.num_field_1)
        invalid_field.tags[0]._bottom = 'string'
        with self.assertRaises(TypeError):
            invalid_field.to_dict()

    def test_group_key(self):
        self.num_field_1.group_key = 'abc123'
        self.assertEqual(self.num_field_1.group_key, 'abc123')

        self.num_field_1.group_key = 'ABCDEF'
        self.assertEqual(self.num_field_1.group_key, 'ABCDEF')

        with self.assertRaises(TypeError):
            self.num_field_1.group_key = 1
        with self.assertRaises(TypeError):
            self.num_field_1.group_key = True
        with self.assertRaises(TypeError):
            self.num_field_1.group_key = ['abc']

    def check_keys(self, test_dict):
        to_dict_keys = [IqFieldKeyEnum.name.value, IqFieldKeyEnum.data_type.value, ID,
                        IqFieldKeyEnum.tags.value, IqFieldKeyEnum.group_key.value, IqFieldKeyEnum.value.value]
        self.assertEqual(sorted(test_dict.keys()), sorted(to_dict_keys))
