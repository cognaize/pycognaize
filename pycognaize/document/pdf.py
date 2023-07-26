import logging
from typing import Optional
import fitz
from io import BytesIO
from pathlib import Path
from pycognaize.login import Login
from pycognaize.common.utils import cloud_interface_login

from pycognaize.common.enums import (
    PDF_EXTENSION
)


class Pdf:

    def __init__(self,
                 src_id: str,
                 path: str,
                 ):
        self._src_id = src_id
        self._path = path
        self._login_instance = Login()
        self.ci = cloud_interface_login(self._login_instance)
        self._pdf = None

    @property
    def path(self) -> str:
        return self._path

    @property
    def src(self):
        return self._src_id

    @property
    def pdf(self):
        if self._pdf is None:
            self._pdf = self.get_pdf()
        return self._pdf

    def get_pdf(self) -> Optional[dict]:
        pdf_document = None
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

    def __getitem__(self, page_number: int):
        return self.pdf[page_number]

    def ocr(self, page_number: int):
        return self.pdf[page_number].get_text()
