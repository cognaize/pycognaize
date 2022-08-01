import pydantic
from typing import Union, List
from pycognaize.document.spanning.word import Word


class Line(pydantic.BaseModel):
    """Represents a line for span_tag"""
    left: Union[int, float]
    right: float
    top: float
    bottom: float
    raw_value: str
    words: List[Word]
