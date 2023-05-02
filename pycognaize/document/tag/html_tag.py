import abc
from typing import Optional, List, Union

import bson
import pandas as pd

from pycognaize.common.enums import (IqRecipeEnum, XBRLCellEnum,
                                     XBRLTableTagEnum, XBRLTagEnum, ID)
from pycognaize.document.html_info import HTML
from pycognaize.document.tag.tag import Tag


class HTMLTagABC(Tag, metaclass=abc.ABCMeta):
    """Base class for XBRL document tags"""
    def __init__(self, html_id: Union[str, List[str]], xpath: str,
                 tag_id: Optional[str] = None):
        self._html_id = html_id
        self._xpath = xpath
        self._tag_id = tag_id

    @property
    def html_id(self):
        return self._html_id

    @property
    def xpath(self):
        return self._xpath

    @property
    def tag_id(self):
        return self._tag_id

    @classmethod
    def construct_from_raw(cls, raw: dict, html: HTML) -> 'HTMLTagABC':
        ...


class HTMLTableTag(HTMLTagABC):
    """Represents table's coordinate data in XBRL document"""

    def __init__(self, tag_id: str,  value: str, ocr_value: str,
                 xpath: str, title: str, html_id: Union[str, List[str]],
                 cell_data: dict, html: HTML, source_ids,
                 is_table: bool = True):
        super().__init__(html_id=html_id, xpath=xpath, tag_id=tag_id)
        self._value = value
        self._ocr_value = ocr_value
        self._is_table = is_table
        self._title = title
        self._cell_data = cell_data
        self._cells = {}
        self._html = html
        self._source_ids = source_ids
        self._populate_cells()
        self._build_df()
        self._raw_df = None
        self._df = None

    @property
    def title(self):
        return self._title

    @property
    def source_ids(self):
        return self._source_ids

    @property
    def value(self):
        return self._value

    @property
    def ocr_value(self):
        return self._ocr_value

    @property
    def is_table(self):
        return self._is_table

    @property
    def html(self):
        return self._html

    @property
    def cells(self):
        return self._cells

    @property
    def cell_data(self) -> dict:
        if not self._cell_data:
            raise Exception('Cell data is empty')
        return self._cell_data

    @property
    def raw_df(self) -> pd.DataFrame:
        if self._raw_df is None:
            self._raw_df = self._build_df()
        return self._raw_df

    @property
    def df(self) -> pd.DataFrame:
        if self._df is None:
            self._df = self.raw_df.applymap(
                lambda x: self._extract_value(x))
        return self._df

    @staticmethod
    def _extract_value(x):
        """Returns text value from `HTMLTag` object"""
        try:
            return x.raw_value
        except AttributeError:
            return ''

    def _populate_cells(self):
        for row_col_index, cell_dict in self.cell_data.items():
            keys = tuple((int(i) for i in row_col_index.split(':')))
            if XBRLTableTagEnum.is_bold.value not in cell_dict:
                cell_dict[XBRLTableTagEnum.is_bold.value] = False
            if XBRLTableTagEnum.left_indentation.value not in cell_dict:
                cell_dict[XBRLTableTagEnum.left_indentation.value] = None
            self._cells[keys] = (
                self._populate_cell(keys=keys, cell_dict=cell_dict))

    @staticmethod
    def _populate_cell(keys: tuple, cell_dict: dict) -> 'HTMLCell':
        """ Creates `HTMLCell` object for each item in Table"""
        return HTMLCell(
            html_id=cell_dict[XBRLCellEnum.id.value],
            xpath=cell_dict[XBRLCellEnum.xpath.value],
            row_index=keys[1],
            col_index=keys[0],
            col_span=cell_dict[XBRLCellEnum.col_span.value],
            row_span=cell_dict[XBRLCellEnum.row_span.value],
            raw_value=cell_dict[XBRLCellEnum.raw_value.value],
            is_bold=cell_dict[XBRLCellEnum.is_bold.value],
            left_indentation=cell_dict[XBRLCellEnum.left_indentation.value]
        )

    def to_dict(self) -> dict:
        """Converts HTMLTableTag to dict"""
        table_dict = {
            XBRLTableTagEnum.xpath.value: self.xpath,
            XBRLTableTagEnum.title.value: self.title,
            XBRLTableTagEnum.anchor_id.value: self.html_id,
            XBRLTableTagEnum.cells.value: self.cell_data,
        }
        output_dict = {
            XBRLTableTagEnum._id.value: self.tag_id,
            XBRLTableTagEnum.value.value: '',
            XBRLTableTagEnum.ocr_value.value: '',
            XBRLTableTagEnum.is_table.value: True,
            XBRLTableTagEnum.table.value: table_dict,
            XBRLTableTagEnum.source.value: self.source_ids}

        return output_dict

    @classmethod
    def construct_from_raw(cls, raw: dict, html: HTML) -> 'HTMLTableTag':
        """Builds HTMLTableTag objeTct from pycognaize raw data
        :param raw: pycognaize field's tag info
        :param html: HTML

        :return:
        """
        tag_id = raw[XBRLTableTagEnum._id.value]
        ocr_value = raw[XBRLTableTagEnum.ocr_value.value]
        value = raw[XBRLTableTagEnum.value.value]
        table_raw_data = raw[XBRLTableTagEnum.table.value]
        xpath = table_raw_data[XBRLTableTagEnum.xpath.value]
        title = table_raw_data[XBRLTableTagEnum.title.value]
        html_id = table_raw_data[XBRLTableTagEnum.anchor_id.value]
        cell_data = table_raw_data[XBRLTableTagEnum.cells.value]
        source_ids = raw[XBRLTableTagEnum.source.value]
        return cls(tag_id=tag_id, ocr_value=ocr_value, value=value,
                   is_table=True, xpath=xpath, title=title,
                   html_id=html_id, cell_data=cell_data,
                   html=html, source_ids=source_ids)

    def _build_df(self) -> pd.DataFrame:
        """Build pandas data frame using `HTMLTag` Cells

        :return: DataFrame object,where each cell contains an HTMLTag
            object with the html_id and values from the annotated
            document
        """
        cols = set()
        rows = set()
        for cell_ in self.cells.values():
            cols.add(cell_.col_index - 1)
            rows.add(cell_.row_index - 1)
        cols = list(cols)
        rows = list(rows)
        cols.sort()
        rows.sort()
        df = pd.DataFrame(columns=cols, index=rows)
        for cell_ in self.cells.values():
            row_index = cell_.row_index - 1
            col_index = cell_.col_index - 1
            for col_n in range(col_index, col_index + cell_.col_span):
                for row_n in range(row_index, row_index + cell_.row_span):
                    df[col_n][row_n] = HTMLTag(is_table=False,
                                               html_id=cell_.html_id,
                                               xpath=cell_.xpath,
                                               raw_value=cell_.raw_value,
                                               raw_ocr_value=cell_.raw_value,
                                               field_id='',
                                               tag_id=self.tag_id,
                                               row_index=row_index,
                                               col_index=col_index)
        return df


