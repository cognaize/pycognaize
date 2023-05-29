from anytree import Node

from pycognaize.common.enums import IqDocumentKeysEnum


class ClassificationLabels(dict):

    def __init__(self, raw: dict):
        super().__init__()
        self._label_names = []

        if raw is not None:
            self.create_labels(raw)

    def create_labels(self, raw: dict):
        for src_field_id, data in raw.get(
                IqDocumentKeysEnum.field_category.value, {}).items():
            root = Node('root')
            for label_id, label_names in data.items():
                self._label_names.append(label_names[-1])
                parent = Node(label_names[0], parent=root)
                for label_name in label_names[1:]:
                    node = Node(label_name, parent=parent)
                    parent = node
            self.__setitem__(src_field_id, root)

    @property
    def labels(self):
        return self.__dict__

    @property
    def label_names(self):
        return self._label_names
