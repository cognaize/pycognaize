from collections import OrderedDict

from pycognaize.common.lazy_group_dict import LazyGroupDict
from pycognaize.document.field import Field


class FieldCollection(OrderedDict):
    """Contains fields included in the document by also providing
    functionality to group fields by group_name and group_key"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._groups = None

    @property
    def groups(self) -> dict:
        """Return Groups"""
        if self._groups is None:
            self._groups = LazyGroupDict(self).groups
        return self._groups

    def groups_by_name(self, name: str) -> dict:
        """Returns fields that are contained in group with the
        given group name"""
        if name in self.groups.keys():
            return self.groups[name]
        else:
            raise KeyError

    def groups_by_field(self, field: Field) -> dict:
        """Returns groups that contain the given field"""
        try:
            field_group_name = field.group_name
            return self.groups_by_name(field_group_name)
        except (AttributeError, KeyError):
            # Search with group_key if group_name is not available
            # or can not be found in groups
            field_group_id = field.group_key
            for group_name, value in self.groups.items():
                if field_group_id in value.keys():
                    return {group_name: value}
