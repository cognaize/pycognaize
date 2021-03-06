import logging
from typing import List, Optional, Dict, Type


from pycognaize.common.enums import (
    IqDocumentKeysEnum,
    IqTagKeyEnum,
    ID,
    IqFieldKeyEnum,
    IqDataTypesEnum
)
from pycognaize.document.page import Page
from pycognaize.document.field import Field
from pycognaize.document.tag import ExtractionTag


class NumericField(Field):
    """Base class for all pycognaize number fields"""
    tag_class: Type[ExtractionTag] = ExtractionTag

    def __init__(self,
                 name: str,
                 value: str = '',
                 tags: Optional[List[ExtractionTag]] = None,
                 field_id: Optional[str] = None,
                 group_key: str = None,
                 confidence: Optional[float] = -1.0
                 ):
        super().__init__(name=name, tags=tags, group_key=group_key,
                         confidence=confidence)
        self._field_id = field_id
        self._value = self.convert_to_numeric(value)
        self._raw_value = value
        if self.tags:
            self._value = sum([self.convert_to_numeric(i.raw_value)
                               for i in self.tags])

    @property
    def name(self):
        return self._name

    @property
    def value(self):
        return self._value

    @staticmethod
    def convert_to_numeric(value):
        """converts string value to numeric"""
        # noinspection PyBroadException
        try:
            value = float(value)
        except Exception:
            value = float('nan')
        return value

    @classmethod
    def construct_from_raw(
            cls, raw: dict, pages: Dict[int, Page]) -> 'NumericField':
        """Create NumericField object from dictionary"""
        tag_dicts: List[dict] = raw[IqDocumentKeysEnum.tags.value]
        tags = []
        for i in tag_dicts:
            try:
                tags.append(cls.tag_class.construct_from_raw(
                    raw=i, page=pages[i['page']]))
            except Exception as e:
                logging.debug(f"Failed creating tag for field {raw[ID]}: {e}")
        return cls(name=raw[IqDocumentKeysEnum.name.value],
                   value=raw[IqTagKeyEnum.value.value],
                   tags=tags,
                   field_id=str(raw[ID]),
                   group_key=raw.get(IqFieldKeyEnum.group_key.value, '')
                   )

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
