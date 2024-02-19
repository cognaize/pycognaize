import unittest

from pycognaize.common.classification_labels import ClassificationLabels


class TestClassificationLabels(unittest.TestCase):
    def setUp(self):
        self.classification_labels = ClassificationLabels(
            raw={'fieldCategories': {'srx_field_id': {'field': 'data', 'field2': 'data2'}}}
        )
        self.classification_labels_empty = ClassificationLabels(
            raw={}
        )

    def test_create_labels(self):
        self.assertFalse(self.classification_labels_empty)
        self.assertFalse(self.classification_labels.create_labels(
            raw={
                'fieldCategories': {
                    'srx_field_id': {'field': 'field_data',
                                     'field2': 'field_data2'}
                }
            }
        ))


if __name__ == "__main__":
    unittest.main()
