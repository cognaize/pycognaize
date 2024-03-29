import os
import unittest
from unittest.mock import Mock, patch

from pycognaize.common.exceptions import ServerAPIException
from pycognaize.login import Login


class TestIndex(unittest.TestCase):

    def setUp(self) -> None:
        self.sample_response = Mock()

    def test_singletone(self):
        instance1 = Login()
        instance2 = Login()

        self.assertEqual(instance1, instance2)

    @patch('requests.Session.post')
    def test_login(self, mock_post):
        os.environ["API_HOST"] = "test.api_host.com"
        instance = Login()
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = \
            {
                "credentials": {
                    "AccessKeyId": "AccessKeyId",
                    "SecretAccessKey": "SecretAccessKey",
                    "SessionToken": "SessionToken",
                    "Expiration": "2022-10-04T13:11:50.000Z"
                },
                "snapshotRoot": "s3://test-bucket/snapshots"
            }
        instance.login('test@gmail.com', 'test_password')

        self.assertEqual(instance.aws_access_key, 'AccessKeyId')
        self.assertEqual(instance.aws_secret_access_key, 'SecretAccessKey')
        self.assertEqual(instance.aws_session_token, 'SessionToken')
        self.assertEqual(instance.snapshot_root, 's3://test-bucket/snapshots')
        self.assertEqual(instance.logged_in, True)

        mock_post.return_value.status_code = 403
        self.assertRaises(ServerAPIException, instance.login, 'test@gmail.com', 'test_password')

        mock_post.return_value.status_code = 401
        self.assertRaises(ServerAPIException, instance.login, 'test@gmail.com', 'test_password')

        mock_post.return_value.status_code = 500
        self.assertRaises(ServerAPIException, instance.login, 'test@gmail.com', 'test_password')

        instance.destroy()

    def test_api_host(self):
        os.unsetenv("API_HOST")
        instance = Login()
        self.assertRaises(OSError, instance.login, 'test@gmail.com', 'test_password')