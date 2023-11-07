import logging
from typing import List, Optional, Dict, Type, Union

from pycognaize.common.classification_labels import ClassificationLabels
from pycognaize.common.enums import (
    IqDocumentKeysEnum,
    IqTagKeyEnum,
    ID,
    IqFieldKeyEnum,
    IqDataTypesEnum
)
from pycognaize.document.field import Field
from pycognaize.document.html_info import HTML
from pycognaize.document.tag import ExtractionTag
from pycognaize.document.page import Page
from pycognaize.document.tag.html_tag import HTMLTag


class AreaField(Field):
    """Base class for all pycognaize area fields"""
    tag_class: Type[ExtractionTag] = ExtractionTag

    def __init__(self,
                 name: str,
                 value: str = '',
                 tags: Optional[List[Union[ExtractionTag, HTMLTag]]] = None,
                 field_id: Optional[str] = None,
                 group_key: str = None,
                 confidence: Optional[float] = -1.0,
                 group_name: str = None,
                 classification_labels: Optional[ClassificationLabels] = None
                 ):
        super().__init__(name=name, value=value, tags=tags,
                         group_key=group_key, confidence=confidence,
                         group_name=group_name)
        self._field_id = field_id
        self._classification_labels = classification_labels
        if self.tags:
            self._value = '; '.join([i.raw_value for i in self.tags])
        elif isinstance(value, str):
            self._value = value
        else:
            logging.warning(
                f"Expected value of type str, received {type(value)},"
                f" setting value to empty string")
            self._value = ''

    @property
    def value(self):
        return self._value

    @classmethod
    def construct_from_raw(cls, raw: dict, pages: Dict[int, Page],
                           html: Optional[HTML] = None,
                           labels: ClassificationLabels = None)\
            -> 'AreaField':
        """Create AreaField object from dictionary"""
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
                   group_key=raw.get(IqFieldKeyEnum.group_key.value, ''),
                   group_name=raw.get(IqFieldKeyEnum.group.value, ''),
                   classification_labels=labels)

    def to_dict(self) -> dict:
        """Converts AreaField object to dictionary"""
        field_dict = super().to_dict()
        field_dict[IqFieldKeyEnum.value.value] = self.value
        field_dict[ID] = self._field_id
        field_dict[IqFieldKeyEnum.data_type.value] = IqDataTypesEnum.area.value
        return field_dict

    def __repr__(self):
        """Return a string representation of the object.

        Returns:
            str: A string containing the representation of the object,
                 which includes the class name, object's name, and a
                 concatenation of its tags separated by '|'. If a tag's
                 raw value is None, it will be represented as an empty string.
        """
        tag_str = '|'.join(
            [i.raw_value if i.raw_value is not None else '' for i in self.tags]
        )
        tag_value = "tag value"
        field_str = self.raw_value
        field_value = "field value"
        repr_string = (f"<{self.__class__.__name__}: {self.name}: "
                       f"{field_value} - {field_str}: {tag_value} - "
                       f"{tag_str}>")
        return repr_string

    def __str__(self):
        """Return a string representation of the object.

        Returns:
            str: A string containing the representation of the object's tags
                 as a concatenation, separated by '|'. If a tag's raw value
                 is None, it will be represented as an empty string in the
                  output.
        """
        value_str = '|'.join(
            [i.raw_value if i.raw_value is not None else '' for i in self.tags]
        )
        return value_str
