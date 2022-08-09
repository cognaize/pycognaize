from pycognaize.document.spanning.line import Line
from pycognaize.document.tag.tag import Tag
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from pycognaize.document.page import Page

from pycognaize.common.decorators import module_not_found


class SpanTag(Tag):
    """Represents a Tag included in a spanfield"""

    def __init__(self, left, right, top, bottom,
                 page: 'Page',
                 raw_value: str):
        super().__init__(left=left, right=right, top=top, bottom=bottom,
                         page=page)
        self.line: Line
        self.raw_value = raw_value
        self._spacy_doc = None

    def construct_from_raw(cls, raw: dict, page: 'Page') -> 'SpanTag':
        ...

    def construct_lines(self, metadata: dict) -> Line:
        ...

    @module_not_found
    def __create_spacy_doc(self):
        """Creates spacy nlp object from raw value"""
        import spacy
        nlp = spacy.blank("en")
        self._spacy_doc = nlp(self.raw_value)

    def __getitem__(self, val):
        """Returns slice of the span object"""
        return SpanTag(self._left, self._right, self._top,
                       self._bottom, self._page, self.raw_value[val])