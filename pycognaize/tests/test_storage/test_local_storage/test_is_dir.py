import shutil
from pathlib import Path
from unittest import TestCase

from pycognaize.file_storage import get_storage


class IsDirTestCase(TestCase):
    dir_path = Path(__file__).parent.parent.parent / 'resources' / 'local_is_dir'

    @classmethod
    def setUpClass(cls):
        if not cls.dir_path.is_dir():
            cls.dir_path.mkdir()

    def test_should_return_true_when_directory_exists(self):
        dir_path = self.dir_path / 'directory'
        dir_path.mkdir()

        local_storage = get_storage(dir_path)

        assert local_storage.is_dir(dir_path)

    def test_should_return_false_when_directory_does_not_exist(self):
        dir_path = self.dir_path / 'directory1'
        local_storage = get_storage(dir_path)

        assert local_storage.is_dir(dir_path) is False

    def test_should_return_false_when_path_is_a_file(self):
        file_path = self.dir_path / 'file.txt'
        file_path.touch()

        local_storage = get_storage(file_path)

        assert local_storage.is_dir(file_path) is False

    @classmethod
    def tearDownClass(cls):
        if cls.dir_path.is_dir():
            shutil.rmtree(cls.dir_path)
