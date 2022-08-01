import logging
import pydantic
from typing import Union


class Character(pydantic.BaseModel):
    """Represents a character in a word class for span_tag"""
    left: Union[int, float]
    right: Union[int, float]
    top: Union[int, float]
    bottom: Union[int, float]
    raw_value: str

    @pydantic.root_validator
    @classmethod
    def validate_coordinates(cls, values):
        left, right, top, bottom = values.get('left'), values.get('right'), \
                                   values.get('top'), values.get('bottom')
        if left > right:
            raise ValueError(f"Left ({left}) cannot be"
                             f" bigger than right ({right})")
        elif top > bottom:
            raise ValueError(f"Top ({top}) cannot be"
                             f" bigger than bottom ({bottom})")
        elif left == right:
            raise ValueError(f"Left ({left}) cannot be"
                             f" equal to right ({right})")
        elif top == bottom:
            raise ValueError(f"Top ({top}) cannot be"
                             f" equal to bottom ({bottom})")
        return values

    @pydantic.root_validator
    @classmethod
    def validate_ranges(cls, values):
        left, right, top, bottom = values.get('left'), values.get('right'), \
                                   values.get('top'), values.get('bottom')
        if not 0 <= left <= 100:
            logging.debug(
                f"The left coordinate should be in range 0 to 100, got {left}")
            values["left"] = min(max(0, left), 100)
        if not 0 <= right <= 100:
            logging.debug(
                f"The right coordinate should be in range 0 to 100,"
                f" got {right}")
            values["right"] = min(max(0, right), 100)
        if not 0 <= top <= 100:
            logging.debug(
                f"The top coordinate should be in range 0 to 100, got {top}")
            values["top"] = min(max(0, top), 100)
        if not 0 <= bottom <= 100:
            logging.debug(
                f"The bottom coordinate should be in range 0 to 100,"
                f" got {bottom}")
            values["bottom"] = min(max(0, bottom), 100)
        return values
