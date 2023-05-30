import bson
from typing import Union, Dict, TYPE_CHECKING

from pycognaize.common.enums import IqTagKeyEnum, ID
from pycognaize.document.tag.tag import LineTag

from pycognaize.common.utils import convert_coord_to_num
from pycognaize.document.tag.cell import Cell
if TYPE_CHECKING:
    from pycognaize.document.page import Page


class SectionTag(LineTag):
    """Represents field's coordinate data on document"""

    def __init__(self, top, left, height, width, page, tag_type):
        super().__init__(top=top,
                         page=page, tag_type=tag_type)
        self._type = tag_type
        self._top = top
        self._left = left
        self._height = height
        self._width = width
        self._page = page

    @classmethod
    def construct_from_raw(cls, raw: dict,
                           pages: Dict[int, 'Page'],
                           tag_type: str) -> 'SectionTag':
        """Builds Tag object from pycognaize raw data

        :param raw: pycognaize field's tag info
        :param pages: `Page` to which the tag belongs
        :param tag_type: `Page` to which the tag belongs
        :return:
        """
        page_number = raw['page']
        top = convert_coord_to_num(raw['top'])
        left = convert_coord_to_num(raw['left'])
        height = convert_coord_to_num(raw['height'])
        width = convert_coord_to_num(raw['width'])

        tag = cls(top=top,
                  left=left,
                  height=height,
                  width=width,
                  page=pages[page_number],
                  tag_type=tag_type)
        return tag

    def vshift(self, by) -> 'SectionTag':
        """Shifts line vertically

        :param by: the amount by which the tag should be vertically shifted
        :return: shifted rectangle
        """
        return self.__class__(top=self.top + by,
                              page=self.page,
                              tag_type=self.type)

    def vertical_shift(self, by):
        return self.vshift(by)

    def __add__(self, other: Union['LineTag', Cell]) -> 'SectionTag':
        """Merge two rectangles into one"""
        top = min(self.top, other.top)
        return SectionTag(top=top, page=self.page, tag_type=self.type)

    def to_dict(self) -> dict:
        """Converts extraction tag to dict"""
        return {
            ID: str(bson.ObjectId()),
            IqTagKeyEnum.top.value: f"{self.top}%",
            IqTagKeyEnum.left.value: f"{self._left}%",
            IqTagKeyEnum.height.value: f"{self._height}%",
            IqTagKeyEnum.width.value: f"{self._width}%",
            IqTagKeyEnum.page.value: self.page.page_number}
