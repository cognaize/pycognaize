import json
import unittest
from copy import deepcopy

from pycognaize.document.html_info import HTML

from pycognaize.common.enums import IqDocumentKeysEnum, IqFieldKeyEnum, ID
from pycognaize.document.field import LinkField
from pycognaize.document.page import create_dummy_page
from pycognaize.tests.resources import RESOURCE_FOLDER


class TestLinkField(unittest.TestCase):

    def setUp(self):
        with open(RESOURCE_FOLDER + '/snapshots/6405fdd7420ed0001184e4f3/document.json') as document_json:
            self.data = json.load(document_json)

        self.html = HTML(path=(
            RESOURCE_FOLDER + '/snapshots/6405fdd7420ed0001184e4f3'),
                         document_id='6405fdd7420ed0001184e4f3')

        self.raw_link1 = self.data['input_fields']['main_document_url'][0]
        self.raw_link2 = self.data['input_fields']['main_document_url'][1]
        self.raw_link3 = self.data['input_fields']['supplement_document_url'][1]

        self.pages = {page_num: create_dummy_page(page_n=page_num) for page_num in range(1, 30)}

        self.link_field_1 = LinkField.construct_from_raw(raw=self.raw_link1, pages=self.pages, html=self.html)
        self.link_field_2 = LinkField.construct_from_raw(raw=self.raw_link2, pages=self.pages, html=self.html)
        self.link_field_3 = LinkField.construct_from_raw(raw=self.raw_link3, pages=self.pages, html=self.html)
        self.link_field_4 = LinkField(name='', value='6406023e000ed0001155feec')

    def test___str__(self):
        self.assertEqual(str(self.link_field_1), '6406023e420ed0001184feec')
        self.assertEqual(str(self.link_field_3), 'http://www.iaasa.ie/getmedia/b23890131cf6458b9b8fa98202dc9c3a/')

    def test___repr__(self):
        repr_str_2 = '<LinkField: Main Document: field value - https://uat.cognaize.com/browse/62853fcaf22a6700138cb7d0: tag value - >'
        self.assertEqual(repr(self.link_field_2), repr_str_2)

        repr_str_3 = '<LinkField: Supplement Document: field value - : tag value - http://www.iaasa.ie/getmedia/b23890131cf6458b9b8fa98202dc9c3a/>'
        self.assertEqual(repr(self.link_field_3), repr_str_3)

    def test__field_id(self):
        self.assertEqual(self.link_field_1._field_id, '645b722a2ff9810011de87a6')
        self.assertIsNone(self.link_field_4._field_id)

    def test_value(self):
        self.assertIsInstance(self.link_field_1.value, str)
        self.assertEqual(self.link_field_3.value, 'http://www.iaasa.ie/getmedia/b23890131cf6458b9b8fa98202dc9c3a/')
        self.assertEqual(self.link_field_4.value, '6406023e000ed0001155feec')

    def test__construct_from_raw(self):
        self.assertEqual(self.link_field_1.name, 'Main Document')
        self.assertEqual(self.link_field_3.tags[0].raw_ocr_value, 'http://www.iaasa.ie/getmedia/b23890131cf6458b9b8fa98202dc9c3a/')
        self.assertNotEqual(self.link_field_3.tags[0].top, '45.5%')

    def test_to_dict(self):
        dict_2 = self.link_field_2.to_dict()
        self.check_keys(dict_2)

        dict_3 = self.link_field_3.to_dict()
        self.check_keys(dict_3)

        dict_4 = self.link_field_4.to_dict()

        self.assertIsInstance(dict_3[IqDocumentKeysEnum.tags.value][0], dict)
        self.assertEqual(len(dict_2[IqDocumentKeysEnum.tags.value]), 0)
        self.assertEqual(len(dict_3[IqDocumentKeysEnum.tags.value]), 1)
        self.assertEqual(len(dict_4.keys()), 5)
        self.assertEqual(dict_2[IqFieldKeyEnum.group.value], 'Linked Documents')

        invalid_field = deepcopy(self.link_field_3)
        invalid_field.tags[0]._right = 'string'
        with self.assertRaises(TypeError):
            invalid_field.to_dict()

    def check_keys(self, test_dict):
        to_dict_keys = [IqFieldKeyEnum.name.value, IqFieldKeyEnum.data_type.value, ID, IqFieldKeyEnum.value.value,
                        IqFieldKeyEnum.tags.value, IqFieldKeyEnum.group_key.value, IqFieldKeyEnum.group.value]
        self.assertEqual(sorted(test_dict.keys()), sorted(to_dict_keys))
