import abc
from typing import Optional, List

import bson
import pandas as pd

from pycognaize.common.enums import (IqDataTypesEnum, ID,
                                     IqRecipeEnum, XBRLCellEnum,
                                     XBRLTableTagEnum, XBRLTagEnum)
from pycognaize.document.html_info import HTML
from pycognaize.document.tag.tag import Tag


class HTMLTag(Tag, metaclass=abc.ABCMeta):
    """Base class for XBRL document tags"""

    def __init__(self, html_id: List[str], xpath: str,
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
    def construct_from_raw(cls, raw: dict, html: HTML) -> 'HTMLTag':
        """Builds HTMLTag object from pycognaize raw data
        :param raw: pycognaize field's tag info
        :param html: HTML
        :return:
        """
        table_raw_data = raw[IqDataTypesEnum.table.value]
        html_id = table_raw_data[XBRLTagEnum.anchor_id.value]
        xpath = table_raw_data[XBRLTagEnum.xpath.value]
        tag_id = table_raw_data[XBRLTagEnum.tag_id.value]
        return cls(html_id=html_id, xpath=xpath, tag_id=tag_id)

    # @abc.abstractmethod
    # def to_dict(self) -> dict:
    #     """Return a dictionary representing the tag object"""
    #     pass


class HTMLTableTag(HTMLTag):
    """Represents table's coordinate data in XBRL document"""

    def __init__(self, tag_id: str, ocr_value: str, value: str,
                 xpath: str, title: str, html_id: List[str], cell_data: dict,
                 html: HTML, source_ids, is_table: bool = True):
        super().__init__(html_id=html_id, xpath=xpath, tag_id=tag_id)
        self._ocr_value = ocr_value
        self._value = value
        self._is_table = is_table
        self._title = title
        self._html = html
        self._source_ids = source_ids
        self._cell_data = cell_data
        self._cells = {}
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
    def cell_data(self):
        return self._cell_data

    @property
    def cells(self):
        return self._cells

    @property
    def raw_df(self) -> pd.DataFrame:
        if self._raw_df is None:
            self._raw_df = self._build_df()
        return self._raw_df

    @property
    def df(self) -> pd.DataFrame:
        if self._df is None:
            self._df = self.raw_df.applymap(lambda x: self._extract_value(x))
        return self._df

    @property
    def html(self):
        return self._html


    @staticmethod
    def _extract_value(x):
        """Returns text value from `TDTag` object"""
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
        """ Creates `TDTag` object for each item in Table"""
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
            XBRLTableTagEnum.ocr_value.value: '',
            XBRLTableTagEnum.value.value: '',
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
        """Build pandas data frame using `TDTag` Cells

        :return: DataFrame object,where each cell contains an TDTag
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
                    df[col_n][row_n] = TDTag(td_id='',
                                             is_table=False,
                                             html_id=cell_.html_id,
                                             xpath=cell_.xpath,
                                             value=cell_.raw_value,
                                             raw_value=cell_.raw_value,
                                             field_id='',
                                             tag_id='',
                                             row_index=row_index,
                                             col_index=col_index)
        return df


class HTMLCell:
    """Represents cell tag for XBRL tables"""

    def __init__(self, html_id: List[str], xpath: str, row_index: int,
                 col_index: int, col_span: int,
                 row_span: int, raw_value: str, is_bold: False,
                 left_indentation: None):

        self._html_id = html_id
        self._xpath = xpath
        self._row_index = row_index
        self._col_index = col_index
        self._col_span = col_span
        self._row_span = row_span
        self._raw_value = raw_value
        self._is_bold = is_bold
        self._left_indentation = left_indentation

    @property
    def html_id(self):
        return self._html_id

    @property
    def xpath(self):
        return self._xpath

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
    def raw_value(self) -> str:
        return self._raw_value

    @property
    def is_bold(self) -> bool:
        return self._is_bold

    @property
    def left_indentation(self) -> str:
        return self._left_indentation

    # @abc.abstractmethod
    # def to_dict(self) -> dict:
    #     """Return a dictionary representing the tag object"""
    #     pass

    @classmethod
    def construct_from_raw(cls, raw: dict) -> 'HTMLCell':
        """Build TDTag from pycognaize raw data

        :param raw: pycognaize field's tag info
        :return:
        """
        source_data = raw[XBRLCellEnum.source.value]
        html_id = source_data[XBRLCellEnum.html_id.value]
        xpath = source_data[XBRLCellEnum.xpath.value]
        row_index = source_data[XBRLCellEnum.row_index.value]
        col_index = source_data[XBRLCellEnum.col_index.value]
        col_span = source_data[XBRLCellEnum.col_span.value]
        row_span = source_data[XBRLCellEnum.row_span.value]
        if XBRLCellEnum.is_bold.value in source_data:
            is_bold = source_data[XBRLCellEnum.is_bold.value]
        else:
            is_bold = False
        if XBRLCellEnum.left_indentation.value in source_data:
            left_indentation = source_data[XBRLCellEnum.left_indentation.value]
        else:
            left_indentation = None
        raw_value = raw[XBRLCellEnum.raw_value.value]
        return cls(html_id=html_id, xpath=xpath, row_index=row_index,
                   col_index=col_index, col_span=col_span, row_span=row_span,
                   raw_value=raw_value, is_bold=is_bold,
                   left_indentation=left_indentation)

    def to_dict(self) -> dict:
        """Converts cell to dict"""
        return {
            ID: str(bson.ObjectId()),
            XBRLCellEnum.row_index.value: self.row_index,
            XBRLCellEnum.col_index.value: self.col_index,
            XBRLCellEnum.col_span.value: self.col_span,
            XBRLCellEnum.row_span.value: self.row_span,
            XBRLCellEnum.raw_value.value: self.raw_value,
            XBRLCellEnum.html_id.value: self.html_id,
            XBRLCellEnum.xpath.value: self.xpath,
            XBRLCellEnum.is_bold.value: self.is_bold,
            XBRLCellEnum.left_indentation.value: self.left_indentation}


class TDTag(HTMLTag):
    def __init__(self, td_id, html_id: List[str], value: str,
                 raw_value: str, is_table: bool,
                 field_id: Optional[str], tag_id: Optional[str],
                 row_index: int, col_index: int, xpath: str):
        super().__init__(html_id=html_id, xpath=xpath, tag_id=tag_id)
        self._td_id = td_id
        self._value = value
        self._raw_value = raw_value
        self._is_table = is_table
        self._field_id = field_id
        self._row_index = row_index
        self._col_index = col_index

    @property
    def td_id(self):
        return self._td_id

    @property
    def value(self):
        return self._value

    @property
    def raw_value(self):
        return self._raw_value

    @property
    def is_table(self):
        return self._is_table

    @property
    def field_id(self):
        return self._field_id

    @property
    def tag_id(self):
        return self._tag_id

    @property
    def row_index(self):
        return self._row_index

    @property
    def col_index(self):
        return self._col_index

    @classmethod
    def construct_from_raw(cls, raw: dict, html: HTML) -> 'TDTag':
        """Build TDTag from pycognaize raw data
        :param html: HTML
        :param raw: pycognaize field's tag info
        :return:
        """
        source_data = raw[XBRLTagEnum.source.value]
        td_id = raw[XBRLTagEnum.td_id.value]
        value = raw[XBRLTagEnum.value.value]
        raw_value = raw[XBRLTagEnum.ocr_value.value]
        is_table = raw[XBRLTagEnum.is_table.value]
        html_id = source_data[XBRLTagEnum.ids.value]
        xpath = source_data[XBRLTagEnum.xpath.value]
        row_index = source_data[XBRLTagEnum.row_index.value]
        col_index = source_data[XBRLTagEnum.col_index.value]
        field_id = source_data[IqRecipeEnum.field_id.value]
        tag_id = source_data[XBRLTagEnum.tag_id.value]
        return cls(td_id=td_id, html_id=html_id,  value=value,
                   raw_value=raw_value, is_table=is_table,
                   field_id=field_id, tag_id=tag_id,
                   row_index=row_index, col_index=col_index,
                   xpath=xpath)

    def to_dict(self) -> dict:
        """Converts tag to dict"""
        output_dict = {
            ID: str(bson.ObjectId()),
            XBRLTagEnum.ids.value: self.html_id,
            XBRLTagEnum.xpath.value: self.xpath,
            XBRLTagEnum.value.value: self.value,
            XBRLTagEnum.ocr_value.value: self.raw_value,
            IqRecipeEnum.field_id.value: self.field_id,
            XBRLTagEnum.tag_id.value: self.tag_id,
            XBRLTagEnum.row_index.value: self.row_index,
            XBRLTagEnum.col_index.value: self.col_index}
        return output_dict
