import io
import os
import re

from PIL import Image
import bson
import logging
from itertools import groupby
from typing import Union, List, Optional
from bson.json_util import loads as bson_loads

import numpy as np
from dataclasses import dataclass

from cloudstorageio import CloudInterface

from pycognaize.login import Login
from pycognaize.common.enums import PythonShellEnum
from pycognaize.common.decorators import soon_be_deprecated


REGEX_NO_ALPHANUM_CHARS = re.compile(r'[^a-zA-Z\d)\[\](-.,]')


def is_float(str_number: str) -> bool:
    """Check if the string value is a valid number.
        Infinity and NaN are regarded as invalid"""
    # 'n' check covers both 'NaN', 'Inf' and 'Infinity'
    if 'n' in str_number.lower():
        return False
    try:
        float(str_number)
        return True
    except ValueError:
        return False


def convert_coord_to_num(val: Union[float, int, str]) -> Union[int, float]:
    """If the input is a string representation of a number
        (with or without a %), convert it into float.
        If the input is already a float or an integer, return itself"""
    if isinstance(val, str):
        val = val.rstrip('%')
        if not is_float(val):
            raise ValueError(f"Invalid numeric {val}")
        val = float(val)
    elif isinstance(val, (float, int)):
        pass
    else:
        raise TypeError(f"Invalid type for numeric {type(val)} ({val}")
    return val


def load_bson_by_path(doc_path):
    with open(os.path.join(doc_path), 'r') as f:
        return bson_loads(f.read())


@soon_be_deprecated()
def bytes_to_array(img_str: bytes) -> np.ndarray:
    """Convert image bytes into numpy array

    :param img_str: Bytestream of the image
    :return: numpy array of the image
    """
    import cv2
    nparr = np.frombuffer(img_str, np.uint8)
    img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return img_np


@soon_be_deprecated()
def string_to_array(img_str: bytes):
    """
    Convert a bytestring into a numpy array with opencv

    :param str img_str: image as byte string
    :return: img_np: image as numpy array
    """
    import cv2
    nparr = np.frombuffer(img_str, np.uint8)
    img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    assert type(img_np) == np.ndarray, (
        "Expected numpy array, received {}".format(type(img_np)))

    return img_np


def image_bytes_to_array(img_str: bytes) -> np.ndarray:
    """Convert image bytes into numpy array

    :param img_str: Bytestream of the image
    :return: numpy array of the image
    """
    image = Image.open(io.BytesIO(img_str))
    # Remove <alpha> channel if it exists
    img_np = np.array(image)[..., :3]

    return img_np


def image_string_to_array(img_str: bytes):
    """
    Convert a bytestring into a numpy array with opencv

    :param str img_str: image as byte string
    :return: img_np: image as numpy array
    """
    image = Image.open(io.BytesIO(img_str))
    # Remove <alpha> channel if it exists
    img_np = np.array(image)[..., :3]
    assert type(img_np) == np.ndarray, (
        "Expected numpy array, received {}".format(type(img_np)))

    return img_np


def compute_otsu_threshold(img_array):
    bins_num = 256
    hist, bin_edges = np.histogram(img_array, bins=bins_num)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2.

    weight1 = np.cumsum(hist)
    weight2 = np.cumsum(hist[::-1])[::-1]

    mean1 = np.cumsum(hist * bin_centers) / weight1
    mean2 = (np.cumsum((hist * bin_centers)[::-1]) / weight2[::-1])[::-1]

    weight_mul = weight1[:-1] * weight2[1:]
    inter_class_variance = weight_mul * (mean1[:-1] - mean2[1:]) ** 2
    index_of_max_val = np.argmax(inter_class_variance)

    threshold = bin_centers[:-1][index_of_max_val]

    return threshold


def img_to_black_and_white(img_array):
    """Image to only black and white image

    black pixel --> white pixel
    other pixel --> black pixel

    :return:
    """

    def grayscale2bw(x, threshold_value):
        return 255 if x < threshold_value else 0

    vectorized_converter = np.vectorize(grayscale2bw)
    grayscale = np.dot(img_array[..., :3], [0.299, 0.587, 0.114])
    threshold = compute_otsu_threshold(img_array)
    return vectorized_converter(grayscale, threshold)


