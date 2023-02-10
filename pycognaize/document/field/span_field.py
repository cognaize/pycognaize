from typing import Optional, Dict, List, Type
import logging

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
                 tags: Optional[SpanTag] = None,
                 field_id: Optional[str] = None,
                 group_key: str = None,
                 confidence: Optional[float] = -1.0,
                 group_name: str = None,
                 ):
        tags = [] if tags is None else tags
        super().__init__(name=name, tags=tags,
                         group_key=group_key, confidence=confidence,
                         group_name=group_name)
        self._field_id = field_id

    @classmethod
    def construct_from_raw(cls, raw: dict, pages: Dict[int, Page],
                           html: Optional[HTML] = None) -> 'SpanField':
        """Create SnapField object from dictionary"""
        tag_dicts: List[dict] = raw[IqDocumentKeysEnum.tags.value]
        tags = []
        for i in tag_dicts:
            try:
                tags.append(cls.tag_class.construct_from_raw(
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
        field_dict[ID] = self._field_id
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
