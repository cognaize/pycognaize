import math

import bson
from datetime import datetime
from typing import Union, Optional

from pycognaize.common.enums import IqTagKeyEnum, ID

from pycognaize.common.utils import convert_coord_to_num
from pycognaize.document.tag.cell import Cell
from pycognaize.document.tag.tag import Tag


class ExtractionTag(Tag):
    raw_value: Optional[str]
    raw_ocr_value: Optional[str]
    _value = None
    _has_value_exception = None
    _value_exception_message = None
    _ocr_value = None
    _has_raw_value_exception = None
    _raw_value_exception_message = None

    @classmethod
    def construct_from_raw(cls, raw: dict, page: 'Page') -> 'ExtractionTag':
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
        raw_value = raw['value']
        raw_ocr_value = raw['ocrValue']
        tag = cls(left=left, right=right, top=top, bottom=bottom,
                  page=page, raw_value=raw_value, raw_ocr_value=raw_ocr_value)
        return tag

    def hshift(self, by) -> 'ExtractionTag':
        """Shifts rectangle horizontally

        :param by: the amount by which the tag should be horizontally shifted
        :return: shifted rectangle
        """
        return self.__class__(left=self.left + by, right=self.right + by,
                              top=self.top, bottom=self.bottom,
                              page=self.page, raw_value=self.raw_value,
                              raw_ocr_value=self.raw_ocr_value)

    def horizontal_shift(self, by):
        return self.hshift(by)

    def vshift(self, by) -> 'ExtractionTag':
        """Shifts rectangle vertically

        :param by: the amount by which the tag should be vertically shifted
        :return: shifted rectangle
        """
        return self.__class__(left=self.left, right=self.right,
                              top=self.top + by, bottom=self.bottom + by,
                              page=self.page, raw_value=self.raw_value,
                              raw_ocr_value=self.raw_ocr_value)

    def vertical_shift(self, by):
        return self.vshift(by)

    def __add__(self, other: Union['Tag', Cell]) -> 'ExtractionTag':
        """Merge two rectangles into one"""
        if self.page.page_number == other.page.page_number:
            left = min(self.left, other.left)
            right = max(self.right, other.right)
            top = min(self.top, other.top)
            bottom = max(self.bottom, other.bottom)
            raw_ocr_value_joined = " ".join(
                [i.raw_ocr_value for i in sorted(
                    [self, other], key=lambda x: (x.left, x.top))])
            return ExtractionTag(
                left=left, right=right, top=top, bottom=bottom,
                page=self.page, raw_value=self.raw_value,
                raw_ocr_value=raw_ocr_value_joined)
        else:
            raise ValueError("Tags are not on the same page.")

    def _validate_numeric(self):
        """Validate numerica data"""
        try:
            self._value = (float(self.raw_value) if self.raw_value is not None
                          else math.nan)
            self._has_value_exception = False
        except Exception as ValueException:
            self._has_value_exception = True
            self._value_exception_message = str(ValueException)

        try:
            self._ocr_value = (float(self.raw_ocr_value)
                              if self.raw_ocr_value is not None else math.nan)
            self._has_raw_value_exception = False
        except Exception as RawValueException:
            self._has_raw_value_exception = True
            self._raw_value_exception_message = str(RawValueException)

    def _validate_date(self, date_format):
        """Validate date data"""
        try:
            self._value = datetime.strptime(self.raw_value, date_format)
            self._has_value_exception = False
        except Exception as ValueException:
            self._has_value_exception = True
            self._value_exception_message = str(ValueException)

        try:
            self._ocr_value = datetime.strptime(self.raw_ocr_value, date_format)
            self._has_raw_value_exception = False
        except Exception as RawValueException:
            self._has_raw_value_exception = True
            self._raw_value_exception_message = str(RawValueException)

    def to_dict(self) -> dict:
        """Converts extraction tag to dict"""
        return {
            ID: str(bson.ObjectId()),
            IqTagKeyEnum.ocr_value.value: self.raw_ocr_value,
            IqTagKeyEnum.value.value: str(self.raw_value),
            IqTagKeyEnum.left.value: f"{self.left}%",
            IqTagKeyEnum.top.value: f"{self.top}%",
            IqTagKeyEnum.height.value: f"{self.bottom - self.top}%",
            IqTagKeyEnum.width.value: f"{self.right - self.left}%",
            IqTagKeyEnum.page.value: self.page.page_number
        }