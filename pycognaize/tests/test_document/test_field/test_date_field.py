import json
import unittest
from copy import deepcopy

from pycognaize.common.enums import IqDocumentKeysEnum, IqTagKeyEnum, IqFieldKeyEnum, ID
from pycognaize.document.field import DateField
from pycognaize.document.page import create_dummy_page
from pycognaize.tests.resources import RESOURCE_FOLDER


class TestDateField(unittest.TestCase):

    def setUp(self):
        with open(RESOURCE_FOLDER + '/snapshots/60f554497883ab0013d9d906/document.json', encoding="utf8") as document_json:
            self.data_with_group_key_1 = json.load(document_json)

        with open(RESOURCE_FOLDER + '/snapshots/60f5260c7883ab0013d9c184/document.json', encoding="utf8") as document_json:
            self.data_with_group_key_2 = json.load(document_json)

        # add groupKey value to test in test_to_dict
        self.data_with_group_key_1["input_fields"]["source_date"][0]['groupKey'] = 'test_group_key'
        self.data_with_group_key_2["input_fields"]["source_date"][0]['groupKey'] = 'test_group_key'

        self.raw_date_1 = self.data_with_group_key_1["input_fields"]["source_date"][0]
        self.raw_date_2 = self.data_with_group_key_2["input_fields"]["source_date"][0]

        self.pages_1 = {1: create_dummy_page(1)}
        self.pages_2 = {1: create_dummy_page(1), 2: create_dummy_page(2)}

        self.date_field_1 = DateField.construct_from_raw(raw=self.raw_date_1, pages=self.pages_1)
        self.date_field_2 = DateField.construct_from_raw(raw=self.raw_date_2, pages=self.pages_2)
        self.date_field_3 = DateField(name='', value='01/01/2020')

    def test_field_id(self):
        self.assertEqual(self.date_field_1.field_id, '60251928095a6400123b7368')
        self.assertIsNone(self.date_field_3.field_id)

    def test_value(self):
        self.assertIsInstance(self.date_field_1.value, str)
        self.assertEqual(self.date_field_2.value, 'December 31, 2016')
        self.assertEqual(self.date_field_3.value, '01/01/2020')

    def test__construct_from_raw(self):
        self.assertEqual(self.date_field_1.name, 'source date')
        self.assertAlmostEqual(self.date_field_1.tags[0].left, 51.199427139276764)
        # invalid raw date
        invalid_raw_1 = deepcopy(self.data_with_group_key_1["input_fields"]["source_date"][0])
        invalid_raw_1.pop(IqDocumentKeysEnum.name.value)
        invalid_raw_2 = deepcopy(self.data_with_group_key_2["input_fields"]["source_date"][0])
        invalid_raw_2[IqDocumentKeysEnum.tags.value][0].pop(IqTagKeyEnum.value.value)

        # with self.assertRaises(KeyError):
        #     DateField.construct_from_raw(raw=invalid_raw_1, pages=self.pages_1)
        # with self.assertRaises(KeyError):
        #     DateField.construct_from_raw(raw=invalid_raw_2, pages=self.pages_2)
        # with self.assertRaises(KeyError):
        #     # invalid page number
        #     DateField.construct_from_raw(raw=self.raw_date_1, pages={2: create_dummy_page(2)})
        #
        # with self.assertRaises(KeyError):
        #     # one page for 2 tags
        #     DateField.construct_from_raw(self.raw_date_2, self.pages_1)
        # 
        # with self.assertRaises(KeyError):
        #     # not corresponding page numbers
        #     DateField.construct_from_raw(self.raw_date_2,
        #                                  {1: create_dummy_page(1),
        #                                   3: create_dummy_page(3)})

    def test___str__(self):
        self.assertEqual(str(self.date_field_1), '12/12/2011')
        self.assertEqual(str(self.date_field_2), 'December 31, 2016')

    def test___repr__(self):
        repr_str_1 = "<DateField: source date: field value - : tag value - 12/12/2011>"
        self.assertEqual(repr(self.date_field_1), repr_str_1)

        repr_str_2 = '<DateField: source date: field value - : tag value - December 31, 2016>'
        self.assertEqual(repr(self.date_field_2), repr_str_2)

    def test_to_dict(self):
        dict_1 = self.date_field_1.to_dict()
        self.check_keys(dict_1)

        dict_2 = self.date_field_2.to_dict()
        self.check_keys(dict_2)

        dict_3 = self.date_field_3.to_dict()

        self.assertIsInstance(dict_1[IqDocumentKeysEnum.tags.value][0], dict)
        self.assertEqual(len(dict_3[IqDocumentKeysEnum.tags.value]), 0)
        self.assertEqual(len(dict_2[IqDocumentKeysEnum.tags.value]), 1)

        invalid_field = deepcopy(self.date_field_1)
        invalid_field.tags[0]._left = '123'
        with self.assertRaises(TypeError):
            invalid_field.to_dict()

    def test_group_key(self):
        self.date_field_1.group_key = 'abc123'
        self.assertEqual(self.date_field_1.group_key, 'abc123')

        self.date_field_1.group_key = 'ABCDEF'
        self.assertEqual(self.date_field_1.group_key, 'ABCDEF')

        with self.assertRaises(TypeError):
            self.date_field_1.group_key = 1
        with self.assertRaises(TypeError):
            self.date_field_1.group_key = True
        with self.assertRaises(TypeError):
            self.date_field_1.group_key = ['abc']

    def check_keys(self, test_dict):
        to_dict_keys = [IqFieldKeyEnum.name.value, IqFieldKeyEnum.data_type.value, ID,
                        IqFieldKeyEnum.tags.value, IqFieldKeyEnum.group_key.value, IqFieldKeyEnum.value.value]
        self.assertEqual(sorted(test_dict.keys()), sorted(to_dict_keys))
