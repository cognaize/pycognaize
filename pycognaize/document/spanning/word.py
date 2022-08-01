import pydantic
from typing import Union, List
from pycognaize.document.spanning.character import Character


class Word(pydantic.BaseModel):
    """Represents a word in a line class for span_tag"""
    left: Union[int, float]
    right: float
    top: float
    bottom: float
    raw_value: str
    character: List[Character]
