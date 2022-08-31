import sys
from typing import Optional, List, Dict, Type, Union

from pydantic import BaseModel, validator

from pycognaize.common.decorators import soon_be_deprecated
from pycognaize.common.enums import IqFieldKeyEnum
from pycognaize.document import Page
from pycognaize.document.tag import ExtractionTag, TableTag


class Field(BaseModel):
    """Base class for all Field types in pycognaize"""

    class Config:
        """Configuration for Field Pydantic model"""
        arbitrary_types_allowed = True
        validate_assignment = True
        if sys.version_info < (3, 9):
            kw_only = False

    name: str
    value: str = ''
    tags: Union[Optional[List[ExtractionTag]], Optional[List[TableTag]], List, None] = []
    # tags: Union[ExtractionTag] = []
    field_id: Optional[str] = None
    group_key: Optional[str] = None
    group_name: Optional[str] = None
    confidence: Optional[float] = -1.0

    @validator('tags')
    def validate_tags(cls, v):
        if v is None:
            return []
        return v

    @classmethod
    @soon_be_deprecated(version='1.2.0')
    def construct_from_raw(cls, raw: dict, pages: Dict[int, Page]) -> 'Field':
        """Use raw dictionary in order to recreate the Field python object"""
        pass

    @soon_be_deprecated(version='1.2.0')
    def to_dict(self) -> dict:
        """Return a dictionary representing the field object"""
        field_dict = dict()
        field_dict[IqFieldKeyEnum.name.value] = self.name
        if self.group_key:
            field_dict[IqFieldKeyEnum.group_key.value] = self.group_key
        field_dict[IqFieldKeyEnum.tags.value] = [
            i.to_dict() for i in self.tags]
        return field_dict

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.name}>"

    def __str__(self):
        return f"{self.tags}"
