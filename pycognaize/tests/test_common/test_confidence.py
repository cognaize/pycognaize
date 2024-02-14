import unittest

from pycognaize.common.confidence import Confidence


class TestConfidence(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        self.confidences_dict = {
            'class11': 0.2, 'class12': 0.5, 'class13': 0.3
        }

        self.incorrect_confidences_dict = {
            'class21': 0.2, 'class22': 0.5, 'class23': 0.9
        }
        self.confidences = Confidence(self.confidences_dict)

    def test_add_class(self):
        self.confidences.add_class(
            'class14', 0.0
        )
        self.assertEqual(len(self.confidences.confidences), 4)

    def test_class_names(self):
        class_names = list(self.confidences_dict.keys())
        self.assertEqual(self.confidences.class_names(), class_names)

    def test_get_confidence(self):
        with self.assertRaises(ValueError):
            Confidence(self.incorrect_confidences_dict).get_confidence()
        self.assertEqual(self.confidences_dict, self.confidences.get_confidence())

    def test_is_finalized(self):
        self.assertTrue(self.confidences.is_finalized)

    def test_finalize(self):
        with self.assertRaises(ValueError):
            Confidence(self.incorrect_confidences_dict).finalize()

    def test___getitem__(self):
        self.assertEqual(self.confidences.__getitem__('class11'), 0.2)
        with self.assertRaises(KeyError):
            self.confidences.__getitem__('random_class')
        with self.assertRaises(ValueError):
            Confidence(self.incorrect_confidences_dict).__getitem__('class21')

    def test___setitem__(self):
        self.confidences.__setitem__(key='new_class', value=0.0)


if __name__ == '__main__':
    unittest.main()
