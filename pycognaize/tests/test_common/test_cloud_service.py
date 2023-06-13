import unittest.mock
from unittest import TestCase
from unittest.mock import MagicMock

from botocore.exceptions import ClientError

from pycognaize.common.cloud_service import CloudService


class CloudServiceTestCase(TestCase):

    @unittest.mock.patch('pycognaize.common.decorators.pycognaize')
    @unittest.mock.patch('pycognaize.common.decorators.CloudInterface')
    def test_should_relogin_to_ci_when_token_is_expired(self, ci_mock,
                                                        pycognaize_mock):
        ci = MagicMock()
        ci.listdir = MagicMock()
        ci.listdir.side_effect = ClientError(
            {'error': 'Access Denied'},
            'test'
        )
        login_mock = MagicMock()
        pycognaize_mock.Login.return_value = login_mock

        cloud_service = CloudService(ci)
        cloud_service.listdir('path')

        login_mock.relogin.assert_called_once()
