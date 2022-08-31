import logging
from typing import Type, Dict, List

from pydantic import validator, root_validator

from pycognaize.common.enums import (
    IqDocumentKeysEnum,
    ID,
    IqFieldKeyEnum,
    IqDataTypesEnum, IqTagKeyEnum
)
from pycognaize.document import Page

from pycognaize.document.field.field import Field
from pycognaize.document.tag import ExtractionTag


class NumericField(Field):

    _tag_class: Type[ExtractionTag] = ExtractionTag

    def convert_to_numeric(value):
        try:
            value = float(value)
        except Exception:
            value = float('nan')

        return value

    @root_validator()
    def validate_value(cls, values):
        """Validate and create value from tags"""
        tags = values['tags']
        value = cls.convert_to_numeric(values['value'])

        if tags:
            value = sum([cls.convert_to_numeric(i.raw_value)
                               for i in tags])
        else:
            logging.warning(
                f"Expected tags array, received {tags},"
                f" setting value to empty string")
        values['value'] = value
        return values

    @classmethod
    def construct_from_raw(
            cls, raw: dict, pages: Dict[int, Page]) -> 'NumericField':
        """Create NumericField object from dictionary"""
        tag_dicts: List[dict] = raw[IqDocumentKeysEnum.tags.value]
        tags = []
        for i in tag_dicts:
            try:
                tags.append(cls._tag_class.construct_from_raw(
                    raw=i, page=pages[i['page']]))
            except Exception as e:
                logging.debug(f"Failed creating tag for field {raw[ID]}: {e}")
        return cls(name=raw[IqDocumentKeysEnum.name.value],
                   value=raw[IqTagKeyEnum.value.value],
                   tags=tags,
                   field_id=str(raw[ID]),
                   group_key=raw.get(IqFieldKeyEnum.group_key.value, ''),
                   group_name=raw.get(IqFieldKeyEnum.group.value, '')
                   )

    def to_dict(self) -> dict:
        """Converts NumericField object to dictionary"""
        field_dict = super().to_dict()
        field_dict[ID] = self.field_id
        field_dict[IqFieldKeyEnum.value.value] = self.value
        field_dict[
            IqFieldKeyEnum.data_type.value] = IqDataTypesEnum.number.value
        return field_dict

    def __repr__(self):
        return (f"<{self.__class__.__name__}: {self.name}:"
                f" {'|'.join([i.raw_value for i in self.tags])}>")

    def __str__(self):
        return f"{'|'.join([i.raw_value for i in self.tags])}"
