import abc
import logging
import math
from typing import Union, Tuple

from pycognaize.common.utils import convert_coord_to_num
from pycognaize.document.tag.cell import Cell

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from pycognaize.document.page import Page


class Tag(metaclass=abc.ABCMeta):

    @classmethod
    @abc.abstractmethod
    def construct_from_raw(cls, *args, **kwargs) -> 'Tag':
        ...

    def to_dict(self) -> dict:
        ...


class BoxTag(Tag, metaclass=abc.ABCMeta):
    """Represents a tag that has a varying width and height"""

    def __init__(self,
                 left: Union[int, float],
                 right: Union[int, float],
                 top: Union[int, float],
                 bottom: Union[int, float],
                 page: 'Page'):
        """Creates and validates coordinate data"""

        self._left = left
        self._right = right
        self._top = top
        self._bottom = bottom
        self._page = page
        self.__validate()
        # Properties
        self._height = None
        self._width = None
        self._area = None
        self._xcenter = None
        self._center = None
        self._ycenter = None

    @classmethod
    @abc.abstractmethod
    def construct_from_raw(cls, raw: dict, page: 'Page') -> 'BoxTag':
        ...

    def __repr__(self):
        return (f"<{self.__class__.__name__}:"
                f" left: {self.left}, right: {self.right},"
                f" top: {self.top}, bottom: {self.bottom}>")

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

    def _parse_coordinates(self):
        """If the input coordinates are in string format,
            convert them to numbers"""
        self._left = self._parse_position(val=self.left, val_name='left')
        self._right = self._parse_position(val=self.right, val_name='right')
        self._top = self._parse_position(val=self.top, val_name='top')
        self._bottom = self._parse_position(val=self.bottom, val_name='bottom')

    def __validate(self):
        """Run all input validations and necessary conversions"""
        self._validate_types()
        self._validate_coords()
        self._validate_ranges()

    def _validate_types(self):
        """Validates the input types"""
        if not isinstance(self.left, (int, float)):
            raise TypeError(f"Invalid type for left coord: {type(self.left)}")
        if not isinstance(self.right, (int, float)):
            raise TypeError(
                f"Invalid type for right coord: {type(self.right)}")
        if not isinstance(self.top, (int, float)):
            raise TypeError(f"Invalid type for top coord: {type(self.top)}")
        if not isinstance(self.bottom, (int, float)):
            raise TypeError(
                f"Invalid type for bottom coord: {type(self.bottom)}")

    def _validate_coords(self):
        """Validates the input coordinates"""
        if self.left > self.right:
            raise ValueError(f"Left ({self.left}) cannot be"
                             f" bigger than right ({self.right})")
        if self.top > self.bottom:
            raise ValueError(f"Top ({self.top}) cannot be"
                             f" bigger than bottom ({self.bottom})")
        if self.left == self.right:
            raise ValueError(f"Left ({self.left}) cannot be"
                             f" equal to right ({self.right})")
        if self.top == self.bottom:
            raise ValueError(f"Top ({self.top}) cannot be"
                             f" equal to bottom ({self.bottom})")

    def _validate_ranges(self):
        """Validates the input coordinates"""
        if not 0 <= self.left <= 100:
            logging.debug(
                f"The left coordinate should be in range 0 to 100, got"
                f" {self.left} (page {self.page.page_number})")
            self._left = min(max(0, self.left), 100)
        if not 0 <= self.right <= 100:
            logging.debug(
                f"The right coordinate should be in range 0 to 100, got"
                f" {self.right} (page {self.page.page_number})")
            self._right = min(max(0, self.right), 100)
        if not 0 <= self.top <= 100:
            logging.debug(
                f"The top coordinate should be in range 0 to 100, got"
                f" {self.top} (page {self.page.page_number})")
            self._top = min(max(0, self.top), 100)
        if not 0 <= self.bottom <= 100:
            logging.debug(
                f"The bottom coordinate should be in range 0 to 100, got"
                f" {self.bottom} (page {self.page.page_number})")
            self._bottom = min(max(0, self.bottom), 100)

    @property
    def left(self) -> Union[int, float]:
        return self._left

    @property
    def right(self) -> Union[int, float]:
        return self._right

    @property
    def top(self) -> Union[int, float]:
        return self._top

    @property
    def bottom(self) -> Union[int, float]:
        return self._bottom

    @property
    def page(self) -> 'Page':
        return self._page

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

    @property
    def area(self) -> float:
        """Area of the rectangle"""
        if self._area is None:
            self._area = self.width * self.height
        return self._area

    @property
    def xcenter(self) -> float:
        """Center of horizontal line of the rectangle"""
        if self._xcenter is None:
            self._xcenter = (self.left + self.right) / 2
        return self._xcenter

    @property
    def ycenter(self) -> float:
        """Center of vertical line of the rectangle"""
        if self._ycenter is None:
            self._ycenter = (self.top + self.bottom) / 2
        return self._ycenter

    @property
    def center(self) -> Tuple[float, float]:
        """Center point of the rectangle"""
        if self._center is None:
            self._center = (self.xcenter, self.ycenter)
        return self._center

    def intersects(self, other: Union['BoxTag', Cell]) -> bool:
        """Checks id there is an intersection between this and other rectangle

        :param other: Rectangle object
        """
        if isinstance(other, (BoxTag, Cell)):
            if (self.left < other.right and self.right > other.left
                and self.top < other.bottom and self.bottom > other.top) and \
                    self.page.page_number == other.page.page_number:
                return True
            return False
        else:
            raise NotImplementedError(
                f"Not implemented for item of type {type(other)}")

    def hshift(self, by) -> 'BoxTag':
        """Shifts rectangle horizontally

        :param by: the amount by which the tag should be horizontally shifted
        :return: shifted rectangle
        """
        return self.__class__(left=self.left + by, right=self.right + by,
                              top=self.top, bottom=self.bottom,
                              page=self.page)

    def vshift(self, by) -> 'BoxTag':
        """Shifts rectangle vertically

        :param by: the amount by which the tag should be vertically shifted
        :return: shifted rectangle
        """
        return self.__class__(left=self.left, right=self.right,
                              top=self.top + by, bottom=self.bottom + by,
                              page=self.page)

    def shift(self, horizontal, vertical) -> 'BoxTag':
        """Shifts rectangle by 2 axes simultaneously

        :param horizontal:
        :param vertical:
        :return: shifted rectangle
        """
        return self.hshift(horizontal).vshift(vertical)

    def __contains__(self, item: 'BoxTag') -> bool:
        """Checks if the item is in the rectangle

        :param item: The item to check
        """
        if isinstance(item, BoxTag):
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

    def __and__(self, other: Union['BoxTag', Cell]) -> Union[int, float]:
        """The area of intersection of given rectangles"""
        if isinstance(other, (BoxTag, Cell)):
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
        if isinstance(other, (BoxTag, Cell)):
            if self.page.page_number == other.page.page_number:
                return self.area + other.area - self.__and__(other)
            else:
                return 0
        else:
            raise NotImplementedError(
                f"Not implemented for item of type {type(other)}")

    def iou(self, other) -> Union[int, float]:
        """Calculate Intersection over Union for given rectangles"""
        if isinstance(other, (BoxTag, Cell)):
            if self.page.page_number == other.page.page_number:
                return (self & other) / (self | other)
            else:
                return 0
        else:
            raise NotImplementedError(
                f"Not implemented for item of type {type(other)}")

    def __add__(self, other: Union['BoxTag', Cell]) -> 'BoxTag':
        """Merge two rectangles into one"""
        if self.page.page_number == other.page.page_number:
            left = min(self.left, other.left)
            right = max(self.right, other.right)
            top = min(self.top, other.top)
            bottom = max(self.bottom, other.bottom)
            return BoxTag(left=left, right=right, top=top, bottom=bottom,
                          page=self.page)
        else:
            raise ValueError("Tags are not on the same page")

    def __radd__(self, other) -> 'BoxTag':
        """Merge two rectangles into one,
            required for using sum(<list of rectangles>)

        :param other: Another Rectangle object
        :return: Rectangle object with merged content
        """
        if other == 0:
            return self
        else:
            return self.__add__(other)

    def is_in_rectangle(self, other: "BoxTag", thresh: float) -> bool:
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
        if isinstance(other, BoxTag):
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

    def distance(self, other: 'BoxTag') -> Union[int, float]:
        """Return the Euclidean distance of two tag centers"""
        if self.page.page_number == other.page.page_number:
            dist = math.sqrt(
                (self.xcenter - other.xcenter)**2 +
                (self.ycenter - other.ycenter)**2)
        else:
            raise ValueError(
                "Can't compute distance between tags in different pages")
        return dist


class LineTag(Tag, metaclass=abc.ABCMeta):
    """Represents a tag that does not have height,
     and width is always 100%, hence a line"""

    def __init__(self,
                 top: Union[int, float],
                 page: 'Page',
                 tag_type: str):
        """Creates and validates coordinate data"""

        self._top = top
        self._page = page
        self._type = tag_type

    @property
    def top(self) -> Union[int, float]:
        return self._top

    @property
    def page(self) -> 'Page':
        return self._page

    @property
    def type(self) -> str:
        return self._type

    @classmethod
    @abc.abstractmethod
    def construct_from_raw(cls, raw: dict,
                           page: 'Page',
                           tag_type: str) -> 'LineTag':
        ...

    @abc.abstractmethod
    def to_dict(self) -> dict:
        """Return a dictionary representing the tag object"""
        pass
