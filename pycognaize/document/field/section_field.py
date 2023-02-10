import logging
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
from pycognaize.document.tag.section_tag import SectionTag


class SectionField(Field):
    """Base class for all pycognaize Section fields"""
    tag_class: Type[SectionTag] = SectionTag

    def __init__(self,
                 name: str,
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

    @classmethod
    def construct_from_raw(cls, raw: dict, pages: Dict[int, Page],
                           html: Optional[HTML] = None) -> 'SectionField':
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
                   tags=tags,
                   field_id=str(raw[ID]),
                   group_key=raw.get(IqFieldKeyEnum.group_key.value, ''),
                   group_name=raw.get(IqFieldKeyEnum.group.value, '')
                   )

    def to_dict(self) -> dict:
        """Converts TextField object to dictionary"""
        field_dict = super().to_dict()
        field_dict[ID] = self._field_id
        field_dict[IqFieldKeyEnum.value.value] = self.value
        field_dict[IqFieldKeyEnum.data_type.value] = IqDataTypesEnum.text.value
        return field_dict

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.name}>"

    def __str__(self):
        return f"<{self.__class__.__name__}: {self.name}>"
