"""This module defines the Document object,
which includes the input and output fields for the model,
as well as the OCR data and page images of the document"""
import copy
import itertools
import json
import logging
import multiprocessing
import os
import platform
from collections import OrderedDict
from typing import Dict, List, Tuple, Any, Optional, Callable, Union, Literal

import fitz
import pandas as pd
import requests
from fitz.utils import getColor, getColorList
from requests.adapters import HTTPAdapter, Retry
from typing_extensions import deprecated

from pycognaize.common.classification_labels import ClassificationLabels
from pycognaize.common.enums import ApiConfigEnum, EnvConfigEnum
from pycognaize.common.enums import IqDocumentKeysEnum, FieldTypeEnum
from pycognaize.common.field_collection import FieldCollection
from pycognaize.document.field import FieldMapping, TableField
from pycognaize.document.field.field import Field
from pycognaize.document.html_info import HTML
from pycognaize.document.page import Page
from pycognaize.document.tag import TableTag, ExtractionTag
from pycognaize.document.tag.cell import Cell
from pycognaize.document.tag.tag import BoxTag, LineTag
from pycognaize.file_storage import get_storage
from pycognaize.login import Login

RETRY_ADAPTER = Retry(total=3,
                      backoff_factor=10,
                      status_forcelist=[500, 502, 503, 504])


