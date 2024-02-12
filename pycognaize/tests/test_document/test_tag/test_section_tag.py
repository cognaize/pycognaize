import json
import unittest
from copy import deepcopy
from pycognaize import Snapshot
from pycognaize.document.tag.section_tag import SectionTag
from pycognaize.tests.resources import RESOURCE_FOLDER


class TestSectionTag(unittest.TestCase):
    def setUp(self) -> None:
        with open(
                RESOURCE_FOLDER + '/snapshots/60f554497883ab0013d9d906/document.json',
                encoding="utf8") as document_json:
            self.data = json.load(document_json)
        snapshot = Snapshot(RESOURCE_FOLDER + '/snapshots')
        doc = snapshot.documents['63d4486c0e3fe60011fe3a75']
        self.page = doc.pages
        self.ext_tag_dict = deepcopy(
            self.data['input_fields']['ref'][0]['tags'][0])
        self.tag_dict = SectionTag(self.ext_tag_dict["top"],
                                   self.ext_tag_dict["left"],
                                   self.ext_tag_dict["height"],
                                   self.ext_tag_dict["width"],
                                   self.ext_tag_dict["page"],
                                   "ExtractionTag")  # clarify number
        self.tag = self.tag_dict.construct_from_raw(self.ext_tag_dict,
                                                    self.page,
                                                    "ExtractionTag")  # clarify number

    def test_construct_from_raw(self):
        constructed_tag = self.tag.construct_from_raw(self.ext_tag_dict,
                                                      self.page,
                                                      "ExtractionTag")  # clarify number
        self.assertAlmostEqual(constructed_tag._height, 1.16424453184715)
        self.assertAlmostEqual(constructed_tag._width, 2.1482277121374866)
        self.assertAlmostEqual(constructed_tag._top, 26.42328894018314)
        self.assertAlmostEqual(constructed_tag._left, 10.812746151092016)

    # def test_vshift(self):
    #     tag = self.tag.vshift(3.3)
    #
    # def test_vertical_shift(self):
    #     tag = self.tag.vertical_shift(3.3)

    def test_confidence(self):
        self.assertEqual(len(self.tag.confidence.confidences), 0)

    def test_type(self):
        self.assertEqual(self.tag.type, "ExtractionTag")

    def test_to_dict(self):
        section_tag_dict = self.tag.to_dict()
        self.assertEqual(section_tag_dict["height"], "1.16424453184715%")
        self.assertEqual(section_tag_dict["width"], "2.1482277121374866%")
        self.assertEqual(section_tag_dict["top"], "26.42328894018314%")
        self.assertEqual(section_tag_dict["left"], "10.812746151092016%")


if __name__ == '__main__':
    unittest.main()
