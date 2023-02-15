import itertools
import unicodedata
from typing import Optional, Dict, List, Type, Union

import logging


from pycognaize.common.enums import (
    IqDocumentKeysEnum,
    ID,
    IqDataTypesEnum,
    IqFieldKeyEnum
)
from pycognaize.common.utils import (
    convert_tag_coords_to_percentages,
    get_index_of_first_non_empty_list, filter_out_nested_lines
)
from pycognaize.document.field import Field
from pycognaize.document.html_info import HTML
from pycognaize.document.tag import TableTag, ExtractionTag
from pycognaize.document.tag.html_tag import HTMLTableTag
from pycognaize.document.tag.tag import BoxTag
from pycognaize.document.page import Page


class TableField(Field):
    """Base class for all pycognaize table fields"""
    tag_class: Type[BoxTag] = TableTag
    html_tag_class: Type[HTMLTableTag] = HTMLTableTag

    def __init__(self,
                 name: str,
                 tag: Optional[Union[TableTag, HTMLTableTag]] = None,
                 field_id: Optional[str] = None,
                 group_key: str = None,
                 confidence: Optional[float] = -1.0,
                 group_name: str = None
                 ):
        tags = [] if tag is None else [tag]
        super().__init__(name=name, tags=tags, group_key=group_key,
                         confidence=confidence, group_name=group_name)
        self._field_id = field_id

    def get_table_title(self, n_lines_above=8, margin=10) -> str:
        title = ''
        if isinstance(self.tags[0], HTMLTableTag):
            title = self._get_table_title_from_html(
                self.tags[0], n_lines_above=n_lines_above)
        elif isinstance(self.tags[0], (ExtractionTag, TableTag)):
            title = self._get_table_title_from_pdf(
                self.tags[0], n_lines_above=n_lines_above, margin=margin)
        return title

    @staticmethod
    def _get_table_title_from_html(tag: HTMLTableTag, n_lines_above: int
                                   ) -> str:
        table_html = tag.html.html_soup.find_all(
            'table', {'id': tag.html_id})[0]
        above_lines = []
        for count, above_line in enumerate(table_html.previous_elements):
            line_text = unicodedata.normalize('NFKD',
                                              above_line.text.strip().lower())
            if line_text and line_text not in above_lines:
                above_lines.append(line_text)
            if count >= n_lines_above:
                break
        filtered_above_lines = filter_out_nested_lines(above_lines)
        title = ' '.join(filtered_above_lines)
        return title

    @staticmethod
    def _get_table_title_from_pdf(tag: ExtractionTag, n_lines_above=8,
                                  margin=10) -> str:
        """Return the title of the table found on the pdf"""
        h = tag.page.image_height
        w = tag.page.image_width
        tags_converted = convert_tag_coords_to_percentages(
            tag, w=w, h=h)
        table_top = tags_converted['top']
        all_rows_above = []
        for line in tag.page.lines:
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
    def construct_from_raw(cls, raw: dict, pages: Dict[int, Page],
                           html: Optional[HTML] = None) -> 'TableField':
        """Create TableField object from dictionary"""
        tag_dicts: List[dict] = raw[IqDocumentKeysEnum.tags.value]
        tags = []
        for i in tag_dicts:
            try:
                if not pages:
                    tags.append(cls.html_tag_class.construct_from_raw(
                        raw=i, html=html))
                else:
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

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.name}>"

    def __str__(self):
        return self.__repr__()
