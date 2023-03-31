from unittest import TestCase

from click.testing import CliRunner


class SubmitTestCase(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.runner = CliRunner()

    def should_abort_when_git_is_missing(self):

        pass
