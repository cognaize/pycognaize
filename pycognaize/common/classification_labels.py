class ParentLabel:

    def __init__(self, label_name, parent=None):
        self._name = label_name
        self.children = []
        self.parent = parent

    @property
    def name(self):
        return self._name

    def add_child(self, child):
        self.children.append(child)

    def add_parent(self, parent):
        self.parent.append(parent)


class Label:

    def __init__(self, label_id, label_name, parent):
        self._label_id = label_id
        self._name = label_name
        self._parent = parent

    @property
    def label_id(self):
        return self._label_id

    @property
    def name(self):
        return self._name

    @property
    def parents(self):
        return self._parent


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
        else:
            parent.add_child(label)

    def create_labels(self, classification_labels_data):
        if classification_labels_data is not None:
            tree = self.build_tree(classification_labels_data)
            self.traverse(tree)

    def traverse(self, tree, parent=None):
        for key, value in tree.items():
            if isinstance(value, dict):
                label = ParentLabel(label_name=key, parent=parent)
                self.add_node(parent, label)
                self.traverse(value, parent=label)
            else:
                label = Label(label_id=value[0],
                              label_name=value[1],
                              parent=parent)
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