class HTMLCell:
    """Represents cell tag for XBRL tables"""
    def __init__(self, row_index: int, col_index: int,
                 col_span: int, row_span: int,
                 html_id: Union[str, List[str]], xpath: str,
                 raw_value: str, is_bold: False,
                 left_indentation: None):
        self._row_index = row_index
        self._col_index = col_index
        self._col_span = col_span
        self._row_span = row_span
        self._html_id = html_id
        self._xpath = xpath
        self._raw_value = raw_value
        self._is_bold = is_bold
        self._left_indentation = left_indentation

    @property
    def row_index(self) -> int:
        return self._row_index

    @property
    def col_index(self) -> int:
        return self._col_index

    @property
    def col_span(self) -> int:
        return self._col_span

    @property
    def row_span(self) -> int:
        return self._row_span

    @property
    def html_id(self):
        return self._html_id

    @property
    def xpath(self):
        return self._xpath

    @property
    def raw_value(self) -> str:
        return self._raw_value

    @property
    def is_bold(self) -> bool:
        return self._is_bold

    @property
    def left_indentation(self) -> str:
        return self._left_indentation

    @classmethod
    def construct_from_raw(cls, raw: dict) -> 'HTMLCell':
        """Build HTMLTAG from pycognaize raw data

        :param raw: pycognaize field's tag info
        :return:
        """
        source_data = raw[XBRLCellEnum.source.value]
        row_index = source_data[XBRLCellEnum.row_index.value]
        col_index = source_data[XBRLCellEnum.col_index.value]
        col_span = source_data[XBRLCellEnum.col_span.value]
        row_span = source_data[XBRLCellEnum.row_span.value]
        raw_value = raw[XBRLCellEnum.raw_value.value]
        html_id = source_data[XBRLCellEnum.html_id.value]
        xpath = source_data[XBRLCellEnum.xpath.value]
        is_bold = (source_data[XBRLCellEnum.is_bold.value]
                   if XBRLCellEnum.is_bold.value in source_data else False)
        left_indentation = (source_data[XBRLCellEnum.left_indentation.value]
                            if XBRLCellEnum.left_indentation.value else None)
        return cls(html_id=html_id, xpath=xpath, row_index=row_index,
                   col_index=col_index, col_span=col_span, row_span=row_span,
                   raw_value=raw_value, is_bold=is_bold,
                   left_indentation=left_indentation)

    def to_dict(self) -> dict:
        """Converts cell to dict"""
        cell_dict = {
            XBRLCellEnum.col_span.value: self.col_span,
            XBRLCellEnum.row_span.value: self.row_span,
            XBRLCellEnum.html_id.value: self.html_id,
            XBRLCellEnum.xpath.value: self.xpath,
            XBRLCellEnum.raw_value.value: self.raw_value,
            XBRLCellEnum.left_indentation.value: self.left_indentation,
            XBRLCellEnum.is_bold.value: self.is_bold}
        return {f"{self.col_index}:{self.row_index}": cell_dict}


