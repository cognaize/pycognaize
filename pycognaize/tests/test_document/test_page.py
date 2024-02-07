import os
import shutil
import tempfile
import unittest
from copy import deepcopy

import numpy as np

import pycognaize
from pycognaize.common.enums import EnvConfigEnum, StorageEnum
from pycognaize.document.page import create_dummy_page, Page
from pycognaize.tests.resources import RESOURCE_FOLDER


class TestPage(unittest.TestCase):
    # set constants
    SNAPSHOT_PATH = os.path.join(tempfile.gettempdir(), 'local_snapshot')
    ORIGINAL_SNAPSHOT_PATH = os.environ.get(EnvConfigEnum.SNAPSHOT_PATH.value)

    @classmethod
    def setUpClass(cls) -> None:

        # set env variables
        os.environ[EnvConfigEnum.SNAPSHOT_PATH.value] = cls.SNAPSHOT_PATH
        cls.path = 'sample_snapshot_1'

        # local prepositioning
        cls.snap_path = os.path.join(cls.SNAPSHOT_PATH, cls.path)
        cls.images_folder_path = os.path.join(cls.snap_path, StorageEnum.image_folder.value)
        cls.ocr_folder_path = os.path.join(cls.snap_path, StorageEnum.ocr_folder.value)

        # images
        if os.path.exists(cls.images_folder_path):
            shutil.rmtree(cls.images_folder_path)
        os.makedirs(cls.images_folder_path)
        # resource_images_path: str = os.path.join(RESOURCE_FOLDER, StorageEnum.image_folder.value)
        cls.resource_images_path: str = RESOURCE_FOLDER + '/snapshots/60f554497883ab0013d9d906/images'
        for image in os.listdir(cls.resource_images_path):
            shutil.copyfile(os.path.join(cls.resource_images_path, image),
                            os.path.join(cls.images_folder_path, image))

        # ocr
        os.makedirs(cls.ocr_folder_path, exist_ok=True)
        cls.resource_data_path: str = RESOURCE_FOLDER + '/snapshots/60f554497883ab0013d9d906/data'
        for page_json in os.listdir(cls.resource_data_path):
            shutil.copyfile(os.path.join(cls.resource_data_path, page_json),
                            os.path.join(cls.ocr_folder_path, page_json))

    def setUp(self) -> None:
        self.page6 = Page(page_number=6, document_id='60f554497883ab0013d9d906', path=self.snap_path)
        self.page3 = create_dummy_page(page_n=3, path=self.snap_path)
        self.no_path_page = create_dummy_page(page_n=100, path="")
        self.empty_res = dict(words=[], paragraphs=[])

    def test_page_number(self):
        self.assertEqual(self.page6.page_number, 6)

    def test_path(self):
        self.assertEqual(self.page6.path, self.snap_path)

    def test_doc_id(self):
        self.assertEqual(self.page6.doc_id, '60f554497883ab0013d9d906')

    def test_ocr(self):
        with self.assertRaises(ValueError):
            self.no_path_page.get_ocr()
        self.assertEqual(set(self.page6.get_ocr().keys()), {'page', 'image', 'data'})

    def test___repr__(self):
        self.assertEqual(self.page6.__repr__(), '<Page 6>')
        self.assertEqual(self.page3.__repr__(), '<Page 3>')

    def test_ocr_tags(self):
        with self.assertRaises(ValueError):
            self.no_path_page.get_ocr()
        self.assertEqual(len(self.page6.ocr_tags['words']), 581)

    def test_line_tags(self):
        self.assertEqual(len(self.page3.line_tags), 44)
        self.assertEqual(len(self.page3.line_tags[0]), 20)
        self.assertEqual(self.page6.line_tags[1][0].left, 11.0397946084724)

    def test_get_page_data(self):
        with self.assertRaises(ValueError):
            self.no_path_page.get_page_data()

    def test_get_image(self):
        with self.assertRaises(ValueError):
            self.no_path_page.get_image()
        with open(self.resource_images_path + '/image_6.jpeg', 'rb') as image_6:
            image = image_6.read()
            self.assertEqual(self.page6.get_image(), image)
        # Unknown file case
        page3_copy = deepcopy(self.page3)
        page3_copy._image = None
        page3_copy._page_number = 3333
        with open(os.path.join(os.path.dirname(pycognaize.common.__file__), 'white_pixel.jpeg'), 'rb') as f:
            self.assertEqual(page3_copy.get_image(), f.read())

    def test_image_height(self):
        self.page6._image_height = None
        self.assertEqual(self.page6.image_height, self.page6.image_arr.shape[0])
        self.assertEqual(self.page3.image_height, 3306)
        self.assertEqual(self.page6._image_height, 3306)

    def test_image_width(self):
        self.page3._image_width = None
        self.assertEqual(self.page3.image_width, self.page3.image_arr.shape[1])
        self.assertEqual(self.page3.image_width, 2337)
        self.assertEqual(self.page3._image_width, 2337)

    def test_ocr_raw(self):
        self.page6._ocr_raw = None
        self.assertEqual(self.page6.ocr_raw, self.page6.get_ocr())
        self.assertIsNotNone(self.page6.ocr_raw)
        self.assertIsNotNone(self.page6._ocr_raw)

    def test_lines(self):
        self.assertEqual(len(self.page3.lines), 44)
        self.assertEqual(len(self.page6.lines[0]), 19)
        self.assertEqual(self.page6.lines[1][0]['ocr_text'], 'scope')

    def test_create_lines(self):
        no_tags = self.page6._create_lines(return_tags=True)
        self.assertIsInstance(no_tags[0][0], pycognaize.document.tag.extraction_tag.ExtractionTag)

    def test_search_text(self):
        area_dict = {'top': 1000, 'bottom': 1500, 'left': 200, 'right': 500}
        return_tags = self.page6.search_text(text='a', return_tags=True)
        self.assertIsInstance(return_tags[0][0], pycognaize.document.tag.extraction_tag.ExtractionTag)
        self.assertEqual(self.page6.search_text('Federal Deposit Insurance Act')[0]['top'], 2241)
        self.assertEqual(len(self.page6.search_text('WIRE TRANSFER')), 0)
        self.assertEqual(self.page3.search_text('Hi'), [])
        self.assertEqual(self.page3.search_text('Board', area=area_dict), self.page3.search_text('Board', area=None))
        self.assertEqual(self.page3.search_text('a', area=area_dict), [])
        self.assertGreater(len(self.page3.search_text('by', area=None)),
                           len(self.page3.search_text('by', area=area_dict)))
        self.assertEqual(len(self.page3.search_text('has (Added', area=area_dict)), 1)
        self.assertEqual(self.page3.search_text('has the menaning', area=area_dict), [])

    def test_extract_area_words(self):
        with self.assertRaises(ValueError):
            self.page6.extract_area_words(left=200, right=560, top=69, bottom=110, threshold=5)
        with self.assertRaises(ValueError):
            self.page3.extract_area_words(left=-200, right=560, top=69, bottom=110)
        with self.assertRaises(ValueError):
            self.page3.extract_area_words(left=200, right=200, top=69, bottom=110)
        with self.assertRaises(ValueError):
            self.page3.extract_area_words(left=-200, right=560, top=130, bottom=110)
        self.assertEqual(len(self.page6.extract_area_words(left=258, right=1151, top=594, bottom=635)), 8)
        self.assertDictEqual(self.page3.extract_area_words(left=257, right=425, top=5, bottom=41)[0],
                             {'left': 258, 'right': 424, 'top': 5, 'bottom': 41, 'ocr_text': 'committee',
                              'word_id_number': 0})
        with self.assertRaises(ValueError):
            self.page3.extract_area_words(left=240, right=200, top=69, bottom=110)
        with self.assertRaises(ValueError):
            self.page3.extract_area_words(left=200, right=180, top=69, bottom=40)
        with self.assertRaises(ValueError):
            self.page3.extract_area_words(left=200, right=560, top=110, bottom=110)
        with self.assertRaises(ValueError):
            self.page3.extract_area_words(left=200, right=560, top=111, bottom=110)

    def test_get_ocr(self):
        none_path_page = deepcopy(self.no_path_page)
        none_path_page._path = None
        with self.assertRaises(ValueError):
            none_path_page.get_ocr()
        # Unknown file case
        page3_copy = deepcopy(self.page3)
        page3_copy._raw_ocr = None
        page3_copy._page_number = 3333
        ocr_sample = {"page": {"number": page3_copy.page_number,
                               "width": 1, "height": 1},
                      "image": {"width": 1, "height": 1},
                      "data": []}
        self.assertEqual(page3_copy.get_ocr(), ocr_sample)

    def test_get_ocr_formatted(self):
        formatted_ocr = self.page6.get_ocr_formatted()
        formatted_ocr_stuck = self.page6.get_ocr_formatted(stick_coords=True)

        self.assertEqual(formatted_ocr['words'][86]['ocr_text'], '188.')
        self.assertEqual(formatted_ocr['words'][86]['bottom'], 375)
        self.assertEqual(formatted_ocr['words'][86]['top'], 341)

        self.assertEqual(formatted_ocr_stuck['words'][0]['ocr_text'], '“Member')
        self.assertEqual(formatted_ocr_stuck['words'][0]['bottom'], 34)
        self.assertEqual(formatted_ocr_stuck['words'][0]['top'], 9)

    def test_draw(self):
        img_path = os.path.join(self.images_folder_path, 'draw_sample_img.png')
        page = create_dummy_page(page_n=1, path=self.snap_path)
        img = page.draw(preview=False, save=img_path)
        img_size1 = page.draw(preview=False, save=img_path, size=1000)
        img_size2 = page.draw(preview=False, save=img_path, size=2000)
        self.assertTrue(type(img) == np.ndarray, 'image type is not np.ndarray')
        self.assertTrue(os.path.exists(img_path), 'image was not saved')
        self.assertEqual(img_size1.size, img_size2.size)
        with self.assertRaises(ValueError):
            page.draw(preview=False, size=-1)

    def test_free_form_text(self):
        self.assertEqual(len(self.page6.free_form_text()), 3543)
        self.assertEqual(len(self.page3.free_form_text()), 3853)
        self.assertEqual(self.page6.free_form_text().split(" ")[7], "except")
        self.assertEqual(self.page3.free_form_text().split(" ")[15], "also")

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(cls.SNAPSHOT_PATH)
        if cls.ORIGINAL_SNAPSHOT_PATH is not None:
            os.environ[EnvConfigEnum.SNAPSHOT_PATH.value] = cls.ORIGINAL_SNAPSHOT_PATH
        else:
            del os.environ[EnvConfigEnum.SNAPSHOT_PATH.value]
