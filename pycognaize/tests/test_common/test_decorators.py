import unittest

from pycognaize.common.decorators import module_not_found, soon_be_deprecated


@module_not_found()
def import_non_ex_module():
    import non_ex_module


@soon_be_deprecated()
def not_deprecated_function():
    pass


class TestDecorators(unittest.TestCase):
    def test_module_not_found_warning(self):
        with self.assertWarns(UserWarning):
            import_non_ex_module()

    def test_soon_be_deprecated_warning(self):
        with self.assertWarns(DeprecationWarning):
            not_deprecated_function()


if __name__ == '__main__':
    unittest.main()
