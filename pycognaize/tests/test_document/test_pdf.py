import unittest
from pycognaize.document.pdf import Pdf
from pycognaize.tests.resources import RESOURCE_FOLDER

class TestPdf(unittest.TestCase):
    def setUp(self):
        self.path1 = RESOURCE_FOLDER + '/snapshots/60f554497883ab0013d9d906'
        self.src_id_1 = '6645954b30f92ce8b63b5dc1274ee829dcc322073d238955536ce497fc4149e3'

        self.pdf_1 = Pdf(src_id=self.src_id_1,path=self.path1).pdf


    def test_get_pdf(self):
        self.assertEqual(self.pdf_1.is_pdf, True)
        self.assertEqual(self.pdf_1.pdf_catalog(), 322)
        self.assertEqual(self.pdf_1.page_count, 7)
        self.assertEqual(self.pdf_1.is_closed,False)


