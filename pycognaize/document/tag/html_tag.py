import abc
from typing import Optional, List

import pandas as pd

from pycognaize.common.enums import (XBRLEnum, IqDataTypesEnum,
                                     IqTableTagEnum, IqCellKeyEnum,
                                     IqTagKeyEnum, IqRecipeEnum)
from pycognaize.document.html_ import HTML
from pycognaize.document.tag.tag import Tag


class HTMLTag(Tag, metaclass=abc.ABCMeta):
    """Base class for XBRL document tags"""
    def __init__(self, html_id: List[str], xpath: str):
        self._html_id = html_id
        self._xpath = xpath

    @property
    def html_id(self):
        return self._html_id

    @property
    def xpath(self):
        return self._xpath


    @classmethod
    def construct_from_raw(cls, raw: dict, html: HTML) -> 'HTMLTag':
        """Builds HTMLTag object from pycognaize raw data
        :param raw: pycognaize field's tag info
        :return:
        """
        table_raw_data = raw[IqDataTypesEnum.table.value]
        html_id = table_raw_data[XBRLEnum.anchor_id.value]
        xpath = table_raw_data[XBRLEnum.xpath.value]
        return cls(html_id=html_id, xpath=xpath)

    # @abc.abstractmethod
    # def to_dict(self) -> dict:
    #     """Return a dictionary representing the tag object"""
    #     pass



class HTMLTableTag(HTMLTag):
    """Represents table's coordinate data in XBRL document"""
    def __init__(self, html_id: List[str], xpath: str, cell_data: dict,
                 html: HTML):
        super().__init__(html_id=html_id, xpath=xpath)
        self._cell_data = cell_data
        self._html = html
        self._cells = {}
        self._populate_cells()
        self._build_df()
        self._raw_df = None
        self._df = None

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

    # @abc.abstractmethod
    # def to_dict(self) -> dict:
    #     """Return a dictionary representing the tag object"""
    #     pass

    def _populate_cells(self):
        for row_col_index, cell_dict in self.cell_data.items():
            keys = tuple((int(i) for i in row_col_index.split(':')))
            if XBRLEnum.is_bold.value not in cell_dict:
                cell_dict[XBRLEnum.is_bold.value] = False
            if XBRLEnum.left_indentation.value not in cell_dict:
                cell_dict[XBRLEnum.left_indentation.value] = None
            self._cells[keys] = (
                self._populate_cell(keys=keys, cell_dict=cell_dict))

    @staticmethod
    def _populate_cell(keys: tuple, cell_dict: dict) -> 'TableCell':
        """ Creates `TDTag` object for each item in Table"""
        return TableCell(html_id=cell_dict[XBRLEnum.id.value],
                     xpath=cell_dict[XBRLEnum.xpath.value],
                     row_index=keys[1],
                     col_index=keys[0],
                     col_span=cell_dict[IqCellKeyEnum.col_span.value],
                     row_span=cell_dict[IqCellKeyEnum.row_span.value],
                     raw_value=cell_dict[IqCellKeyEnum.text.value],
                     is_bold=cell_dict[XBRLEnum.is_bold.value],
                     left_indentation=cell_dict[XBRLEnum.left_indentation.value])

    @classmethod
    def construct_from_raw(cls, raw: dict, html: HTML) -> 'HTMLTableTag':
        """Builds HTMLTableTag object from pycognaize raw data
        :param raw: pycognaize field's tag info
        :return:
        """
        table_raw_data = raw[IqDataTypesEnum.table.value]
        html_id = table_raw_data[XBRLEnum.anchor_id.value]
        xpath = table_raw_data[XBRLEnum.xpath.value]
        cell_data = table_raw_data[IqTableTagEnum.cells.value]
        return cls(html_id=html_id, xpath=xpath, cell_data=cell_data, html=html)


    def _build_df(self) -> pd.DataFrame:
        """Build pandas data frame using `TDTag` Cells

        :return: DataFrame object,where each cell contains an TDTag
            object with the html_id and values from the annotated
            document
        """
        cols = set()
        rows = set()
        for cell_ in self.cells.values():
            cols.add(cell_.col_index)
            rows.add(cell_.row_index)
        cols = list(cols)
        rows = list(rows)
        cols.sort()
        rows.sort()
        df = pd.DataFrame(columns=cols, index=rows)
        for cell_ in self.cells.values():
            row_index = cell_.row_index
            col_index = cell_.col_index
            for col_n in range(col_index, col_index + cell_.col_span):
                for row_n in range(row_index, row_index + cell_.row_span):
                    df[col_n][row_n] = TDTag(html_id=cell_.html_id,
                                             xpath=cell_.xpath,
                                             value=cell_.raw_value,
                                             raw_value=cell_.raw_value,
                                             field_id='',
                                             tag_id='',
                                             row_index=row_index,
                                             col_index=col_index)
        return df


class TableCell:
    """Represents cell tag for XBRL tables"""
    def __init__(self, html_id: List[str], xpath: str, row_index: int,
                 col_index: Optional[int], col_span: Optional[int],
                 row_span: int, raw_value: str, is_bold: Optional[bool],
                 left_indentation: Optional[str]):

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
    def construct_from_raw(cls, raw: dict) -> 'TableCell':
        """Build TDTag from pycognaize raw data

        :param raw: pycognaize field's tag info
        :return:
        """
        source_data = raw[XBRLEnum.source.value]
        html_id = source_data[XBRLEnum.ids.value]
        xpath = source_data[XBRLEnum.xpath.value]
        row_index = source_data[XBRLEnum.row_index.value]
        col_index = source_data[XBRLEnum.col_index.value]
        col_span = source_data[IqCellKeyEnum.col_span.value]
        row_span = source_data[IqCellKeyEnum.row_span.value]
        is_bold = source_data[XBRLEnum.is_bold.value]
        left_indentation = source_data[XBRLEnum.left_indentation.value]

        raw_value = raw[IqTagKeyEnum.ocr_value.value]
        return cls(html_id=html_id, xpath=xpath, row_index=row_index,
                   col_index=col_index, col_span=col_span, row_span=row_span,
                   raw_value=raw_value, is_bold=is_bold,
                   left_indentation=left_indentation)

class TDTag(HTMLTag):
    def __init__(self, html_id: List[str], xpath: str, value: str,
                 raw_value: str, field_id: Optional[str],
                 tag_id: Optional[str], row_index: int, col_index: int):
        super().__init__(html_id=html_id, xpath=xpath)
        self._value = value
        self._raw_value = raw_value
        self._field_id = field_id
        self._tag_id = tag_id
        self._row_index = row_index
        self._col_index = col_index

    @property
    def value(self):
        return self._value

    @property
    def raw_value(self):
        return self._raw_value

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

        :param raw: pycognaize field's tag info
        :return:
        """
        source_data = raw[XBRLEnum.source.value]
        html_id = source_data[XBRLEnum.ids.value]
        xpath = source_data[XBRLEnum.xpath.value]
        row_index = source_data[XBRLEnum.row_index.value]
        col_index = source_data[XBRLEnum.col_index.value]
        raw_value = raw[IqTagKeyEnum.ocr_value.value]
        value = raw[IqTagKeyEnum.ocr_value.value]
        field_id = source_data[IqRecipeEnum.field_id.value]
        tag_id = source_data[XBRLEnum.tag_id.value]
        return cls(html_id=html_id, xpath=xpath, value=value,
                   raw_value=raw_value, field_id=field_id, tag_id=tag_id,
                   row_index=row_index, col_index=col_index)
