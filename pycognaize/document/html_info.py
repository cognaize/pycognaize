import logging
import os

from bs4 import BeautifulSoup

from pycognaize.login import Login
from pycognaize.common.enums import StorageEnum
from pycognaize.common.utils import cloud_interface_login


class HTML:
    """Represents html of a xbrl document in pycognaize"""
    def __init__(self, path: str, doc_id: str) -> None:
        """
        :param path: Local or remote path to the document folder,
            which includes the html file
        """
        self._login_instance = Login()
        self.ci = cloud_interface_login(self._login_instance)
        self._path = self._validate_path(path, doc_id)
        self._html_file = None
        self._html_soup = None

    @property
    def path(self):
        """Path of the source document"""
        return self._path

    def _validate_path(self, path, doc_id):
        valid_path = ''
        if self.ci.isdir(os.path.join(path, doc_id)):
            valid_path = os.path.join(path, doc_id)
        elif StorageEnum.html_file.value in self.ci.listdir(path):
            valid_path = path
        return valid_path

    def _read_html(self, path: str) -> str:
        if self._html_file is None:
            with self.ci.open(path, 'r') as file:
                self._html_file = file.read()
        return self._html_file

    @property
    def html_soup(self):
        if self._html_soup is None:
            if self.path:
                self._html_soup = BeautifulSoup(self.get_html(),
                                                features="html.parser")
        return self._html_soup

    def get_html(self):
        html_bytes = None
        uri = os.path.join(self.path, StorageEnum.html_file.value)
        try:
            html_bytes = self._read_html(path=uri)
        except FileNotFoundError as e:
            logging.debug(
                f"Unable to get the html: {e}")
        return html_bytes
