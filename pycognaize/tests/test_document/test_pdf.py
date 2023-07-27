import unittest
from pycognaize.document.pdf import Pdf
from pycognaize.tests.resources import RESOURCE_FOLDER


class TestPdf(unittest.TestCase):
    def setUp(self):
        self.path1 = RESOURCE_FOLDER + '/snapshots/60f554497883ab0013d9d906'
        self.path2 = RESOURCE_FOLDER + '/snapshots/60f53e967883ab0013d9c6f9'
        self.src_id_1 = '6645954b30f92ce8b63b5dc1274ee829dcc322073d238955536ce497fc4149e3'
        self.src_id_2 = '21377e697b6eda6bf316779abf375794a58875455ad1bf44d1a2f1b86424fdc5'
        self.pdf_1 = Pdf(src_id=self.src_id_1, path=self.path1)
        self.pdf_2 = Pdf(src_id=self.src_id_2, path=None)

    def test_get_pdf(self):
        with self.assertRaises(ValueError):
            _ = self.pdf_2.pdf
        self.assertTrue(isinstance(self.pdf_1, Pdf))

    def test_path(self):
        self.assertEqual(self.pdf_1.path, self.path1)

    def test_src(self):
        self.assertEqual(self.pdf_1.src, self.src_id_1)

    def test__getitem__(self):
        with self.assertRaises(IndexError):
            _ = self.pdf_1[7]
        self.assertIsNotNone(self.pdf_1[6])
