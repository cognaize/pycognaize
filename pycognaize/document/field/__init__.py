import enum

from .field import Field
from .date_field import DateField
from .numeric_field import NumericField
from .section_field import SectionField
from .table_field import TableField
from .text_field import TextField
from .area_field import AreaField
from .link_field import LinkField
from .span_field import SpanField

__all__ = ['Field', 'DateField', 'NumericField',
           'TableField', 'TextField', 'AreaField', 'FieldMapping', 'LinkField',
           'SpanField']


class FieldMapping(enum.Enum):
    """Mapping of IQ field type names and python classes"""
    number = NumericField
    date = DateField
    text = TextField
    table = TableField
    area = AreaField
    section = SectionField
    link = LinkField
    text_span = SpanField
