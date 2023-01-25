class Confidence:

    def __init__(self, confidences=None):
        self._is_finalized = False
        if confidences and isinstance(confidences, dict):
            self.confidences = confidences
            self.finalize()
        else:
            self.confidences = {}

    def add_class(self, class_name, confidence):
        self.confidences[class_name] = confidence

    def get_confidence(self, class_name=None):
        if not self._is_finalized:
            raise ValueError('Confidence scores have to be finalized.')
        if class_name:
            result = self.confidences[class_name]
        else:
            result = self.confidences

        return result

    def class_names(self):
        return self.confidences.keys()

    def number_of_classes(self):
        return len(self.confidences)

    @property
    def is_finalized(self):
        return self._is_finalized

    def finalize(self):
        if not sum(self.confidences.values()) == 1:
            raise ValueError('Confidence scores have to sum up to 1.')
        self._is_finalized = True
