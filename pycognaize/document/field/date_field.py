import logging
from typing import Type, Dict, List

from pydantic import root_validator

from pycognaize.common.enums import (
    IqDocumentKeysEnum,
    ID,
    IqFieldKeyEnum,
    IqDataTypesEnum
)
from pycognaize.document import Page

from pycognaize.document.field.field import Field
from pycognaize.document.tag import ExtractionTag


class DateField(Field):

    tag_class: Type[ExtractionTag] = ExtractionTag

    @root_validator()
    def validate_value(cls, values):
        """Validate and create value from tags"""
        tags = values['tags']
        value = values['value']
        if tags:
            value = '; '.join([i.raw_value for i in tags])\
                    if tags else value
        else:
            logging.warning(
                f"Expected tags array, received {tags},"
                f" setting value to empty string")
            value = ''
        values['value'] = value
        return values

    @classmethod
    def construct_from_raw(
            cls, raw: dict, pages: Dict[int, Page]) -> 'DateField':
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
        field_dict[ID] = self.field_id
        field_dict[IqFieldKeyEnum.data_type.value] = IqDataTypesEnum.date.value
        return field_dict

    def __repr__(self):
        return (f"<{self.__class__.__name__}: {self.name}:"
                f" {'|'.join([i.raw_value for i in self.tags])}>")

    def __str__(self):
        return f"{'|'.join([i.raw_value for i in self.tags])}"
