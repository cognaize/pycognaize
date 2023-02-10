import logging
import os

from bs4 import BeautifulSoup

from pycognaize.login import Login
from pycognaize.common.enums import StorageEnum
from pycognaize.common.utils import cloud_interface_login


class HTML:
    """Represents html of a xbrl document in pycognaize"""
    def __init__(self, path: str) -> None:
        """
        :param path: Local or remote path to the document folder, which includes the html file
        """
        self._path = path
        self._login_instance = Login()
        self.ci = cloud_interface_login(self._login_instance)
        self._html_file = None
        self._html_soup = None

    @property
    def path(self):
        """Path of the source document"""
        return self._path

    def _read_html(self, path: str) -> str:
        if self._html_file is None:
            with open(path, 'r') as file:
                self._html_file = file.read()
        return self._html_file

    @property
    def html_soup(self):
        if self._html_soup is None:
            if self.get_html():
                self._html_soup = BeautifulSoup(self.get_html(),
                                                features="html.parser")
        return self._html_soup

    def get_html(self):
        html_bytes = None
        if StorageEnum.html_file.value not in os.listdir(self.path):
            return html_bytes
        uri = os.path.join(self.path, StorageEnum.html_file.value)
        try:
            html_bytes = self._read_html(path=uri)
        except FileNotFoundError as e:
            logging.debug(
                f"Unable to get the html: {e}")
        return html_bytes