class HTMLTag(HTMLTagABC):
    def __init__(self, raw_value: str, raw_ocr_value: str,
                 is_table: bool, html_id: Union[str, List[str]],
                 field_id: Optional[str], tag_id: Optional[str],
                 row_index: int, col_index: int, xpath: str,
                 is_td: bool = True):
        super().__init__(html_id=html_id, xpath=xpath, tag_id=tag_id)
        self._raw_value = raw_value
        self._raw_ocr_value = raw_ocr_value
        self._is_table = is_table
        self._field_id = field_id
        self._row_index = row_index
        self._col_index = col_index
        self._is_td = is_td

    @property
    def raw_value(self):
        """returns adjusted value"""
        return self._raw_value

    @property
    def raw_ocr_value(self):
        return self._raw_ocr_value

    @property
    def is_table(self):
        return self._is_table

    @property
    def field_id(self):
        return self._field_id

    @property
    def row_index(self):
        return self._row_index

    @property
    def col_index(self):
        return self._col_index

    @property
    def is_td(self):
        return self._is_td

    @classmethod
    def construct_from_raw(cls, raw: dict, html: HTML) -> 'HTMLTag':
        """Build HTMLTag from pycognaize raw data
        :param html: HTML
        :param raw: pycognaize field's tag info
        :return:
        """
        source_data = raw[XBRLTagEnum.source.value]
        if XBRLTagEnum.html.value in source_data:
            is_td = False
            html_id = source_data[XBRLTagEnum.html.value][
                XBRLTagEnum.parent_id.value]
        else:
            is_td = True
            html_id = source_data[XBRLTagEnum.ids.value]
        raw_value = raw[XBRLTagEnum.value.value]
        raw_ocr_value = raw[XBRLTagEnum.ocr_value.value]
        is_table = raw[XBRLTagEnum.is_table.value]
        field_id = source_data[IqRecipeEnum.field_id.value]
        tag_id = source_data[XBRLTagEnum.tag_id.value]
        row_index = source_data[XBRLTagEnum.row_index.value]
        col_index = source_data[XBRLTagEnum.col_index.value] - 1
        xpath = source_data[XBRLTagEnum.xpath.value]
        return cls(html_id=html_id,  raw_value=raw_value,
                   raw_ocr_value=raw_ocr_value, is_table=is_table,
                   field_id=field_id, tag_id=tag_id,
                   row_index=row_index, col_index=col_index,
                   xpath=xpath, is_td=is_td)

    def to_dict(self) -> dict:
        """Converts tag to dict"""
        if self.is_td:
            tag_info = {
                XBRLTagEnum.ids.value: self.html_id,
                IqRecipeEnum.field_id.value: self.field_id,
                XBRLTagEnum.tag_id.value: self.tag_id,
                XBRLTagEnum.row_index.value: self.row_index,
                XBRLTagEnum.col_index.value: self.col_index + 1,
                XBRLTagEnum.xpath.value: self.xpath,
            }
        else:
            tag_info = {
                XBRLTagEnum.html.value: {
                    XBRLTagEnum.parent_id.value: self.html_id,
                    XBRLTagEnum.value.value: self.raw_value
                },
                XBRLTagEnum.ids.value: [],
                IqRecipeEnum.field_id.value: self.field_id,
                XBRLTagEnum.tag_id.value: self.tag_id,
                XBRLTagEnum.row_index.value: self.row_index,
                XBRLTagEnum.col_index.value: self.col_index + 1,
                XBRLTagEnum.xpath.value: self.xpath,
            }
        output_dict = {
            ID: str(bson.ObjectId()),
            XBRLTagEnum.value.value: self.raw_value,
            XBRLTagEnum.ocr_value.value: self.raw_ocr_value,
            XBRLTagEnum.is_table.value: self.is_table,
            XBRLTagEnum.source.value: tag_info,
         }
        return output_dict