def group_sequence(list_of_integers):
    """Group sequence into list
    example ->
    test_list = [1, 2, 3, 8, 15, 23, 24, 25, 10, 11, 13, 15]
    sequence_list = [[1, 2, 3], [23, 24, 25], [10, 11]]
    :param list_of_integers: list of integers
    :return: list of grouped integers
    """
    it = iter(list_of_integers)
    prev, res = next(it), []

    while prev is not None:
        start = next(it, None)
        if prev + 1 == start:
            res.append(prev)
        elif res:
            yield list(res + [prev])
            res = []
        prev = start


def stick_word_boxes(box_coord: List[dict], img_bytes: bytes, padding=1):
    """Stick boxes with OpenCV
        1) Stick by y (height), add "2 pixel" padding in bottom and right
            Get bigger sequence of 255 < vectors_y < 0  --> bigger_sequence
            new_top = min(bigger_sequence)
            new_bottom = max(bigger_sequence)

        2) stick by x (width), add "2 pixel" padding in bottom
            Get numpy array of 255 < vectors_x < 0  --> min_max_x
            new_left = min(min_max_x)
            new_right = max(min_max_x)

    :param box_coord: List of dictionaries representing
        boxes with the following format:
        ({'left': <int>, 'right': <int>, 'top': <int>, 'bottom': <int>})
    :param img_bytes: The original image to which the coordinates correspond to
    :param padding: Expand the final boxes with this amount of pixels
        on each four sides
    :return:
    """
    np_image = image_bytes_to_array(img_bytes)
    b_and_w_image = img_to_black_and_white(np_image)
    h, w, _ = np_image.shape
    for word in box_coord:
        start_point_xmin = max(0, int(round(word['left'])) - 1)
        start_point_ymin = max(0, int(round(word['top'])) - 1)

        end_point_xmax = int(round(word['right'])) + 2
        end_point_ymax = int(round(word['bottom'])) + 2

        cropped_word = b_and_w_image[start_point_ymin:end_point_ymax,
                                     start_point_xmin:end_point_xmax]

        vectors_y = np.mean(cropped_word, axis=1)
        min_max_y = np.where((vectors_y != 0) & (vectors_y != 255))

        if len(min_max_y[0]) == 0:
            continue
        elif 0 < len(min_max_y[0]) < 3:
            vectors_x = np.mean(cropped_word, axis=0)
            min_max_x = np.where((vectors_x != 0) & (vectors_x != 255))

            new_top = min(min_max_y[0]) - 2 if len(min_max_y[0]) else 0
            new_bottom = max(min_max_y[0]) + 2 if len(min_max_y[0]) else 0
            new_left = min(min_max_x[0]) - 2 if len(min_max_x[0]) else 0
            new_right = max(min_max_x[0]) + 2 if len(min_max_x[0]) else 0
        else:
            try:
                sequence_y = list(group_sequence(list(min_max_y[0])))
                if len(sequence_y) > 0:
                    sequence_y = sorted(sequence_y, key=lambda x: len(x),
                                        reverse=True)
                max_sequence = sequence_y[0]
                new_top = min(max_sequence)
                new_bottom = max(max_sequence)
                new_bottom_cropped = new_bottom + 2

                cropped_word_height = cropped_word[
                                      new_top:new_bottom_cropped, :]

                vectors_x_height_stuck = np.mean(cropped_word_height, axis=0)
                min_max_x_height_stuck = np.where(
                    (vectors_x_height_stuck != 0
                     ) & (vectors_x_height_stuck != 255)
                )

                new_left = int(min(min_max_x_height_stuck[0]))
                new_right = int(max(min_max_x_height_stuck[0]))
            except Exception as e:
                logging.debug(f"Failed for word {word}: {e}")
                continue

        word['left'] = int(new_left) + start_point_xmin - padding
        word['right'] = int(new_right) + start_point_xmin + padding
        word['top'] = int(new_top) + start_point_ymin - padding
        word['bottom'] = int(new_bottom) + start_point_ymin + padding

    return box_coord


