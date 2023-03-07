import math
from typing import Union


class Confidence:
    """
    This class is used by tag object to store confidence values
    of possible classes.
    """

    def __init__(self, confidences=None):
        """
        Initialize class with confidence scores.
        :param confidences: dictionary of class names and their confidence
        """
        self._is_finalized = False
        if confidences is not None and isinstance(confidences, dict):
            self.confidences = confidences
            self.finalize()
        else:
            self.confidences = {}

    def add_class(self, class_name: str,
                  confidence: Union[float, int]) -> None:
        """Add new class for confidence scores
        :param class_name: name of the class
        :param confidence: confidence score for the class
        """
        self.confidences[class_name] = confidence

    def number_of_classes(self) -> int:
        """Returns number of classes"""
        return len(self.confidences)

    def class_names(self) -> list:
        """Returns class names"""
        return list(self.confidences.keys())

    def get_confidence(self) -> dict:
        """Returns confidence scores if finalized"""
        if not self._is_finalized:
            raise ValueError('Confidence scores have to be finalized.')
        return self.confidences

    @property
    def is_finalized(self) -> bool:
        return self._is_finalized

    def finalize(self, tolerance=0.0001) -> None:
        """Finalize confidence scores by checking if all scores sum to 1
        :param tolerance: tolerance for comparing sum of confidences (float)
        with 1
        """
        sum_scores = sum(self.confidences.values())
        if not math.isclose(sum_scores, 1, rel_tol=tolerance) and \
                self.number_of_classes() > 0:
            raise ValueError('Confidence scores have to sum up to 1.')
        self._is_finalized = True

    def __getitem__(self, item: str) -> Union[float, int]:
        if not self._is_finalized:
            raise ValueError('Confidence scores have to be finalized.')
        if item in self.confidences:
            return self.confidences[item]
        else:
            raise KeyError(f'Class {item} not found in confidence scores.')

    def __setitem__(self, key, value) -> None:
        self.confidences[key] = value
