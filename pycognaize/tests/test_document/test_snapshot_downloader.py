import unittest
import os
from types import GeneratorType

import boto3

from pycognaize.document.snapshot_downloader import SnapshotDownloader


class TestSnapshotDownloader(unittest.TestCase):
    def setUp(self):
        self.PREFIX = 's3://'
        self.elements = 'cognaize-elements'
        self.snapshots = 'snapshots'
        self.path = os.path.join(self.PREFIX, self.elements, self.snapshots)
        self.random_path = 'random/path'
        self.snapshot_downloader = SnapshotDownloader()
        self.s3 = boto3.client('s3')
        self.paginator = self.s3.get_paginator('list_objects_v2')
        self.paginator_params = {'Bucket': self.elements,
                                 'Prefix': self.PREFIX}
        self.bucket_name, self.path_without_bucket = (
            self.snapshot_downloader._get_parts_from_path(self.path))
        self.page_iterator, self.pagination_config = (
            self.snapshot_downloader._get_page_iterator(
                bucket_name=self.bucket_name,
                continue_token='a',
                paginator=self.paginator,
                path_without_bucket=self.path_without_bucket))

    def test__get_parts_from_path(self):
        self.assertEqual(str(self.path_without_bucket), self.snapshots)
        self.assertEqual(self.bucket_name, self.elements)
        with self.assertRaises(ValueError):
            self.snapshot_downloader._get_parts_from_path(self.random_path)
        self.assertEqual(
            self.snapshot_downloader._get_parts_from_path(''),
            ('', '')
        )

    def test__init_s3_objects(self):
        self.assertIsNone(self.snapshot_downloader._init_s3_objects())

    def test__get_page_iterator(self):
        self.assertIsInstance(self.page_iterator, GeneratorType)
        self.assertEqual(self.pagination_config, {'StartingToken': 'a'})


if __name__ == '__main__':
    unittest.main()
