import os.path
import unittest

import bs4

from pycognaize.document.html_info import HTML
from pycognaize.tests.resources import RESOURCE_FOLDER


class TestHTML(unittest.TestCase):
    def setUp(self):
        self.path1 = RESOURCE_FOLDER + '/xbrl_snapshot'
        self.path2 = RESOURCE_FOLDER
        self.path3 = RESOURCE_FOLDER + '/snapshots/60b76b3d6f3f980019105dac'
        self.doc_id_1 = '63fd387178232c6001119a41a'

        self.html_info_1 = HTML(path=self.path1, doc_id=self.doc_id_1)
        self.html_info_2 = HTML(path=self.path2, doc_id=self.doc_id_1)
        self.html_info_3 = HTML(path=self.path3, doc_id=self.doc_id_1)


    def test_path(self):
        self.assertEqual(self.html_info_1.path, os.path.join(self.path1, self.doc_id_1))
        self.assertEqual(self.html_info_2.path, self.path2)
        self.assertEqual(self.html_info_3.path, '')

    def test__html_soup(self):
        self.assertIsInstance(self.html_info_1.html_soup, bs4.BeautifulSoup)
        self.assertIsInstance(self.html_info_2.html_soup, bs4.BeautifulSoup)
        self.assertIsNone(self.html_info_3.html_soup)

        self.assertEqual(self.html_info_1.html_soup.text, '\n\n\n This is a blank HTML page \n\n')
        self.assertEqual(self.html_info_2.html_soup.text, '\n\n\n This is a blank HTML page \n\n')

if __name__ == '__main__':
    unittest.main()