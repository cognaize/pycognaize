import tempfile
import unittest
import os
import json
import uuid

from pycognaize.common.enums import EnvConfigEnum
from pycognaize.common.table_utils import (
    filter_out_invalid_tables,
    _sort_table_horizontally,
    assign_indices_to_tables,
)
from pycognaize.tests.resources import RESOURCE_FOLDER
from pycognaize.document.document import Document


class TestTableUtils(unittest.TestCase):
    snap_path = '/snapshots/5eb8ee1c6623f200192a0651'
    xbrl_snap_path = '/snapshots/63dfb66b7861050010cd64b5'

    @classmethod
    def setUpClass(cls) -> None:

        with open(
                RESOURCE_FOLDER + cls.snap_path + '/document.json',
                encoding="utf8") as document_json:
            cls.data = json.load(document_json)
        with open(
                RESOURCE_FOLDER + cls.xbrl_snap_path + '/document.json',
                encoding="utf8") as document_json:
            cls.data_xbrl = json.load(document_json)

    def setUp(self):
        self.document = Document.from_dict(
            self.data,
            data_path=RESOURCE_FOLDER + '/snapshots/5eb8ee1c6623f200192a0651')
        self.xbrl_document = Document.from_dict(
            self.data_xbrl,
            data_path=RESOURCE_FOLDER + '/snapshots/63dfb66b7861050010cd64b5')
        self.tables = self.document.x['table']
        self.table_with_no_tags = [self.tables[-1]]
        self.tables_with_tags = self.tables[:4]
        self.xbrl_tables = self.xbrl_document.x['table']

    def test_filter_out_invalid_tables(self):
        valid_tables = filter_out_invalid_tables(tables=self.tables)
        self.assertEqual(len(valid_tables), 4)

    def test__sort_table_horizontally(self):
        hsorted_tables = _sort_table_horizontally(
            self.tables_with_tags, threshold=0.1
        )
        hsorted_tables2 = _sort_table_horizontally(
            self.tables_with_tags, threshold=2
        )
        self.assertEqual(
            len(hsorted_tables), 4)
        self.assertEqual(
            len(hsorted_tables2), 4)

    def test_assign_indices_to_tables(self):
        assigned_tables = assign_indices_to_tables(self.tables_with_tags)
        assigned_tables_empty = assign_indices_to_tables(
            self.table_with_no_tags
        )
        assigned_tables_xbrl_empty = assign_indices_to_tables(self.xbrl_tables)
        assigned_tables_xbrl = assign_indices_to_tables(
            self.xbrl_tables, all_tables=self.xbrl_tables
        )
        self.assertEqual(len(assigned_tables), 4)
        self.assertEqual(len(assigned_tables_xbrl), 79)
        self.assertFalse(assigned_tables_empty)
        self.assertFalse(assigned_tables_xbrl_empty)


if __name__ == '__main__':
    unittest.main()
