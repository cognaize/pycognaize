import shutil
from pathlib import Path
from unittest import TestCase

from pycognaize.file_storage import local_storage


class IsFileTestCase(TestCase):
    dir_path = Path(__file__).parent.parent.parent / 'resources' / 'local_is_file'

    @classmethod
    def setUpClass(cls):
        if not cls.dir_path.is_dir():
            cls.dir_path.mkdir()

    def test_should_return_true_when_file_exists(self):
        file_path = self.dir_path / 'file.txt'
        file_path.touch()

        assert local_storage.is_file(file_path)

    def test_should_return_false_when_file_does_not_exist(self):
        file_path = self.dir_path / 'file.txt'

        assert local_storage.is_file(file_path) is False

    def test_should_return_false_when_path_is_directory(self):
        dir_path = self.dir_path / 'directory'
        dir_path.mkdir()

        assert local_storage.is_file(dir_path) is False

    @classmethod
    def tearDownClass(cls):
        if cls.dir_path.is_dir():
            shutil.rmtree(cls.dir_path)
