import logging
import os
import requests

from pycognaize.common.exceptions import AWS_connection_exception


class login:
    """Allows to access the AWS S3 bucket using cognaize credentials"""

    def __init__(self, username, password):
        self._login(username, password)
        self._access_key = ''
        self._secret_access_key = ''
        self._session_token = ''
        self._snapshot_root = ''

    @property
    def aws_access_key(self) -> str:
        """Access key for AWS"""
        return self._access_key

    @property
    def aws_secret_access_key(self) -> str:
        """Secret access key for AWS"""
        return self._secret_access_key

    @property
    def aws_session_token(self) -> str:
        """Session token for AWS"""
        return self._session_token

    @property
    def snapshot_root(self) -> str:
        """Root path for snapshots"""
        return self._snapshot_root

    def _login(self, email: str = '', password: str = ''):
        """Get AWS access credentials and stores in the instance"""
        host = os.environ.get('COGNAIZE_HOST')
        url = f"{host}/api/v1/integration/storage/token"

        authentication = {'email': email,
                          'password': password}

        try:
            user_credentials_response = requests.post(url, json=authentication)
        except requests.exceptions.ConnectionError:
            logging.info(f'Failed connecting to url: {url}')
            raise AWS_connection_exception
        except requests.exceptions.Timeout:
            logging.info(f'Connection timed out: {url}')
            raise AWS_connection_exception

        user_credentials = user_credentials_response.json()
        if user_credentials_response.status_code == 200:
            self._access_key = user_credentials['credentials']['AccessKeyId']
            self._secret_access_key = \
                user_credentials['credentials']['SecretAccessKey']
            self._session_token = \
                user_credentials['credentials']['SessionToken']
            self._snapshot_root = user_credentials['snapshotRoot']
        elif user_credentials_response.status_code == 403:
            raise AWS_connection_exception("data download permission error. "
                                           "Please make sure you have access"
                                           " to Snapshots")
        elif user_credentials_response.status_code == 401:
            raise AWS_connection_exception("wrong email or password. "
                                           "Please make sure you entered the "
                                           "correct credentials")
        else:
            raise AWS_connection_exception("server error. There was a problem "
                                           "with the serve")
