from unittest import TestCase, mock
from unittest.mock import MagicMock

from pycognaize.common.cloud_interface import get_cloud_interface


class GetCITestCase(TestCase):
    def test_should_return_ci_without_login_when_login_was_not_called(self):
        ci = get_cloud_interface()

        assert ci._kwargs['aws_access_key_id'] is None

    def test_should_return_the_same_instance_when_called_several_times(self):
        ci = get_cloud_interface()

        ci_2 = get_cloud_interface()

        assert ci is ci_2

    @mock.patch('pycognaize.common.cloud_interface.Login')
    def test_should_return_logged_in_ci_when_is_logged_in(self, login_mock):
        instance_mock = MagicMock()
        login_mock.return_value = instance_mock
        instance_mock.logged_in = True
        instance_mock.aws_access_key = 'test_key'

        ci = get_cloud_interface()

        assert ci._kwargs['aws_access_key_id'] == 'test_key'


    @mock.patch('pycognaize.common.cloud_interface.Login')
    def test_should_return_same_instance_when_is_logged_in_and_called_several_times(self, login_mock):
        instance_mock = MagicMock()
        login_mock.return_value = instance_mock
        instance_mock.logged_in = True
        instance_mock.aws_access_key = 'test_key'

        ci = get_cloud_interface()

        ci_2 = get_cloud_interface()

        assert ci is ci_2
