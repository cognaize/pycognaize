import os
import requests

from pycognaize.common.enums import EnvConfigEnum
from pycognaize.common.exceptions import ServerAPIException


class Login(object):
    """Allows to access the AWS S3 bucket using cognaize credentials"""
    _access_key = ''
    _secret_access_key = ''
    _session_token = ''
    _snapshot_root = ''
    _logged_in = False

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Login, cls).__new__(cls)
        return cls.instance

    @property
    def logged_in(self) -> bool:
        """Access key for AWS"""
        return self._logged_in

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

    def login(self, email: str, password: str):
        """Get AWS access credentials and stores in the instance"""
        host = os.environ.get(EnvConfigEnum.HOST.value)
        url = f"{host}/api/v1/integration/storage/token"

        authentication = {'email': email,
                          'password': password}

        try:
            user_credentials_response = requests.post(url, json=authentication)
        except requests.exceptions.ConnectionError:
            raise ServerAPIException(f'Failed connecting to url: {url}')
        except requests.exceptions.Timeout:
            raise ServerAPIException(f'Connection timed out: {url}')

        user_credentials = user_credentials_response.json()
        if user_credentials_response.status_code == 200:
            self._logged_in = True
            self._access_key = user_credentials['credentials']['AccessKeyId']
            self._secret_access_key = \
                user_credentials['credentials']['SecretAccessKey']
            self._session_token = \
                user_credentials['credentials']['SessionToken']
            self._snapshot_root = user_credentials['snapshotRoot']
        elif user_credentials_response.status_code == 403:
            raise ServerAPIException("Data download permission error. "
                                     "Please make sure you have access"
                                     " to Snapshots")
        elif user_credentials_response.status_code == 401:
            raise ServerAPIException("Wrong email or password. "
                                     "Please make sure you entered the "
                                     "correct credentials")
        else:
            raise ServerAPIException("Server error. There was a problem "
                                     "with the serve")

    @classmethod
    def destroy(cls):
        del cls.instance
