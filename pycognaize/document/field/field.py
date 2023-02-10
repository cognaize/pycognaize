import abc

from typing import List, Optional, Dict, Type

from pycognaize.common.enums import IqFieldKeyEnum
from pycognaize.document.html_info import HTML
from pycognaize.document.page import Page
from pycognaize.document.tag.tag import BoxTag


class Field(metaclass=abc.ABCMeta):
    """Base class for all Field types"""
    tag_class: Type[BoxTag] = BoxTag

    def __init__(self, name: str,
                 value: str = '',
                 tags: Optional[List[BoxTag]] = None,
                 field_id: Optional[str] = None,
                 group_key: Optional[str] = None,
                 confidence: Optional[float] = -1.0,
                 group_name: Optional[str] = None,
                 ):
        self._raw_value = value
        self._confidence = confidence
        if group_key is None:
            group_key = ''
        self._group_key = group_key
        if group_name is None:
            group_name = ''
        self._group_name = group_name
        self._name = name
        if tags is None:
            self._tags = []
        else:
            self._tags = tags
        self._value = value
        self._field_id = field_id

    @property
    def raw_value(self):
        return self._raw_value

    @property
    def name(self):
        return self._name

    @property
    def tags(self):
        return self._tags

    @property
    def group_key(self):
        return self._group_key

    @property
    def group_name(self):
        return self._group_name

    @property
    def value(self):
        return self._value

    @property
    def field_id(self):
        return self._field_id

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
    def construct_from_raw(cls, raw: dict, pages: Dict[int, Page],
                           html: Optional[HTML] = None) -> 'Field':
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
