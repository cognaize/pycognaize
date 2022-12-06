import bson
import string

import pandas as pd
from typing import Optional, Tuple

from pycognaize.common.enums import (
    IqCellKeyEnum,
    IqTableTagEnum,
    IqTagKeyEnum,
    ID
)
from pycognaize.document.tag import ExtractionTag
from pycognaize.document.tag.tag import BoxTag
from pycognaize.document.tag.cell import Cell
from pycognaize.common.utils import convert_coord_to_num
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from pycognaize.document.page import Page


class TableTag(BoxTag):
    """Base class for all pycognaize table fields"""

    def __init__(self, left, right, top, bottom,
                 page: 'Page',
                 cell_data: dict):
        super().__init__(left=left, right=right, top=top, bottom=bottom,
                         page=page)
        self._cell_data = cell_data
        self._cells = {}
        self._populate_cells()
        self._build_df()
        self._raw_df = None
        self._df = None

    def __getitem__(self, val: Tuple[int, int]) -> Cell:
        """Gets the cell through index"""
        if len(val) == 2:
            if any([isinstance(i, slice) for i in val]):
                raise NotImplementedError("Slice lookup not implemented")
            elif val in self.cells.keys():
                return self.cells[val]
            raise IndexError(
                f"No cell with the following index in the table: {val}")
        else:
            raise ValueError(f"Invalid argument {val}")

    @property
    def cell_data(self) -> dict:
        if not self._cell_data:
            raise Exception('Cell data is empty')
        return self._cell_data

    @property
    def cells(self) -> dict:
        return self._cells

    @property
    def raw_df(self) -> pd.DataFrame:
        if self._raw_df is None:
            self._raw_df = self._build_df()
        return self._raw_df

    @property
    def df(self) -> pd.DataFrame:
        if self._df is None:
            self._df = self.raw_df.applymap(lambda x: self._extract_raw_ocr(x))
        return self._df

    @staticmethod
    def _extract_raw_ocr(x):
        """Returns OCR extraction data"""
        try:
            return x.raw_ocr_value
        except AttributeError:
            return ''

    @classmethod
    def construct_from_raw(cls, raw: dict, page: 'Page') -> 'TableTag':
        """Build Field from pycognaize raw data

        :param raw: pycognaize field's tag info
        :param page: `Page` to which the tag belongs
        :return:
        """
        table_raw_data = raw[IqTableTagEnum.table.value]
        left = convert_coord_to_num(table_raw_data['left'])
        top = convert_coord_to_num(table_raw_data['top'])
        height = convert_coord_to_num(table_raw_data['height'])
        width = convert_coord_to_num(table_raw_data['width'])
        cells = table_raw_data[IqTableTagEnum.cells.value]
        right = left + width
        bottom = top + height
        return cls(left=left, right=right, top=top, bottom=bottom,
                   page=page,
                   cell_data=cells)

    def to_dict(self) -> dict:
        """Converts table tag to dict"""
        table_dict = {
            IqTableTagEnum.page.value: self.page.page_number,
            IqTableTagEnum.left.value: f"{self.left}%",
            IqTableTagEnum.top.value: f"{self.top}%",
            IqTableTagEnum.height.value: f"{self.height}%",
            IqTableTagEnum.width.value: f"{self.width}%",
            IqTableTagEnum.cells.value: self.cell_data,
        }
        output_dict = {
            ID: bson.ObjectId(),
            IqTagKeyEnum.page.value: self.page.page_number,
            IqTagKeyEnum.ocr_value.value:
                f"table on page {self.page.page_number}",
            IqTagKeyEnum.value.value:
                f"table on page {self.page.page_number}",
            IqTagKeyEnum.is_table.value: True,
            IqTableTagEnum.table.value: table_dict
        }
        return output_dict

    def _populate_cells(self):
        for left_col_top_row, cell_dict in self.cell_data.items():
            keys = tuple((int(i) for i in left_col_top_row.split(':')))
            self._cells[keys] = (
                self._populate_cell(keys=keys, cell_dict=cell_dict))

    @staticmethod
    def _populate_cell(keys: tuple, cell_dict: dict) -> Cell:
        """Creates Cell object for each item in Table"""
        for key in IqCellKeyEnum:
            if key == IqCellKeyEnum.left_col_top_row:
                continue
            if key.value not in cell_dict:
                raise KeyError(
                    f"Required key '{key.value}' not in cell: {cell_dict}")

        return Cell(
            value=cell_dict[IqCellKeyEnum.text.value],
            left_col=keys[0],
            top_row=keys[1],
            top=cell_dict[IqCellKeyEnum.top.value],
            right=cell_dict[IqCellKeyEnum.left.value] + cell_dict[
                IqCellKeyEnum.width.value],
            bottom=cell_dict[IqCellKeyEnum.top.value] + cell_dict[
                IqCellKeyEnum.height.value],
            left=cell_dict[IqCellKeyEnum.left.value],
            col_span=cell_dict[IqCellKeyEnum.col_span.value],
            row_span=cell_dict[IqCellKeyEnum.row_span.value]
        )

    def _build_df(self, use_ocr_text: bool = False) -> pd.DataFrame:
        """Build pandas data frame using `TableTag` Cells

        :param use_ocr_text: If true, the raw OCR data will be used for
            the content of the cells
        :return: DataFrame object,where each cell contains an ExtractionTag
            object with the coordinates and values from the annotated
            document
        """
        cols = set()
        rows = set()
        image_width = self.page.image_width
        image_height = self.page.image_height
        region_in_pixels = dict(page=self.page)
        if image_width > image_height:
            image_width, image_height = image_height, image_width

        for cell_ in self.cells.values():
            cols.add(cell_.left)
            rows.add(cell_.top)

        cols = list(cols)
        rows = list(rows)
        cols.sort()
        rows.sort()

        headers_df = list(range(len(cols)))
        indices_df = list(range(len(rows)))
        df = pd.DataFrame(columns=headers_df, index=indices_df)

        for cell_ in self.cells.values():
            text = cell_.value
            top_index = rows.index(cell_.top)
            left_index = cols.index(cell_.left)
            for col_n in range(left_index, left_index + cell_.col_span):
                for row_n in range(top_index, top_index + cell_.row_span):
                    if use_ocr_text:
                        x = cell_.left * image_width / 100
                        y = cell_.top * image_height / 100,
                        w = (cell_.right - cell_.left) * image_width / 100,
                        h = (cell_.bottom - cell_.top) * image_height / 100,
                        region_in_pixels.update(
                            dict(x=x, y=y, w=w, h=h, width_scale=image_width,
                                 height_scale=image_height))
                        # FIXME: Define get_ocr_for_region and use it here
                        text = self.page.get_ocr_for_cell(region_in_pixels)
                    if not pd.isnull(df.iloc[row_n, col_n]):
                        raise ValueError(
                            "table_tag provides multiple values"
                            " for the same cell.")
                    df[col_n][row_n] = df[col_n][row_n] = ExtractionTag(
                        left=cell_.left, right=cell_.right,
                        top=cell_.top, bottom=cell_.bottom,
                        page=self.page,
                        raw_value=cell_.value,
                        raw_ocr_value=text)
        return df

    @staticmethod
    def _is_ascii(str_) -> bool:
        return not any((i for i in str_ if i not in string.ascii_letters))

    def letter_2_num(self, letters) -> int:
        """Convert excel style coordinates into zero index coordinate"""
        letters = letters.upper()
        res = 0
        if self._is_ascii(letters):
            weight = len(letters) - 1
            for i, c in enumerate(letters):
                res += (ord(c) - 64) * 26 ** (weight - i)
        return res

    @staticmethod
    def split_excel_letters_numbers(
            str_coord: str) -> Optional[Tuple[str, int]]:
        """Return the letters and numbers of the Excel coordinate as a tuple.
            If the string is not a valid Excel coordinate, return None"""
        for n, ch in enumerate(str_coord):
            if ch.isdigit():
                letters, numbers = str_coord[:n], str_coord[n:]
                if letters.isalpha() and numbers.isdigit():
                    return letters, int(numbers)
                else:
                    return
