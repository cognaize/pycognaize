import logging
from typing import List, Optional, Dict, Type


from pycognaize.common.enums import (
    IqDocumentKeysEnum,
    ID,
    IqFieldKeyEnum,
    IqDataTypesEnum
)
from pycognaize.document.field import Field
from pycognaize.document.html_info import HTML
from pycognaize.document.tag import ExtractionTag
from pycognaize.document.page import Page


class DateField(Field):
    """Base class for all pycognaize date fields"""
    tag_class: Type[ExtractionTag] = ExtractionTag

    def __init__(self,
                 name: str,
                 value: str = '',
                 tags: Optional[List[ExtractionTag]] = None,
                 field_id: Optional[str] = None,
                 group_key: str = None,
                 confidence: Optional[float] = -1.0,
                 group_name: str = None
                 ):
        super().__init__(name=name, value=value, tags=tags,
                         group_key=group_key, confidence=confidence,
                         group_name=group_name)
        self._field_id = field_id
        self._value = '; '.join([i.raw_value
                                 for i in self.tags]) if self.tags else value

    @property
    def field_id(self):
        return self._field_id

    @property
    def value(self):
        return self._value

    @classmethod
    def construct_from_raw(
            cls, raw: dict, pages: Dict[int, Page],
            html: Optional[HTML] = None) -> 'DateField':
        """Create DateField object from dictionary"""
        tag_dicts: List[dict] = raw[IqDocumentKeysEnum.tags.value]
        tags = []
        for i in tag_dicts:
            try:
                tags.append(cls.tag_class.construct_from_raw(
                    raw=i, page=pages[i['page']]))
            except Exception as e:
                logging.debug(f"Failed creating tag for field {raw[ID]}: {e}")
        return cls(name=raw[IqDocumentKeysEnum.name.value],
                   value=raw[IqFieldKeyEnum.value.value],
                   tags=tags,
                   field_id=str(raw[ID]),
                   group_key=raw.get(IqFieldKeyEnum.group_key.value, ''),
                   group_name=raw.get(IqFieldKeyEnum.group.value, '')
                   )

    def to_dict(self) -> dict:
        """Converts DateField object to dictionary"""
        field_dict = super().to_dict()
        field_dict[IqFieldKeyEnum.value.value] = self.value
        field_dict[ID] = self._field_id
        field_dict[IqFieldKeyEnum.data_type.value] = IqDataTypesEnum.date.value
        return field_dict

    def __repr__(self):
        return (f"<{self.__class__.__name__}: {self.name}:"
                f" {'|'.join([i.raw_value for i in self.tags])}>")

    def __str__(self):
        return f"{'|'.join([i.raw_value for i in self.tags])}"
