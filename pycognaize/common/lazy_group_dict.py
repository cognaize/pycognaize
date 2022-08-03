from collections import defaultdict
from collections.abc import Mapping


class LazyGroupDict(Mapping):
    """Contains groups included in the document"""

    def __init__(self, document_x: dict):
        self._groups = None
        self.create_groups(document_x)

    @property
    def groups(self) -> dict:
        return self._groups

    def create_groups(self, document_fields: dict):
        """Add fields to group """
        groups = defaultdict(dict)
        group_names = set()

        for field_name in document_fields.keys():
            group_names.update(
                [item.group_name for item in document_fields[field_name]
                 if item.group_name])

            for group_name in group_names:
                groups[group_name] = defaultdict(list)
                for field_name in document_fields.keys():
                    for item in document_fields[field_name]:
                        if item.group_name == group_name:
                            groups[group_name][item.group_key].append(item)

        self._groups = groups

    def __getitem__(self, group_name) -> dict:
        """The Document object, retrieved from provided path
        Note: Path can be both local and remote
        """
        # return self._groups[group_name]
        return self._groups[group_name]

    def __iter__(self):
        ...

    def __len__(self):
        ...
