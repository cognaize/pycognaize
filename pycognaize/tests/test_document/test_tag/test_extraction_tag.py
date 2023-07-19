import copy
import json
import unittest
from copy import deepcopy

from pycognaize.document.page import create_dummy_page
from pycognaize.document.tag import ExtractionTag
from pycognaize.tests.resources import RESOURCE_FOLDER
from pycognaize.tests.resources.field_and_tag_samples import raw_date_tag, invalid_raw_value_tag, \
    invalid_raw_text_tag
from pycognaize.tests.resources import RESOURCE_FOLDER
from pycognaize import Snapshot

class TestExtractionTag(unittest.TestCase):

    def setUp(self):
        self.date_format_1 = '%Y-%m-%d-%H.%M.%S'
        self.date_format_2 = '%m/%d/%Y'
        self.date_format_3 = '%m.%d.%Y'
        self.date_format_4 = '%b %d %Y'

        self.page = create_dummy_page()

        with open(RESOURCE_FOLDER + '/snapshots/60f554497883ab0013d9d906/document.json') as document_json:
            self.data = json.load(document_json)
        with open(RESOURCE_FOLDER + '/snapshots/63d4486c0e3fe60011fe3a75/document.json') as document_json:
            self.data1 = json.load(document_json)
        snapshot = Snapshot(RESOURCE_FOLDER + '/snapshots')
        doc = snapshot.documents['63d4486c0e3fe60011fe3a75']

        self.ext_tag_dict_1 = deepcopy(self.data['input_fields']['ref'][0]['tags'][0])
        self.ext_tag_dict_2 = deepcopy(self.data['input_fields']['paragraph'][0]['tags'][0])
        self.ext_tag_dict_3 = deepcopy(self.data['input_fields']['ref'][7]['tags'][0])
        self.ext_tag_dict_4 = deepcopy(self.data['input_fields']['ref'][9]['tags'][0])
        self.ext_tag_dict_5 = deepcopy(self.data['input_fields']['paragraph'][9]['tags'][0])
        self.ext_tag_dict_6 = deepcopy(self.data['input_fields']['ref'][1]['tags'][0])
        self.ext_tag_dict_7 = deepcopy(self.data['input_fields']['ref'][2]['tags'][0])
        self.ext_tag_dict_8 = deepcopy(self.data['input_fields']['ref'][3]['tags'][0])
        self.ext_tag_dict_9 = deepcopy(self.data['input_fields']['ref'][4]['tags'][0])
        self.ext_tag_dict_10 = deepcopy(self.data['input_fields']['ref'][5]['tags'][0])
        self.ext_tag_dict_11 = deepcopy(self.data['input_fields']['ref'][6]['tags'][0])
        self.ext_tag_dict_12 = deepcopy(self.data['input_fields']['ref'][8]['tags'][0])
        self.ext_tag_dict_13 = deepcopy(self.data['input_fields']['ref'][10]['tags'][0])
        self.ext_tag_dict_14 = deepcopy(self.data['input_fields']['ref'][11]['tags'][0])
        self.ext_tag_dict_15 = deepcopy(self.data['input_fields']['paragraph'][1]['tags'][0])
        self.ext_tag_dict_16 = deepcopy(self.data['input_fields']['paragraph'][2]['tags'][0])
        self.ext_tag_dict_17 = deepcopy(self.data['input_fields']['paragraph'][3]['tags'][0])
        self.ext_tag_dict_18 = deepcopy(self.data['input_fields']['paragraph'][10]['tags'][0])
        self.ext_tag_dict_19 = deepcopy(self.data['input_fields']['paragraph'][11]['tags'][0])
        self.ext_tag_dict_20 = deepcopy(self.data['input_fields']['paragraph'][3]['tags'][1])
        self.ext_tag_dict_21 = deepcopy(self.data['input_fields']['paragraph'][3]['tags'][2])
        self.ext_tag_dict_22 = deepcopy(self.data['input_fields']['paragraph'][4]['tags'][0])
        self.ext_tag_dict_23 = deepcopy(self.data['input_fields']['paragraph'][5]['tags'][0])
        self.ext_tag_dict_24 = deepcopy(self.data['input_fields']['paragraph'][6]['tags'][0])
        self.ext_tag_dict_25 = deepcopy(self.data['input_fields']['paragraph'][7]['tags'][0])
        self.ext_tag_dict_26 = deepcopy(self.data['input_fields']['paragraph'][8]['tags'][0])
        self.ext_tag_dict_27 = deepcopy(self.data1['output_fields']['v_other_income_is__current'][0]['tags'][0])
        self.ext_tag_dict_28 = deepcopy(self.data1['output_fields']["v_interest_income_is__tr"][0]['tags'][0])

        self.ext_tag_1 = ExtractionTag.construct_from_raw(self.ext_tag_dict_1,
                                                          page=create_dummy_page(self.ext_tag_dict_1['page']))
        self.ext_tag_2 = ExtractionTag.construct_from_raw(self.ext_tag_dict_2,
                                                          page=create_dummy_page(self.ext_tag_dict_2['page']))
        self.ext_tag_3 = ExtractionTag.construct_from_raw(self.ext_tag_dict_3,
                                                          page=create_dummy_page(self.ext_tag_dict_3['page']))
        self.ext_tag_4 = ExtractionTag.construct_from_raw(self.ext_tag_dict_4,
                                                          page=create_dummy_page(self.ext_tag_dict_4['page']))
        self.ext_tag_5 = ExtractionTag.construct_from_raw(self.ext_tag_dict_5,
                                                          page=create_dummy_page(self.ext_tag_dict_5['page']))
        self.ext_tag_6 = ExtractionTag.construct_from_raw(self.ext_tag_dict_6,
                                                          page=create_dummy_page(self.ext_tag_dict_6['page']))
        self.ext_tag_7 = ExtractionTag.construct_from_raw(self.ext_tag_dict_7,
                                                          page=create_dummy_page(self.ext_tag_dict_7['page']))
        self.ext_tag_8 = ExtractionTag.construct_from_raw(self.ext_tag_dict_8,
                                                          page=create_dummy_page(self.ext_tag_dict_8['page']))
        self.ext_tag_9 = ExtractionTag.construct_from_raw(self.ext_tag_dict_9,
                                                          page=create_dummy_page(self.ext_tag_dict_9['page']))
        self.ext_tag_10 = ExtractionTag.construct_from_raw(self.ext_tag_dict_10,
                                                           page=create_dummy_page(self.ext_tag_dict_10['page']))
        self.ext_tag_11 = ExtractionTag.construct_from_raw(self.ext_tag_dict_11,
                                                           page=create_dummy_page(self.ext_tag_dict_11['page']))
        self.ext_tag_12 = ExtractionTag.construct_from_raw(self.ext_tag_dict_12,
                                                           page=create_dummy_page(self.ext_tag_dict_12['page']))
        self.ext_tag_13 = ExtractionTag.construct_from_raw(self.ext_tag_dict_13,
                                                           page=create_dummy_page(self.ext_tag_dict_13['page']))
        self.ext_tag_14 = ExtractionTag.construct_from_raw(self.ext_tag_dict_14,
                                                           page=create_dummy_page(self.ext_tag_dict_14['page']))
        self.ext_tag_15 = ExtractionTag.construct_from_raw(self.ext_tag_dict_15,
                                                           page=create_dummy_page(self.ext_tag_dict_15['page']))
        self.ext_tag_16 = ExtractionTag.construct_from_raw(self.ext_tag_dict_16,
                                                           page=create_dummy_page(self.ext_tag_dict_16['page']))
        self.ext_tag_17 = ExtractionTag.construct_from_raw(self.ext_tag_dict_17,
                                                           page=create_dummy_page(self.ext_tag_dict_17['page']))
        self.ext_tag_18 = ExtractionTag.construct_from_raw(self.ext_tag_dict_18,
                                                           page=create_dummy_page(self.ext_tag_dict_18['page']))
        self.ext_tag_19 = ExtractionTag.construct_from_raw(self.ext_tag_dict_19,
                                                           page=create_dummy_page(self.ext_tag_dict_19['page']))
        self.ext_tag_20 = ExtractionTag.construct_from_raw(self.ext_tag_dict_20,
                                                           page=create_dummy_page(self.ext_tag_dict_20['page']))
        self.ext_tag_21 = ExtractionTag.construct_from_raw(self.ext_tag_dict_21,
                                                           page=create_dummy_page(self.ext_tag_dict_21['page']))
        self.ext_tag_22 = ExtractionTag.construct_from_raw(self.ext_tag_dict_22,
                                                           page=create_dummy_page(self.ext_tag_dict_22['page']))
        self.ext_tag_23 = ExtractionTag.construct_from_raw(self.ext_tag_dict_23,
                                                           page=create_dummy_page(self.ext_tag_dict_23['page']))
        self.ext_tag_24 = ExtractionTag.construct_from_raw(self.ext_tag_dict_24,
                                                           page=create_dummy_page(self.ext_tag_dict_24['page']))
        self.ext_tag_25 = ExtractionTag.construct_from_raw(self.ext_tag_dict_25,
                                                           page=create_dummy_page(self.ext_tag_dict_25['page']))
        self.ext_tag_26 = ExtractionTag.construct_from_raw(self.ext_tag_dict_26,
                                                           page=create_dummy_page(self.ext_tag_dict_26['page']))
        self.ext_tag_27 = ExtractionTag.construct_from_raw(self.ext_tag_dict_27, page = doc.pages[19])
        self.ext_tag_28 = ExtractionTag.construct_from_raw(self.ext_tag_dict_28, page = doc.pages[19])

        self.invalid_numeric_ext_tag = ExtractionTag(left=11.1, right=13.1, top=10, bottom=13,
                                                     page=copy.deepcopy(self.page),
                                                     raw_value='100.1%', raw_ocr_value=None)
        self.date_ext_ext_tag_1 = ExtractionTag(left=11.1, right=13.1, top=10, bottom=13,
                                                page=create_dummy_page(),
                                                raw_value='2020-04-14-17.36.21', raw_ocr_value='Dec 20 2020'
                                                )
        self.date_ext_ext_tag_2 = ExtractionTag(left=11.1, right=13.1, top=10, bottom=13,
                                                page=create_dummy_page(),
                                                raw_value='04/14/2020', raw_ocr_value='04.14.2020',
                                                )

        self.raw_date_tag = raw_date_tag
        self.invalid_raw_value_tag = invalid_raw_value_tag
        self.invalid_raw_text_tag = invalid_raw_text_tag

    def test_raw_value(self):
        self.assertEqual(self.ext_tag_1.raw_value, '99.')
        self.assertEqual(self.date_ext_ext_tag_1.raw_value, '2020-04-14-17.36.21')

    def test_raw_ocr_value(self):
        self.assertNotEqual(self.ext_tag_3.raw_ocr_value, '145. ')
        self.assertIsNone(self.invalid_numeric_ext_tag.raw_ocr_value)

    def test_coordinates(self):
        self.assertAlmostEqual(self.ext_tag_1.right, 12.960973863229503)
        self.assertAlmostEqual(self.ext_tag_1.top, 26.42328894018314)
        self.assertNotEqual(self.ext_tag_1.bottom, "27.58753347203029")

    def test__validate_date(self):
        self.date_ext_ext_tag_1._validate_date(self.date_format_1)
        self.assertFalse(self.date_ext_ext_tag_1.has_value_exception)
        self.assertTrue(self.date_ext_ext_tag_1.has_raw_value_exception)

        self.date_ext_ext_tag_2._validate_date(self.date_format_3)
        self.assertTrue(self.date_ext_ext_tag_2.has_value_exception)

        self.assertFalse(self.date_ext_ext_tag_2.has_raw_value_exception)

    def test__validate_numeric(self):
        self.ext_tag_1._validate_numeric()
        self.assertFalse(self.ext_tag_1.has_value_exception)

        self.invalid_numeric_ext_tag._validate_numeric()
        self.assertTrue(self.invalid_numeric_ext_tag.has_value_exception)
        self.assertFalse(self.invalid_numeric_ext_tag.has_raw_value_exception)

    def test__construct_from_raw(self):
        ExtractionTag.construct_from_raw(raw=self.ext_tag_dict_2, page=self.page)
        with self.assertRaises(KeyError):
            # no ocr value
            ExtractionTag.construct_from_raw(raw=self.invalid_raw_value_tag, page=self.page)

        with self.assertRaises(KeyError):
            ExtractionTag.construct_from_raw(raw=self.invalid_raw_text_tag, page=self.page)

    def test_to_dict(self):
        num_dict = self.ext_tag_1.to_dict()
        date_dict = self.date_ext_ext_tag_1.to_dict()
        self.assertEqual(num_dict.keys(), date_dict.keys())

        invalid_field = deepcopy(self.ext_tag_1)
        invalid_field._bottom = 'INVALID STRING TYPE'
        with self.assertRaises(TypeError):
            invalid_field.to_dict()

    def test_hshift(self):
        self.assertAlmostEqual(self.ext_tag_1.hshift(0.1).left, 10.912746151092016)
        self.assertAlmostEqual(self.ext_tag_1.hshift(0.1).right, 13.060973863229503)
        self.assertAlmostEqual(self.ext_tag_1.hshift(89).left, 99.81274615109201)
        self.assertAlmostEqual(self.ext_tag_1.hshift(89).right, 100)
        self.assertAlmostEqual(self.ext_tag_1.hshift(-.1).left, 10.712746151092016)
        self.assertAlmostEqual(self.ext_tag_1.hshift(-.1).right,  12.860973863229503)
        self.assertAlmostEqual(self.ext_tag_1.hshift(-15).left, 0)
        self.assertAlmostEqual(self.ext_tag_1.hshift(-15).right, 0)

    def test_vshift(self):
        self.assertAlmostEqual(self.ext_tag_1.vshift(2).top,28.42328894018314)
        self.assertAlmostEqual(self.ext_tag_1.vshift(2).bottom, 29.58753347203029)

        self.assertAlmostEqual(self.ext_tag_1.vshift(91).top, 100)
        self.assertAlmostEqual(self.ext_tag_1.vshift(91).bottom, 100)
        self.assertAlmostEqual(self.ext_tag_1.vshift(-1).top, 25.42328894018314)
        self.assertAlmostEqual(self.ext_tag_1.vshift(-1).bottom, 26.58753347203029)

        self.assertAlmostEqual(self.ext_tag_1.vshift(-30).top, 0)
        self.assertAlmostEqual(self.ext_tag_1.vshift(-30).bottom, 0)

    def test_shift(self):
        self.assertAlmostEqual(self.ext_tag_18.shift(1, -1).left, 15.219694276573053)
        self.assertAlmostEqual(self.ext_tag_18.shift(1, -1).right, 21.90295058656239)
        self.assertAlmostEqual(self.ext_tag_18.shift(1, -1).top, 26.99441018914645)
        self.assertAlmostEqual(self.ext_tag_18.shift(1, -1).bottom, 28.552447381001997)

        self.assertAlmostEqual(self.ext_tag_15.shift(10, -37).left, 18.306480486931616)
        self.assertAlmostEqual(self.ext_tag_15.shift(10, -37).right, 100)
        self.assertAlmostEqual(self.ext_tag_15.shift(10, -37).top, 0)
        self.assertAlmostEqual(self.ext_tag_15.shift(10, -37).bottom, 2.33121744544502)


    def test___contains__(self):
        self.assertTrue(self.ext_tag_1 in self.ext_tag_2)
        self.assertFalse(self.ext_tag_2 in self.ext_tag_1)
        self.assertFalse(self.ext_tag_6 in self.ext_tag_15)
        self.assertFalse(self.ext_tag_13 in self.ext_tag_2)
        with self.assertRaises(NotImplementedError):
            self.ext_tag_11.__contains__('5')

    def test___and__(self):
        self.assertAlmostEqual(round(self.ext_tag_1 & self.ext_tag_2, 2), 2.5)
        self.assertEqual(round(self.ext_tag_1 & self.ext_tag_12, 2), 0)
        self.assertEqual(self.ext_tag_15 & self.ext_tag_25, 0)
        with self.assertRaises(NotImplementedError):
            self.ext_tag_11 & '5'

    def test___or__(self):
        self.assertAlmostEqual(round(self.ext_tag_1 | self.ext_tag_2, 2), 519.7)
        self.assertAlmostEqual(round(self.ext_tag_9 | self.ext_tag_22, 2), 170.48)
        self.assertEqual(self.ext_tag_15 | self.ext_tag_25, 0)
        with self.assertRaises(NotImplementedError):
            self.ext_tag_11 | '5'

    def test_iou(self):
        self.assertAlmostEqual(round(self.ext_tag_1.iou(self.ext_tag_2), 3), 0.005)
        self.assertEqual(self.ext_tag_1.iou(self.ext_tag_7), 0)
        self.assertEqual(self.ext_tag_1 | self.ext_tag_5, 0)
        with self.assertRaises(NotImplementedError):
            self.ext_tag_11.iou('5')

    def test_is_in_rectangle(self):
        self.assertFalse(self.ext_tag_7.is_in_rectangle(self.ext_tag_16, 1))
        self.assertTrue(self.ext_tag_7.is_in_rectangle(self.ext_tag_16, .5))
        self.assertFalse(self.ext_tag_16.is_in_rectangle(self.ext_tag_7, 1))
        self.assertFalse(self.ext_tag_13.is_in_rectangle(self.ext_tag_8, 0.2))
        self.assertFalse(self.ext_tag_13.is_in_rectangle(self.ext_tag_2, 0.5))
        with self.assertRaises(ValueError):
            self.ext_tag_11.is_in_rectangle(self.ext_tag_7, -1)
        with self.assertRaises(NotImplementedError):
            self.ext_tag_11.is_in_rectangle(1, 0.1)

    def test___add__(self):
        self.assertAlmostEqual((self.ext_tag_1 + self.ext_tag_2).left, 10.025062656641603)
        self.assertAlmostEqual((self.ext_tag_1 + self.ext_tag_2).right,  92.15896885069819)
        self.assertAlmostEqual((self.ext_tag_1 + self.ext_tag_2).top, 25.765237683052145)
        self.assertAlmostEqual((self.ext_tag_1 + self.ext_tag_2).bottom, 32.092653617004046)
        self.assertAlmostEqual((self.ext_tag_27 + self.ext_tag_28).left,12.3525)
        self.assertEqual((self.ext_tag_27 + self.ext_tag_27).raw_ocr_value, '11,916')
        self.assertEqual((self.ext_tag_27 + self.ext_tag_28).raw_ocr_value,'Interest on loans with Group undertakings 21,776 Fair value gain on derivatives - interest rate swaps 11,916')
        with self.assertRaises(ValueError):
            self.ext_tag_1 + self.ext_tag_3

    def test___radd__(self):
        self.assertAlmostEqual(sum([self.ext_tag_17, self.ext_tag_20, self.ext_tag_21]).left, 6.301467955603295)
        self.assertAlmostEqual(sum([self.ext_tag_17, self.ext_tag_20, self.ext_tag_21]).right, 44.68313641245972)
        self.assertAlmostEqual(sum([self.ext_tag_17, self.ext_tag_20, self.ext_tag_21]).top, 51.22675940127459)
        self.assertAlmostEqual(sum([self.ext_tag_17, self.ext_tag_20, self.ext_tag_21]).bottom, 57.452936680283266)

        with self.assertRaises(ValueError):
            sum([self.ext_tag_23, self.ext_tag_26])

    def test_intersects(self):
        self.assertTrue(self.ext_tag_1.intersects(self.ext_tag_2))
        self.assertTrue(self.ext_tag_6.intersects(self.ext_tag_15))
        self.assertTrue(self.ext_tag_7.intersects(self.ext_tag_16))
        self.assertTrue(self.ext_tag_8.intersects(self.ext_tag_17))
        self.assertTrue(self.ext_tag_17.intersects(self.ext_tag_8))
        self.assertTrue(self.ext_tag_20.intersects(self.ext_tag_17))
        self.assertTrue(self.ext_tag_9.intersects(self.ext_tag_22))
        self.assertTrue(self.ext_tag_10.intersects(self.ext_tag_23))
        self.assertTrue(self.ext_tag_11.intersects(self.ext_tag_24))
        self.assertTrue(self.ext_tag_24.intersects(self.ext_tag_11))
        self.assertTrue(self.ext_tag_12.intersects(self.ext_tag_26))
        self.assertTrue(self.ext_tag_14.intersects(self.ext_tag_19))
        self.assertTrue(self.ext_tag_19.intersects(self.ext_tag_14))
        self.assertFalse(self.ext_tag_2.intersects(self.ext_tag_5))
        self.assertFalse(self.ext_tag_20.intersects(self.ext_tag_21))
        self.assertFalse(self.ext_tag_15.intersects(self.ext_tag_25))


if __name__ == '__main__':
    unittest.main()
