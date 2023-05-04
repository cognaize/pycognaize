import logging
import os

from bs4 import BeautifulSoup

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

    def _validate_path(self, path: str, document_id: str) -> str:
        """
        If the input path contains a directory with the same name
            as the document ID and if that directory contains a file
            named `source.html`, the valid path
            is the combination of the input path and the document id
        If the input path contains a file named `source.html`,
            the valid path is simply the input path.
        Otherwise, the function returns an empty string as the valid path.

        :param path: path of the source document
        :param document_id: document id
        :return: valid path for the `source.html` file
            corresponding to the document id
        """
        valid_path = ''
        try:
            joined_path = os.path.join(path, document_id)
            if (
                    self.ci.isdir(joined_path)
                    and StorageEnum.html_file.value
                    in self.ci.listdir(joined_path, exclude_folders=True)
            ):
                valid_path = joined_path
            elif StorageEnum.html_file.value in self.ci.listdir(path):
                valid_path = path
        except Exception as e:
            logging.debug(f"An error occurred while validating the path: {e}")
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
