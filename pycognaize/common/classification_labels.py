from anytree import Node


class ClassificationLabels:

    def __init__(self, raw: dict):
        self._label_names = []
        self._labels = []
        self.tree = None

        if raw is not None:
            self.create_labels(raw)

    def add_node(self, parent, label):
        if parent is None:
            self._labels.append(label)

    def create_labels(self, classification_labels_data):
        if classification_labels_data is not None:
            tree = self.build_tree(classification_labels_data)
            self.traverse(tree)

    def traverse(self, tree, parent=None):
        for key, value in tree.items():
            if isinstance(value, dict):
                label = Node(name=key, parent=parent)
                self.add_node(parent, label)
                # self.add_node(parent, label)
                self.traverse(value, parent=label)
            else:
                label = Node(name=value[0], label_name=value[1], parent=parent)
                self.add_node(parent, label)

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
