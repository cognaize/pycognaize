import json
import os
import tempfile
import unittest
import uuid
import requests

from unittest.mock import Mock, patch, create_autospec
from bson import json_util
from cloudstorageio import CloudInterface
from urllib.parse import urljoin
from pycognaize import Model
from pycognaize.common.enums import EnvConfigEnum, IqDocumentKeysEnum, StorageEnum
from pycognaize.document import Document
from pycognaize.document.field import TextField
from pycognaize.document.page import create_dummy_page
from pycognaize.document.tag import ExtractionTag
from pycognaize.tests.resources import RESOURCE_FOLDER


def set_empty_ids_from_dict_convert_percent_string_to_float(doc_data):
    if isinstance(doc_data, dict):
        for key, value in doc_data.items():
            if (key == '_id' or key == 'document_id') and isinstance(value, str):
                doc_data[key] = ''
            else:
                doc_data[key] = set_empty_ids_from_dict_convert_percent_string_to_float(value)
    elif isinstance(doc_data, list):
        for idx, el in enumerate(doc_data):
            doc_data[idx] = set_empty_ids_from_dict_convert_percent_string_to_float(el)
    elif isinstance(doc_data, str) and doc_data.endswith('%'):
        doc_data = float(doc_data.rstrip('%'))
    return doc_data


class ExampleModel(Model):
    def predict(self, document: Document):
        # Adding non existing field to the document
        # page = create_dummy_page(page_n=1)
        # tag_1 = ExtractionTag(left=41.05, right=48.15, top=14.77, bottom=16.33,
        #                       page=page, raw_value="KAMAN CORPORATION", raw_ocr_value="KAMAN CORPORATION")
        # tag_2 = ExtractionTag(left=43.05, right=50.15, top=16.77, bottom=18.33,
        #                       page=page, raw_value="Aerospace Group, Inc.", raw_ocr_value="Aerospace Group, Inc.")
        #
        # document.y['parent_company_name'] = [TextField(name='Parent company name',
        #                                                tags=[tag_1, tag_2])]
        return document

    def evaluate(self, act_document: Document, pred_document: Document, only_content=False) -> dict:
        """ General evaluate functionality by tag, field and group level
        :param act_document: actual document (ground truth)
        :param pred_document: predicted document
        :param only_content: if True evaluation ignores locations of tags, considers only content"""

        results = {'tag_level': self.eval_tag_level(act_document=act_document, pred_document=pred_document,
                                                    only_content=only_content),
                   'field_level': self.eval_field_level(act_document=act_document, pred_document=pred_document,
                                                        only_content=only_content),
                   'group_level': self.eval_group_level(act_document=act_document, pred_document=pred_document,
                                                        only_content=only_content)}
        return results


