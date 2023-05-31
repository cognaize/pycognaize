import logging
from typing import List, Optional, Dict, Type

import bson

from pycognaize.common.enums import (
    IqDocumentKeysEnum,
    ID, START, END,
    IqFieldKeyEnum, IqDataTypesEnum,
)
from pycognaize.document.html_info import HTML
from pycognaize.document.page import Page
from pycognaize.document.field import Field
from pycognaize.document.tag.section_tag import SectionTag


class SectionField(Field):
    """Base class for all pycognaize Section fields"""
    tag_class: Type[SectionTag] = SectionTag

    def __init__(self,
                 name: str,
                 value: str = '',
                 ocr_value: str = '',
                 tags: Optional[List[SectionTag]] = None,
                 field_id: Optional[str] = None,
                 group_key: str = None,
                 confidence: Optional[float] = -1.0,
                 group_name: str = None
                 ):
        """ Create a SectionField object

        :param name: Name of the field
        :param value: Value of the field
            (left empty if values provided through tags)
        :param tags: List of tag objects
        :param field_id: The id of the field
        """
        super().__init__(name=name, tags=tags,
                         group_key=group_key, confidence=confidence,
                         group_name=group_name)
        self._field_id = field_id
        self._value = value
        self._ocr_value = ocr_value

    @property
    def start(self) -> Optional[SectionTag]:
        """Returns the start tag of the field"""
        return self.tags[0] if len(self.tags) > 0 else None

    @property
    def end(self) -> Optional[SectionTag]:
        """Returns the end tag of the field"""
        return self.tags[1] if len(self.tags) == 2 else None

    @classmethod
    def construct_from_raw(cls, raw: dict, pages: Dict[int, Page],
                           html: Optional[HTML] = None,
                           labels=None) -> 'SectionField':
        """Create SectionField object from dictionary"""
        section_dict: List[dict] = raw[IqDocumentKeysEnum.tags.value]
        tags = []
        for i in section_dict:
            for tag_type, tag_data in i[IqDocumentKeysEnum.
                                        section.value].items():
                try:
                    tags.append(cls.tag_class.construct_from_raw(
                                raw=tag_data,
                                pages=pages,
                                tag_type=tag_type))
                except Exception as e:
                    logging.debug(f"Failed creating tag"
                                  f" for field {raw[ID]}: {e}")

        return cls(name=raw[IqDocumentKeysEnum.name.value],
                   value=section_dict[0][
                       IqFieldKeyEnum.value.value] if section_dict else '',
                   ocr_value=section_dict[0][
                       IqFieldKeyEnum.ocr_value.value] if section_dict else '',
                   tags=tags,
                   field_id=str(raw[ID]),
                   group_key=raw.get(IqFieldKeyEnum.group_key.value, ''),
                   group_name=raw.get(IqFieldKeyEnum.group.value, '')
                   )

    def to_dict(self) -> dict:
        """Converts SectionField object to dictionary"""
        field_dict = dict()
        field_dict[IqFieldKeyEnum.name.value] = self.name
        field_dict[ID] = self.field_id
        field_dict[IqFieldKeyEnum.group_key.value] = self._group_key
        field_dict[IqFieldKeyEnum.group.value] = self._group_name
        field_dict[IqFieldKeyEnum.value.value] = ''
        field_dict[IqFieldKeyEnum.data_type.value] =\
            IqDataTypesEnum.section.value
        field_dict[IqFieldKeyEnum.tags.value] = []
        if self.start is not None and self.end is not None:
            tag_data = {
                ID: str(bson.ObjectId()),
                IqFieldKeyEnum.value.value: self._value,
                IqFieldKeyEnum.ocr_value.value: self._ocr_value,
                IqFieldKeyEnum.section.value: {
                    START: self.start.to_dict(),
                    END: self.end.to_dict()
                }
            }
            field_dict[IqFieldKeyEnum.tags.value].append(tag_data)
        return field_dict

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.name}>"

    def __str__(self):
        return f"<{self.__class__.__name__}: {self.name}>"
