import math

import bson
from datetime import datetime
from typing import Union

from pycognaize.common.enums import IqTagKeyEnum, ID
from pycognaize.document.tag.tag import Tag

from pycognaize.common.utils import convert_coord_to_num
from pycognaize.document.tag.cell import Cell
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from pycognaize.document.page import Page


class SectionTag(Tag):
    """Represents field's coordinate data on document"""

    def __init__(self, left, right, top, bottom, page):
        super().__init__(left=left, right=right, top=top, bottom=bottom,
                         page=page)

    @classmethod
    def construct_from_raw(cls, raw: dict, page: 'Page') -> 'SectionTag':
        """Builds Tag object from pycognaize raw data

        :param raw: pycognaize field's tag info
        :param page: `Page` to which the tag belongs
        :return:
        """
        left = convert_coord_to_num(raw['left'])
        top = convert_coord_to_num(raw['top'])
        height = convert_coord_to_num(raw['height'])
        width = convert_coord_to_num(raw['width'])
        right = left + width
        bottom = top + height
        tag = cls(left=left, right=right, top=top, bottom=bottom,
                  page=page)
        return tag

    def hshift(self, by) -> 'SectionTag':
        """Shifts rectangle horizontally

        :param by: the amount by which the tag should be horizontally shifted
        :return: shifted rectangle
        """
        return self.__class__(left=self.left + by, right=self.right + by,
                              top=self.top, bottom=self.bottom,
                              page=self.page)

    def horizontal_shift(self, by):
        return self.hshift(by)

    def vshift(self, by) -> 'SectionTag':
        """Shifts rectangle vertically

        :param by: the amount by which the tag should be vertically shifted
        :return: shifted rectangle
        """
        return self.__class__(left=self.left, right=self.right,
                              top=self.top + by, bottom=self.bottom + by,
                              page=self.page)

    def vertical_shift(self, by):
        return self.vshift(by)

    def __add__(self, other: Union['Tag', Cell]) -> 'SectionTag':
        """Merge two rectangles into one"""
        left = min(self.left, other.left)
        right = max(self.right, other.right)
        top = min(self.top, other.top)
        bottom = max(self.bottom, other.bottom)
        return SectionTag(
            left=left, right=right, top=top, bottom=bottom,
            page=self.page)

    def to_dict(self) -> dict:
        """Converts extraction tag to dict"""
        return {
            ID: str(bson.ObjectId()),
            IqTagKeyEnum.left.value: f"{self.left}%",
            IqTagKeyEnum.top.value: f"{self.top}%",
            IqTagKeyEnum.height.value: f"{self.bottom - self.top}%",
            IqTagKeyEnum.width.value: f"{self.right - self.left}%",
            IqTagKeyEnum.page.value: self.page.page_number
        }
