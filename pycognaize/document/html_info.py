import logging
import os

from bs4 import BeautifulSoup
from cloudpathlib import CloudPath

from pycognaize.login import Login
from pycognaize.common.enums import StorageEnum
from pycognaize.common.utils import cloud_interface_login


class HTML:
    """Represents html of a xbrl document in pycognaize"""
    def __init__(self, path: str, document_id: str) -> None:
        """
        :param path: Local or remote path to the document folder,
            which includes the html file
        """
        self._login_instance = Login()
        self.ci = cloud_interface_login(self._login_instance)
        self._path = self._validate_path(path, document_id)
        self._html_file = None
        self._html_soup = None

    @property
    def path(self) -> str:
        """Path of the source document"""
        return self._path

    @property
    def html_soup(self):
        if self._html_soup is None:
            if self.path:
                self._html_soup = BeautifulSoup(self._get_html(),
                                                features="html.parser")
        return self._html_soup

    @staticmethod
    def _validate_s3_path(path: str, document_id: str) -> str:
        cloudpath = CloudPath(path)
        joined_path = cloudpath.joinpath(document_id)
        valid_path = ''
        if joined_path.is_dir() and joined_path.joinpath(
                StorageEnum.html_file.value) in joined_path.iterdir():
            valid_path = str(joined_path)
        elif cloudpath.joinpath(
                StorageEnum.html_file.value) in cloudpath.iterdir():
            valid_path = str(cloudpath)
        return valid_path

    @staticmethod
    def _validate_local_path(path: str, document_id: str) -> str:
        from pathlib import Path
        path = Path(path)
        joined_path = path.joinpath(document_id)
        valid_path = ''
        if joined_path.is_dir() and joined_path.joinpath(
                StorageEnum.html_file.value) in joined_path.iterdir():
            valid_path = str(joined_path)
        elif path.joinpath(StorageEnum.html_file.value) in path.iterdir():
            valid_path = str(path)
        return valid_path

    def _validate_path(self, path: str, document_id: str) -> str:
        if path.startswith('s3://'):
            valid_path = self._validate_s3_path(path, document_id)
        else:
            valid_path = self._validate_local_path(path, document_id)
        return valid_path

    def _read_html(self, path: str) -> str:
        if self._html_file is None:
            with self.ci.open(path, 'r') as file:
                self._html_file = file.read()
        return self._html_file

    def _get_html(self):
        html_bytes = None
        uri = os.path.join(self.path, StorageEnum.html_file.value)
        try:
            html_bytes = self._read_html(path=uri)
        except FileNotFoundError as e:
            logging.debug(
                f"Unable to get the html: {e}")
        return html_bytes
