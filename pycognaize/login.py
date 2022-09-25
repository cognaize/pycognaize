import json
import logging
import os
from glob import glob

import requests
import tempfile

from pycognaize.common.exceptions import AWS_connection_exception


class login:
    """Allows to access the AWS S3 bucket using cognaize credentials"""

    def __init__(self, username, password):
        self._login(username, password)
        self._aws_access_key = ''
        self._aws_secret_access_key = ''
        self._aws_session_token = ''
        self._snapshot_root = ''

    @property
    def aws_access_key(self) -> str:
        return self._aws_access_key

    @property
    def aws_secret_access_key(self) -> str:
        return self._aws_secret_access_key

    @property
    def aws_session_token(self) -> str:
        return self._aws_session_token

    @property
    def snapshot_root(self) -> str:
        return self._snapshot_root

    def _login(self, email: str = '', password: str = ''):
        """Get AWS access credentials and store in file"""
        HOST = os.environ.get('COGNAIZE_HOST')
        HOST = "https://elements-uat-api.cognaize.com"
        url = f"{HOST}/api/v1/integration/storage/token"

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
            self._aws_access_key = user_credentials['credentials']['AccessKeyId']
            self._aws_secret_access_key = user_credentials['credentials']['SecretAccessKey']
            self._aws_session_token = user_credentials['credentials']['SessionToken']
            self._snapshot_root = user_credentials['snapshotRoot']
        elif user_credentials_response.status_code == 403:
            raise AWS_connection_exception("data download permission error. "
                                           "Please make sure you have access to Snapshots")
        elif user_credentials_response.status_code == 401:
            raise AWS_connection_exception("wrong email or password. "
                                           "Please make sure you entered the correct credentials")
        else:
            raise AWS_connection_exception("server error. There was a problem with the server,"
                                           " we are fixing it")

    def _create_aws_config_file(self) -> tempfile.NamedTemporaryFile:
        # Creates AWS config file in /tmp directory
        self.remove_aws_config_file()
        temp = tempfile.NamedTemporaryFile(prefix='cognaize_aws_access_',
                                           suffix='.json', delete=False)
        return temp

    @staticmethod
    def _write_aws_config_file(credentials, file) -> str:
        """Writes AWS credentials to a file and returns files name"""
        file.write(json.dumps(credentials).encode())
        file.flush()
        return file.name

    def logout(self):
        """Logout from AWS"""
        self.remove_aws_config_file()
        os.environ['AWS_ACCESS_KEY'] = ''
        os.environ['AWS_SECRET_ACCESS_KEY'] = ''
        os.environ['AWS_SESSION_TOKEN'] = ''
        # os.environ.clear()

    @staticmethod
    def remove_aws_config_file():
        """Delete AWS credentials file"""
        AWS_credentials_files = glob("/tmp/cognaize_aws_access_*.json")
        if AWS_credentials_files:
            for file in AWS_credentials_files:
                os.remove(file)


if __name__ == '__main__':
    login('hovhannes.zohrabyan@cognaize.com', 'Format/Cognaize_dat')