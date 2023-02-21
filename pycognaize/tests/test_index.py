import json
import os
import shutil
import tempfile
import unittest
import uuid
from abc import ABC
from typing import Tuple
from unittest.mock import patch, create_autospec

import requests
from pycognaize.document.html_info import HTML

from pycognaize.common.enums import EnvConfigEnum
from pycognaize.document import Document
from pycognaize.index import Index
from pycognaize.tests.resources import RESOURCE_FOLDER

# TODO: REWRITE WITH NEW TABLE FORMAT SNAPSHOT
class SampleIndex(Index, ABC):

    def build(self, document: Document) -> str:
        return 'built'

    def match(self, document: Document, full_index: dict) -> Tuple[Document, float]:
        percentage = 66.6
        return document, percentage


class TestIndex(unittest.TestCase):
    path = 'sample_folder_path'
    data = None
    snap_path = None
    ORIGINAL_SNAPSHOT_PATH = os.environ.get(EnvConfigEnum.SNAPSHOT_PATH.value)
    SNAPSHOT_PATH = os.path.join(tempfile.gettempdir(), str(uuid.uuid4()))

    @classmethod
    def setUpClass(cls):
        os.environ[EnvConfigEnum.SNAPSHOT_PATH.value] = cls.SNAPSHOT_PATH
        cls.snap_storage_path = os.path.join(cls.SNAPSHOT_PATH, cls.path)

        # load resource data
        with open(RESOURCE_FOLDER + '/snapshots/60f5260c7883ab0013d9c184/document.json') as document_json:
            cls.data = json.load(document_json)

        cls.snap_path = os.path.join(cls.SNAPSHOT_PATH, 'sample_snapshot_1',
                                     str(cls.data['metadata']['document_id']))

        shutil.copytree(RESOURCE_FOLDER + '/snapshots/60f5260c7883ab0013d9c184/', cls.snap_path)

    def setUp(self) -> None:
        with open(RESOURCE_FOLDER + '/snapshots/60f5260c7883ab0013d9c184/document.json') as document_json:
            data = json.load(document_json)
        snap_path = os.path.join(self.SNAPSHOT_PATH, 'sample_snapshot_1',
                                 str(data['metadata']['document_id']))
        self.document = Document.from_dict(data, data_path=snap_path)

        self.token = 'sample_token'
        self.url = 'sample_url'

        self.api_data1 = {'total': 3, 'pageSize': 0, 'findexes': [{'_id': 'sample_id',
                                                                   'documentId': '60f95f4dd3061500199021a5',
                                                                   'index': 'spreading',
                                                                   '__v': 0,
                                                                   'data': '000100010101001'},
                                                                  {'_id': 'sample_id',
                                                                   'documentId': '60f554497883ab0013d9d906',
                                                                   'index': 'spreading',
                                                                   '__v': 0,
                                                                   'data': '010011101010101'},
                                                                  {'_id': 'sample_id',
                                                                   'documentId': '60f5260c7883ab0013d9c184',
                                                                   'index': 'spreading',
                                                                   '__v': 0,
                                                                   'data': '101100101100101'}]}
        self.api_data2 = {'total': 1, 'pageSize': 0, 'findexes': [{'_id': 'sample_id',
                                                                   'documentId': '60f95f4dd3061500199021a5',
                                                                   'index': 'spreading',
                                                                   '__v': 0,
                                                                   'data': '000100010101001'}]}

        self.request_mock = create_autospec(requests)
        self.session_mock = create_autospec(requests.Session)
        self.get_response_mock = create_autospec(requests.Response)
        self.put_response_mock = create_autospec(requests.Response)
        self.get_response_mock.status_code = 200
        self.put_response_mock.status_code = 200
        self.request_mock.Session.return_value = self.session_mock
        self.session_mock.get.return_value = self.get_response_mock
        self.session_mock.put.return_value = self.put_response_mock

    def test_build_and_store(self):
        encoding = {self.document.id: SampleIndex(url=self.url,
                                                  token=self.token).build(self.document.id)}
        with patch('pycognaize.index.requests', self.request_mock):
            sample_index = SampleIndex(token=self.token, url=self.url)
            sample_index.build_and_store(document=self.document)
            self.session_mock.put.assert_called_with(url=self.url, json={'data': encoding},
                                                     verify=False)
            self.session_mock.put.assert_called_once()

    def test_match_and_get(self):
        # If the document ID exists in the API
        self.get_response_mock.json.return_value = self.api_data1
        with patch('pycognaize.index.requests', self.request_mock):
            sample_index = SampleIndex(token=self.token, url=self.url)
            doc, percentage = sample_index.match_and_get(document=self.document)
            self.assertEqual(doc.id, self.document.id)
            self.assertAlmostEqual(percentage, 66.6)
            self.session_mock.get.assert_called_with(self.url, verify=False)
            self.get_response_mock.json.assert_called_once()

        # If the document ID doesn't exist in the API
        self.get_response_mock.json.return_value = self.api_data2
        with patch('pycognaize.index.requests', self.request_mock):
            sample_index = SampleIndex(token=self.token, url=self.url)
            doc2, _ = sample_index.match_and_get(self.document)
            self.session_mock.get.assert_called_with(self.url, verify=False)
            self.session_mock.put.assert_called_once()

    def test_id(self):
        sample_index = SampleIndex(token=self.token, url=self.url)
        self.assertGreater(len(sample_index.id), 0)

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(cls.SNAPSHOT_PATH)
        if cls.ORIGINAL_SNAPSHOT_PATH is not None:
            os.environ[EnvConfigEnum.SNAPSHOT_PATH.value] = cls.ORIGINAL_SNAPSHOT_PATH
        else:
            del os.environ[EnvConfigEnum.SNAPSHOT_PATH.value]
