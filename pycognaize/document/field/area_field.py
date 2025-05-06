"""
| Base class for all pycognaize area fields.
| AreaField objects represent a defined area within a document, often used for extracting specific regions such as blocks of text, images, or tables.
| These fields can contain one or more tags defining their boundaries, or a direct value if tags are not available.
"""
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
from pycognaize.document.page import Page
from pycognaize.document.tag import ExtractionTag
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
                 classification_labels: Optional[ClassificationLabels] = None,
                 mapping: Optional[List[Dict[str, str]]] = None
                 ):
        """
        Create a new AreaField object.

        :param name: Name of the field.
        :param value: Value of the field (if no tags are provided).
        :param tags: List of tag objects defining the area boundaries.
        :param field_id: The unique identifier for the field.
        :param group_key: Group key for the field.
        :param confidence: Confidence level of the extracted field.
        :param group_name: Group name for the field.
        :param classification_labels: Optional classification labels.
        """
        super().__init__(name=name, value=value, tags=tags,
                         group_key=group_key, confidence=confidence,
                         group_name=group_name, mapping=mapping)
        self._field_id = field_id
        self._classification_labels = classification_labels
        # If tags are provided, concatenate their values; otherwise, use the provided value
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
        """Get the value of the field."""
        return self._value

    @classmethod
    def construct_from_raw(cls, raw: dict, pages: Dict[int, Page],
                           html: Optional[HTML] = None,
                           labels: ClassificationLabels = None) \
            -> 'AreaField':
        """
        Create AreaField object from dictionary

        :param raw: Raw dictionary containing field data.
        :param pages: Dictionary containing page objects.
        :param html: HTML info object.
        :param labels: Classification labels object.
        :return: Constructed AreaField object.
        """
        
        tag_dicts: List[dict] = raw[IqDocumentKeysEnum.tags.value]
        tags = []
        # Construct tag objects from raw data        
        for i in tag_dicts:
            try:
                tags.append(cls.tag_class.construct_from_raw(
                    raw=i, page=pages[i['page']]))
            except Exception as e:
                logging.debug(f"Failed creating tag for field {raw[ID]}: {e}")
        # Extract classes from raw data
        try:
            classes_from_raw = raw[IqDocumentKeysEnum.classes.value]
        except KeyError:
            classes = None
        else:
            classes = classes_from_raw.split(';') if classes_from_raw else None
        # Create new AreaField object
        new_object = cls(name=raw[IqDocumentKeysEnum.name.value],
                         value=raw[IqTagKeyEnum.value.value],
                         tags=tags,
                         field_id=str(raw[ID]),
                         group_key=raw.get(IqFieldKeyEnum.group_key.value, ''),
                         group_name=raw.get(IqFieldKeyEnum.group.value, ''),
                         classification_labels=labels,
                         mapping=raw.get(IqFieldKeyEnum.mapping.value, [])
                         )

        new_object._classes = classes
        return new_object

    def to_dict(self) -> dict:
        """Converts an AreaField object to dictionary"""
        field_dict = super().to_dict()
        field_dict[IqFieldKeyEnum.value.value] = self.value
        field_dict[ID] = self._field_id
        field_dict[IqFieldKeyEnum.data_type.value] = IqDataTypesEnum.area.value
        return field_dict

    def __repr__(self):
        """Return a string representation of the AreaField object."""
        return (f"<{self.__class__.__name__}: {self.name}:"
                f" {'|'.join([i.raw_value for i in self.tags])}>")

    def __str__(self):
        """Return a string representation of the AreaField object."""
        return f"{'|'.join([i.raw_value for i in self.tags])}"
