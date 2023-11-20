import shutil
from pathlib import Path
from typing import Iterable
from unittest import TestCase

from pycognaize.file_storage import get_storage


class ListDirTestCase(TestCase):
    dir_path = Path(__file__).parent.parent.parent / 'resources' / 'local_list_dir'

    @classmethod
    def setUpClass(cls):
        if not cls.dir_path.is_dir():
            cls.dir_path.mkdir()

    def test_should_raise_exception_when_directory_does_not_exist(self):
        dir_path = self.dir_path / 'directory'

        local_storage = get_storage(dir_path)

        with self.assertRaises(NotADirectoryError):
            list(local_storage.list_dir(dir_path))

        with self.assertRaises(NotADirectoryError):
            list(local_storage.list_dir(str(dir_path)))

    def test_should_return_empty_list_when_contents_are_missing(self):
        dir_path = self.dir_path / 'directory'
        try:
            dir_path.mkdir()

            local_storage = get_storage(dir_path)

            res = local_storage.list_dir(dir_path)

            assert isinstance(res, Iterable)
            assert len(list(res)) == 0
        finally:

            shutil.rmtree(dir_path)

    def test_should_include_all_files_in_directory(self):
        dir_path = self.dir_path / 'directory'

        try:
            dir_path.mkdir()

            file_path = dir_path / 'file.txt'
            file1_path = dir_path / 'file2.txt'

            file_path.touch()
            file1_path.touch()

            local_storage = get_storage(dir_path)

            res = local_storage.list_dir(dir_path)

            assert isinstance(res, Iterable)
            res = list(res)
            assert len(res) == 2
            assert isinstance(res[0], Path)
        finally:
            shutil.rmtree(dir_path)

    def test_should_include_folders_when_option_provided(self):
        dir_path = self.dir_path / 'directory'

        try:
            dir_path.mkdir()

            file_path = dir_path / 'file.txt'
            dir1_path = dir_path / 'directory1'

            file_path.touch()
            dir1_path.mkdir()

            local_storage = get_storage(dir_path)

            res = local_storage.list_dir(dir_path, exclude_folders=False)

            assert isinstance(res, Iterable)
            res = list(res)
            assert len(res) == 2
            assert isinstance(res[0], Path)
        finally:
            shutil.rmtree(dir_path)

    def test_should_exclude_files_when_option_provided(self):
        dir_path = self.dir_path / 'directory'

        try:
            dir_path.mkdir()

            file_path = dir_path / 'file.txt'
            dir1_path = dir_path / 'directory1'

            file_path.touch()
            dir1_path.mkdir()

            local_storage = get_storage(dir_path)

            res = local_storage.list_dir(dir_path, include_files=False)

            assert isinstance(res, Iterable)
            res = list(res)
            assert len(res) == 1
        finally:
            shutil.rmtree(dir_path)

    def test_should_return_recursive_results_when_option_provided(self):
        dir_path = self.dir_path / 'directory'

        try:
            dir_path.mkdir()

            file_path = dir_path / 'file.txt'
            dir1_path = dir_path / 'directory1'
            file2_path = dir1_path / 'file2.txt'

            file_path.touch()
            dir1_path.mkdir()
            file2_path.touch()

            local_storage = get_storage(dir_path)

            res = local_storage.list_dir(dir_path, recursive=True)

            assert isinstance(res, Iterable)
            res = list(res)
            assert len(res) == 3
        finally:
            shutil.rmtree(dir_path)

    @classmethod
    def tearDownClass(cls):
        if cls.dir_path.is_dir():
            shutil.rmtree(cls.dir_path)