class TestModel(unittest.TestCase):

    tempdir = tempfile.mkdtemp(prefix="iq_test_model_")

    # get original env vars
    ORIGINAL_IQ_DOCUMENTS_STORAGE_PATH = os.environ.get(EnvConfigEnum.IQ_DOCUMENTS_STORAGE_PATH.value)
    ORIGINAL_IQ_SNAP_STORAGE_PATH = os.environ.get(EnvConfigEnum.IQ_SNAP_STORAGE_PATH.value)
    ORIGINAL_SNAPSHOT_PATH = os.environ.get(EnvConfigEnum.SNAPSHOT_PATH.value)

    CI = CloudInterface()

    @classmethod
    def setUpClass(cls) -> None:

        # set env var constants
        cls.IQ_DOCUMENTS_STORAGE_PATH = os.path.join(cls.tempdir, 'document_storage')
        cls.IQ_SNAP_STORAGE_PATH = os.path.join(cls.tempdir, 'snap_storage')
        cls.SNAPSHOT_PATH = os.path.join(cls.tempdir, 'snap_storage')

        # load resource data
        cls.doc_path = os.path.join(RESOURCE_FOLDER, 'document_for_digestor.bson')
        cls.rec_path = os.path.join(RESOURCE_FOLDER, 'sample_recipe.bson')
        cls.snap_path = os.path.join(RESOURCE_FOLDER, 'sample_snapshot.bson')

        with open(cls.doc_path, "rb") as f:
            cls.doc_data = json_util.loads(f.read())
        with open(cls.rec_path, "rb") as f:
            cls.recipe_data = json_util.loads(f.read())
        with open(cls.snap_path, "rb") as f:
            cls.snap_data = json_util.loads(f.read())

        # set expected constants
        cls.doc_src = str(cls.doc_data[IqDocumentKeysEnum.src.value])
        cls.doc_folder_path = os.path.join(cls.IQ_DOCUMENTS_STORAGE_PATH, cls.doc_src)
        cls.images_path = os.path.join(cls.doc_folder_path, StorageEnum.image_folder.value)

        # execute genie inputs
        cls.task_id = 'sample_task_id'
        cls.token = 'sample_token'
        cls.url = "http://some_url"

        # set the mocks
        cls.request_mock = create_autospec(requests)
        cls.session_mock = create_autospec(requests.Session)
        cls.get_response_mock = create_autospec(requests.Response)
        cls.post_response_mock = create_autospec(requests.Response)

        # return values of mocks
        cls.request_mock.Session.return_value = cls.session_mock
        cls.session_mock.get.return_value = cls.get_response_mock
        with open(os.path.join(RESOURCE_FOLDER, 'get_response_example_for_testing_execute_genie.json'), 'r') as f:
            get_response_dict = json.load(f)
            get_response_dict["documentRootPath"] = os.path.join(
                RESOURCE_FOLDER, 'resources_for_testing_execute_genie_v2')
        cls.get_response_mock.json.return_value = get_response_dict
        with open(os.path.join(RESOURCE_FOLDER, 'output_doc_example_for_testing_execute_genie.json'), 'r') as f:
            cls.output_document_json_dict = json.load(f)
            # cls.output_document_json_dict["pages"]["1"] = os.path.join(
            #     RESOURCE_FOLDER, 'resources_for_testing_execute_genie_v2')
            set_empty_ids_from_dict_convert_percent_string_to_float(cls.output_document_json_dict)
        cls.session_mock.post.return_value = cls.post_response_mock
        cls.post_response_mock.status_code = 200

    def setUp(self) -> None:
        self.model = ExampleModel()

    def test_execute_genie_v2(self):

        with patch('pycognaize.model.requests', self.request_mock):

            response = self.model.execute_genie_v2(self.task_id, self.token, self.url)

            self.assertEqual(response.status_code, 200)
            self.session_mock.get.assert_called_with(urljoin(self.url, self.task_id),
                                                     verify=False, timeout=10)
            self.get_response_mock.json.assert_called_once()
            self.session_mock.post.assert_called_once()

            call_args = self.session_mock.post.call_args
            doc_data = json.loads(call_args[1]["data"])
            doc_data_with_empty_ids = set_empty_ids_from_dict_convert_percent_string_to_float(doc_data)

            self.assertDictEqual(doc_data_with_empty_ids, self.output_document_json_dict)

    def test_eval_tag_level(self):
        page = create_dummy_page(page_n=1)
        mock_act = Mock()
        mock_pred = Mock()

        tag_1_act = ExtractionTag(left=41.05, right=48.15, top=14.77, bottom=16.33,
                                  page=page, raw_value="KAMAN CORPORATION", raw_ocr_value="KAMAN CORPORATION")
        tag_2_act = ExtractionTag(left=43.05, right=50.15, top=16.77, bottom=18.33,
                                  page=page, raw_value="Aerospace Group, Inc.", raw_ocr_value="Aerospace Group, Inc.")
        tag_3_act = ExtractionTag(left=45.05, right=52.15, top=18.77, bottom=20.33,
                                  page=page, raw_value="Yerevan City", raw_ocr_value="Yerevan City")
        tag_4_act = ExtractionTag(left=47.05, right=54.15, top=20.77, bottom=22.33,
                                  page=page, raw_value="Adidas comp.", raw_ocr_value="Adidas comp.")
        tag_4_1_act = ExtractionTag(left=47.05, right=54.15, top=20.77, bottom=22.33,
                                    page=page, raw_value="Adidas comp.", raw_ocr_value="Adidas comp.")
        tag_5_act = ExtractionTag(left=41.05, right=48.15, top=14.77, bottom=16.33,
                                  page=page, raw_value="cognaize cjsc", raw_ocr_value="cognaize cjsc")
        tag_6_act = ExtractionTag(left=41.05, right=48.15, top=14.77, bottom=16.33,
                                  page=page, raw_value="Ford Motors", raw_ocr_value="Ford Motors")

        tag_1_pred = ExtractionTag(left=41.05, right=48.15, top=14.77, bottom=16.33,
                                   page=page, raw_value="KAMAN CORPORATION", raw_ocr_value="KAMAN CORPORATION")
        tag_2_pred = ExtractionTag(left=43.05, right=50.15, top=16.77, bottom=18.33,
                                   page=page, raw_value="Aerospace Group, Inc.", raw_ocr_value="Aerospace Group, Inc.")
        tag_3_pred = ExtractionTag(left=45.05, right=52.15, top=18.77, bottom=20.33,
                                   page=page, raw_value="Yerevan City", raw_ocr_value="Yerevan City")
        tag_4_pred = ExtractionTag(left=47.05, right=54.15, top=20.77, bottom=22.33,
                                   page=page, raw_value="Adidas comp.", raw_ocr_value="Adidas comp.")
        tag_4_1_pred = ExtractionTag(left=38.05, right=45.15, top=20.77, bottom=22.33,
                                     page=page, raw_value="Adidas comp.", raw_ocr_value="Adidas comp.")
        tag_5_pred = ExtractionTag(left=42.05, right=49.15, top=15.77, bottom=17.33,
                                   page=page, raw_value="SCDM Armenia", raw_ocr_value="SCDM Armenia")
        tag_6_pred = ExtractionTag(left=43.05, right=50.15, top=16.77, bottom=19.33,
                                   page=page, raw_value="", raw_ocr_value="")
        tag_7_pred = ExtractionTag(left=58.05, right=64.15, top=30.77, bottom=32.33,
                                   page=page, raw_value="Nike", raw_ocr_value="Nike")

        # Simple testing
        mock_act.y = {'parent_company_name': [TextField(name='Parent company name',
                                                        tags=[tag_1_act, tag_2_act, tag_3_act, tag_4_act, tag_5_act,
                                                              tag_6_act])]}
        mock_pred.y = {'parent_company_name': [TextField(name='Parent company name',
                                                         tags=[tag_1_pred, tag_2_pred, tag_3_pred, tag_4_pred,
                                                               tag_5_pred, tag_6_pred, tag_7_pred])]}
        result = self.model.eval_tag_level(mock_act, mock_pred)
        act = {'parent_company_name': {'confusion matrix': {'TP': 4, 'TN': 0, 'FP': 3, 'FN': 2},
                                       'f1 score': 0.6153846153846154,
                                       'precision': 0.5714285714285714,
                                       'recall': 0.6666666666666666,
                                       'accuracy': 0.4444444444444444}}
        self.assertDictEqual(result, act)

        # Testing the case when only content is true
        mock_act.y = {'parent_company_name': [TextField(name='Parent company name',
                                                        tags=[tag_1_act, tag_2_act, tag_3_act, tag_4_1_act,
                                                              tag_5_act, tag_6_act])]}
        mock_pred.y = {'parent_company_name': [TextField(name='Parent company name',
                                                         tags=[tag_1_pred, tag_2_pred, tag_3_pred,
                                                               tag_4_1_pred, tag_5_pred, tag_6_pred,
                                                               tag_7_pred])]}
        result_only_content = self.model.eval_tag_level(mock_act, mock_pred, only_content=True)
        act_only_content = {'parent_company_name': {'confusion matrix': {'TP': 4, 'TN': 0, 'FP': 3, 'FN': 2},
                                                    'f1 score': 0.6153846153846154,
                                                    'precision': 0.5714285714285714,
                                                    'recall': 0.6666666666666666,
                                                    'accuracy': 0.4444444444444444}}
        self.assertDictEqual(result_only_content, act_only_content)

        # Testing multiple tags case
        mock_act.y = {'parent_company_name': [TextField(name='Parent company name',
                                                        tags=[tag_1_act, tag_1_act, tag_1_act, tag_2_act])]}
        mock_pred.y = {'parent_company_name': [TextField(name='Parent company name',
                                                         tags=[tag_1_pred, tag_1_pred, tag_2_pred, tag_2_pred,
                                                               tag_2_pred])]}
        result_multi_tag = self.model.eval_tag_level(mock_act, mock_pred, only_content=True)
        act_multi_tag = {'parent_company_name': {'confusion matrix': {'TP': 3, 'TN': 0, 'FP': 2, 'FN': 1},
                                                 'f1 score': 0.6666666666666666,
                                                 'precision': 0.6,
                                                 'recall': 0.75,
                                                 'accuracy': 0.5}}
        self.assertDictEqual(result_multi_tag, act_multi_tag)

    def test_eval_field_level(self):
        page = create_dummy_page(page_n=1)
        mock_act = Mock()
        mock_pred = Mock()

        level_tag_1_act = ExtractionTag(left=41.05, right=48.15, top=14.77, bottom=16.33,
                                        page=page, raw_value="1.1", raw_ocr_value="1.1")
        level_tag_2_act = ExtractionTag(left=43.05, right=50.15, top=16.77, bottom=18.33,
                                        page=page, raw_value="1.2", raw_ocr_value="1.2")
        level_tag_2_1_act = ExtractionTag(left=43.05, right=50.15, top=16.77, bottom=18.33,
                                          page=page, raw_value="1.2", raw_ocr_value="1.2")
        level_tag_3_act = ExtractionTag(left=45.05, right=52.15, top=18.77, bottom=20.33,
                                        page=page, raw_value="1.3", raw_ocr_value="1.3")
        level_tag_4_act = ExtractionTag(left=47.05, right=54.15, top=20.77, bottom=22.33,
                                        page=page, raw_value="1.4", raw_ocr_value="1.4")
        level_tag_5_act = ExtractionTag(left=49.05, right=56.15, top=22.77, bottom=24.33,
                                        page=page, raw_value="1.5", raw_ocr_value="1.5")
        paragraph_tag_1_act = ExtractionTag(left=41.05, right=48.15, top=14.77, bottom=16.33,
                                            page=page, raw_value="GOVERNMENT CODE - GOV, TITLE 2.",
                                            raw_ocr_value="GOVERNMENT CODE - GOV, TITLE 2.")
        paragraph_tag_2_act = ExtractionTag(left=43.05, right=50.15, top=16.77, bottom=18.33,
                                            page=page, raw_value="Notwithstanding subdivision (b)",
                                            raw_ocr_value="Notwithstanding subdivision (b)")
        paragraph_tag_2_1_act = ExtractionTag(left=43.05, right=50.15, top=16.77, bottom=18.33,
                                              page=page, raw_value="Notwithstanding subdivision (b)",
                                              raw_ocr_value="Notwithstanding subdivision (b)")
        paragraph_tag_3_act = ExtractionTag(left=45.05, right=52.15, top=18.77, bottom=20.33,
                                            page=page, raw_value="The department, consistent with board rules",
                                            raw_ocr_value="The department, consistent with board rules")

        level_tag_1_pred = ExtractionTag(left=41.05, right=48.15, top=14.77, bottom=16.33,
                                         page=page, raw_value="1.1", raw_ocr_value="1.1")
        level_tag_2_pred = ExtractionTag(left=43.05, right=50.15, top=16.77, bottom=18.33,
                                         page=page, raw_value="1.2", raw_ocr_value="1.2")
        level_tag_2_1_pred = ExtractionTag(left=36.05, right=43.15, top=16.77, bottom=18.33,
                                           page=page, raw_value="1.2", raw_ocr_value="1.2")
        level_tag_3_pred = ExtractionTag(left=46.05, right=51.15, top=17.77, bottom=19.33,
                                         page=page, raw_value="1.2", raw_ocr_value="1.2")
        level_tag_4_pred = ExtractionTag(left=45.05, right=52.15, top=18.77, bottom=20.33,
                                         page=page, raw_value="1.3", raw_ocr_value="1.3")
        paragraph_tag_1_pred = ExtractionTag(left=41.05, right=48.15, top=14.77, bottom=16.33,
                                             page=page, raw_value="GOVERNMENT CODE - GOV, TITLE 2.",
                                             raw_ocr_value="GOVERNMENT CODE - GOV, TITLE 2.")
        paragraph_tag_2_pred = ExtractionTag(left=43.05, right=50.15, top=16.77, bottom=18.33,
                                             page=page, raw_value="Notwithstanding subdivision (b)",
                                             raw_ocr_value="Notwithstanding subdivision (b)")
        paragraph_tag_2_1_pred = ExtractionTag(left=37.05, right=43.15, top=16.77, bottom=18.33,
                                               page=page, raw_value="Notwithstanding subdivision (b)",
                                               raw_ocr_value="Notwithstanding subdivision (b)")
        paragraph_tag_3_pred = ExtractionTag(left=58.05, right=70.15, top=33.77, bottom=36.33,
                                             page=page, raw_value="Limited Examination and Appointment Program",
                                             raw_ocr_value="Limited Examination and Appointment Program")
        paragraph_tag_4_pred = ExtractionTag(left=63.05, right=75.15, top=30.77, bottom=35.33,
                                             page=page, raw_value="Person with a developmental disability",
                                             raw_ocr_value="Person with a developmental disability")
        paragraph_tag_5_pred = ExtractionTag(left=66.05, right=78.15, top=33.77, bottom=38.33,
                                             page=page, raw_value="This section shall remain in effect only",
                                             raw_ocr_value="This section shall remain in effect only")

        # Testing simple case
        mock_act.y = {'level': [TextField(name='level', tags=[level_tag_1_act, level_tag_2_act]),
                                TextField(name='level', tags=[level_tag_1_act, level_tag_3_act]),
                                TextField(name='level', tags=[level_tag_1_act, level_tag_2_act, level_tag_3_act]),
                                TextField(name='level', tags=[level_tag_4_act, level_tag_5_act]),
                                TextField(name='level', tags=[level_tag_1_act, level_tag_4_act])],
                      'paragraph': [TextField(name='paragraph', tags=[paragraph_tag_1_act, paragraph_tag_2_act]),
                                    TextField(name='paragraph', tags=[paragraph_tag_2_act, paragraph_tag_3_act]),
                                    TextField(name='paragraph', tags=[paragraph_tag_1_act, paragraph_tag_2_act,
                                                                      paragraph_tag_3_act])],
                      'classification_field': [TextField(name='Classification Field', value="Yes"),
                                               TextField(name='Classification Field', value="Yes"),
                                               TextField(name='Classification Field', value="No")]}

        mock_pred.y = {'level': [TextField(name='level', tags=[level_tag_1_pred, level_tag_2_pred]),
                                 TextField(name='level', tags=[level_tag_1_pred, level_tag_4_pred], ),
                                 TextField(name='level', tags=[level_tag_2_pred, level_tag_2_pred, level_tag_3_pred]),
                                 TextField(name='level', tags=[level_tag_4_pred]),
                                 TextField(name='level', tags=[level_tag_4_pred]),
                                 TextField(name='level', tags=[level_tag_3_pred])],
                       'paragraph': [TextField(name='paragraph', tags=[paragraph_tag_1_pred, paragraph_tag_2_pred]),
                                     TextField(name='paragraph', tags=[paragraph_tag_2_pred, paragraph_tag_3_pred]),
                                     TextField(name='paragraph', tags=[paragraph_tag_1_pred, paragraph_tag_2_pred,
                                                                       paragraph_tag_3_act]),
                                     TextField(name='paragraph', tags=[paragraph_tag_4_pred, paragraph_tag_5_pred]),
                                     TextField(name='paragraph', tags=[paragraph_tag_2_pred, paragraph_tag_4_pred])],
                       'classification_field': [TextField(name='Classification Field', value="Yes"),
                                                TextField(name='Classification Field', value="No")]}

        result = self.model.eval_field_level(mock_act, mock_pred)
        act = {'level': {'confusion matrix': {'TP': 2, 'TN': 0, 'FP': 4, 'FN': 3},
                         'f1 score': 0.36363636363636365,
                         'precision': 0.3333333333333333,
                         'recall': 0.4,
                         'accuracy': 0.2222222222222222},
               'paragraph': {'confusion matrix': {'TP': 2, 'TN': 0, 'FP': 3, 'FN': 1},
                             'f1 score': 0.5,
                             'precision': 0.4,
                             'recall': 0.6666666666666666,
                             'accuracy': 0.3333333333333333},
               'classification_field': {'confusion matrix': {'TP': 2, 'TN': 0, 'FP': 0, 'FN': 1},
                                        'f1 score': 0.8,
                                        'precision': 1,
                                        'recall': 0.6666666666666666,
                                        'accuracy': 0.6666666666666666}}
        self.assertDictEqual(result, act)

        # Testing the case when only content is true
        mock_act.y = {'level': [TextField(name='level', tags=[level_tag_1_act, level_tag_2_act]),
                                TextField(name='level', tags=[level_tag_1_act, level_tag_2_1_act])],
                      'paragraph': [TextField(name='paragraph', tags=[paragraph_tag_1_act, paragraph_tag_2_act]),
                                    TextField(name='paragraph', tags=[paragraph_tag_1_act, paragraph_tag_2_1_act])]}

        mock_pred.y = {'level': [TextField(name='level', tags=[level_tag_1_pred, level_tag_2_pred]),
                                 TextField(name='level', tags=[level_tag_1_pred, level_tag_2_1_pred])],
                       'paragraph': [TextField(name='paragraph', tags=[paragraph_tag_1_pred, paragraph_tag_2_pred]),
                                     TextField(name='paragraph', tags=[paragraph_tag_1_pred, paragraph_tag_2_1_pred])]}

        result_only_content = self.model.eval_field_level(mock_act, mock_pred, only_content=True)
        act_only_content = {'level': {'confusion matrix': {'TP': 2, 'TN': 0, 'FP': 0, 'FN': 0},
                                      'f1 score': 1.0,
                                      'precision': 1.0,
                                      'recall': 1.0,
                                      'accuracy': 1.0},
                            'paragraph': {'confusion matrix': {'TP': 2, 'TN': 0, 'FP': 0, 'FN': 0},
                                          'f1 score': 1.0,
                                          'precision': 1.0,
                                          'recall': 1.0,
                                          'accuracy': 1.0}}
        self.assertDictEqual(result_only_content, act_only_content)

        # Testing the case when the same field is repeating
        mock_act.y = {'paragraph': [TextField(name='paragraph', tags=[paragraph_tag_1_act, paragraph_tag_2_act]),
                                    TextField(name='paragraph', tags=[paragraph_tag_1_act, paragraph_tag_2_act]),
                                    TextField(name='paragraph', tags=[paragraph_tag_1_act, paragraph_tag_2_act]),
                                    TextField(name='paragraph', tags=[paragraph_tag_1_act, paragraph_tag_2_1_act])]}

        mock_pred.y = {'paragraph': [TextField(name='paragraph', tags=[paragraph_tag_1_pred, paragraph_tag_2_pred]),
                                     TextField(name='paragraph', tags=[paragraph_tag_1_pred, paragraph_tag_2_pred]),
                                     TextField(name='paragraph', tags=[paragraph_tag_1_pred, paragraph_tag_2_1_pred])]}
        result_act_repeating_field = {'paragraph': {'confusion matrix': {'TP': 2, 'TN': 0, 'FP': 1, 'FN': 2},
                                                    'f1 score': 0.5714285714285714,
                                                    'precision': 0.6666666666666666,
                                                    'recall': 0.5,
                                                    'accuracy': 0.4}}
        result_repeating_field = self.model.eval_field_level(mock_act, mock_pred)
        self.assertDictEqual(result_repeating_field, result_act_repeating_field)

    def test_eval_group_level(self):
        page = create_dummy_page(page_n=1)
        mock_act = Mock()
        mock_pred = Mock()
        group_key = str(uuid.uuid4())
        group_key_1 = str(uuid.uuid4())
        group_key_2 = str(uuid.uuid4())
        group_key_3 = str(uuid.uuid4())
        group_key_4 = str(uuid.uuid4())
        group_key_5 = str(uuid.uuid4())
        group_key_6 = str(uuid.uuid4())

        country_tag_1_act = ExtractionTag(left=41.05, right=48.15, top=14.77, bottom=16.33,
                                          page=page, raw_value="Armenia", raw_ocr_value="Armenia")
        country_tag_1_1_act = ExtractionTag(left=30.52, right=40.15, top=14.77, bottom=16.33,
                                            page=page, raw_value="Armenia", raw_ocr_value="Armenia")
        country_tag_2_act = ExtractionTag(left=41.05, right=46.15, top=17.77, bottom=19.33,
                                          page=page, raw_value="Georgia", raw_ocr_value="Georgia")
        country_tag_3_act = ExtractionTag(left=41.05, right=50.15, top=20.77, bottom=22.33,
                                          page=page, raw_value="Argentina", raw_ocr_value="Argentina")
        area_tag_1_act = ExtractionTag(left=50.05, right=53.15, top=14.77, bottom=16.33,
                                       page=page, raw_value="29.8", raw_ocr_value="29.8")
        area_tag_1_1_act = ExtractionTag(left=50.05, right=53.15, top=17.77, bottom=19.33,
                                         page=page, raw_value="29.8", raw_ocr_value="29.8")
        area_tag_2_act = ExtractionTag(left=50.05, right=53.15, top=17.77, bottom=19.33,
                                       page=page, raw_value="69.7", raw_ocr_value="1.1")
        area_tag_3_act = ExtractionTag(left=50.05, right=53.15, top=19.77, bottom=22.33,
                                       page=page, raw_value="200.3", raw_ocr_value="200.3")

        country_tag_1_pred = ExtractionTag(left=41.05, right=48.15, top=14.77, bottom=16.33,
                                           page=page, raw_value="Armenia", raw_ocr_value="Armenia")
        country_tag_2_pred = ExtractionTag(left=41.05, right=46.15, top=17.77, bottom=19.33,
                                           page=page, raw_value="Georgia", raw_ocr_value="Georgia")
        area_tag_1_pred = ExtractionTag(left=50.05, right=53.15, top=14.77, bottom=16.33,
                                        page=page, raw_value="29.8", raw_ocr_value="29.8")
        area_tag_2_pred = ExtractionTag(left=50.05, right=53.15, top=17.77, bottom=19.33,
                                        page=page, raw_value="69.7", raw_ocr_value="1.1")

        # Testing simple case
        mock_act.y = {'level': [TextField(name='level', value="Yes", group_key=group_key),
                                TextField(name='level', value="No", group_key=group_key_1),
                                TextField(name='level', value="No", group_key=group_key_2),
                                TextField(name='level', value="Yes", group_key=group_key_6)],
                      'country': [TextField(name='country', tags=[country_tag_1_act, country_tag_2_act],
                                            group_key=group_key),
                                  TextField(name='country', tags=[country_tag_1_act], group_key=group_key_1),
                                  TextField(name='country', tags=[country_tag_1_act, country_tag_2_act],
                                            group_key=group_key_2),
                                  TextField(name='country', tags=[country_tag_3_act], group_key=group_key_6)],
                      'area': [TextField(name='country', tags=[area_tag_1_act, area_tag_2_act], group_key=group_key),
                               TextField(name='country', tags=[area_tag_1_act], group_key=group_key_1),
                               TextField(name='country', tags=[area_tag_1_act, area_tag_2_act], group_key=group_key_2),
                               TextField(name='country', tags=[area_tag_3_act], group_key=group_key_6)]}

        mock_pred.y = {'level': [TextField(name='level', value="Yes", group_key=group_key_3),
                                 TextField(name='level', value="Yes", group_key=group_key_4),
                                 TextField(name='level', value="No", group_key=group_key_5)],
                       'country': [TextField(name='country', tags=[country_tag_1_pred, country_tag_2_pred],
                                             group_key=group_key_3),
                                   TextField(name='country', tags=[country_tag_1_pred], group_key=group_key_4),
                                   TextField(name='country', tags=[country_tag_1_pred], group_key=group_key_5)],
                       'area': [TextField(name='country', tags=[area_tag_1_pred, area_tag_2_pred],
                                          group_key=group_key_3),
                                TextField(name='country', tags=[area_tag_1_pred], group_key=group_key_4),
                                TextField(name='country', tags=[area_tag_1_pred, area_tag_2_pred],
                                          group_key=group_key_5)]}

        result = self.model.eval_group_level(mock_act, mock_pred)
        act = {'confusion matrix': {'TP': 1, 'TN': 0, 'FP': 2, 'FN': 3},
               'f1 score': 0.2857142857142857,
               'precision': 0.3333333333333333,
               'recall': 0.25,
               'accuracy': 0.16666666666666666}
        self.assertDictEqual(result, act)

        # Testing simple case 2
        mock_act.y = {'level': [TextField(name='level', value="Yes", group_key=group_key),
                                TextField(name='level', value="No", group_key=group_key_1)],
                      'country': [TextField(name='country', tags=[country_tag_1_act, country_tag_3_act],
                                            group_key=group_key),
                                  TextField(name='country', tags=[country_tag_1_act], group_key=group_key_1)],
                      'area': [TextField(name='country', tags=[area_tag_1_act, area_tag_2_act], group_key=group_key),
                               TextField(name='country', tags=[area_tag_1_act], group_key=group_key_1)]}

        mock_pred.y = {'level': [TextField(name='level', value="Yes", group_key=group_key_3),
                                 TextField(name='level', value="No", group_key=group_key_4)],
                       'country': [TextField(name='country', tags=[country_tag_1_pred, country_tag_2_pred],
                                             group_key=group_key_3),
                                   TextField(name='country', tags=[country_tag_1_pred], group_key=group_key_4)],
                       'area': [TextField(name='country', tags=[area_tag_1_pred, area_tag_2_pred],
                                          group_key=group_key_3),
                                TextField(name='country', tags=[area_tag_1_pred], group_key=group_key_4)]}

        result_2 = self.model.eval_group_level(mock_act, mock_pred)
        act_2 = {'confusion matrix': {'TP': 1, 'TN': 0, 'FP': 1, 'FN': 1},
                 'f1 score': 0.5,
                 'precision': 0.5,
                 'recall': 0.5,
                 'accuracy': 0.3333333333333333}
        self.assertDictEqual(result_2, act_2)

        # Testing the case when only content is true
        mock_act.y = {'level': [TextField(name='level', value="Yes", group_key=group_key),
                                TextField(name='level', value="No", group_key=group_key_1),
                                TextField(name='level', value="No", group_key=group_key_2),
                                TextField(name='level', value="Yes", group_key=group_key_6)],
                      'country': [TextField(name='country', tags=[country_tag_1_1_act, country_tag_2_act],
                                            group_key=group_key),
                                  TextField(name='country', tags=[country_tag_1_act], group_key=group_key_1),
                                  TextField(name='country', tags=[country_tag_1_act, country_tag_2_act],
                                            group_key=group_key_2),
                                  TextField(name='country', tags=[country_tag_3_act], group_key=group_key_6)],
                      'area': [TextField(name='country', tags=[area_tag_1_1_act, area_tag_2_act], group_key=group_key),
                               TextField(name='country', tags=[area_tag_1_act], group_key=group_key_1),
                               TextField(name='country', tags=[area_tag_1_act, area_tag_2_act], group_key=group_key_2),
                               TextField(name='country', tags=[area_tag_3_act], group_key=group_key_6)]}

        mock_pred.y = {'level': [TextField(name='level', value="Yes", group_key=group_key_3),
                                 TextField(name='level', value="Yes", group_key=group_key_4),
                                 TextField(name='level', value="No", group_key=group_key_5)],
                       'country': [TextField(name='country', tags=[country_tag_1_pred, country_tag_2_pred],
                                             group_key=group_key_3),
                                   TextField(name='country', tags=[country_tag_1_pred], group_key=group_key_4),
                                   TextField(name='country', tags=[country_tag_1_pred], group_key=group_key_5)],
                       'area': [TextField(name='country', tags=[area_tag_1_pred, area_tag_2_pred],
                                          group_key=group_key_3),
                                TextField(name='country', tags=[area_tag_1_pred], group_key=group_key_4),
                                TextField(name='country', tags=[area_tag_1_pred, area_tag_2_pred],
                                          group_key=group_key_5)]}

        result_only_content = self.model.eval_group_level(mock_act, mock_pred, only_content=True)
        act_only_content = {'confusion matrix': {'TP': 1, 'TN': 0, 'FP': 2, 'FN': 3},
                            'f1 score': 0.2857142857142857,
                            'precision': 0.3333333333333333,
                            'recall': 0.25,
                            'accuracy': 0.16666666666666666}
        self.assertDictEqual(result_only_content, act_only_content)

        # Testing the case when the same group is repeating
        mock_act.y = {'level': [TextField(name='level', value="Yes", group_key=group_key),
                                TextField(name='level', value="Yes", group_key=group_key_4)],
                      'country': [TextField(name='country', tags=[country_tag_1_act, country_tag_2_act],
                                            group_key=group_key),
                                  TextField(name='country', tags=[country_tag_1_act, country_tag_2_act],
                                            group_key=group_key_4)],
                      'area': [TextField(name='country', tags=[area_tag_1_act, area_tag_2_act], group_key=group_key),
                               TextField(name='country', tags=[area_tag_1_act, area_tag_2_act], group_key=group_key_4)]}

        mock_pred.y = {'level': [TextField(name='level', value="Yes", group_key=group_key_3),
                                 TextField(name='level', value="Yes", group_key=group_key_5),
                                 TextField(name='level', value="Yes", group_key=group_key_2)],
                       'country': [TextField(name='country', tags=[country_tag_1_pred, country_tag_2_pred],
                                             group_key=group_key_3),
                                   TextField(name='country', tags=[country_tag_1_pred, country_tag_2_pred],
                                             group_key=group_key_5),
                                   TextField(name='country', tags=[country_tag_1_pred, country_tag_2_pred],
                                             group_key=group_key_2)],
                       'area': [TextField(name='country', tags=[area_tag_1_pred, area_tag_2_pred],
                                          group_key=group_key_3),
                                TextField(name='country', tags=[area_tag_1_pred, area_tag_2_pred],
                                          group_key=group_key_5),
                                TextField(name='country', tags=[area_tag_1_pred, area_tag_2_pred],
                                          group_key=group_key_2)]}
        result_repeating_group = self.model.eval_group_level(mock_act, mock_pred)
        result_act_repeating_group = {'confusion matrix': {'TP': 2, 'TN': 0, 'FP': 1, 'FN': 0},
                                      'f1 score': 0.8,
                                      'precision': 0.6666666666666666,
                                      'recall': 1.0,
                                      'accuracy': 0.6666666666666666}
        self.assertDictEqual(result_repeating_group, result_act_repeating_group)
