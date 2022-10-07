import enum

from .field import Field
from .date_field import DateField
from .numeric_field import NumericField
from .section_field import SectionField
from .table_field import TableField
from .text_field import TextField
from .area_field import AreaField


__all__ = ['Field', 'DateField', 'NumericField',
           'TableField', 'TextField', 'AreaField', 'FieldMapping']


class FieldMapping(enum.Enum):
    """Mapping of IQ field type names and python classes"""
    number = NumericField
    date = DateField
    text = TextField
    table = TableField
    area = AreaField
    section = SectionField
