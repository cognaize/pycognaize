import abc
from collections import Counter, defaultdict
from typing import Tuple, List

import requests
import simplejson as json
from cloudstorageio import CloudInterface

from pycognaize.common.utils import (
    replace_object_ids_with_string,
    ConfusionMatrix
)
from pycognaize.document.document import Document
from pycognaize.document.tag import ExtractionTag


def join_url(*parts):
    """Join parts into a single url string"""
    return '/'.join(s.strip('/') for s in parts)


class Model(metaclass=abc.ABCMeta):
    """Inherit from this abstract class and implement `predict` method

    The model inputs and outputs are available from the document attribute.
    """
    CI = CloudInterface()

    @abc.abstractmethod
    def predict(self, document: Document) -> Document:
        raise NotImplementedError

    @abc.abstractmethod
    def evaluate(self, act_document: Document, pred_document: Document,
                 only_content=False) -> dict:
        """ General evaluate functionality by tag, field and group level
        :param act_document: actual document (ground truth)
        :param pred_document: predicted document
        :param only_content: if True evaluation ignores locations of tags,
            considers only content
        """
        raise NotImplementedError

    def copy(self, document: Document, base_document: Document) -> Document:
        raise NotImplementedError

    @staticmethod
    def _post_response(doc, session, url, task_id):
        output_document_bson: dict = doc.to_dict()
        output_document_dict = replace_object_ids_with_string(
            output_document_bson)
        output_document_json = json.dumps(output_document_dict,
                                          ignore_nan=True)
        session.headers.update({"Content-Type": "application/json"})
        post_response: requests.Response = session.post(
            url + '/' + task_id, data=output_document_json, verify=False)
        return post_response

    def execute_based_on_match(self, task_id: str, base_doc_task_id: str,
                               token: str, url: str) -> requests.Response:
        session = requests.Session()
        session.headers = {'x-auth': token}

        get_response: requests.Response = session.get(url + '/' + task_id,
                                                      verify=False)
        get_response_dict: dict = get_response.json()
        doc_data_path: str = get_response_dict['documentRootPath']
        document_json: dict = get_response_dict['inputDocument']
        doc: Document = Document.from_dict(document_json,
                                           data_path=doc_data_path)

        base_doc_get_response: requests.Response = session.get(
            url + '/' + base_doc_task_id, verify=False)
        base_doc_get_response_dict: dict = base_doc_get_response.json()
        base_doc_data_path: str = base_doc_get_response_dict[
            'documentRootPath']
        base_document_json: dict = base_doc_get_response_dict['inputDocument']
        base_doc: Document = Document.from_dict(base_document_json,
                                                data_path=base_doc_data_path)

        doc = self.copy(document=doc, base_document=base_doc)
        return self._post_response(doc=doc, session=session, url=url,
                                   task_id=task_id)

    def execute_genie(
            self, task_id: str, token: str, url: str) -> requests.Response:
        """Alias for execute_genie_v2"""
        return self.execute_genie_v2(task_id=task_id, token=token, url=url)

    def execute_genie_v2(self, task_id: str, token: str,
                         url: str) -> requests.Response:
        """Execute genie for a given task_id"""
        session = requests.Session()
        session.headers = {'x-auth': token}
        get_response: requests.Response = session.get(url + '/' + task_id,
                                                      verify=False)
        get_response_dict: dict = get_response.json()
        doc_data_path: str = get_response_dict['documentRootPath']
        document_json: dict = get_response_dict['inputDocument']
        doc: Document = Document.from_dict(document_json,
                                           data_path=doc_data_path)
        doc = self.predict(doc)
        return self._post_response(doc=doc, session=session, url=url,
                                   task_id=task_id)

    def eval_tag_level(self, act_document: Document,
                       pred_document: Document, only_content=False) -> dict:
        """ Evaluation on tag level.
        Comparison is between all actual and predicted tags
            of each extraction field
        :returns: dict with keys - extraction field names and values - dict
            of computed metrics
        for that field"""

        result = {}
        for field_name in act_document.y.keys():
            tp_t, tn_t, fp_t, fn_t = 0, 0, 0, 0
            act_tags = []
            pred_tags = []
            for act_field in act_document.y[field_name]:
                act_tags.extend(act_field.tags)
            for pred_field in pred_document.y[field_name]:
                pred_tags.extend(pred_field.tags)
            if act_tags or pred_tags:
                tp_t = self.compute_tag_level_tp(
                    act_tags=act_tags, pred_tags=pred_tags,
                    only_content=only_content)
                fp_t = len(pred_tags) - tp_t
                fn_t = len(act_tags) - tp_t
                conf_matrix = ConfusionMatrix(TP=tp_t,
                                              TN=tn_t,
                                              FP=fp_t,
                                              FN=fn_t)
                result[field_name] = conf_matrix.compute_metrics()
        return result

    def eval_field_level(self, act_document: Document,
                         pred_document: Document, only_content=False) -> dict:
        """ Evaluation on field level.
        Comparison is between all actual and predicted
            fields of each extraction field.
        :returns: dict with keys - field names, values
            - dict of computed metrics for that
        field"""

        result = {}
        for field_name in act_document.y.keys():
            pred_fields = pred_document.y[field_name]
            act_fields = act_document.y[field_name]
            conf_matrix = self.get_field_level_conf_matrix(
                act_fields=act_fields, pred_fields=pred_fields,
                only_content=only_content)
            if (conf_matrix.TP == conf_matrix.TN == conf_matrix.FP
                    == conf_matrix.FN == 0):
                continue
            result[field_name] = conf_matrix.compute_metrics()
        return result

    def eval_group_level(self, act_document: Document,
                         pred_document: Document,
                         only_content=False) -> dict:
        """ Evaluation on group level
        Comparison is between all actual and predicted groups/entities.
        :returns: dict with keys - metrics names, values - computed scores"""

        matched_keys = []
        act_data_grouped = self.group_entities(act_document)
        pred_data_grouped = self.group_entities(pred_document)
        matched_act_keys = []
        matched_pred_keys = []
        if act_data_grouped or pred_data_grouped:
            matched_keys = self.detect_entity_matches(
                act_entities=act_data_grouped, pred_entities=pred_data_grouped)
        tp_g, tn_g, fp_g, fn_g = 0, 0, 0, 0
        for keys in matched_keys:
            tp_f = 0
            group_key_act = keys['group_key_act']
            group_key_pred = keys['group_key_pred']
            if (group_key_act not in matched_act_keys
                    and group_key_pred not in matched_pred_keys):
                group_field_names = act_data_grouped[group_key_act].keys()
                for field_name in group_field_names:
                    act_field = act_data_grouped[group_key_act][field_name]
                    pred_field = pred_data_grouped[group_key_pred][field_name]
                    if act_field.tags or pred_field.tags:
                        tp_f_per = self.compute_field_level_tp(
                            act_field=act_field, pred_field=pred_field,
                            only_content=only_content)
                        if tp_f_per == 1:
                            tp_f += 1
                        else:
                            break
                    elif act_field.value or pred_field.value:
                        if pred_field.value == act_field.value:
                            tp_f += 1
                        else:
                            break
                    else:
                        tp_f += 1
                if tp_f == len(group_field_names):
                    tp_g += 1
                    matched_act_keys.append(group_key_act)
                    matched_pred_keys.append(group_key_pred)
        fp_g = len(pred_data_grouped.keys()) - tp_g
        fn_g = len(act_data_grouped.keys()) - tp_g
        conf_matrix = ConfusionMatrix(TP=tp_g, TN=tn_g, FP=fp_g, FN=fn_g)
        result = conf_matrix.compute_metrics()
        return result

    def compute_tag_level_tp(self, act_tags: list, pred_tags: list,
                             only_content=False) -> int:
        """ Given lists of actual and predicted tags calculates tp,
        i.e. number of identical matches"""
        tp_t = 0
        if only_content:
            act_values = [act_tag.raw_value for act_tag in act_tags]
            pred_values = [pred_tag.raw_value for pred_tag in pred_tags]
            tp_t = len(list((Counter(act_values)
                             & Counter(pred_values)).elements()))
        else:
            matched_act_idxs = []
            matched_pred_idxs = []
            for act_tag_idx, act_tag in enumerate(act_tags):
                for pred_tag_idx, pred_tag in enumerate(pred_tags):
                    if (act_tag_idx not in matched_act_idxs
                            and pred_tag_idx not in matched_pred_idxs):
                        if (self.matches(act_tag=act_tag, pred_tag=pred_tag)
                                and act_tag.raw_ocr_value
                                == pred_tag.raw_ocr_value):
                            tp_t += 1
                            matched_act_idxs.append(act_tag_idx)
                            matched_pred_idxs.append(pred_tag_idx)
        return tp_t

    def get_field_level_conf_matrix(self, act_fields: list,
                                    pred_fields: list,
                                    only_content=False) -> ConfusionMatrix:
        """ Given two lists of actual and predicted fields,
            computes ConfusionMatrix.
            Takes into account both classification and extraction fields.
            Ignores empty fields"""

        tp_f, tn_f, fp_f, fn_f = 0, 0, 0, 0
        if not any(act_field.tags for act_field in act_fields) and not any(
                pred_field.tags for pred_field in pred_fields):
            act_values = [field.value for field in act_fields]
            pred_values = [field.value for field in pred_fields]
            num_empty_act_fields = len(
                [field for field in act_fields if not field.value])
            num_empty_pred_fields = len(
                [field for field in pred_fields if not field.value])
            tp_f = len(list((Counter(act_values)
                             & Counter(pred_values)).elements()))
        else:
            num_empty_act_fields = len(
                [field for field in act_fields if not field.tags])
            num_empty_pred_fields = len(
                [field for field in pred_fields if not field.tags])
            matched_act_idxs = []
            matched_pred_idxs = []
            for act_field_idx, act_field in enumerate(act_fields):
                for pred_field_idx, pred_field in enumerate(pred_fields):
                    if (act_field_idx not in matched_act_idxs
                            and pred_field_idx not in matched_pred_idxs):
                        tp_f_one = self.compute_field_level_tp(
                            act_field=act_field, pred_field=pred_field,
                            only_content=only_content)
                        tp_f += tp_f_one
                        if tp_f_one == 1:
                            matched_act_idxs.append(act_field_idx)
                            matched_pred_idxs.append(pred_field_idx)
                            break
        fp_f = len(pred_fields) - tp_f - num_empty_pred_fields
        fn_f = len(act_fields) - tp_f - num_empty_act_fields
        return ConfusionMatrix(TP=tp_f, TN=tn_f, FP=fp_f, FN=fn_f)

    def compute_field_level_tp(self,
                               act_field,
                               pred_field,
                               only_content=False) -> int:
        """ Given 2 extraction fields, actual and predicted,
        calculates tp, i.e. number of identical field matches"""
        tp_f, tp_t = 0, 0
        act_tags = [act_tag for act_tag in act_field.tags if act_tag]
        pred_tags = [pred_tag for pred_tag in pred_field.tags if pred_tag]
        if not act_tags or not pred_tags:
            return tp_f
        if len(act_tags) == len(pred_tags):
            tp_t = self.compute_tag_level_tp(act_tags=act_tags,
                                             pred_tags=pred_tags,
                                             only_content=only_content)
            if tp_t == len(act_tags):
                tp_f = 1
                return tp_f
        return tp_f

    def detect_entity_matches(self, act_entities: dict,
                              pred_entities: dict) -> list:
        """ Given actual and predicted groups/entities, finds pairs which have
        any match (even one tag in one of the fields)
        :return matched_keys: list of dicts, where each dict contains
            matched pairs' group keys """

        matched_keys = []
        for group_key_act, entity_act in act_entities.items():
            for group_key_pred, entity_pred in pred_entities.items():
                if set(entity_act.keys()) == set(entity_pred.keys()):
                    for field_name in entity_act.keys():
                        if (entity_act[field_name].tags
                                or entity_pred[field_name].tags):
                            if any(self.matches(act_tag=act_tag,
                                                pred_tag=pred_tag)
                                   for act_tag in entity_act[field_name].tags
                                   for pred_tag
                                   in entity_pred[field_name].tags):
                                matched_keys.append(
                                    {'group_key_act': group_key_act,
                                     'group_key_pred': group_key_pred})
                                break
                        elif (entity_act[field_name].value
                              == entity_pred[field_name].value):
                            matched_keys.append(
                                {'group_key_act': group_key_act,
                                 'group_key_pred': group_key_pred})
                            break
        return matched_keys

    @staticmethod
    def group_entities(document: Document) -> dict:
        """
        Group the entities by group keys.
            Fields having the same group key belong to the same entity.
            Returns dict of dicts, where keys are group keys of found entities,
            values are dicts with field names (keys): fields (values) belonging
            to that entity
        :param document:
        :return: dict of dicts
        """
        group_keys = set()
        groups = defaultdict(dict)
        for field_name in document.y.keys():
            group_keys.update(
                [item.group_key for item in document.y[field_name]
                 if item.group_key])
        for key in group_keys:
            groups[key] = {}
            for field_name in document.y.keys():
                for item in document.y[field_name]:
                    if item.group_key == key:
                        groups[key][field_name] = item
        return groups

    @staticmethod
    def matches(act_tag: ExtractionTag, pred_tag: ExtractionTag,
                threshold: float = 0.6) -> bool:
        """ Detects if there is a match between two extraction tags
            having the same page number. Returns true if
        intersection is greater than the threshold"""
        return act_tag.page.page_number == pred_tag.page.page_number and (
                act_tag & pred_tag) / min(
            act_tag, pred_tag, key=lambda x: x.area).area >= threshold

    def execute_eval(self,
                     token: str,
                     url: str,
                     model_version: str
                     ) -> List[requests.Response]:
        """ Execute evaluation for a given model_version """
        session = requests.Session()
        session.headers = {'x-auth': token}

        ground_truth_ids = session.get(
            url=f'{url}/groundtruths/{model_version}',
            verify=False
        ).json()

        post_responses = []
        for gt_id in ground_truth_ids:
            ground_truth_model_task = session.get(
                url=f'{url}/evaluations/{model_version}/{gt_id}',
                verify=False
            ).json()

            act_doc, pred_doc = self._get_doc_pair(ground_truth_model_task)
            eval_result = self.evaluate(act_document=act_doc,
                                        pred_document=pred_doc,
                                        only_content=False)

            data = {
                'modelVersion': model_version,
                'groundTruth': gt_id,
                'modelTask': ground_truth_model_task["modelTask"]["_id"],
                'evaluation': eval_result,
                'gitHash': ground_truth_model_task["modelTask"]['gitHash']
            }

            post_response = self._post_response_eval(
                session=session,
                endpoint=f'{url}/evaluations',
                data=data)
            post_responses.append(post_response)
        return post_responses

    @staticmethod
    def _get_doc_pair(data: dict) -> Tuple[Document, Document]:
        """Return the pair of actual and predicted Document objects
        from the dictionary of ground truth and model task pair."""
        pred_doc = Document.from_dict(
            raw=data["modelTask"]["outputDocument"],
            data_path=data["modelTask"]["documentRootPath"])
        act_doc = Document.from_dict(
            raw={
                "input_fields": {},
                "output_fields": data["groundTruth"]["fields"],
                "metadata": data["modelTask"]["outputDocument"]["metadata"]
            },
            data_path=data["modelTask"]["documentRootPath"])
        return act_doc, pred_doc

    @staticmethod
    def _post_response_eval(session: requests.Session,
                            endpoint: str,
                            data: dict
                            ) -> requests.Response:
        session.headers.update({"Content-Type": "application/json"})
        post_response = session.post(endpoint,
                                     data=json.dumps(data, ignore_nan=True),
                                     verify=False)
        return post_response
