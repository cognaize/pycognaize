import logging
from typing import Optional
import os
import re
import PyPDF2
import fitz
from io import BytesIO
from PyPDF2 import PdfReader
from pathlib import Path
# from langchain.document_loaders import pdf
from pycognaize.login import Login
from pycognaize.common.utils import cloud_interface_login

from pycognaize.common.enums import (
    PDF_EXTENSION
)


class Pdf:
    """Representing a page of a document in pycognaize"""
    REGEX_NO_ALPHANUM_CHARS = re.compile(r'[^a-zA-Z\d)\[\](-.,]')

    def __init__(self,
                 src_id: str,
                 path: str,
                 ):
        self._src_id = src_id
        self._path = path
        self._login_instance = Login()
        self.ci = cloud_interface_login(self._login_instance)

    @property
    def path(self) -> str:
        """Path of the source document"""
        return self._path

    @property
    def src(self):
        return self._src_id

    def get_pdf(self) -> Optional[dict]:
        if self.path is None:
            raise ValueError("No path defined for getting the pdf")
        uri = Path(self.path) / f"{self._src_id}.{PDF_EXTENSION}"
        try:
            with self.ci.open(str(uri), 'rb') as f:
                pdf_data = f.read()
                pdf_document = fitz.open(filetype="pdf", stream=BytesIO(pdf_data))
        except FileNotFoundError as e:
            logging.debug("Unable to get the pdf")
        return pdf_document