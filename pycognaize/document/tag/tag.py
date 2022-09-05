import abc
import logging
import math
import sys
from typing import Union, Tuple

from pydantic import BaseModel, root_validator, validator

from pycognaize.common.utils import convert_coord_to_num
from pycognaize.document.tag.cell import Cell

# from typing_extensions import TYPE_CHECKING
# if TYPE_CHECKING:
#     from pycognaize.document.page import Page
# from typing_extensions import TYPE_CHECKING
# if TYPE_CHECKING:
from pycognaize.document.page_typing import PageTyping

class Tag(BaseModel):

    class Config:
        """Configuration for Field Pydantic model"""
        arbitrary_types_allowed = True
        validate_assignment = True
        if sys.version_info < (3, 9):
            kw_only = False

    left: Union[float, int]
    right: Union[float, int]
    top: Union[float, int]
    bottom: Union[float, int]
    page: PageTyping = None
    _height: Union[float, int]
    _width: Union[float, int]
    _area: Union[float, int]
    _xcenter: Union[float, int]
    _ycenter: Union[float, int]
    _center: Tuple[float, float]

    # def __init__(__pydantic_self__, **data: Any):
    #     super().__init__(data)
    #     __pydantic_self__.page = None

    @staticmethod
    def _validate_coords(left, right, top, bottom):
        """Validates the input coordinates"""
        if left > right:
            raise ValueError(f"Left ({left}) cannot be"
                             f" bigger than right ({right})")
        if top > bottom:
            raise ValueError(f"Top ({top}) cannot be"
                             f" bigger than bottom ({bottom})")
        if left == right:
            raise ValueError(f"Left ({left}) cannot be"
                             f" equal to right ({right})")
        if top == bottom:
            raise ValueError(f"Top ({top}) cannot be"
                             f" equal to bottom ({bottom})")

    @staticmethod
    def _validate_ranges(left, right, top, bottom, page):
        """Validates the input coordinates"""
        if not 0 <= left <= 100:
            logging.debug(
                f"The left coordinate should be in range 0 to 100, got"
                f" {left} (page {page.page_number})")
            left = min(max(0, left), 100)
        if not 0 <= right <= 100:
            logging.debug(
                f"The right coordinate should be in range 0 to 100, got"
                f" {right} (page {page.page_number})")
            right = min(max(0, right), 100)
        if not 0 <= top <= 100:
            logging.debug(
                f"The top coordinate should be in range 0 to 100, got"
                f" {top} (page {page.page_number})")
            top = min(max(0, top), 100)
        if not 0 <= bottom <= 100:
            logging.debug(
                f"The bottom coordinate should be in range 0 to 100, got"
                f" {bottom} (page {page.page_number})")
            bottom = min(max(0, bottom), 100)

        return left, right, top, bottom

    @staticmethod
    def _parse_position(val: Union[float, int, str],
                        val_name: str) -> Union[int, float]:
        """Parse a number into a proper coordinate value
        :param val: Integer, float or a string
        :param val_name: String representing the position name
            (left/right/top/bottom)
        :return: Parsed numeric value (int or float)
        """
        try:
            return convert_coord_to_num(val)
        except TypeError as e:
            raise TypeError(f"Invalid type for {val_name} coordinate: {e}")
        except ValueError as e:
            raise ValueError(f"Failed to parse {val_name} coordinate: {e}")

    @root_validator()
    def validate_and_calculate_parameters(cls, values):
        left, right, top, bottom = values['left'], values['right'],\
                                   values['top'], values['bottom']
        page = values['page']
        cls._validate_coords(left, right, top, bottom)
        left, right, top, bottom = cls._validate_ranges(left, right,
                                                        top, bottom, page)

        values['left'] = left
        values['right'] = right
        values['top'] = top
        values['bottom'] = bottom
        values['width'] = right - left
        values['height'] = bottom - top
        values['area'] = values['width'] * values['height']
        values['xcenter'] = (left + right) / 2
        values['ycenter'] = (top + bottom) / 2
        values['center'] = (values['xcenter'], values['ycenter'])
        return values

    @validator('left', 'right', 'top', 'bottom')
    def validate_coordnates(cls, v):
        if isinstance(v, str):
            v = cls._parse_position(val=v)
        return v

    def intersects(self, other: Union['Tag', Cell]) -> bool:
        """Checks id there is an intersection between this and other rectangle

        :param other: Rectangle object
        """
        if isinstance(other, (Tag, Cell)):
            if (self.left < other.right and self.right > other.left
                and self.top < other.bottom and self.bottom > other.top) and \
                    self.page.page_number == other.page.page_number:
                return True
            return False
        else:
            raise NotImplementedError(
                f"Not implemented for item of type {type(other)}")

    def hshift(self, by) -> 'Tag':
        """Shifts rectangle horizontally

        :param by: the amount by which the tag should be horizontally shifted
        :return: shifted rectangle
        """
        return self.__class__(left=self.left + by, right=self.right + by,
                              top=self.top, bottom=self.bottom,
                              page=self.page)

    def vshift(self, by) -> 'Tag':
        """Shifts rectangle vertically

        :param by: the amount by which the tag should be vertically shifted
        :return: shifted rectangle
        """
        return self.__class__(left=self.left, right=self.right,
                              top=self.top + by, bottom=self.bottom + by,
                              page=self.page)

    def shift(self, horizontal, vertical) -> 'Tag':
        """Shifts rectangle by 2 axes simultaneously

        :param horizontal:
        :param vertical:
        :return: shifted rectangle
        """
        return self.hshift(horizontal).vshift(vertical)

    def __contains__(self, item: 'Tag') -> bool:
        """Checks if the item is in the rectangle

        :param item: The item to check
        """
        if isinstance(item, Tag):
            if (self.left <= item.left <= self.right and
                self.left <= item.right <= self.right and
                self.top <= item.top <= self.bottom and
                self.top <= item.bottom <= self.bottom) and \
                    self.page.page_number == item.page.page_number:
                return True
            return False
        else:
            raise NotImplementedError(
                f"Not implemented for item of type {type(item)}")

    def __and__(self, other: Union['Tag', Cell]) -> Union[int, float]:
        """The area of intersection of given rectangles"""
        if isinstance(other, (Tag, Cell)):
            if self.intersects(other):
                left = max([self.left, other.left])
                top = max([self.top, other.top])
                right = min([self.right, other.right])
                bottom = min([self.bottom, other.bottom])
                return (right - left) * (bottom - top)
            else:
                return 0
                # raise ValueError("Rectangles are disjointed")
        else:
            raise NotImplementedError(
                f"Not implemented for item of type {type(other)}")

    def __or__(self, other) -> Union[int, float]:
        """The area of union of given rectangles"""
        if isinstance(other, (Tag, Cell)):
            if self.page.page_number == other.page.page_number:
                return self.area + other.area - self.__and__(other)
            else:
                return 0
        else:
            raise NotImplementedError(
                f"Not implemented for item of type {type(other)}")

    def iou(self, other) -> Union[int, float]:
        """Calculate Intersection over Union for given rectangles"""
        if isinstance(other, (Tag, Cell)):
            if self.page.page_number == other.page.page_number:
                return (self & other) / (self | other)
            else:
                return 0
        else:
            raise NotImplementedError(
                f"Not implemented for item of type {type(other)}")

    def __add__(self, other: Union['Tag', Cell]) -> 'Tag':
        """Merge two rectangles into one"""
        if self.page.page_number == other.page.page_number:
            left = min(self.left, other.left)
            right = max(self.right, other.right)
            top = min(self.top, other.top)
            bottom = max(self.bottom, other.bottom)
            return Tag(left=left, right=right, top=top, bottom=bottom,
                       page=self.page)
        else:
            raise ValueError("Tags are not on the same page")

    def __radd__(self, other) -> 'Tag':
        """Merge two rectangles into one,
            required for using sum(<list of rectangles>)

        :param other: Another Rectangle object
        :return: Rectangle object with merged content
        """
        if other == 0:
            return self
        else:
            return self.__add__(other)

    def is_in_rectangle(self, other: "Tag", thresh: float) -> bool:
        """Check if the rectangle is in the other rectangle

        :param other: Another rectangle object
        :param thresh: If the fraction area of the rectangle
            is in the other rectangle
            is larger or equal to thresh, it is in the other rectangle
        :return: True if rectangle is in other rectangle, False otherwise
        """
        if thresh < 0 or thresh > 1:
            raise ValueError(
                "Threshold should be a float number between 0 to 1")
        if isinstance(other, Tag):
            if self.page.page_number == other.page.page_number:
                return ((self & other) / self.area) >= thresh
            else:
                return False
        else:
            raise NotImplementedError(
                f"Not implemented for item of type {type(other)}")

    def get_top_left(self):
        return self.top, self.left

    def get_width_height(self):
        return self.width, self.height

    @abc.abstractmethod
    def to_dict(self) -> dict:
        """Return a dictionary representing the tag object"""
        pass

    def distance(self, other: 'Tag') -> Union[int, float]:
        """Return the Euclidean distance of two tag centers"""
        if self.page.page_number == other.page.page_number:
            dist = math.sqrt(
                (self.xcenter - other.xcenter) ** 2 +
                (self.ycenter - other.ycenter) ** 2)
        else:
            raise ValueError(
                "Can't compute distance between tags in different pages")
        return dist
