import itertools
import logging
from typing import Dict, List, Type, Optional

from pydantic import validator, root_validator

from pycognaize.common.enums import (
    IqDocumentKeysEnum,
    ID,
    IqFieldKeyEnum,
    IqDataTypesEnum
)
from pycognaize.common.utils import get_index_of_first_non_empty_list,\
                                    convert_tag_coords_to_percentages
from pycognaize.document import Page
from pycognaize.document.field.field import Field
from pycognaize.document.tag import TableTag
from pycognaize.document.tag.tag import Tag


class TableField(Field):
    """Representing AreaField in pycognaize"""

    tags: Optional[TableTag] = None

    _tag_class: Type[Tag] = TableTag

    @validator('tags')
    def validate_tags(cls, v):
        if v is None:
            return []
        return [v]

    def get_table_title(self, n_lines_above=8, margin=10) -> str:
        """Return the title of the table found on the pdf"""
        h = self.tags[0].page.image_height
        w = self.tags[0].page.image_width
        tags_converted = convert_tag_coords_to_percentages(
            self.tags[0], w=w, h=h)
        table_top = tags_converted['top']
        all_rows_above = []
        for line in self.tags[0].page.lines:
            all_rows_above.append(
                [w['ocr_text'] for w in line
                 if w['bottom'] < table_top + margin])
        index_of_first_non_empty_line = get_index_of_first_non_empty_list(
            all_rows_above)
        all_rows_above = all_rows_above[:index_of_first_non_empty_line + 1]
        title = ' '.join(
            itertools.chain.from_iterable(all_rows_above[-n_lines_above:]))
        return title

    @classmethod
    def construct_from_raw(
            cls, raw: dict, pages: Dict[int, Page]) -> 'TableField':
        """Create TableField object from dictionary"""
        tag_dicts: List[dict] = raw[IqDocumentKeysEnum.tags.value]
        tags = []
        for i in tag_dicts:
            try:
                tags.append(cls._tag_class.construct_from_raw(
                    raw=i, page=pages[i['page']]))
            except Exception as e:
                logging.debug(f"Failed creating tag for field {raw[ID]}: {e}")
        if len(tags) > 1:
            raise ValueError(
                f"{cls.__name__} cannot have {len(tags)}"
                f" {cls._tag_class.__name__}s")
        print(tags)
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

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.name}>"

    def __str__(self):
        return self.__repr__()
