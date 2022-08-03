from collections import OrderedDict

from pycognaize.common.lazy_group_dict import LazyGroupDict


class FieldCollection(OrderedDict):
    """Contains fields included in the document by also providing
    functionality to group fields by group_name and group_key"""

    def groups(self):
        """Return Groups"""
        LazyGroupDict(self.__root)
