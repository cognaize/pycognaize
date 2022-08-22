import json
import unittest

from copy import deepcopy
from pydantic import ValidationError

from pycognaize.common.enums import IqDocumentKeysEnum, IqFieldKeyEnum, ID
from pycognaize.document.field.area_field import AreaField
from pycognaize.document.page import create_dummy_page
from pycognaize.tests.resources import RESOURCE_FOLDER


class TestAreaField(unittest.TestCase):

    def setUp(self):
        with open(RESOURCE_FOLDER + '/snapshots/60f5260c7883ab0013d9c184/document.json') as document_json:
            self.data = json.load(document_json)

        self.data_with_group_key = deepcopy(self.data)
        # add groupKey value to test in test_to_dict
        self.data_with_group_key["input_fields"]["table_area"][0]['groupKey'] = 'test_group_key'
        self.raw_area_field_with_group_key = deepcopy(self.data_with_group_key["input_fields"]["table_area"][0])

        self.raw_area_field_no_group_key = deepcopy(self.data["input_fields"]["table_area"][1])
        self.pages = {1: create_dummy_page(1), 2: create_dummy_page(2)}

        self.area_field_with_tags = AreaField.construct_from_raw(self.raw_area_field_with_group_key,
                                                                 self.pages)
        self.area_field_without_tags = AreaField(
            name=self.raw_area_field_no_group_key[IqDocumentKeysEnum.name.value],
            value='sample_value')

        # self.area_field_with_invalid_value = AreaField(
        #     name=self.raw_area_field_no_group_key[IqDocumentKeysEnum.name.value],
        #     value=['Invalid Value Type'])

    def test_value(self):
        self.assertIsInstance(self.area_field_without_tags.value, str)
        self.assertEqual(self.area_field_with_tags.value, 'selection on page 2')
        self.assertEqual(self.area_field_without_tags.value, 'sample_value')

    def test__field_id(self):
        self.assertEqual(self.area_field_with_tags.field_id, '5e41a093f4b20400137938d9')
        self.assertIsNone(self.area_field_without_tags.field_id)

    def test__construct_from_raw(self):
        self.assertAlmostEqual(self.area_field_with_tags.tags[0].left, 9.16577157178661)

        self.assertEqual(self.area_field_without_tags.name, 'Table')
        self.assertEqual(len(self.area_field_without_tags.tags), 0)

        # invalid raw area
        self.invalid_raw_1 = deepcopy(self.raw_area_field_with_group_key)
        self.invalid_raw_1.pop(IqDocumentKeysEnum.name.value)
        self.invalid_raw_2 = deepcopy(self.raw_area_field_with_group_key)

        with self.assertRaises(KeyError):
            AreaField.construct_from_raw(raw=self.invalid_raw_1,
                                         pages=self.pages)
        # with self.assertRaises(KeyError):
        #     # invalid page number
        #     AreaField.construct_from_raw(raw=self.raw_area_field_with_group_key,
        #                                  pages={3: create_dummy_page(3)})

    def test_to_dict(self):
        to_dict_keys = [IqFieldKeyEnum.name.value, IqFieldKeyEnum.data_type.value,
                        IqFieldKeyEnum.value.value, ID, IqFieldKeyEnum.tags.value, IqFieldKeyEnum.group_key.value]

        raw_area_field_1 = deepcopy(self.raw_area_field_with_group_key)
        field_dict = self.area_field_with_tags.to_dict()

        self.assertIsInstance(field_dict[IqDocumentKeysEnum.tags.value][0], dict)
        self.assertEqual(sorted(field_dict.keys()), sorted(to_dict_keys))

        for key in field_dict:
            if key in [IqFieldKeyEnum.name.value, IqFieldKeyEnum.group_key.value, IqFieldKeyEnum.data_type.value]:
                self.assertEqual(field_dict[key], raw_area_field_1[key])

        self.assertEqual(field_dict[IqFieldKeyEnum.value.value],
                         raw_area_field_1[IqFieldKeyEnum.tags.value][0][IqFieldKeyEnum.value.value])
        self.assertEqual(field_dict[ID], str(self.raw_area_field_with_group_key[ID]))

    def test_group_key(self):
        self.area_field_with_tags.group_key = 'abc123'
        self.assertEqual(self.area_field_with_tags.group_key, 'abc123')

        self.area_field_with_tags.group_key = 'ABCDEF'
        self.assertEqual(self.area_field_with_tags.group_key, 'ABCDEF')

        self.area_field_without_tags.group_key = 'ABCDEF'
        self.assertEqual(self.area_field_without_tags.group_key, 'ABCDEF')

        self.area_field_with_tags.group_key = 1
        self.assertEqual(self.area_field_with_tags.group_key, '1')

        self.area_field_with_tags.group_key = True
        self.assertEqual(self.area_field_with_tags.group_key, 'True')

        with self.assertRaises(ValidationError):
            self.area_field_with_tags.group_key = ['abc']

    def test___repr__(self):
        self.assertEqual(self.area_field_with_tags.__repr__(), '<AreaField: Table: selection on page 2>')
        self.assertEqual(self.area_field_without_tags.__repr__(), '<AreaField: Table: >')

    def test___str__(self):
        self.assertEqual(self.area_field_without_tags.__str__(), '')
        self.assertEqual(self.area_field_with_tags.__str__(), 'selection on page 2')

    def test_confidence(self):
        self.assertAlmostEqual(self.area_field_with_tags.confidence, -1.0)
