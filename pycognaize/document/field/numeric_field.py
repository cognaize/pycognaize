import logging
import math
from typing import List, Optional, Dict, Type


from pycognaize.common.enums import (
    IqDocumentKeysEnum,
    ID,
    IqFieldKeyEnum,
    IqDataTypesEnum
)

from pycognaize.document.html_info import HTML
from pycognaize.document.page import Page
from pycognaize.document.field import Field
from pycognaize.document.tag import ExtractionTag
from pycognaize.document.tag.html_tag import HTMLTag


class NumericField(Field):
    """Base class for all pycognaize number fields"""
    tag_class: Type[ExtractionTag] = ExtractionTag
    html_tag_class: Type[HTMLTag] = HTMLTag

    def __init__(self,
                 name: str,
                 value: str = '',
                 calculated_value: str = '',
                 tags: Optional[List[ExtractionTag]] = None,
                 field_id: Optional[str] = None,
                 group_key: str = None,
                 confidence: Optional[float] = -1.0,
                 group_name: str = None,
                 scale: int = None
                 ):
        super().__init__(name=name, tags=tags, value=value,
                         group_key=group_key, confidence=confidence,
                         group_name=group_name)
        self.scale = scale
        self._field_id = field_id
        self._raw_field_value = value
        self._calculated_value = self.convert_to_numeric(calculated_value)
        self._value = self.convert_to_numeric(value)
        if math.isnan(self._value):
            self._value = self.calculated_value
        self._field_value = self.convert_to_numeric(value)
        self._tag_value = None
        if self.tags:
            self._value = sum([self.convert_to_numeric(i.raw_value)
                               for i in self.tags])
            self._tag_value = self._value

    @property
    def name(self):
        return self._name

    @property
    def value(self):
        return self._value

    @property
    def calculated_value(self):
        return self._calculated_value

    @property
    def field_value(self):
        return self._field_value

    @property
    def tag_value(self):
        return self._tag_value

    @property
    def raw_field_value(self):
        return self._raw_field_value

    @classmethod
    def construct_from_raw(cls, raw: dict, pages: Dict[int, Page],
                           html: Optional[HTML] = None,
                           labels=None) -> 'NumericField':
        """Create NumericField object from dictionary"""
        tag_dicts: List[dict] = raw[IqDocumentKeysEnum.tags.value]
        tags = []
        for i in tag_dicts:
            try:
                if pages:
                    tags.append(cls.tag_class.construct_from_raw(
                        raw=i, page=pages[i['page']]))
                else:
                    tags.append(cls.html_tag_class.construct_from_raw(
                        raw=i, html=html))
            except Exception as e:
                logging.debug(f"Failed creating tag for field {raw[ID]}: {e}")
        calculated_value = raw.get(IqFieldKeyEnum.calculated_value.value, '')
        field_value = raw[IqFieldKeyEnum.value.value]
        field_value = (tags[0].raw_value if (html.path and tags)
                       else field_value)
        return cls(name=raw[IqDocumentKeysEnum.name.value],
                   value=field_value,
                   calculated_value=calculated_value,
                   tags=tags,
                   field_id=str(raw[ID]),
                   group_key=raw.get(IqFieldKeyEnum.group_key.value, ''),
                   group_name=raw.get(IqFieldKeyEnum.group.value, ''),
                   scale=raw.get(IqFieldKeyEnum.scale.value, '')
                   )

    @staticmethod
    def convert_to_numeric(value):
        """converts string value to numeric"""
        # noinspection PyBroadException
        try:
            value = float(value)
        except Exception:
            value = float('nan')
        return value

    def to_dict(self) -> dict:
        """Converts NumericField object to dictionary"""
        field_dict = super().to_dict()
        field_dict[ID] = self._field_id
        field_dict[IqFieldKeyEnum.value.value] = self.value
        field_dict[
            IqFieldKeyEnum.data_type.value] = IqDataTypesEnum.number.value
        return field_dict

    def __repr__(self):
        return (f"<{self.__class__.__name__}: {self.name}:"
                f" {'|'.join([i.raw_value for i in self.tags])}>")

    def __str__(self):
        return f"{'|'.join([i.raw_value for i in self.tags])}"
