import logging
from typing import Dict, List, Type

from pycognaize.common.enums import (
    IqDocumentKeysEnum,
    ID,
    IqFieldKeyEnum,
    IqDataTypesEnum
)
from pycognaize.document import Page
from pycognaize.document.field.field import Field
from pycognaize.document.tag.span_tag import SpanTag


class SpanField(Field):
    """Representing AreaField in pycognaize"""

    _tag_class: Type[SpanTag] = SpanTag

    @classmethod
    def construct_from_raw(
            cls, raw: dict, pages: Dict[int, Page]) -> 'SpanField':
        """Create SnapField object from dictionary"""
        tag_dicts: List[dict] = raw[IqDocumentKeysEnum.tags.value]
        tags = []
        for i in tag_dicts:
            try:
                tags.append(cls._tag_class.construct_from_raw(
                    raw=i, page=pages[i['page']]))
            except Exception as e:
                logging.debug(f"Failed creating tag for field {raw[ID]}: {e}")
        return cls(name=raw[IqDocumentKeysEnum.name.value],
                   tags=tags[0] if tags else None,
                   field_id=str(raw[ID]),
                   group_key=raw.get(IqFieldKeyEnum.group_key.value, ''),
                   group_name=raw.get(IqFieldKeyEnum.group.value, '')
                   )

    def to_dict(self) -> dict:
        """Converts TableField object to dictionary"""
        field_dict = super().to_dict()
        field_dict[ID] = self.field_id
        field_dict[
            IqFieldKeyEnum.data_type.value] = IqDataTypesEnum.table.value
        field_dict[IqFieldKeyEnum.value.value] = ''
        return field_dict

    def order_tags(self):
        """Order tags by pdf data"""
        raise NotImplementedError

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.name}>"

    def __str__(self):
        return self.__repr__()
