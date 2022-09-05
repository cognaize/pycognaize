import json
import logging
import os
import re
from typing import Optional, List, Iterable, Union
import numpy as np
from pycognaize.common.decorators import module_not_found
#
# from typing import TYPE_CHECKING
# if TYPE_CHECKING:


class PageTyping:

    def __init__(self, page_number: int, document_id: str, path: str):
        """

        :param page_number: The number of the page (1-based index)
        :param document_id: The unique id of the document
        :param path:
        """
        self._page_number = int(page_number)
        self._document_id = document_id
        self._ci = None
        self._path = path
        self._ocr_raw = None
        self._ocr = None
        self._lines = None
        self._row_word_groups = None
        self._image_bytes = None
        self._image_arr = None
        self._image_height = None
        self._image_width = None
