from unittest import TestCase

from pycognaize.document.field import TextField
from pycognaize.document.html_info import HTML


class ClassesTestCase(TestCase):

    def test_should_return_none_when_classes_missing_in_raw(self):
        raw = {
            'tags': [],
            'value': '',
            'name': 'test',
            '_id': 'tsefdsdf'
        }
        html = HTML('', 'adfsd')
        field = TextField.construct_from_raw(raw, pages={}, html=html)

        assert field.classes is None

    def test_should_return_none_when_classes_is_empty_string(self):
        raw = {
            'tags': [],
            'value': '',
            'name': 'test',
            '_id': 'tsefdsdf',
            'classes': ''
        }
        html = HTML('', 'adfsd')
        field = TextField.construct_from_raw(raw, pages={}, html=html)

        assert field.classes is None

    def test_should_return_one_class_when_classes_has_one_element(self):
        raw = {
            'tags': [],
            'value': '',
            'name': 'test',
            '_id': 'tsefdsdf',
            'classes': 'test'
        }
        html = HTML('', 'adfsd')
        field = TextField.construct_from_raw(raw, pages={}, html=html)

        assert field.classes is not None
        assert isinstance(field.classes, list)
        assert len(field.classes) == 1
        assert field.classes[0] == 'test'

    def test_should_return_list_when_classes_are_separated_by_semicolon(self):
        raw = {
            'tags': [],
            'value': '',
            'name': 'test',
            '_id': 'tsefdsdf',
            'classes': 'test;test2;test3'
        }
        html = HTML('', 'adfsd')
        field = TextField.construct_from_raw(raw, pages={}, html=html)

        assert field.classes is not None
        assert isinstance(field.classes, list)
        assert len(field.classes) == 3
        assert field.classes[0] == 'test'
