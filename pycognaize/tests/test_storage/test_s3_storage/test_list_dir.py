from typing import Iterable
from unittest import TestCase

import pytest
from cloudpathlib import implementation_registry
from cloudpathlib.local import LocalS3Path, local_s3_implementation, LocalS3Client

from pycognaize.file_storage import get_storage


class ListDirTestCase(TestCase):
    dir_path = LocalS3Path('s3://test-bucket') / 'resources' / 'local_list_dir'

    @pytest.fixture(autouse=True)
    def patch_cloudpathlib(self, monkeypatch):
        monkeypatch.setitem(implementation_registry, "s3", local_s3_implementation)

        if not self.dir_path.is_dir():
            self.dir_path.mkdir()

        yield

        LocalS3Client.reset_default_storage_dir()

    def test_should_raise_exception_when_directory_does_not_exist(self):
        dir_path = self.dir_path / 'directory'

        s3_storage = get_storage(dir_path)

        with self.assertRaises(NotADirectoryError):
            list(s3_storage.list_dir(dir_path))

        with self.assertRaises(NotADirectoryError):
            list(s3_storage.list_dir(str(dir_path)))

    def test_should_include_all_files_in_directory(self):
        dir_path = self.dir_path / 'directory'

        try:
            dir_path.mkdir()

            file_path = dir_path / 'file.txt'
            file1_path = dir_path / 'file2.txt'

            file_path.touch()
            file1_path.touch()

            s3_storage = get_storage(dir_path)

            res = s3_storage.list_dir(dir_path)

            assert isinstance(res, Iterable)
            res = list(res)
            assert len(res) == 2
            assert isinstance(res[0], LocalS3Path)
        finally:
            dir_path.rmtree()

    def test_should_include_folders_when_option_provided(self):
        dir_path = self.dir_path / 'directory'

        try:
            dir_path.mkdir()

            file_path = dir_path / 'file.txt'
            file1_path = dir_path / 'test' / 'file1.txt'

            file_path.touch()
            file1_path.touch()

            s3_storage = get_storage(dir_path)

            res = s3_storage.list_dir(dir_path, exclude_folders=False)

            assert isinstance(res, Iterable)
            res = list(res)
            assert len(res) == 2
        finally:
            dir_path.rmtree()

    def test_should_exclude_files_when_option_provided(self):
        dir_path = self.dir_path / 'directory'

        try:
            dir_path.mkdir()

            file_path = dir_path / 'file.txt'
            dir1_path = dir_path / 'directory1'

            file_path.touch()
            dir1_path.mkdir()

            s3_storage = get_storage(dir_path)

            res = s3_storage.list_dir(dir_path, include_files=False)

            assert isinstance(res, Iterable)
            res = list(res)
            assert len(res) == 0
        finally:
            dir_path.rmtree()

    def test_should_include_files_in_subfolders_when_recursive(self):
        dir_path = self.dir_path / 'directory'

        try:
            dir_path.mkdir()

            file_path = dir_path / 'file.txt'
            file1_path = dir_path / 'test' / 'file1.txt'

            file_path.touch()
            file1_path.touch()

            s3_storage = get_storage(dir_path)

            res = s3_storage.list_dir(dir_path, recursive=True)

            assert isinstance(res, Iterable)
            res = list(res)
            assert len(res) == 3
        finally:
            dir_path.rmtree()
