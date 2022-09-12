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

    def _login(self, username: str = '', password: str = ''):
        """Get AWS access credentials and store in file"""
        # url = CFG.host + CFG.API_ENDPOINT
        url = "http://0.0.0.0:5002/api/v1/integration/storage/token"

        authentication = {'username': username,
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
            credentials_file = self._create_aws_config_file()
            self._write_aws_config_file(user_credentials, credentials_file)
        elif user_credentials_response.status_code == 403:
            logging.info('You are not allowed to download data')
            raise AWS_connection_exception
        elif user_credentials_response.status_code == 401:
            logging.info('Invalid Username or Password')
            raise AWS_connection_exception
        else:
            logging.info('Failed to login: {user_credentials}')
            raise AWS_connection_exception

    @staticmethod
    def _create_aws_config_file() -> tempfile.NamedTemporaryFile:
        # Creates AWS config file in /tmp directory
        AWS_credentials_files = glob("/tmp/cognaize_aws_access_*.json")
        if AWS_credentials_files:
            for file in AWS_credentials_files:
                os.remove(file)
        temp = tempfile.NamedTemporaryFile(prefix='cognaize_aws_access_',
                                           suffix='.json', delete=False)
        return temp

    @staticmethod
    def _write_aws_config_file(credentials, file) -> str:
        """Writes AWS credentials to a file and returns files name"""
        json.dump(credentials, file)
        file.flush()
        return file.name
