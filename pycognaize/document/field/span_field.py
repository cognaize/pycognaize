from typing import Optional, Dict, List, Type
import logging

from pycognaize.common.classification_labels import ClassificationLabels
from pycognaize.common.enums import (
    IqDocumentKeysEnum,
    ID,
    IqDataTypesEnum,
    IqFieldKeyEnum
)

from pycognaize.document.field import Field
from pycognaize.document.html_info import HTML
from pycognaize.document.tag.span_tag import SpanTag
from pycognaize.document.page import Page


class SpanField(Field):
    """Base class for all pycognaize table fields"""
    tag_class: Type[SpanTag] = SpanTag

    def __init__(self,
                 name: str,
                 value: str,
                 tags: Optional[SpanTag] = None,
                 field_id: Optional[str] = None,
                 group_key: str = None,
                 confidence: Optional[float] = -1.0,
                 group_name: str = None,
                 ):
        tags = [] if tags is None else tags
        super().__init__(name=name, tags=tags,
                         group_key=group_key, confidence=confidence,
                         group_name=group_name, value=value)

        self._field_id = field_id
        self._value = ''
        self._line_values = [i.raw_value for i in self.tags] \
            if self.tags else value

    @property
    def value(self):
        return self._value

    @property
    def line_values(self):
        return self._line_values

    @classmethod
    def construct_from_raw(cls, raw: dict, pages: Dict[int, Page],
                           html: Optional[HTML] = None,
                           labels: ClassificationLabels = None) -> 'SpanField':
        """Create SnapField object from dictionary"""
        tag_dicts: List[dict] = raw[IqDocumentKeysEnum.tags.value]
        tags = []
        value = ''
        for i in tag_dicts:
            try:
                tags.append(cls.tag_class.construct_from_raw(
                    raw=i, page=pages[i['page']]))
                value = value + i['value']
            except Exception as e:
                logging.debug(f"Failed creating tag for field {raw[ID]}: {e}")
        return cls(name=raw[IqDocumentKeysEnum.name.value],
                   tags=tags if tags else None,
                   value=value,
                   field_id=str(raw[ID]),
                   group_key=raw.get(IqFieldKeyEnum.group_key.value, ''),
                   group_name=raw.get(IqFieldKeyEnum.group.value, ''),
                   )

    def to_dict(self) -> dict:
        """Converts SpanField object to dictionary"""
        field_dict = dict()
        field_dict[ID] = self._field_id
        field_dict[IqFieldKeyEnum.name.value] = self.name
        field_dict[
            IqFieldKeyEnum.data_type.value] = IqDataTypesEnum.span.value
        field_dict[IqFieldKeyEnum.value.value] = ""
        field_dict[IqFieldKeyEnum.group_key.value] = self._group_key
        field_dict[IqFieldKeyEnum.tags.value] = []
        if self.tags:
            for tag in self.tags:
                field_dict[IqFieldKeyEnum.tags.value].append(tag.to_dict())
        return field_dict

    def order_tags(self):
        """Order tags by pdf data"""
        raise NotImplementedError

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.name}>"

    def __str__(self):
        return self.__repr__()
