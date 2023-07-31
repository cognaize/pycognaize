"""
| TextField objects represent a single labeled pycognaize field.
| The latter can have no tags, a single tag or multiple tags.

>>> from pycognaize.document.field.text_field import TextField
>>> text_field = TextField(name='company name', value='gooloogooloo')
>>> text_field.name
'company name'
>>> text_field.value
'gooloogooloo'
>>> text_field.tags
[]
"""
import logging
from typing import List, Optional, Dict, Type

from pycognaize.common.classification_labels import ClassificationLabels
from pycognaize.common.enums import (
    IqDocumentKeysEnum,
    IqTagKeyEnum,
    ID,
    IqFieldKeyEnum,
    IqDataTypesEnum
)
from pycognaize.document.html_info import HTML
from pycognaize.document.page import Page
from pycognaize.document.field import Field
from pycognaize.document.tag import ExtractionTag
from pycognaize.document.tag.html_tag import HTMLTag


class TextField(Field):
    """Base class for all pycognaize text fields"""
    tag_class: Type[ExtractionTag] = ExtractionTag
    html_tag_class: Type[HTMLTag] = HTMLTag

    def __init__(self,
                 name: str,
                 value: str = '',
                 tags: Optional[List[ExtractionTag]] = None,
                 field_id: Optional[str] = None,
                 group_key: str = None,
                 confidence: Optional[float] = -1.0,
                 group_name: str = None,
                 classification_labels: Optional[ClassificationLabels] = None
                 ):
        """ Create a TextField object

        :param name: Name of the field
        :param value: Value of the field
            (left empty if values provided through tags)
        :param tags: List of tag objects
        :param field_id: The id of the field
        """
        super().__init__(name=name, tags=tags, value=value,
                         group_key=group_key, confidence=confidence,
                         group_name=group_name)
        self._classification_labels = classification_labels
        self._field_id = field_id
        self._value = '; '.join([i.raw_value
                                 for i in self.tags]) if self.tags else value

    @property
    def value(self):
        return self._value

    @classmethod
    def construct_from_raw(cls, raw: dict, pages: Dict[int, Page],
                           html: Optional[HTML] = None,
                           labels: ClassificationLabels = None)\
            -> 'TextField':
        """Create TextField object from dictionary"""
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
        value = (tags[0].raw_value if (html.path and tags)
                 else raw[IqTagKeyEnum.value.value])
        return cls(name=raw[IqDocumentKeysEnum.name.value],
                   value=value,
                   tags=tags,
                   field_id=str(raw[ID]),
                   group_key=raw.get(IqFieldKeyEnum.group_key.value, ''),
                   group_name=raw.get(IqFieldKeyEnum.group.value, ''),
                   classification_labels=labels)

    def to_dict(self) -> dict:
        """Converts TextField object to dictionary"""
        field_dict = super().to_dict()
        field_dict[ID] = self._field_id
        field_dict[IqFieldKeyEnum.value.value] = self.value
        field_dict[IqFieldKeyEnum.data_type.value] = IqDataTypesEnum.text.value
        return field_dict

    def __repr__(self):
        """Return a string representation of the object.

        Returns:
            str: A string containing the representation of the object,
                 which includes the class name, object's name, and a
                 concatenation of its tags separated by '|'. If a tag's
                 raw value is None, it will be represented as an empty string.
        """
        tags_str = '|'.join(
            [i.raw_value if i.raw_value is not None else '' for i in self.tags]
        )
        repr_string = f"<{self.__class__.__name__}: {self.name}: {tags_str}>"
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
