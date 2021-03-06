import abc

from typing import List, Optional, Dict, Type

from pycognaize.common.enums import IqFieldKeyEnum
from pycognaize.document.page import Page
from pycognaize.document.tag.tag import Tag


class Field(metaclass=abc.ABCMeta):
    """Base class for all Field types"""
    tag_class: Type[Tag] = Tag

    def __init__(self, name: str, tags: Optional[List[Tag]] = None,
                 group_key: Optional[str] = None,
                 confidence: Optional[float] = -1.0
                 ):
        self._confidence = confidence
        if group_key is None:
            group_key = ''
        self._group_key = group_key
        self._name = name
        if tags is None:
            self._tags = []
        else:
            self._tags = tags

    @property
    def name(self):
        return self._name

    @property
    def tags(self):
        return self._tags

    @property
    def group_key(self):
        return self._group_key

    @group_key.setter
    def group_key(self, value):
        if not isinstance(value, str):
            raise TypeError(f"expected str, got {type(value)}")
        self._group_key = value

    @property
    def confidence(self):
        return self._confidence

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.name}>"

    def __str__(self):
        return f"{self.tags}"

    @classmethod
    @abc.abstractmethod
    def construct_from_raw(cls, raw: dict, pages: Dict[int, Page]) -> 'Field':
        """Use raw dictionary in order to recreate the Field python object"""
        pass

    @abc.abstractmethod
    def to_dict(self) -> dict:
        """Return a dictionary representing the field object"""
        field_dict = dict()
        field_dict[IqFieldKeyEnum.name.value] = self.name
        if self._group_key:
            field_dict[IqFieldKeyEnum.group_key.value] = self._group_key
        field_dict[IqFieldKeyEnum.tags.value] = [
            i.to_dict() for i in self.tags]
        return field_dict
