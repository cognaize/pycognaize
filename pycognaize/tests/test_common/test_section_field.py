import json
import os
import unittest
from copy import deepcopy

from pycognaize.common.enums import IqFieldKeyEnum
from pycognaize.document.field import SectionField
from pycognaize.document.page import create_dummy_page
from pycognaize.tests.resources import RESOURCE_FOLDER


class TestSectionField(unittest.TestCase):

    def setUp(self) -> None:
        doc_id = '632c61fc86d52800197d03f3'
        self.snap_storage_path = os.path.join('dir')
        with open(os.path.join(RESOURCE_FOLDER, 'snapshots', doc_id, 'document.json')) as document_json:
            self.data = json.load(document_json)

        self.raw_section = self.data['input_fields']['section'][0]
        section_elem = self.raw_section['tags'][0]
        page_n = section_elem['section']['start']['page']
        self.pages = {page_n: create_dummy_page(page_n=page_n,
                                                path=self.snap_storage_path)}
        self.section_field = SectionField.construct_from_raw(self.raw_section, self.pages)

    def test_construct_from_raw(self):
        self.assertEqual(self.section_field.name, 'Section')
        self.assertEqual(self.section_field._ocr_value, '')
        self.assertEqual(self.section_field.field_id, '6315e0cbdcbc3e484997c09c')
        self.assertEqual(self.section_field.value, '')
        self.assertEqual(len(self.section_field.tags), 2)

        wrong_raw = deepcopy(self.raw_section)
        wrong_raw['tags'][0]['section']['start']['left'] = 'ddd'
        wrong_section_field = SectionField.construct_from_raw(wrong_raw, self.pages)
        self.assertEqual(len(wrong_section_field.tags), 1)

    def test_start(self):
        start = self.section_field.start
        self.assertAlmostEqual(start.top, 9.150914913083255)
        self.assertAlmostEqual(start._left, 0.0)
        self.assertAlmostEqual(start._height, 0.15)
        self.assertAlmostEqual(start._width, 100.0)

    def test_end(self):
        end = self.section_field.end
        self.assertAlmostEqual(end.top, 15.873376029277221)
        self.assertAlmostEqual(end._left, 0.0)
        self.assertAlmostEqual(end._height, 0.15)
        self.assertAlmostEqual(end._width, 100.0)

    def test___repr__(self):
        self.assertEqual(repr(self.section_field),
                         f"<{self.section_field.__class__.__name__}:"
                         f" {self.raw_section[IqFieldKeyEnum.name.value]}>")

    def test___str__(self):
        self.assertEqual(str(self.section_field),
                         f"<{self.section_field.__class__.__name__}: {self.section_field.name}>")

    def test_to_dict(self):
        dict = self.section_field.to_dict()
        raw = self.raw_section
        keys = [IqFieldKeyEnum.name.value, IqFieldKeyEnum.group_key.value, IqFieldKeyEnum.group.value]
        for key in keys:
            self.assertEqual(dict[key], raw[key])


if __name__ == '__main__':
    unittest.main()