class Document:
    """Definition of input and output for a single document,
     depending on a given model"""

    def __init__(self,
                 input_fields: 'FieldCollection[str, List[Field]]',
                 output_fields: 'FieldCollection[str, List[Field]]',
                 pages: Dict[int, Page],
                 classification_labels: Dict[str, ClassificationLabels],
                 html_info: HTML,
                 metadata: Dict[str, Any],
                 data_path: Optional[str] = None,
                 ):
        self._metadata = metadata
        self._pages: Dict[int, Page] = pages if pages else None
        self._classification_labels = classification_labels
        self._is_xbrl: bool = False
        self._html_info: HTML = html_info
        self._x: FieldCollection[str, List[Field]] = input_fields
        self._y: FieldCollection[str, List[Field]] = output_fields
        self._data_path = data_path

    @property
    def x(self) -> 'FieldCollection[str, List[Field]]':
        """Returns a dictionary, where keys are input field names
        and values are list of Field objects"""
        return self._x

    @property
    def y(self) -> 'FieldCollection[str, List[Field]]':
        """Returns a dictionary, where keys are output field names
        and values are list of Field objects"""
        return self._y

    @staticmethod
    def __create_and_get_task_id(document_id: str, recipe_id: str,
                                 api_host: str, x_auth: str) -> str:
        """Create a modeltask object in the database given a document
         id and recipe id"""
        url = api_host + ApiConfigEnum.CREATE_TASK_ENDPOINT.value
        payload = "{\"documentId\": \"%s\",\n \"recipeId\": \"%s\"\n}\n" \
                  % (document_id, recipe_id)
        headers = {'x-auth': x_auth,
                   'content-type': "application/json"}
        response = requests.request("POST", url, data=payload,
                                    headers=headers)
        response.raise_for_status()
        response_json = response.json()
        if 'taskId' not in response_json:
            raise ValueError(f"No task ID found in response: {response_json}"
                             f" (url: {url})")
        return response_json['taskId']

    @staticmethod
    def __get_document_by_task_id(task_id: str,
                                  api_host: str, x_auth: str):
        """Given a task, return a document object"""
        session = requests.Session()
        session.mount('http://', HTTPAdapter(max_retries=RETRY_ADAPTER))
        session.mount('https://', HTTPAdapter(max_retries=RETRY_ADAPTER))
        session.headers = {'x-auth': x_auth}
        get_response: requests.Response = \
            session.get(api_host +
                        ApiConfigEnum.RUN_MODEL_ENDPOINT.value +
                        '/' + task_id, verify=False,
                        timeout=ApiConfigEnum.DEFAULT_TIMEOUT.value)
        get_response.raise_for_status()
        get_response_dict: dict = get_response.json()
        doc_data_path: str = get_response_dict['documentRootPath']
        document_json: dict = get_response_dict['inputDocument']
        return doc_data_path, document_json

    @property
    def data_path(self) -> Optional[str]:
        """Returns the path to the document data"""
        if self._data_path is None:
            self._data_path = next(iter(self.pages.values())).path
        return self._data_path

    @property
    def metadata(self) -> Dict[str, Any]:
        """Returns document metadata"""
        return self._metadata

    @property
    def id(self) -> str:
        """Returns the pycognaize id of the document"""
        return self.metadata['document_id']

    @property
    def document_src(self):
        """Returns the source of the document"""
        return self.metadata['src']

    @property
    def pages(self) -> Dict[int, Page]:
        """Returns a dictionary, where each key is the page number
        and values are Page objects"""
        return self._pages

    @property
    def is_xbrl(self) -> bool:
        """Returns True if document is XBRL, otherwise False"""
        return self._html_info.path != ''

    @property
    def html(self):
        """Returns `HTML` object"""
        return self._html_info

    @classmethod
    def fetch_document(cls, recipe_id, doc_id,
                       api_host: Optional[str] = None,
                       x_auth: Optional[str] = None):
        """
        Get the document object, given a document id and recipe id

        :param recipe_id: ID of the document AI
            (the second ID in the url)
        :param doc_id: ID of the document
            (the ID in the annotation view URL of the document)
        :param api_host: https://<ENVIRONMENT NAME>-api.cognaize.com.
            If not provided will default to the environment variable
             "API_HOST"
        :param x_auth: X-Authorization token
            If not provided will default to the environment variable
             "X_AUTH_TOKEN"
        """
        doc_data_path, document_json = cls._get_document_dict(
            recipe_id=recipe_id,
            doc_id=doc_id,
            api_host=api_host,
            x_auth=x_auth)
        document = Document.from_dict(document_json,
                                      data_path=doc_data_path)
        return document

    @classmethod
    def _get_document_dict(
            cls,
            recipe_id,
            doc_id,
            api_host: Optional[str] = None,
            x_auth: Optional[str] = None
    ) -> Tuple[str, dict]:
        api_host = api_host or os.environ[EnvConfigEnum.HOST.value]
        x_auth = x_auth or os.environ[EnvConfigEnum.X_AUTH.value]
        if api_host is None:
            raise ValueError('No API host provided')
        if x_auth is None:
            raise ValueError('No X-Authorization token provided')
        api_host = api_host.rstrip('/')
        task_id = cls.__create_and_get_task_id(document_id=doc_id,
                                               recipe_id=recipe_id,
                                               api_host=api_host,
                                               x_auth=x_auth,
                                               )
        doc_data_path, document_json = cls.__get_document_by_task_id(
            task_id=task_id,
            api_host=api_host,
            x_auth=x_auth)
        return doc_data_path, document_json

    @staticmethod
    def get_matching_table_cells_for_tag(
            tag: BoxTag,
            table_tags: List[TableTag],
            one_to_one: bool
    ) -> List[Tuple[BoxTag, TableTag, Cell, float]]:
        """Create a list which includes the original extraction tag,
           the corresponding table tag and Cell objects
           and the IOU of the intersection

        :param tag: The `tag` for which matching
            table and cells should be found
        :param table_tags: List of `table_tag`s
        :param one_to_one: If true,
            for each tag only one corresponding cell will be returned
        :return: List of tuples,
            which include the original extraction tag,
            the corresponding table tag and Cell objects
            and the IOU of the intersection
        """
        intersection = []
        if isinstance(tag, TableTag):
            return []
        for ttag in table_tags:
            if ttag.page.page_number != tag.page.page_number:
                continue
            for cell in ttag.cells.values():
                temp_cell = copy.deepcopy(cell)
                temp_cell.page = ttag.page
                iou = tag.iou(temp_cell)
                if iou <= 0:
                    continue
                if one_to_one:
                    if (not intersection or (
                            intersection and intersection[0][-1] < iou
                    )):
                        intersection = [(tag, ttag, cell, iou)]
                else:
                    intersection.append((tag, ttag, cell, iou))
        return intersection

    def get_table_cell_overlap(
            self, source_field: str,
            one_to_one: bool) -> List[Tuple[BoxTag, TableTag, Cell, float]]:
        """Create a list which includes the original extraction tag,
           the corresponding table tag and Cell objects
           and the IOU of the intersection

        :param source_field: Name of the field,
            for which to return the corresponding table cells
        :param one_to_one: If true,
            for each tag only one corresponding cell will be returned
        :return: List of tuples,
            which include the original extraction tag,
            the corresponding table tag and Cell objects
            and the IOU of the intersection
        """
        # noinspection PyUnresolvedReferences
        table_tags = [
            tag
            for fields in itertools.chain(self.x.values(), self.y.values())
            for field in fields
            for tag in field.tags
            if isinstance(tag, TableTag)
        ]
        res = []
        if source_field in self.x:
            fields = self.x[source_field]
        elif source_field in self.y:
            fields = self.y[source_field]
        else:
            return []
        for field in fields:
            for tag in field.tags:
                intersection = self.get_matching_table_cells_for_tag(
                    tag=tag, table_tags=table_tags, one_to_one=one_to_one)
                res.extend(intersection)
        return res

    def get_tied_fields(self, tag: ExtractionTag,
                        field_type: str = FieldTypeEnum.BOTH.value,
                        threshold: float = 0.5,
                        pn_filter: Callable = lambda x: True
                        ) -> Dict[str, List[Field]]:
        """Given an `ExtractionTag`, return all the fields that contain
           tags in the same physical location.

        :param tag: Input `ExtractionTag`
        :param field_type: Types of fields to consider {input/output/both}
        :param threshold: The IoU threshold to consider the tags in the same
            location
        :param pn_filter: If provided, only fields with
            names passing the filter will be considered
        :return: Dictionary where key is pname
            and value is List of `Field` objects
        """
        all_tied_fields: Dict[str, List[Field]] = OrderedDict()
        if field_type == FieldTypeEnum.INPUT_FIELD.value:
            scopes = (self.x,)
        elif field_type == FieldTypeEnum.OUTPUT_FIELD.value:
            scopes = (self.y,)
        elif field_type == FieldTypeEnum.BOTH.value:
            scopes = (self.x, self.y)
        else:
            raise ValueError(
                f"'field_type' should be one of "
                f"{tuple(i.value for i in FieldTypeEnum.__members__.values())}"
                f" got {field_type}")
        for scope in scopes:
            for pname, fields in scope.items():
                if not pn_filter(pname):
                    continue
                tied_fields = {field for field in fields
                               if not isinstance(field, TableField)
                               for field_tag in field.tags
                               if isinstance(field_tag, ExtractionTag)
                               and (tag & field_tag)
                               / min({tag.area, field_tag.area}) >= threshold}
                if tied_fields:
                    all_tied_fields[pname] = list(tied_fields)
        return all_tied_fields

    def get_tied_tags(self, tag: ExtractionTag,
                      field_type: str = FieldTypeEnum.BOTH.value,
                      threshold: float = 0.9,
                      pn_filter: Callable = lambda x: True
                      ) -> Dict[str, List[ExtractionTag]]:
        """Given a single tag, return all other tags in the document that are
            in the same physical location in the document

        :param tag: Input `ExtractionTag`
        :param field_type: Types of fields to consider {input/output/both}
        :param threshold: The IoU threshold to consider the tags in the same
            location
        :param pn_filter: If provided, only tags that are in fields
            with names passing the filter will be considered
        :return: Dictionary where key is pname
            and value is List of `ExtractionTag` objects
        """
        all_tied_tags: Dict[str, List[ExtractionTag]] = OrderedDict()
        if field_type == FieldTypeEnum.INPUT_FIELD.value:
            scopes = (self.x,)
        elif field_type == FieldTypeEnum.OUTPUT_FIELD.value:
            scopes = (self.y,)
        elif field_type == FieldTypeEnum.BOTH.value:
            scopes = (self.x, self.y)
        else:
            raise ValueError(
                f"'field_type' should be one of "
                f"{tuple(i.value for i in FieldTypeEnum.__members__.values())}"
                f" got {field_type}")
        for scope in scopes:
            for pname, fields in scope.items():
                if not pn_filter(pname):
                    continue
                tied_tags = {field_tag for field in fields
                             if not isinstance(field, TableField)
                             for field_tag in field.tags
                             if isinstance(field_tag, ExtractionTag)
                             if tag.iou(field_tag) >= threshold}
                if tied_tags:
                    all_tied_tags[pname] = list(tied_tags)
        return all_tied_tags

    def get_first_tied_field(self, tag: ExtractionTag,
                             pn_filter: Callable = lambda x: True
                             ) -> Tuple[str, Field]:
        """Return the first field that is in the same location as the given tag

        :param tag: Input `ExtractionTag`
        :param pn_filter: If provided, only fields with
            names passing the filter will be considered
        :return: If match found, return Tuple of the matching pname
            and `Field`, otherwise return `None`
        """
        res = None
        fields = self.get_tied_fields(tag=tag,
                                      pn_filter=pn_filter)
        if fields:
            pname = list(fields)[0]
            first_tied_field = fields[pname][0]
            res = (pname, first_tied_field) if first_tied_field else res
        return res

    def get_first_tied_field_value(self, tag: ExtractionTag,
                                   pn_filter: Callable =
                                   lambda x: True):
        """Return the value of the first field that is in the
         same location as the given tag

        :param tag: Input `ExtractionTag`
        :param pn_filter: If provided, only tags that are
            in fields with names passing the filter will be considered
        :return:
        """
        if isinstance(tag, float):
            val = ''
        else:
            tied_field = self.get_first_tied_field(
                tag=tag, pn_filter=pn_filter)
            if tied_field is None:
                val = tag.raw_value
            else:
                pname, matching_field = self.get_first_tied_field(
                    tag=tag, pn_filter=pn_filter)
                # noinspection PyUnresolvedReferences
                val = matching_field.value
        return val

    def get_first_tied_tag(self, tag: ExtractionTag,
                           pn_filter: Callable = lambda x: True
                           ) -> Tuple[str, ExtractionTag]:
        """Return the first tag that is in the same location as the given tag

        :param tag: Input `ExtractionTag`
        :param pn_filter: If provided, only tags that
            are in fields with names passing the filter will be considered
        :return: If match found, return Tuple of the matching pname
            and `ExtractionTag`, otherwise return `None`
        """
        res = None
        tags = self.get_tied_tags(tag=tag,
                                  pn_filter=pn_filter)
        if tags:
            pname = list(tags)[0]
            first_tied_tag = tags[pname][0]
            res = (pname, first_tied_tag) if first_tied_tag else res
        return res

    def get_first_tied_tag_value(self, tag: ExtractionTag,
                                 pn_filter: Callable =
                                 lambda x: True):
        """Return the value of the first tag that is in the same
            location as the given tag

        :param tag: Input `ExtractionTag`
        :param pn_filter: If provided, only tags that are in
            fields with names passing the filter will be considered
        :return:
        """
        tied_tag = self.get_first_tied_tag(tag=tag,
                                           pn_filter=pn_filter)
        if tied_tag is None:
            val = tag.raw_value
        else:
            pname, matching_tag = tied_tag
            val = matching_tag.raw_value
        return val

    def get_df_with_tied_field_values(self, table_tag: TableTag,
                                      pn_filter: Callable =
                                      lambda x: True
                                      ) -> pd.DataFrame:
        """Return the dataframe of the TableTag, where each cell
           value is replaced with the values in the fields of
           tied values (e.i. values that are in
           the same physical location as the cell)

        :param table_tag: Input `TableTag`
        :param pn_filter: : If provided, only fields with
            names passing the filter will be considered
        :return: Dataframe of the TableTag
        """
        if "map" not in dir(table_tag.raw_df):
            return table_tag.raw_df.applymap(
                lambda x: self.get_first_tied_field_value(
                    x,
                    pn_filter=pn_filter))
        else:
            return table_tag.raw_df.map(
                lambda x: self.get_first_tied_field_value(
                    x,
                    pn_filter=pn_filter))

    def load_page_images(self, page_filter: Callable = lambda x: True) -> None:
        """Get all images of the pages in the document
         (Using multiprocessing)"""
        global _get_page

        # noinspection PyRedeclaration
        def _get_page(page, filter_pages: Callable = page_filter):
            if filter_pages(page):
                _ = page.image_bytes
            return page
        if platform.machine() in ["arm64", "aarch64"]:
            ctx = multiprocessing.get_context('fork')
            pool = ctx.Pool(min(multiprocessing.cpu_count() * 2, 16))
        else:
            pool = multiprocessing.Pool(
                min(multiprocessing.cpu_count() * 2, 16))
        pages = pool.map(_get_page, self.pages.values())
        for page, populated_page in zip(self.pages.values(), pages):
            page._image_arr = populated_page._image_arr
            page._image_bytes = populated_page._image_bytes

    @deprecated("Use `load_ocr` instead. It should be faster and more stable")
    def load_page_ocr(self,
                      page_filter: Callable = lambda x: True,
                      stick_coords: bool = False,
                      ) -> None:
        """Get all OCR of the pages in the document
           (Using multiprocessing)"""
        global _get_page

        # noinspection PyRedeclaration
        def _get_page(page, filter_pages: Callable = page_filter):
            if filter_pages(page):
                page._ocr = page.get_ocr_formatted(stick_coords=stick_coords)
                _ = page.lines
            return page
        if platform.machine() in ["arm64", "aarch64"]:
            ctx = multiprocessing.get_context('fork')
            pool = ctx.Pool(min(multiprocessing.cpu_count() * 2, 16))
        else:
            pool = multiprocessing.Pool(
                min(multiprocessing.cpu_count() * 2, 16))
        pages = pool.map(_get_page, self.pages.values())
        for page, populated_page in zip(self.pages.values(), pages):
            page._ocr = populated_page._ocr
            page._ocr_raw = populated_page._ocr_raw
            page._lines = populated_page._lines

    def load_ocr(self, stick_coords: bool = False) -> None:
        ocr_path = os.path.join(self.data_path, f"{self.document_src}.json")
        login_instance = Login()
        if login_instance.logged_in:
            storage_config = {
                'aws_access_key_id': login_instance.aws_access_key,
                'aws_session_token': login_instance.aws_session_token,
                'aws_secret_access_key': login_instance.aws_secret_access_key
            }
        else:
            storage_config = None
        storage = get_storage(ocr_path, config=storage_config)
        with storage.open(ocr_path, 'r') as f:
            ocr_data = json.loads(f.read())
        for raw_ocr in ocr_data:
            page_number = raw_ocr['page']['number']
            for word in raw_ocr['data']:
                word['x'] = float(word['x'])
                word['y'] = float(word['y'])
                word['w'] = float(word['w'])
                word['h'] = float(word['h'])
            raw_ocr['page']['width'] = float(raw_ocr['page']['width'])
            raw_ocr['page']['height'] = float(raw_ocr['page']['height'])
            self.pages[page_number]._ocr_raw = raw_ocr
            self.pages[page_number]._ocr = self.pages[
                page_number].get_ocr_formatted(stick_coords=stick_coords)

    def to_dict(self) -> dict:
        """Converts Document object to dict"""
        input_fields = OrderedDict(
            {name: [field.to_dict() for field in fields]
             for name, fields in self.x.items()})
        output_fields = OrderedDict(
            {name: [field.to_dict() for field in fields]
             for name, fields in self.y.items()})
        data = OrderedDict(input_fields=input_fields,
                           output_fields=output_fields,
                           metadata=self.metadata)
        return data

    @classmethod
    def from_dict(cls, raw: dict,
                  data_path: str) -> 'Document':
        """Document object created from data of dict
        :param raw: document dictionary
        :param data_path: path to the documents OCR and page images
        """
        if not isinstance(raw, dict):
            raise TypeError(
                f"Expected dict for 'raw' argument got {type(raw)} instead")
        metadata = raw['metadata']
        pages = OrderedDict()
        html_info = HTML(path=data_path, document_id=metadata['document_id'])
        classification_labels = ClassificationLabels(raw)
        for page_n in range(1, metadata['numberOfPages'] + 1):
            if (
                    'pages' in raw
                    and str(page_n) in raw['pages']
                    and 'width' in raw['pages'][str(page_n)]
                    and 'height' in raw['pages'][str(page_n)]
            ):
                image_width = raw['pages'][str(page_n)]['width']
                image_height = raw['pages'][str(page_n)]['height']
            else:
                image_width = None
                image_height = None
            pages[page_n] = Page(page_number=page_n,
                                 document_id=metadata['document_id'],
                                 path=data_path,
                                 image_width=image_width,
                                 image_height=image_height)
        input_fields = FieldCollection(
            {name: [
                FieldMapping[
                    field[IqDocumentKeysEnum.data_type.value].replace('-', '_')
                ].value.construct_from_raw(raw=field, pages=pages,
                                           html=html_info,
                                           labels=classification_labels.get(
                                               field.get(
                                                   IqDocumentKeysEnum.
                                                   src_field_id.value, ''),
                                               None))
                for field in fields]
                for name, fields in raw['input_fields'].items()})
        output_fields = FieldCollection(
            {name: [
                FieldMapping[
                    field[IqDocumentKeysEnum.data_type.value].replace('-', '_')
                ].value.construct_from_raw(raw=field, pages=pages,
                                           html=html_info,
                                           labels=classification_labels.get(
                                               field.get(
                                                   IqDocumentKeysEnum.
                                                   src_field_id.value, ''),
                                               None))
                for field in fields]
                for name, fields in raw['output_fields'].items()})
        return cls(input_fields=input_fields,
                   output_fields=output_fields,
                   pages=pages, html_info=html_info,
                   metadata=metadata,
                   classification_labels=classification_labels,
                   data_path=data_path
                   )

    def _collect_all_tags_for_fields(self,
                                     field_names: List[str],
                                     is_input_field: bool = True) \
            -> List[Union[BoxTag, LineTag]]:
        """Collect all tags of given field names from either input or output
            fields

        :param field_names: List of strings representing the field names
        :param is_input_field: If true, collect tags from input fields,
            otherwise collect tags from output fields
        :return: List of tags from the specified fields
        """
        all_tags = []
        if is_input_field:
            field_dict = self.x
            field_type = 'input field'
        else:
            field_dict = self.y
            field_type = 'output field'
        if field_names is not None:
            for field_name in field_names:
                if field_name not in field_dict.keys():
                    raise ValueError(f'Invalid {field_type} {field_name}')
                for field in field_dict.get(field_name, []):
                    for tag in field.tags:
                        all_tags.append(tag)
        return all_tags

    def to_pdf(self,
               input_fields: Optional[List[str]] = None,
               output_fields: Optional[List[str]] = None,
               input_color: str = 'deeppink1',
               output_color: str = 'deepskyblue3',
               input_opacity: float = 0.2,
               output_opacity: float = 0.3) -> bytes:

        """
        Adds tags of input_fields and output_fields to the bytes object
        representing the pdf file of the document.

        :param input_fields: Input fields
        :param output_fields: Output fields
        :param input_color: The color of the annotation rectangle
            of the input field
        :param output_color: The color of the annotation rectangle
            of the output field
        :param input_opacity: The opacity of the annotation rectangle
            of the input field
        :param output_opacity: The opacity of the annotation rectangle
            of the output field
        :return: bytes object of the pdf
        """
        login_instance = Login()
        if login_instance.logged_in:
            storage_config = {
                'aws_access_key_id': login_instance.aws_access_key,
                'aws_session_token': login_instance.aws_session_token,
                'aws_secret_access_key': login_instance.aws_secret_access_key
            }

        else:
            storage_config = None

        pdf_path = os.path.join(self.data_path,
                                self.document_src) + '.pdf'

        storage = get_storage(pdf_path, config=storage_config)

        with storage.open(pdf_path, 'rb') as f:
            pdf_bytes = f.read()
        doc_fitz = fitz.open('pdf', pdf_bytes)

        if input_fields is not None:
            input_tags = self._collect_all_tags_for_fields(
                field_names=input_fields, is_input_field=True)
            for tag in input_tags:
                pdf_bytes = annotate_pdf(
                    doc=doc_fitz,
                    tag=tag,
                    color=input_color,
                    opacity=input_opacity)
        if output_fields is not None:
            input_tags = self._collect_all_tags_for_fields(
                field_names=output_fields, is_input_field=False)
            for tag in input_tags:
                pdf_bytes = annotate_pdf(
                    doc=doc_fitz,
                    tag=tag,
                    color=output_color,
                    opacity=output_opacity)
        return pdf_bytes

    @staticmethod
    def _get_page_text_from_layout_info(
            layout_fields_on_page: list[Field],
            table_parser: Callable
    ) -> str:
        text = ""
        for field in layout_fields_on_page:
            if not field.tags:
                continue
            if isinstance(field, TableField):
                text += table_parser(field)
            else:
                area_tag: ExtractionTag = sum(field.tags)
                lines = area_tag.page.extract_words_in_tag_area(
                    area_tag=area_tag,
                    return_tags=False, line_by_line=True)
                for line in lines:
                    if not line:
                        continue
                    for word in line:
                        text += " " + word['ocr_text']
                    text += "\n"
        return text

    @classmethod
    def _get_document_text_from_layout_info(
            cls,
            layout_fields_on_page: dict[int, list[Field]],
            table_parser: Callable
    ) -> list[str]:
        layout_fields_on_page = sorted(layout_fields_on_page.items(),
                                       key=lambda item: item[0])
        return [
            cls._get_page_text_from_layout_info(page_fields,
                                                table_parser=table_parser)
            for page_n, page_fields in layout_fields_on_page]

    def _get_layout_fields_for_page(
            self,
            page: Page,
            field_type: Literal["input", "output", "both"],
            field_filter: Callable,
            sorting_function: Optional[Callable] = None
    ) -> list[Field]:
        layout_fields = []
        if field_type == "input":
            fields_by_python_name = self.x.items()
        elif field_type == "output":
            fields_by_python_name = self.y.items()
        elif field_type == "both":
            fields_by_python_name = itertools.chain(
                self.x.items(), self.y.items())
        else:
            raise ValueError(f"Unknown field type {field_type}")
        for python_name, fields in fields_by_python_name:
            for field in fields:
                if not field.tags or not field_filter(python_name, field):
                    continue
                if len(field.tags) > 1:
                    logging.warning(
                        f"Skipping field. A layout field should not have more"
                        f" than one tag (python name: {python_name}, field"
                        f" name: {field.name}, tags: {field.tags})")
                    continue
                if field.tags[0].page.page_number != page.page_number:
                    continue
                layout_fields.append(field)
        if sorting_function:
            layout_fields = sorted(layout_fields, key=sorting_function)
        return layout_fields

    def get_layout_fields(
            self,
            field_type: Literal["input", "output", "both"],
            field_filter: Callable = lambda pname, field: True,
            sorting_function: Optional[Callable] = None):
        return {
            page_n: self._get_layout_fields_for_page(
                page,
                field_type=field_type,
                field_filter=field_filter,
                sorting_function=sorting_function
            )
            for page_n, page in self.pages.items()
        }

    def get_layout_text(
            self,
            field_type: Literal["input", "output", "both"],
            field_filter: Callable = lambda pname, field: True,
            sorting_function: Optional[Callable] = None,
            table_parser: Callable = TableField.parse_table
    ) -> list[str]:
        """
        Sample usage:
        ```
            doc = Document.fetch_document(recipe_id="649a7c0180d898001055a354",
                                  doc_id="65db38f7dc54d400119ae1f3")

            def parse_table(table_field: TableField) -> str:
                df = table_field.tags[0].df
                new_header = df.iloc[0]
                df = df[1:]
                df.columns = new_header
                df_text = df.to_markdown(index=False)
                return df_text

            doc_text = doc.get_layout_text(
                field_type="both",
                field_filter=lambda pname, field: pname != 'table',
                sorting_function=lambda x: (x.tags[0].top, x.tags[0].left),
                table_parser=parse_table)

            for page_number, page_text in enumerate(doc_text, start=1):
                print(f"---------PAGE {page_number}---------------\n")
                print(page_text)
        ```
        """
        return self._get_document_text_from_layout_info(
            layout_fields_on_page=self.get_layout_fields(
                field_type=field_type,
                field_filter=field_filter,
                sorting_function=sorting_function),
            table_parser=table_parser
        )


def annotate_pdf(doc: fitz.Document,
                 tag: BoxTag,
                 color: str,
                 opacity: float = 0.3) -> bytes:
    """An annotated Document pdf in bytes"""
    page = doc[tag.page.page_number - 1]
    x0 = tag.left * page.mediabox.width / 100
    y0 = tag.top * page.mediabox.height / 100
    x1 = tag.right * page.mediabox.width / 100
    y1 = tag.bottom * page.mediabox.height / 100
    annot_rect = fitz.Rect(x0, y0, x1, y1)
    if color.upper() not in getColorList():
        raise ValueError(f'Wrong color {color}')
    if opacity < 0 or opacity > 1:
        raise ValueError(f'Wrong opacity value {opacity}')
    color_dict = {"stroke": getColor(color), "fill": getColor(color)}
    annot = page.add_rect_annot(annot_rect)
    annot.set_colors(color_dict)
    annot.set_opacity(opacity)
    annot.update()
    return doc.write()