def preview_img(img: np.ndarray, size: int = 1000):
    """Preview the given image in a window

    :param img: Original image as numpy array
    :param size: Resize the window to the given resolution before viewing
    """
    import matplotlib.pyplot as plt
    plt.imshow(img)
    fig = plt.figure(num=1)
    fig.set_dpi(size)
    fig.set_size_inches(1, 1, forward=True)
    plt.axis('off')
    plt.show()


def infer_rows_from_words(box, class_ocr_data, auto_thresh=True, thresh=12,
                          min_height=10, min_width=10):
    """
    Infer row coordinates by class crop (table, column, row)
        from the ocr output
    :param class_ocr_data:
    :param box:
    :param auto_thresh:
    :param thresh:
    :param min_height:
    :param min_width:
    :rtype: tuple(list, list)
    :return:
    """
    class_ocr_data = sorted(class_ocr_data,
                            key=lambda x: (x['top'], x['left']))
    class_ocr_data = [
        i for i in class_ocr_data
        if i['ocr_text'].strip(' \t\n.,:;*_|\\/!\'"')]
    if auto_thresh:
        cleaned_ocr_data_for_height_detection = [
            i for i in class_ocr_data if
            i['ocr_text'].strip(' \t\n.,:;*_-~=|\\/!\'"')]
        all_heights_tuples = [
            (i.get('bottom') - i.get('top'), i['ocr_text']) for i in
            cleaned_ocr_data_for_height_detection
            if i.get('bottom') and i.get('top')]
        all_heights = [i[0] for i in all_heights_tuples]
        if len(all_heights) > 0:
            average_heights = sum(all_heights) / len(all_heights)
        else:
            average_heights = 0
        thresh = int(round(average_heights * 0.8))
        min_height = int(round(average_heights * 0.7))
        min_width = int(round(average_heights * 0.7))
    previous_bottom = 0
    previous_top = 0
    word_groups = []
    # Group aligned rows
    for i, (row_top, row_boxes) in enumerate(
            groupby(class_ocr_data, key=lambda x: x.get('top'))):
        word_boxes = sorted(list(row_boxes), key=lambda x: (x.get('left')))
        row_bottom = max(i['bottom'] for i in word_boxes)
        if not i:
            word_groups.append(word_boxes)
        elif (
                # (row_top - previous_bottom < thresh) or
                (abs(row_top - previous_top)
                 < thresh and abs(row_bottom - previous_bottom) < thresh) or
                (row_top >= previous_top and row_bottom <= previous_bottom) or
                (row_top <= previous_top and row_bottom >= previous_bottom)
        ):
            word_groups[-1] += word_boxes
        else:
            word_groups.append(word_boxes)
        previous_bottom = row_bottom
        previous_top = row_top
    aggregated_rows = []
    # Construct row boxes from row groups
    for row in word_groups:
        temp_d = dict(left=min(i['left'] for i in row) - box['left'],
                      right=max(i['right'] for i in row) - box['left'],
                      top=min(i['top'] for i in row) - box['top'],
                      bottom=max(i['bottom'] for i in row) - box['top'],
                      ocr_text=' '.join(i['ocr_text'] for i in row)
                      )
        if (temp_d['bottom'] - temp_d['top'] > min_width
                and temp_d['right'] - temp_d['left'] > min_height):
            aggregated_rows.append(temp_d)
    return aggregated_rows, word_groups


def clean_ocr_data(ocr_data: dict, thresh: float = 4.0) -> dict:
    """Cleans the ocr data

    :param ocr_data: OCR data dictionary, where values under the key `words`
        have the following form: {'top'}
    :param thresh: Words that
    :return:
    """
    ocr_data['words'] = [i for i in ocr_data['words'] if i['ocr_text'].strip()
                         and (i['bottom'] - i['top'])
                         / max(i['right'] - i['left'], 0.01) <= thresh]
    return ocr_data


