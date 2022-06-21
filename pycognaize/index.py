import abc
from typing import Any
import requests

from pycognaize.document import Document


class Index(metaclass=abc.ABCMeta):
    """
    Use this abstract class for creating task specific Index subclasses,
    which allow comparison and matching between pycognaize documents
    """

    def __init__(self, token: str, url: str):
        self.url = url
        self.session = requests.Session()
        self.session.headers = {'x-auth': token}

    @property
    def id(self) -> str:
        return self.url.strip('/').rsplit('/', 1)[-1]

    def build_and_store(self, document: Document) -> requests.Response:
        """Builds an encoded document and stores it in the session"""
        doc_encoded = self.build(document)
        doc_idx = document.id
        return self._store(doc_id=doc_idx, encoding=doc_encoded)

    def _store(self, doc_id: str, encoding) -> requests.Response:
        return self.session.put(url=self.url,
                                json={'data': {doc_id: encoding}},
                                verify=False)

    @staticmethod
    def response_to_dict(response):
        """Returns a dictionary representing the response
        where keys are document ids and values are the encoded documents"""
        full_index = {}
        for i in response['findexes']:
            full_index[i['documentId']] = i['data']
        return full_index

    def match_and_get(self, document: Document) -> Document:
        """Match a given document with an existing document in the index"""
        get_response: requests.Response = self.session.get(self.url,
                                                           verify=False)
        full_index: dict = self.response_to_dict(get_response.json())
        if document.id not in full_index:
            encoding = self.build(document=document)
            self._store(doc_id=document.id, encoding=encoding)
            full_index[document.id] = encoding
        document = self.match(document=document, full_index=full_index)
        return document

    @abc.abstractmethod
    def build(self, document: Document) -> Any:
        """Build an encoding for a document, which can then be used for
        comparison and matching
        :param document: The document object to be built
        :return: The final encoding. The type of the encoding is task specific,
        therefore allows any type
        """
        raise NotImplementedError

    @abc.abstractmethod
    def match(self, document: Document, full_index: dict) -> Document:
        """Match a given document with an existing document in the index
        :param document: The document to be matched with an existing one
        :param full_index: The document encoding
        :return int: A tuple with the matched document, and a confidence value
        from 0 to 100
        """
        raise NotImplementedError
