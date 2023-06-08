import json
import os
import unittest
from copy import deepcopy

from pycognaize.document.html_info import HTML

from pycognaize.common.enums import IqDocumentKeysEnum, IqTagKeyEnum, IqFieldKeyEnum, ID
from pycognaize.document.field import TextField
from pycognaize.document.page import create_dummy_page
from pycognaize.tests.resources import RESOURCE_FOLDER


class TestTextField(unittest.TestCase):

    def setUp(self):
        with open(RESOURCE_FOLDER + '/snapshots/60f554497883ab0013d9d906/document.json') as document_json:
            self.data_with_group_key = json.load(document_json)

        self.html = HTML(path=(
            RESOURCE_FOLDER + '/snapshots/60f554497883ab0013d9d906'),
                         document_id='60f554497883ab0013d9d906')
        # add groupKey value to test in test_to_dict
        self.data_with_group_key["input_fields"]["ref"][0]['groupKey'] = 'test_group_key'
        self.raw_text_1 = self.data_with_group_key['input_fields']['paragraph'][0]
        self.raw_text_2 = self.data_with_group_key['input_fields']['paragraph'][1]

        self.pages_1 = {1: create_dummy_page(page_n=1)}
        self.pages_2 = {1: create_dummy_page(page_n=1),
                        2: create_dummy_page(page_n=2)}

        self.text_field_1 = TextField.construct_from_raw(raw=self.raw_text_1, pages=self.pages_1, html=self.html)
        self.text_field_2 = TextField.construct_from_raw(raw=self.raw_text_2, pages=self.pages_2, html=self.html)
        self.text_field_3 = TextField(name='', value='SAMPLE TEXT')

        with open(RESOURCE_FOLDER + '/xbrl_snapshot/63fd387178232c6001119a41a/document.json') as document_json:
            self.data_with_group_key = json.load(document_json)

        self.html_2 = HTML(path=(RESOURCE_FOLDER + '/snapshots/63fd387178232c6001119a41a'),
                         document_id='63fd387178232c6001119a41a')

        self.raw_text_4 = self.data_with_group_key["input_fields"]["table"][0]
        self.text_field_4 = TextField.construct_from_raw(raw=self.raw_text_4, pages=None, html=self.html_2)

    def test___str__(self):
        self.assertEqual(str(self.text_field_1), 'This division, Division 1.1 (commencing with Section 1000), Division 1.2 (commencing with Section 2000), Division 1.6 (commencing with Section 4800), Division 2 (commencing with Section 5000), Division 5 (commencing with Section 14000), Division 7 (commencing with Section 18000), and Division 15 (commencing with Section 31000) shall be known, and may be cited, as the “Financial Institutions Law.”')
        self.assertEqual(str(self.text_field_2), '101. If and to the extent that any provision of the Financial Institutions Law is preempted by federal law, the provision does not apply and shall not be enforced.')

    def test___repr__(self):
        repr_str_1 = f"<{self.text_field_1.__class__.__name__}: {self.raw_text_1['name']}: This division, Division 1.1 (commencing with Section 1000), Division 1.2 (commencing with Section 2000), Division 1.6 (commencing with Section 4800), Division 2 (commencing with Section 5000), Division 5 (commencing with Section 14000), Division 7 (commencing with Section 18000), and Division 15 (commencing with Section 31000) shall be known, and may be cited, as the “Financial Institutions Law.”>"
        self.assertEqual(repr(self.text_field_1), repr_str_1)

        repr_str_2 = f"<{self.text_field_2.__class__.__name__}: {self.raw_text_2['name']}: 101. If and to the extent that any provision of the Financial Institutions Law is preempted by federal law, the provision does not apply and shall not be enforced.>"
        self.assertEqual(repr(self.text_field_2), repr_str_2)

    def test__field_id(self):
        self.assertEqual(self.text_field_1._field_id, '60251a61095a6400123b736d')
        self.assertIsNone(self.text_field_3._field_id)

    def test_value(self):
        self.assertIsInstance(self.text_field_1.value, str)
        self.assertEqual(self.text_field_2.value, '101. If and to the extent that any provision of the Financial Institutions Law is preempted by federal law, the provision does not apply and shall not be enforced.')
        self.assertEqual(self.text_field_3.value, 'SAMPLE TEXT')

    def test__construct_from_raw(self):
        self.assertEqual(self.text_field_1.name, 'paragraph')
        self.assertEqual(self.text_field_2.tags[0].raw_ocr_value, '101. If and to the extent that any provision of the Financial Institutions Law is preempted by federal law, the provision does not apply and shall not be enforced.')
        self.assertNotEqual(self.text_field_1.tags[0].top, '45.5%')
        self.assertEqual(self.text_field_4.name, 'table')


        # # invalid raw text
        # invalid_raw_1 = deepcopy(self.raw_text_1)
        # invalid_raw_1.pop(IqDocumentKeysEnum.name.value)
        # invalid_raw_2 = deepcopy(self.raw_text_2)
        # invalid_raw_2[IqDocumentKeysEnum.tags.value][0].pop(IqTagKeyEnum.top.value)
        #
        # with self.assertRaises(KeyError):
        #     TextField.construct_from_raw(raw=invalid_raw_1, pages=self.pages_1)
        # with self.assertRaises(KeyError):
        #     TextField.construct_from_raw(raw=invalid_raw_2, pages=self.pages_2)
        # with self.assertRaises(KeyError):
        #     # invalid page number
        #     TextField.construct_from_raw(raw=self.raw_text_1,
        #                                  pages={2: create_dummy_page(page_n=1)})
        #
        # with self.assertRaises(KeyError):
        #     # one wrong page for 2 same-page tags
        #     TextField.construct_from_raw(self.raw_text_2,
        #                                  pages={2: create_dummy_page(page_n=1)})

    def test_to_dict(self):
        dict_1 = self.text_field_1.to_dict()
        self.check_keys(dict_1)

        dict_2 = self.text_field_2.to_dict()
        self.check_keys(dict_2)

        dict_3 = self.text_field_3.to_dict()

        self.assertIsInstance(dict_1[IqDocumentKeysEnum.tags.value][0], dict)
        self.assertEqual(len(dict_3[IqDocumentKeysEnum.tags.value]), 0)
        self.assertEqual(len(dict_2[IqDocumentKeysEnum.tags.value]), 1)

        invalid_field = deepcopy(self.text_field_1)
        invalid_field.tags[0]._right = 'string'
        with self.assertRaises(TypeError):
            invalid_field.to_dict()

    def test_group_key(self):
        self.text_field_1.group_key = 'abc123'
        self.assertEqual(self.text_field_1.group_key, 'abc123')

        self.text_field_1.group_key = 'ABCDEF'
        self.assertEqual(self.text_field_1.group_key, 'ABCDEF')

        with self.assertRaises(TypeError):
            self.text_field_1.group_key = 1
        with self.assertRaises(TypeError):
            self.text_field_1.group_key = True
        with self.assertRaises(TypeError):
            self.text_field_1.group_key = ['abc']

    def check_keys(self, test_dict):
        to_dict_keys = [IqFieldKeyEnum.name.value, IqFieldKeyEnum.data_type.value, ID,
                        IqFieldKeyEnum.tags.value, IqFieldKeyEnum.group_key.value, IqFieldKeyEnum.value.value]
        self.assertEqual(sorted(test_dict.keys()), sorted(to_dict_keys))