def find_first_word_coords(text: str, ocr_data: list,
                           case_sensitive: bool = False, sort: bool = False,
                           clean: bool = True,
                           cleanup_regex=REGEX_NO_ALPHANUM_CHARS
                           ) -> Optional[dict]:
    """
    Detect the coordinates of the first occurrence
        of `text` in `ocr_data` if any.
    If the `text` is not found in `ocr_data` return None
    :param text:
    :param ocr_data: List of dictionaries.
    Each dictionary contains information about a single word.
    Each word dictionary has the following keys: `confidence`, `right`,
        `left`, `top`, `bottom`, `ocr_text`, `word_id_number`
    :param case_sensitive: If True, the search will be case-sensitive
    :param sort: If True, ocr_data will be ordered by `word_id_number`
        key before searching
    :param clean: If true, disregard all non-alphanumeric character
        from the search
    :param re._pattern_type cleanup_regex: Optional.
        Provide the regex for cleanup to be used
        (has effect only if `clean=True`)
    :return: Dictionary with word coordinates
        (keys: `left`, `right`, `top`, `bottom`, `matched_words`.
        `matched_words` includes the original word coordinate data
        for the matched words)
    """
    matched_words = []
    if sort:
        ocr_data = sorted(ocr_data, key=lambda x: float(x['word_id_number']))
    if not case_sensitive:
        text = text.lower()
    words = text.split(' ')
    idx = 0
    for ocr_d in ocr_data:
        ocr_word = ocr_d['ocr_text']
        if clean:
            ocr_word = cleanup_regex.sub('', ocr_word)
            word = cleanup_regex.sub('', words[idx])
        else:
            word = words[idx]
        ocr_word = ocr_word.strip()
        if not case_sensitive:
            ocr_word = ocr_word.lower()
        if ocr_word == word:
            idx += 1
            matched_words.append(ocr_d)
            if idx >= len(words):
                break
        else:
            matched_words = []
            idx = 0
    else:
        return
    return dict(top=min(matched_words, key=lambda x: x['top'])['top'],
                bottom=max(matched_words, key=lambda x: x['bottom'])['bottom'],
                left=min(matched_words, key=lambda x: x['left'])['left'],
                right=max(matched_words, key=lambda x: x['right'])['right'],
                matched_words=matched_words)


def intersects(word: dict,
               left: [int, float],
               right: [int, float],
               top: [int, float],
               bottom: [int, float]) -> bool:
    """
    Given the word and coordinates of the area,
        returns true if word intersects area, otherwise false
    :param word: dictionary, containing coordinates,
        ocr_text and word_id_number of the word
    :param left: left coordinate
    :param right: right coordinate
    :param top: top coordinate
    :param bottom: bottom coordinate
    :return: bool
    """
    return (word['left'] < right and word['right'] > left
            and word['top'] < bottom and word['bottom'] > top)


def compute_intersection_area(word: dict,
                              left: [int, float],
                              right: [int, float],
                              top: [int, float],
                              bottom: [int, float]) -> [int, float]:
    """
    Given the word and coordinates of the area, computes area of intersection
    :param word: dictionary, containing coordinates,
        ocr_text and word_id_number of the word
    :param left: left coordinate
    :param right: right coordinate
    :param top: top coordinate
    :param bottom: bottom coordinate
    :return: area of intersection
    """
    left = max([left, word['left']])
    top = max([top, word['top']])
    right = min([right, word['right']])
    bottom = min([bottom, word['bottom']])
    return (right - left) * (bottom - top)


def detect_python_shell() -> str:
    """Detect what python shell is being used - Standard Interpreter,
        Jupyter Notebook, Interactive shell or other"""
    try:
        # noinspection PyUnresolvedReferences
        shell = get_ipython().__class__.__name__
        if shell == PythonShellEnum.zmq_interactive_shell.value:
            # Jupyter notebook or qtconsole
            return PythonShellEnum.zmq_interactive_shell.value
        elif shell == PythonShellEnum.terminal_interactive_shell.value:
            # Terminal running IPython
            return PythonShellEnum.terminal_interactive_shell.value
        else:
            # Other type (?)
            return PythonShellEnum.other_type_shell.value
    except NameError:
        # Probably standard Python interpreter
        return PythonShellEnum.standard_python_interpreter.value


