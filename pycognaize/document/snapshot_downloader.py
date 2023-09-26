import fnmatch
import logging
import os
from pathlib import Path, PurePath

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
from botocore.paginate import Paginator

from ..login import Login


class SnapshotDownloader:
    """
        A class for downloading snapshots from an S3 bucket to a
        local destination.

        Attributes:
            PREFIX (str): The prefix used to indicate S3 paths,
            which is 's3://'.

        Methods:
            download(
                snapshot_path, destination_path, exclude=None,
                continue_token=None):
                Downloads snapshots from an S3 bucket to a local destination.

        Private Methods:
            _get_parts_from_path(path):
                Extracts the bucket name and path from an S3 path.
            _init_s3_objects():
                Initializes the S3 client and resource objects.
            _get_page_iterator(bucket_name, continue_token,
            paginator, path_without_bucket):
                Returns an iterator for paginating through S3 bucket contents.
            _get_relogined_page_iterator(bucket_name,
            next_token, pagination_config, path_without_bucket):
                Returns a relogged-in iterator for paginating through
                 S3 bucket contents.
            _relogin():
                Performs reauthentication for AWS credentials.
            _copy_objects_from_page(bucket_name, exclude,
             page, snapshot_path, destination_path):
                Copies objects from an S3 page to the destination.
            _copy_file_to_dest(s3_object, snapshot_path, destination_path):
                Copies a single S3 object to the destination.
            _write_file(path, file_data):
                Writes file data to a local path.
            _should_exclude(file_path, exclude):
                Determines if a file path should be excluded from copying.
        """

    PREFIX = 's3://'

    def _get_parts_from_path(self, path: str):
        """
        Extracts the bucket name and path from an S3 path.

        Args:
            path (str): The S3 path to extract parts from.

        Returns:
            tuple: A tuple containing the bucket name
            and path without the bucket name.
        """

        if not path:
            return '', ''

        if not path.startswith(self.PREFIX):
            raise ValueError('S3 prefix not in path. '
                             'It must start with s3://.')

        path_without_prefix = PurePath(
            path.split(self.PREFIX, 1)[-1]
        )
        path_parts = path_without_prefix.parts
        bucket_name = path_parts[0]
        path_without_bucket = path_without_prefix.relative_to(bucket_name)
        return bucket_name, path_without_bucket

    def _init_s3_objects(self):
        """
        Initializes the AWS S3 client and resource objects
         for interacting with S3.

        This method sets up the AWS S3 client and resource
         objects using the AWS credentials
        obtained from the `Login` class. It also configures
         the client with retry settings.

        Note:
            This method should be called before performing any
             S3-related operations.

        Raises:
            None
        """

        login = Login()
        session = boto3.session.Session(
            login.aws_access_key,
            login.aws_secret_access_key,
            login.aws_session_token
        )

        client_config = Config(retries={
            'max_attempts': 5,
            'mode': 'standard'
        })

        self._client = session.client('s3', config=client_config)
        self._s3 = session.resource('s3', config=client_config)

    def _get_page_iterator(
            self,
            bucket_name: str,
            continue_token: str,
            paginator: Paginator,
            path_without_bucket: str
    ):
        """
        Returns an iterator for paginating through the
        contents of an S3 bucket.

        Args:
            bucket_name (str): The name of the S3 bucket to paginate.
            continue_token (str): An optional continuation
             token for resuming pagination.
            paginator (botocore.paginate.Paginator): The
             paginator object for list objects.
            path_without_bucket (str): The path within the
            S3 bucket to start pagination from.

        Returns:
            tuple: A tuple containing the page iterator
            and pagination configuration.

        The page iterator allows you to iterate through pages
         of S3 objects within the specified bucket
        and path. The pagination configuration may include
         a continuation token for resuming pagination.

        Raises:
            None
        """

        pagination_config = dict()
        if continue_token:
            pagination_config['StartingToken'] = continue_token
        page_iterator = iter(paginator.paginate(
            Bucket=bucket_name,
            Prefix=str(path_without_bucket),
            PaginationConfig=pagination_config
        ))
        return page_iterator, pagination_config

    def _get_relogined_page_iterator(
            self,
            bucket_name: str,
            next_token: str,
            pagination_config: dict,
            path_without_bucket: str
    ):
        """
        Returns a relogged-in iterator for paginating
        through the contents of an S3 bucket.

        This method is used to obtain an iterator for paginating
         through S3 objects within the specified
        bucket and path, while reauthenticating
        the AWS connection objects.

        Args:
            bucket_name (str): The name of the S3 bucket to paginate.
            next_token (str): An optional continuation token for
             resuming pagination.
            pagination_config (dict): The pagination configuration,
             including the continuation token.
            path_without_bucket (str): The path within the S3
             bucket to start pagination from.

        Returns:
            iter: An iterator for paginating through S3 objects.

        The iterator allows you to iterate through pages
        of S3 objects within the specified bucket
        and path, handling reauthentication when needed.
        The updated pagination configuration may
        contain a new continuation token if reauthentication occurs.

        Raises:
            None
        """
        self._relogin()
        paginator = self._client.get_paginator('list_objects_v2')
        if next_token:
            pagination_config['StartingToken'] = next_token
        return iter(paginator.paginate(
            Bucket=bucket_name,
            Prefix=str(path_without_bucket),
            PaginationConfig=pagination_config
        ))

    def _relogin(self):
        """
        Performs reauthentication to refresh AWS credentials.

        This method reauthenticates to AWS to refresh the
        AWS credentials used by the S3 client and resource
        objects. It utilizes the `Login` class to obtain
         updated AWS credentials.

        Note:
            This method should be called when AWS credentials
             have expired, typically due to an 'ExpiredToken'
            error.

        Raises:
            None
        """
        print('Relogin called')
        login = Login()
        login.relogin()
        self._init_s3_objects()

    def _copy_objects_from_page(
            self,
            bucket_name: str,
            exclude: list,
            include: list,
            page: dict,
            snapshot_path: str,
            destination_path: Path
    ):
        """
        Copies objects from an S3 page to the local destination path.

        This method iterates through the objects in the
         specified S3 page and copies them to the local
        destination path, excluding any objects that
         match patterns in the 'exclude' list.

        Args:
            bucket_name (str): The name of the S3 bucket.
            exclude (list): A list of file
            path patterns to
            exclude from copying.
            include (list): A list of file
            path patterns to
            include even if excluded.
            page (dict): The page of S3 objects to copy.
            snapshot_path (str): The original S3 snapshot path.
            destination_path (Path): The local destination path.

        Returns:
            None

        This method copies each object from the S3 page to the
         destination path, excluding objects based on
        the patterns provided in the 'exclude' list.

        Raises:
            None
        """
        if 'Contents' not in page:
            return

        for obj in page['Contents']:
            s3_object = self._s3.Object(bucket_name, obj['Key'])

            if (self._matches_patterns(s3_object.key, exclude)
                    and not self._matches_patterns(s3_object.key, include)):
                continue

            self._copy_file_to_dest(s3_object, snapshot_path, destination_path)

    def _copy_file_to_dest(
            self,
            s3_object, snapshot_path, destination_path):
        """
        Copies a single S3 object to the local destination path.

        This method copies a single S3 object to the
        specified local destination path. It also handles
        reauthentication if an 'ExpiredToken' error is
        encountered while accessing the S3 object.

        Args:
            s3_object (boto3.resources.factory.s3.Object):
            The S3 object to copy.
            snapshot_path (str): The original S3 snapshot path.
            destination_path (Path): The local destination path.

        Returns:
            None

        This method copies the S3 object to the destination path, and in
         case of an 'ExpiredToken' error,
        it reauthenticates to AWS and retries the copy operation.

        Raises:
            None
        """

        bucket_name = s3_object.bucket_name

        object_full_path = f's3://{str(bucket_name / PurePath(s3_object.key))}'

        print(f'Copying: {object_full_path} to {destination_path}.')

        object_relative_path = (
            PurePath(object_full_path).relative_to(snapshot_path))

        try:
            file_data = s3_object.get()['Body'].read()
        except ClientError as e:
            if e.response['Error']['Code'] == 'ExpiredToken':
                self._relogin()
                s3_object = self._s3.Object(bucket_name, s3_object.key)
                file_data = s3_object.get()['Body'].read()
            else:
                raise

        new_file_path = str(destination_path / object_relative_path)

        self._write_file(new_file_path, file_data)

        print(f'Copied: {object_full_path} to {destination_path}.')

    def _write_file(self, path, file_data):
        """
        Writes file data to a local path.

        This method writes the provided file data to the
        specified local path. It also ensures that the
        necessary directories leading to the path exist,
        and it handles potential conflicts gracefully.

        Args:
            path (str): The local path where the file data should be written.
            file_data (bytes): The binary file data to be written.

        Returns:
            None

        This method creates any missing directories in the path
        and writes the file data to the specified
        location.

        Raises:
            None
        """
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
        except FileExistsError:
            logging.info(f'File/folder conflict for '
                         f'{os.path.dirname(path)} path')
            return None

        try:
            with open(path, 'wb') as f:
                f.write(file_data)
        except IsADirectoryError:
            logging.info(f'File/folder conflict for '
                         f'{os.path.dirname(path)} path')

    def _matches_patterns(self, file_path: str,
                          patterns: list):
        """
        Determines whether a file path matches at least one of the patterns.

        This method checks if the provided file path matches any
        of the patterns in the 'patterns' list.
        If a match is found, it returns True, indicating that the
        file is matched; otherwise, it
        returns False.

        Args:
            file_path (str): The file path to be checked for exclusion.
            patterns (list): A list of file path patterns to compare against.

        Returns:
            bool: True if the file path matches one of the patterns,
             False otherwise.

        This method is used to filter out files based on
        specified exclusion or inclusion patterns.

        Raises:
            None
        """
        if not patterns:
            return False

        for pattern in patterns:
            if fnmatch.fnmatch(file_path, pattern):
                return True

        return False

    def download(
            self,
            snapshot_path: str,
            destination_path: str,
            exclude=None,
            include=None,
            continue_token: str = None
    ):
        """
        Downloads snapshots from an S3 bucket to a local destination.

        This method allows you to download snapshots from an S3 bucket to a
         specified local destination
        path. It supports optional exclusion patterns for excluding
        specific files and can continue
        downloading from a specified continuation token.

        Args:
            snapshot_path (str): The S3 path of the snapshot to download.
            destination_path (str): The local destination directory where
                snapshots will be saved.
            exclude (list, optional): A list of file path patterns to
                exclude from copying.
            include (list, optional): A list of file path patterns to
                include even if excluded.
            continue_token (str, optional): An optional continuation token for
                resuming downloads.

        Returns:
            None

        This method initiates the download of snapshots from the specified
         S3 path to the local destination
        path. It handles pagination and reauthentication as needed.
        Progress and status information is
        printed during the download process.

        Note:
            - The 'snapshot_path' should start with 's3://'.
            - The 'destination_path' will be created if it doesn't exist.

        Raises:
            ValueError: If 'snapshot_path' doesn't start with 's3://'.
        """
        if not snapshot_path.startswith('s3://'):
            raise ValueError('Snapshot path should start with "s3://".')

        destination_path = Path(destination_path)

        bucket_name, path_without_bucket = self._get_parts_from_path(
            snapshot_path
        )

        self._init_s3_objects()

        paginator = self._client.get_paginator('list_objects_v2')

        page_iterator, pagination_config = self._get_page_iterator(
            bucket_name, continue_token, paginator,
            path_without_bucket
        )

        next_token = None

        while True:
            try:
                page = next(page_iterator)
                next_token = page.get('NextContinuationToken')

                self._copy_objects_from_page(
                    bucket_name,
                    exclude,
                    include,
                    page,
                    snapshot_path,
                    destination_path
                )
            except ClientError as e:
                if e.response['Error']['Code'] == 'ExpiredToken':
                    page_iterator = self._get_relogined_page_iterator(
                        bucket_name, next_token, pagination_config,
                        path_without_bucket
                    )
                    continue
                raise
            except StopIteration:
                break
