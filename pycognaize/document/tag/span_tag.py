from pycognaize.common.utils import convert_coord_to_num
from pycognaize.document.tag.tag import BoxTag
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from pycognaize.document.page import Page

from pycognaize.common.decorators import module_not_found


class SpanTag(BoxTag):
    """Represents a Tag included in a spanfield"""

    def __init__(self, left, right, top, bottom,
                 page: 'Page',
                 raw_value: str, raw_ocr_value: str):
        super().__init__(left=left, right=right, top=top, bottom=bottom,
                         page=page)
        self.raw_value = raw_value
        self.raw_ocr_value = raw_ocr_value
        self._spacy_doc = None

    @classmethod
    def construct_from_raw(cls, raw: dict, page: 'Page') -> 'SpanTag':
        """Create a SpanTag from a raw dictionary"""
        left = convert_coord_to_num(raw['left'])
        top = convert_coord_to_num(raw['top'])
        height = convert_coord_to_num(raw['height'])
        width = convert_coord_to_num(raw['width'])
        right = left + width
        bottom = top + height
        raw_value = raw['value']
        raw_ocr_value = raw['ocrValue']
        tag = cls(left=left, right=right, top=top, bottom=bottom,
                  page=page, raw_value=raw_value, raw_ocr_value=raw_ocr_value)
        return tag

    @module_not_found
    def __create_spacy_doc(self):
        """Creates spacy nlp object from raw value"""
        import spacy
        nlp = spacy.blank("en")
        self._spacy_doc = nlp(self.raw_value)

    def __getitem__(self, val):
        """Returns slice of the span object"""
        return SpanTag(self._left, self._right, self._top,
                       self._bottom, self._page, self.raw_value[val],
                       self.raw_ocr_value[val])
