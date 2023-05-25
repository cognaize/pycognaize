from collections import defaultdict


class ParentLabel:

    def __init__(self, label_name, parent=None):
        self._name = label_name
        self.children = []
        self.parent = parent

    def add_child(self, child):
        self.children.append(child)

    def add_parent(self, parent):
        self.parent.append(parent)

    @property
    def name(self):
        return self._name


class Label:

    def __init__(self, label_id, label_name, parent):
        self._label_id = label_id
        self._name = label_name
        self._parents = parent

    @property
    def label_id(self):
        return self._label_id

    @property
    def name(self):
        return self._name

    @property
    def parents(self):
        return self._parents

class ClassificationLabels:
    # classification_labels: list

    def __init__(self, classification_labels_data):
        self._label_names = []
        self._labels = []
        self.create_labels(classification_labels_data)

    #     TODO: Add validation step to ensure that the labels are unique

    def create_labels(self, classification_labels_data):

        tree = self.build_tree(classification_labels_data)
        self.traverse(tree)

    def traverse(self, tree, parent=None):
        for key, value in tree.items():
            if isinstance(value, dict):
                label = ParentLabel(label_name=key, parent=parent)
                if parent is None:
                    self._labels.append(label)
                else:
                    parent.add_child(label)
                self.traverse(value, parent=label)
            else:
                label = Label(label_id=value[0], label_name=value[1], parent=parent)
                parent.add_child(label)


    def build_tree(self, classification_labels_data):
        tree = {}

        for label_id, labels in classification_labels_data.items():
            current_level = tree

            for label_idx in range(len(labels)):
                label = labels[label_idx]
                if label_idx == len(labels) - 1:
                    current_level[label] = (label_id, label)
                    self._label_names.append(label)
                elif label not in current_level:
                    current_level[label] = {}
                current_level = current_level[label]

        return tree

    @property
    def labels(self):
        return self._labels

    @property
    def label_names(self):
        return self._label_names

    # def get_label_by_id(self, label_id):
    #     for label in self.labels:
    #         if label.label_id == label_id:
    #             return label
    #     return None



if __name__ == '__main__':
    classification_labels_raw = {
        "64476dec06058bde57f97c29": ["Balance Sheet", "Assets",
                                     "Accumulated Depreciation"],
        "64476dec06058bde57f97c2a": ["Balance Sheet", "Assets",
                                     "acquired intellectual property"],
        "64476dec06058bde57f97c2b": ["Balance Sheet", "AUAU", "Assets",
                                     "assets of discontinued operations"],
        "64476dec06058bde57f97c2c": ["Balance Sheet", "Assets",
                                     "Assets under construction"],
        "64476dec06058bde57f97c2d": ["Balance Sheet", "Assets",
                                     "book inventory"],
        "64476dec06058bde57f97c2e": ["Balance Sheet", "Assets",
                                     "buildings and land"],
        "64476dec06058bde57f97c2f": ["Balance Sheet", "Assets",
                                     "Buildings and Leasehold Improvements"],
        "64476dec06058bde57f97c30": ["Balance Sheet", "Assets",
                                     "certificates of deposit"],
        "64476dec06058bde57f97c31": ["Balance Sheet", "Assets",
                                     "Construction in progress"]}
    classification_labels = ClassificationLabels(classification_labels_raw)
