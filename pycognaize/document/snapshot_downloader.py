import fnmatch
import logging
import os
from pathlib import Path, PurePath

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

from ..login import Login


class SnapshotDownloader:
    PREFIX = 's3://'

    def _get_parts_from_path(self, path):
        if not path:
            return '', ''

        if self.PREFIX not in path:
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
            bucket_name,
            continue_token,
            paginator,
            path_without_bucket
    ):
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
            bucket_name, next_token, pagination_config,
            path_without_bucket
    ):
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
        login = Login()
        login.relogin()
        self._init_s3_objects()

    def _copy_objects_from_page(self, bucket_name, exclude, page,
                                snapshot_path, destination_path):
        if 'Contents' not in page:
            return

        for obj in page['Contents']:
            s3_object = self._s3.Object(bucket_name, obj['Key'])

            if self._should_exclude(s3_object.key, exclude):
                continue

            self._copy_file_to_dest(s3_object, snapshot_path, destination_path)

    def _copy_file_to_dest(self, s3_object, snapshot_path, destination_path):

        bucket_name = s3_object.bucket_name

        object_full_path = f's3://{str(bucket_name / PurePath(s3_object.key))}'

        print(f'Copying: {object_full_path} to {destination_path}.')

        object_relative_path = PurePath(object_full_path).relative_to(snapshot_path)

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

    def _should_exclude(self, file_path: str,
                        exclude: list):
        if not exclude:
            return False

        for pattern in exclude:
            if fnmatch.fnmatch(file_path, pattern):
                return True

        return False

    def download(self, snapshot_path: str, destination_path: str, exclude=None, continue_token: str = None):
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
