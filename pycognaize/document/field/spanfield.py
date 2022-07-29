import itertools
from typing import Optional, Dict, List, Type

import logging


from pycognaize.common.enums import (
    IqDocumentKeysEnum,
    ID,
    IqDataTypesEnum,
    IqFieldKeyEnum
)

from pycognaize.document.field import Field
from pycognaize.document.tag.span_tag import SpanTag
from pycognaize.document.page import Page


class SpanField(Field):
    """Base class for all pycognaize table fields"""
    tag_class: Type[SpanTag] = SpanTag

    def __init__(self,
                 name: str,
                 tag: Optional[SpanTag] = None,
                 field_id: Optional[str] = None,
                 group_key: str = None,
                 confidence: Optional[float] = -1.0
                 ):
        tags = [] if tag is None else [tag]
        super().__init__(name=name, tags=tags, group_key=group_key,
                         confidence=confidence)
        self._field_id = field_id

    @classmethod
    def construct_from_raw(
            cls, raw: dict, pages: Dict[int, Page]) -> 'SpanField':
        """Create SnapField object from dictionary"""
        tag_dicts: List[dict] = raw[IqDocumentKeysEnum.tags.value]
        tags = []
        for i in tag_dicts:
            try:
                tags.append(cls.tag_class.construct_from_raw(
                    raw=i, page=pages[i['page']]))
            except Exception as e:
                logging.debug(f"Failed creating tag for field {raw[ID]}: {e}")
        if len(tags) > 1:
            raise ValueError(
                f"{cls.__name__} cannot have {len(tags)}"
                f" {cls.tag_class.__name__}s")
        return cls(name=raw[IqDocumentKeysEnum.name.value],
                   tag=tags[0] if tags else None,
                   field_id=str(raw[ID]),
                   group_key=raw.get(IqFieldKeyEnum.group_key.value, '')
                   )

    def to_dict(self) -> dict:
        """Converts TableField object to dictionary"""
        field_dict = super().to_dict()
        field_dict[ID] = self._field_id
        field_dict[
            IqFieldKeyEnum.data_type.value] = IqDataTypesEnum.table.value
        field_dict[IqFieldKeyEnum.value.value] = ''
        return field_dict

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.name}>"

    def __str__(self):
        return self.__repr__()
