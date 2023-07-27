import logging
from typing import Optional
import fitz
from io import BytesIO
from pathlib import Path
from pycognaize.login import Login
from pycognaize.common.utils import cloud_interface_login
from pycognaize.common.enums import PDF_EXTENSION


class Pdf:
    """
    A class representing a PDF document with OCR capabilities.

    Attributes:
        src_id (str): The source ID for the PDF document.
        path (str): The local or remote path to the PDF document.

    """

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
        """Get the path to the PDF document.
         Returns:
            str: The path to the PDF document."""
        return self._path

    @property
    def src(self):
        """Get the source ID of the document.
        Returns:
            str: The source ID of the PDF document."""
        return self._src_id

    @property
    def pdf(self):
        """Get the PDF document object
         Returns:
            fitz.Document: The PDF document object."""
        if self._pdf is None:
            self._pdf = self.get_pdf()
        return self._pdf

    def get_pdf(self) -> Optional[fitz.Document]:
        """Retrieve the PDF document from the specified path.
        Returns:
            Optional[fitz.Document]"""
        pdf_document = None
        if self.path is None:
            raise ValueError("No path defined for getting the pdf")
        uri = Path(self.path).joinpath(f"{self._src_id}.{PDF_EXTENSION}")
        try:
            with self.ci.open(str(uri), 'rb') as f:
                pdf_data = f.read()
                pdf_document = fitz.open(
                    filetype="pdf", stream=BytesIO(pdf_data))
        except FileNotFoundError as e:
            logging.warning(f"Unable to get the pdf: {e}")
        return pdf_document

    def ocr(self, page_number: int):
        """Perform OCR on a specific page and return the extracted text.
        Args:
            page_number (int): The page number to perform OCR on.
        Returns:
            str: The extracted text from the specified page."""
        return self.pdf[page_number].get_text()

    def __getitem__(self, page_number: int):
        """Get a specific page from the PDF document.
        Args:
            page_number (int): The page number to retrieve.
        Returns:
            fitz.Page: The specified page from the PDF document."""
        return self.pdf[page_number]
