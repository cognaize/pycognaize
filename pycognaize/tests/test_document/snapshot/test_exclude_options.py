from unittest import TestCase

from pycognaize import Snapshot


class ExcludeOptionsTestCase(TestCase):

    def test_should_exclude_image_folder_when_images_are_excluded(self):
        res = Snapshot._get_exclude_patterns(
            True,
            False,
            False,
            False
        )

        assert len(res) == 1
        assert '*/images/*.jpeg' in res

    def test_should_exclude_data_folder_when_ocr_is_excluded(self):
        res = Snapshot._get_exclude_patterns(
            False,
            True,
            False,
            False
        )

        assert len(res) == 1
        assert '*/data/*.json' in res

    def test_should_exclude_pdf_files_when_pdf_is_excluded(self):
        res = Snapshot._get_exclude_patterns(
            False,
            False,
            True,
            False
        )

        assert len(res) == 1
        assert '*.pdf' in res

    def test_should_exclude_html_files_when_html_is_excluded(self):
        res = Snapshot._get_exclude_patterns(
            False,
            False,
            False,
            True
        )

        assert len(res) == 1
        assert '*.html' in res

    def test_should_include_all_options_when_all_are_excluded(self):
        res = Snapshot._get_exclude_patterns(
            True,
            True,
            True,
            False
        )

        assert len(res) == 3
        assert '*.pdf' in res
        assert '*/data/*.json' in res
        assert '*/images/*.jpeg' in res
