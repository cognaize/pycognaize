import bson
from typing import Union

from pycognaize.common.enums import IqCellKeyEnum, ID


class Cell:
    """Represents a single element in TableTag"""

    def __init__(self, value, left_col, top_row, top, right, bottom, left,
                 col_span, row_span):
        # TODO: check for valid values
        self._value = value
        self._left_col = left_col
        self._top_row = top_row
        self._col_span = col_span
        self._row_span = row_span
        self._top = top
        self._right = right
        self._bottom = bottom
        self._left = left
        self._width = None
        self._height = None
        self._area = None

    @property
    def value(self):
        return self._value

    @property
    def left_col(self):
        return self._left_col

    @property
    def top_row(self):
        return self._top_row

    @property
    def col_span(self):
        return self._col_span

    @property
    def row_span(self):
        return self._row_span

    @property
    def top(self):
        return self._top

    @property
    def right(self):
        return self._right

    @property
    def bottom(self):
        return self._bottom

    @property
    def left(self):
        return self._left

    @property
    def area(self) -> float:
        """Area of the rectangle"""
        if self._area is None:
            self._area = self.width * self.height
        return self._area

    @property
    def width(self) -> Union[int, float]:
        """Width of the rectangle"""
        if self._width is None:
            self._width = self.right - self.left
        return self._width

    @property
    def height(self) -> Union[int, float]:
        """Height of the rectangle"""
        if self._height is None:
            self._height = self.bottom - self.top
        return self._height

    def __repr__(self):
        return (
            f'<{self.__class__.__name__}:'
            f' coords: ({self.top:<9.5f}, {self.right:<9.5f},'
            f' {self.bottom:<9.5f}, {self.left:<9.5f})'
            f' spans: ({self.row_span:<3}, {self.col_span:<3})'
            f' corner coords: ({self.left_col:<3}, {self.top_row:<3})'
            f' value: {self.value}>'
        )

    def __str__(self):
        return f'Left: {self._left_col}, Top: {self._top_row}'

    def __eq__(self, obj):
        """Adjusts method for equating with strings and other cell objects"""
        if isinstance(obj, str):
            return self._value == obj
        elif isinstance(obj, Cell):
            return (self._value == obj.value and
                    self._left_col == obj.left_col and
                    self._top_row == obj.top_row and
                    self._col_span == obj.col_span and
                    self._row_span == obj.row_span)

    def to_dict(self) -> dict:
        """Converts cell to dict"""
        return {
            ID: str(bson.ObjectId()),
            IqCellKeyEnum.left_col_top_row.value: f"{self.left_col}"
                                                  f":{self.top_row}",
            IqCellKeyEnum.col_span.value: self.col_span,
            IqCellKeyEnum.row_span.value: self.row_span,
            IqCellKeyEnum.text.value: self.value,
            IqCellKeyEnum.left.value: self.left,
            IqCellKeyEnum.top.value: self.top,
            IqCellKeyEnum.width.value: self.right - self.left,
            IqCellKeyEnum.height.value: self.bottom - self.top
        }