def replace_object_ids_with_string(bson_obj):
    if isinstance(bson_obj, dict):
        for key, value in bson_obj.items():
            bson_obj[key] = replace_object_ids_with_string(value)
    if isinstance(bson_obj, list):
        for idx, el in enumerate(bson_obj):
            bson_obj[idx] = replace_object_ids_with_string(el)
    if isinstance(bson_obj, bson.ObjectId):
        return str(bson_obj)
    else:
        return bson_obj


@dataclass
class ConfusionMatrix:
    TP: int = 0
    TN: int = 0
    FP: int = 0
    FN: int = 0

    @property
    def f1(self) -> float:
        try:
            return self.TP / (self.TP + 0.5 * (self.FP + self.FN))
        except ZeroDivisionError:
            return 0

    @property
    def precision(self) -> float:
        try:
            return self.TP / (self.TP + self.FP)
        except ZeroDivisionError:
            return 0

    @property
    def recall(self) -> float:
        try:
            return self.TP / (self.TP + self.FN)
        except ZeroDivisionError:
            return 0

    @property
    def accuracy(self) -> float:
        try:
            return (self.TP + self.TN) / (
                    self.FP + self.FN + self.TP + self.TN)
        except ZeroDivisionError:
            return 0

    def to_dict(self) -> dict:
        return {
            'TP': self.TP,
            'TN': self.TN,
            'FP': self.FP,
            'FN': self.FN
        }

    def compute_metrics(self) -> dict:
        """ Given confusion matrix, computes f1 score, precision,
            recall and accuracy.
         :return: results in dict"""
        result = {
            'confusion matrix': self.to_dict(),
            'f1 score': self.f1,
            'precision': self.precision,
            'recall': self.recall,
            'accuracy': self.accuracy}
        return result

    def draw_cm(self, title: str = 'Confusion Matrix'):
        cf_matrix = [self.TP, self.FP, self.FN, self.TN]
        cf_matrix = np.asarray(cf_matrix).reshape(2, 2)
        group_names = ['True Positive', 'False Positive',
                       'False Negative', 'True Negative']
        group_counts = ["{0:0.0f}".format(value)
                        for value in cf_matrix.flatten()]
        group_percentages = [
            "{0:.2%}".format(value)
            for value in cf_matrix.flatten() / np.sum(cf_matrix)]
        labels = [
            f'{v1}\n{v2}\n{v3}'
            for v1, v2, v3 in zip(group_names,
                                  group_counts,
                                  group_percentages)]
        labels = np.asarray(labels).reshape(2, 2)
        import seaborn as sns
        import matplotlib.pyplot as plt

        plt.figure(figsize=(12, 7))
        plt.title(title, fontsize=20)
        sns.heatmap(
            cf_matrix,
            annot=labels,
            fmt='',
            xticklabels=[1, 0],
            yticklabels=[1, 0],
            cmap='Blues',
            annot_kws={"size": 17})
        plt.show()


def get_index_of_first_non_empty_list(list_of_lists):
    non_empty_idx = len(list_of_lists)
    for idx, line in reversed(list(enumerate(list_of_lists))):
        if line:
            return idx
    return non_empty_idx


def convert_tag_coords_to_percentages(tag, w, h) -> dict:
    return dict(left=tag.left * w / 100,
                right=tag.right * w / 100,
                top=tag.top * h / 100,
                bottom=tag.bottom * h / 100)


def cloud_interface_login(login_instance: Login) -> CloudInterface:
    """Logs in to cloud interface"""

    if login_instance.logged_in:
        ci_instance = CloudInterface(
            aws_access_key_id=login_instance.aws_access_key,
            aws_secret_access_key=login_instance.aws_secret_access_key,
            aws_session_token=login_instance.aws_session_token)
    else:
        ci_instance = CloudInterface()
    return ci_instance
