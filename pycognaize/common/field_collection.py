import logging
from collections import OrderedDict

from pycognaize.common.lazy_group_dict import LazyGroupDict
from pycognaize.document.field import Field


class FieldCollection(OrderedDict):
    """Contains fields included in the document by also providing
    functionality to group fields by group_name and group_key"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._groups = None
        self._groups_by_key = None

    @property
    def groups(self) -> dict:
        """Return Groups"""
        if self._groups is None:
            self._groups = LazyGroupDict(self).groups
        return self._groups

    @property
    def key_groups(self) -> dict:
        """Return Groups"""
        if self._groups_by_key is None:
            self._groups_by_key = LazyGroupDict(self).groups_by_key
        return self._groups_by_key

    def groups_by_key(self, group_key: str) -> dict:
        """Returns groups that contain the given group_key"""
        if group_key in self.key_groups.keys():
            return self.key_groups[group_key]
        else:
            raise KeyError

    def groups_by_name(self, name: str) -> dict:
        """Returns fields that are contained in group with the
        given group name"""
        if name in self.groups.keys():
            return self.groups[name]
        else:
            raise KeyError

    def groups_by_field(self, field: Field) -> list:
        """Returns groups that contain the given field"""
        name_group = self.groups_by_name(field.group_name)
        if field.group_key in name_group:
            return name_group[field.group_key]
        else:
            logging.warning(f"Field {field} is not in any group")
            return []
