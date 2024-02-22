import json
import os
import shutil
import unittest
import tempfile
from unittest import mock
from unittest.mock import MagicMock

from pycognaize.common.enums import StorageEnum
from pycognaize.common.utils import (
    intersects,
    is_float, convert_coord_to_num,
    stick_word_boxes,
    bytes_to_array,
    string_to_array,
    image_bytes_to_array,
    img_to_black_and_white,
    group_sequence, ConfusionMatrix,
    filter_out_nested_lines,
    directory_summary_hash,
)
from pycognaize.tests.resources import RESOURCE_FOLDER


class TestUtils(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.mkdtemp()

    def setUp(self) -> None:
        page_images_folder_path = os.path.join(RESOURCE_FOLDER, StorageEnum.image_folder.value)
        page_image_path = os.path.join(page_images_folder_path, "image_1.jpeg")

        with open(os.path.join(RESOURCE_FOLDER, 'ocr.json'), 'r') as f:
            self.ocr_data = json.load(f)

        with open(page_image_path, 'rb') as f:
            self.page_image_bytes = f.read()

    def test_is_float(self):
        str_number = "NaN"
        str_number_1 = "7"
        str_number_2 = "Float"
        str_number_3 = "0"
        str_number_4 = "1.67"
        str_number_5 = "1.67f"

        self.assertFalse(is_float(str_number))
        self.assertTrue(is_float(str_number_1))
        self.assertFalse(is_float(str_number_2))
        self.assertTrue(is_float(str_number_3))
        self.assertTrue(is_float(str_number_4))
        self.assertFalse(is_float(str_number_5))

    def test_convert_coord_to_num(self):
        result = convert_coord_to_num("5.69%")
        result_1 = convert_coord_to_num("5.69")
        result_2 = convert_coord_to_num(5.69)
        result_3 = convert_coord_to_num(80)

        self.assertAlmostEqual(result, 5.69)
        self.assertAlmostEqual(result_1, 5.69)
        self.assertAlmostEqual(result_2, 5.69)
        self.assertAlmostEqual(result_3, 80.0)
        with self.assertRaises(ValueError):
            convert_coord_to_num("l5.69m")
        with self.assertRaises(TypeError):
            convert_coord_to_num([23, 33])

    def test_stick_word_boxes(self):
        box_coord = {'left': 10, 'right': 300, 'top': 15, 'bottom': 500}
        box_coord_1 = {'left': 0, 'right': 0, 'top': 0, 'bottom': 0}
        box_coord_2 = {'left': 255, 'right': 255, 'top': 255, 'bottom': 255}
        box_coord_3 = {'left': 254, 'right': 254, 'top': 254, 'bottom': 254}
        box_coord_4 = {'left': 500, 'right': 600, 'top': 400, 'bottom': 523}
        box_coord_5 = {'left': -10, 'right': -300, 'top': -15, 'bottom': -523}

        self.assertListEqual(stick_word_boxes([box_coord], self.page_image_bytes),
                             [{'left': 219, 'right': 302, 'top': 70, 'bottom': 99}])
        self.assertListEqual(stick_word_boxes([box_coord_1], self.page_image_bytes),
                             [{'left': 0, 'right': 0, 'top': 0, 'bottom': 0}])
        self.assertListEqual(stick_word_boxes([box_coord_2], self.page_image_bytes),
                             [{'left': 255, 'right': 255, 'top': 255, 'bottom': 255}])
        self.assertListEqual(stick_word_boxes([box_coord_3], self.page_image_bytes),
                             [{'left': 254, 'right': 254, 'top': 254, 'bottom': 254}])
        self.assertListEqual(stick_word_boxes([box_coord], self.page_image_bytes, padding=2),
                             [{'left': 218, 'right': 305, 'top': 69, 'bottom': 100}])
        self.assertListEqual(stick_word_boxes([box_coord_4], self.page_image_bytes),
                             [{'left': 499, 'right': 602, 'top': 423, 'bottom': 443}])
        self.assertListEqual(stick_word_boxes([box_coord_5], self.page_image_bytes),
                             [{'left': 215, 'right': 1402, 'top': 553, 'bottom': 778}])
        self.assertIsInstance(stick_word_boxes([box_coord], self.page_image_bytes), list)
        for item in stick_word_boxes([box_coord], self.page_image_bytes):
            self.assertIsInstance(item, dict)
        self.assertEqual(len(stick_word_boxes([box_coord], self.page_image_bytes)), len([box_coord]))

    def test_image_bytes_to_array(self):
        img_array = image_bytes_to_array(img_str=self.page_image_bytes)

        self.assertEqual(img_array.size, 11220000)
        self.assertTrue(((img_array >= 0) & (img_array <= 255)).all())

    def test_img_to_black_and_white(self):
        img_array = image_bytes_to_array(img_str=self.page_image_bytes)
        binary_image = img_to_black_and_white(img_array=img_array)

        self.assertTrue(((binary_image == 0) | (binary_image == 255)).all())
        self.assertEqual(binary_image.shape, (2200, 1700))

    def test_group_sequence(self):
        test_list_1 = [1, 2, 3, 8, 15, 23, 24, 25, 10, 11, 13, 15]
        test_list_2 = list(range(10))

        sequence_list = [[1, 2, 3], [23, 24, 25], [10, 11]]

        self.assertEqual(list(group_sequence(test_list_1)), sequence_list)
        self.assertEqual(list(group_sequence(test_list_2)), [test_list_2])

    def test_f1(self):
        case_1 = ConfusionMatrix(0, 0, 0, 0)
        self.assertAlmostEqual(case_1.f1, 0)
        case_2 = ConfusionMatrix(1, 0, 0, 0)
        self.assertAlmostEqual(case_2.f1, 1.0)
        case_3 = ConfusionMatrix(7, 3, 6, 5)
        self.assertAlmostEqual(case_3.f1, 0.56)

    def test_precision(self):
        case_1 = ConfusionMatrix(0, 0, 0, 0)
        self.assertAlmostEqual(case_1.precision, 0)
        case_2 = ConfusionMatrix(1, 0, 0, 0)
        self.assertAlmostEqual(case_2.precision, 1.0)
        case_3 = ConfusionMatrix(7, 3, 6, 5)
        self.assertAlmostEqual(case_3.precision, 0.5384615384615384)

    def test_recall(self):
        case_1 = ConfusionMatrix(0, 0, 0, 0)
        self.assertAlmostEqual(case_1.recall, 0)
        case_2 = ConfusionMatrix(1, 0, 0, 0)
        self.assertAlmostEqual(case_2.recall, 1.0)
        case_3 = ConfusionMatrix(7, 3, 6, 5)
        self.assertAlmostEqual(case_3.recall, 0.5833333333333334)

    def test_accuracy(self):
        case_1 = ConfusionMatrix(0, 0, 0, 0)
        self.assertAlmostEqual(case_1.accuracy, 0)
        case_2 = ConfusionMatrix(1, 0, 0, 0)
        self.assertAlmostEqual(case_2.accuracy, 1.0)
        case_3 = ConfusionMatrix(7, 3, 6, 5)
        self.assertAlmostEqual(case_3.accuracy, 0.47619047619047616)

    def test_to_dict(self):
        case_1 = ConfusionMatrix(0, 0, 0, 0)
        self.assertDictEqual(case_1.to_dict(), {'TP': 0, 'TN': 0, 'FP': 0, 'FN': 0})
        case_2 = ConfusionMatrix(1, 0, 0, 0)
        self.assertDictEqual(case_2.to_dict(), {'TP': 1, 'TN': 0, 'FP': 0, 'FN': 0})
        case_3 = ConfusionMatrix(7, 3, 6, 5)
        self.assertDictEqual(case_3.to_dict(), {'TP': 7, 'TN': 3, 'FP': 6, 'FN': 5})

    def test_compute_metrics(self):
        case_1 = ConfusionMatrix(0, 0, 0, 0)
        self.assertDictEqual(case_1.compute_metrics(), {'confusion matrix': {'TP': 0, 'TN': 0, 'FP': 0, 'FN': 0},
                                                        'f1 score': 0, 'precision': 0, 'recall': 0, 'accuracy': 0})
        case_2 = ConfusionMatrix(1, 0, 0, 0)
        self.assertDictEqual(case_2.compute_metrics(), {'confusion matrix': {'TP': 1, 'TN': 0, 'FP': 0, 'FN': 0},
                                                        'f1 score': 1.0,
                                                        'precision': 1.0,
                                                        'recall': 1.0,
                                                        'accuracy': 1.0})
        case_3 = ConfusionMatrix(7, 3, 6, 5)
        self.assertDictEqual(case_3.compute_metrics(), {'confusion matrix': {'TP': 7, 'TN': 3, 'FP': 6, 'FN': 5},
                                                        'f1 score': 0.56,
                                                        'precision': 0.5384615384615384,
                                                        'recall': 0.5833333333333334,
                                                        'accuracy': 0.47619047619047616})

    def test_intersects(self):
        self.assertTrue(intersects({"left": 10.812746151092016, "right": 12.960973863229503, "top": 26.42328894018314,
                                    "bottom": 27.58753347203029, 'ocr_text': '99.', 'word_id_number':
                                        '60f5561fc23c8f0000e05d1a'}, 10.025062656641603, 92.15896885069819,
                                   25.765237683052145, 32.092653617004046))
        self.assertTrue(intersects({"left": 10.526315789473683, "right": 14.106695309702827, "top": 35.68662586748872,
                                    "bottom": 38.36945022348433, 'ocr_text': '101.', 'word_id_number':
                                        '60f55634c23c8f0000e05d1f'}, 8.306480486931616, 91.87253848907984,
                                   36.24343846967649, 39.33121744544502))
        self.assertTrue(intersects({"left": 9.595417114214106, "right": 14.321518080916576, "top": 44.140053555248464,
                                    "bottom": 45.75987203434015, 'ocr_text': '103.', 'word_id_number':
                                        '60f55656c23c8f0000e05d25'}, 11.027568922305765, 91.01324740422484,
                                   43.53262162558909, 47.177213203545385))
        self.assertTrue(intersects({"left": 10.6695, "right": 13.891839999999998, "top": 50.35425101214575,
                                    "bottom": 53.593117408906885, 'ocr_text': '105.', 'word_id_number':
                                        '60f5566ec23c8f0000e05d2a'}, 8.091657715717867, 44.68313641245972,
                                   51.22675940127459, 53.20091317266758))
        self.assertTrue(intersects({"left": 8.091657715717867, "right": 44.68313641245972, "top": 51.22675940127459,
                                    "bottom": 53.20091317266758, 'ocr_text': '105. Banks are divided into the ',
                                    'word_id_number': '60f55673c23c8f0000e05d2b'}, 10.6695, 13.891839999999998,
                                   50.35425101214575, 53.593117408906885))
        self.assertTrue(intersects({"left": 6.301467955603295, "right": 26.781238811313997, "top": 52.69471989795144,
                                    "bottom": 54.97258963417412, 'ocr_text': '(a) Commercial banks.', 'word_id_number':
                                        '60f556a9c23c8f0000e05d2f'}, 8.091657715717867, 44.68313641245972,
                                   51.22675940127459, 53.20091317266758))
        self.assertTrue(intersects({"left": 9.452201933404941, "right": 14.035087719298247, "top": 63.426017321933855,
                                    "bottom": 64.8939778186107, 'ocr_text': '107.', 'word_id_number':
                                        '60f55730c23c8f0000e05d32'}, 10.307802433786685, 87.18682891911239, 63.9322,
                                   66.10883))
        self.assertTrue(intersects({"left": 10.1158, "right": 14.077, "top": 86.8607, "bottom": 88.29642659391153,
                                    'ocr_text': '111.', 'word_id_number': '60f55876c23c8f0000e05d40'},
                                   13.1221, 89.43227672151127, 86.8464, 88.29674))
        self.assertFalse(intersects({"left": 10.025062656641603, "right": 92.15896885069819, "top": 25.765237683052145,
                                     "bottom": 32.092653617004046, 'ocr_text': 'This division, Division 1.1',
                                     'word_id_number': '60f55624c23c8f0000e05d1b'}, 14.361891219338785,
                                    30.430145751866334, 10.604704757468404, 12.162741949323951))
        self.assertFalse(intersects({"left": 6.301467955603295, "right": 26.781238811313997, "top": 52.69471989795144,
                                     "bottom": 54.97258963417412, 'ocr_text': '(a) Commercial banks.',
                                     'word_id_number': '60f556a9c23c8f0000e05d2f'}, 10.383100608664519,
                                    25.635517364840673, 55.63064089130512, 57.452936680283266))

    def test_bytes_to_array(self):
        with self.assertWarns(DeprecationWarning):
            bytes_to_array(img_str=self.page_image_bytes)

    def test_string_to_array(self):
        with self.assertWarns(DeprecationWarning):
            string_to_array(img_str=self.page_image_bytes)

    def test_filter_out_nested_lines(self):
        lines = ['lines', 'next lines']
        nested_lines = filter_out_nested_lines(lines)
        self.assertEqual(nested_lines, [lines[1]])

    def test_directory_summary_hash(self):
        dir1 = os.path.join(self.temp_dir, "dir1")
        dir2 = os.path.join(self.temp_dir, "dir2")
        dir3 = os.path.join(dir1, "dir3")
        os.makedirs(dir1)
        os.makedirs(dir2)
        os.makedirs(dir3)
        text1 = "This is the content of the first text file."
        text2 = "This is the content of the second text file."
        text3 = "This is the content of the third text file."
        text4 = "This is the content of the fourth text file."
        with open(os.path.join(self.temp_dir, "file1.txt"), "w") as file1:
            file1.write(text1)
        with open(os.path.join(dir1, "file2.txt"), "w") as file2:
            file2.write(text2)
        with open(os.path.join(dir2, "file3.txt"), "w") as file3:
            file3.write(text3)
        with open(os.path.join(dir2, "file4.txt"), "w") as file4:
            file4.write(text4)
        random_path = 'random/path'
        hash_value1 = directory_summary_hash(dirname=self.temp_dir)
        dir_to_delete = os.path.join(self.temp_dir, "dir_to_delete")
        os.makedirs(dir_to_delete)
        hash_value2 = directory_summary_hash(dirname=self.temp_dir)
        os.rmdir(dir_to_delete)
        hash_value3 = directory_summary_hash(dirname=self.temp_dir)
        self.assertNotEqual(hash_value1, hash_value2)
        self.assertEqual(hash_value1, hash_value3)
        with self.assertRaises(TypeError):
            directory_summary_hash(dirname=random_path)

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(cls.temp_dir)
