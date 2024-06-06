import json
import logging
import os
import re
from typing import Optional, List, Iterable, Union
import numpy as np

from pycognaize.file_storage import get_storage
from pycognaize.login import Login
from pycognaize.common.decorators import module_not_found
from pycognaize.common.utils import join_path

from pycognaize.common.enums import (
    StorageEnum,
    OCR_DATA_EXTENSION,
    IMG_EXTENSION
)
import pycognaize.common
from pycognaize.common.utils import (
    infer_rows_from_words,
    clean_ocr_data,
    find_first_word_coords,
    intersects,
    compute_intersection_area,
    stick_word_boxes,
    preview_img,
    image_string_to_array
)
from pycognaize.document.tag import ExtractionTag


class Page:
    """Representing a page of a document in pycognaize"""
    REGEX_NO_ALPHANUM_CHARS = re.compile(r'[^a-zA-Z\d)\[\](-.,]')

    def __init__(self, page_number: int,
                 document_id: str,
                 path: str,
                 image_height: int = None,
                 image_width: int = None
                 ):
        """

        :param page_number: The number of the page (1-based index)
        :param document_id: The unique id of the document
        :param path: Local or remote path to the document folder,
            which includes the image and ocr files
        :param image_width: Page image width
        :param image_height: Page image height
        """
        self._page_number = int(page_number)
        self._document_id = document_id
        login_instance = Login()

        if login_instance.logged_in:
            self._storage_config = {
                'aws_access_key_id': login_instance.aws_access_key,
                'aws_session_token': login_instance.aws_session_token,
                'aws_secret_access_key': login_instance.aws_secret_access_key
            }

        else:
            self._storage_config = None

        self._path = path
        self._ocr_raw = None
        self._ocr = None
        self._lines = None
        self._row_word_groups = None
        self._image_bytes = None
        self._image_arr = None
        self._image_height = image_height
        self._image_width = image_width

    @property
    def page_number(self):
        """Page number of page"""
        return self._page_number

    @property
    def path(self):
        """Path of the source document"""
        return self._path

    @property
    def doc_id(self):
        """Document id of the page"""
        return self._document_id

    @property
    def ocr(self) -> dict:
        """Formatted ocr of page"""
        if self._ocr is None:
            self._ocr = self.get_ocr_formatted()
        return self._ocr

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.page_number}>"

    def get_image(self) -> bytes:
        """Converts image of page in bytes"""

        if not self.path:
            raise ValueError('Path should be specified.')

        storage = get_storage(self.path, config=self._storage_config)

        uri = join_path(
            storage.is_s3_path(self.path),
            self.path,
            StorageEnum.image_folder.value,
            f"image_{self._page_number}.{IMG_EXTENSION}"
        )
        try:
            with storage.open(uri, 'rb') as f:
                image_bytes = f.read()
        except FileNotFoundError as e:
            logging.warning(
                f"Unable to get the image for page {self.page_number}: {e}")
            with open(os.path.join(
                    os.path.dirname(pycognaize.common.__file__),
                    'white_pixel.jpeg'), 'rb') as f:
                image_bytes = f.read()
        return image_bytes

    @property
    def image_bytes(self) -> bytes:
        """Image of page in bytes"""
        if self._image_bytes is None:
            self._image_bytes = self.get_image()
        return self._image_bytes

    @property
    def image_arr(self) -> np.ndarray:
        """Numpy array of the page image"""
        if self._image_arr is None:
            self._image_arr = image_string_to_array(self.image_bytes)
        return self._image_arr

    def get_page_data(self) -> None:
        """Data of the page"""
        if self.path is None:
            raise ValueError("No path defined for getting the images")

        storage = get_storage(self.path, config=self._storage_config)

        uri = join_path(
            storage.is_s3_path(self.path),
            self.path,
            StorageEnum.ocr_folder.value,
            f"page_{self._page_number}." f"{OCR_DATA_EXTENSION}"
        )
        try:
            with storage.open(uri, 'r') as f:
                # Using loads instead of load as a workaround for CI
                page_data = json.loads(f.read())
                self._image_height = int(page_data['image']['height'])
                self._image_width = int(page_data['image']['width'])

        except FileNotFoundError as e:
            logging.warning(
                f"Unable to get the json data for page "
                f"{self.page_number}: {e}")
            self._image_width = 1
            self._image_height = 1

    @property
    def image_height(self) -> int:
        """Height of the page image"""
        if self._image_height is None:
            self.get_page_data()

        return self._image_height

    @property
    def image_width(self) -> int:
        """Width of the page image"""
        if self._image_width is None:
            self.get_page_data()

        return self._image_width

    @property
    def ocr_raw(self) -> dict:
        if self._ocr_raw is None:
            self._ocr_raw = self.get_ocr()
        return self._ocr_raw

    def get_ocr(self) -> Optional[dict]:
        """OCR of the page"""
        if not self.path:
            raise ValueError("No path defined for getting the images")

        storage = get_storage(self.path, config=self._storage_config)

        uri = join_path(
            storage.is_s3_path(self.path),
            self.path, StorageEnum.ocr_folder.value,
            f"page_{self._page_number}."
            f"{OCR_DATA_EXTENSION}"
        )
        try:
            with storage.open(uri, 'r') as f:
                ocr_raw = json.loads(f.read())
                ocr_raw['page']['height'] = float(ocr_raw['page']['height'])
                ocr_raw['page']['width'] = float(ocr_raw['page']['width'])
                for word in ocr_raw['data']:
                    word['x'] = float(word['x'])
                    word['y'] = float(word['y'])
                    word['w'] = float(word['w'])
                    word['h'] = float(word['h'])
        except FileNotFoundError as e:
            logging.warning(
                f"Unable to get the ocr for page {self.page_number}: {e}")
            ocr_raw = {
                "page": {"number": self.page_number,
                         "width": 1, "height": 1},
                "image": {"width": 1, "height": 1},
                "data": []}
        return ocr_raw

    def get_ocr_formatted(self, stick_coords: bool = False,
                          return_tags: bool = False
                          ) -> Union[dict, List[ExtractionTag]]:
        """Dict of words, paragraphs each containing their tag data"""
        res = dict(words=[], paragraphs=[])
        res_words_tags = []
        ocr = self.ocr_raw
        if ocr is None:
            return res
        image_height = float(self.image_height)
        image_width = float(self.image_width)
        page_height = float(ocr['page']['height'])
        page_width = float(ocr['page']['width'])
        if image_width > image_height and page_width < page_height:
            page_height, page_width = page_width, page_height
        height_ratio = image_height / page_height
        width_ratio = image_width / page_width
        for n, i in enumerate(ocr['data']):
            if not i['value'].strip():
                continue
            word = dict(
                left=round(float(i['x']) * width_ratio),
                right=round((float(i['x']) + float(i['w'])) * width_ratio),
                top=round(float(i['y']) * height_ratio),
                bottom=round((float(i['y']) + float(i['h'])) * height_ratio),
                ocr_text=i['value'],
                word_id_number=n)
            if word['left'] >= word['right']:
                word['right'] = word['left'] + 1
            if word['top'] >= word['bottom']:
                word['bottom'] = word['top'] + 1
            res['words'].append(word)
        if stick_coords:
            stick_word_boxes(box_coord=res['words'],
                             img_bytes=self.get_image())
        if return_tags:
            for word in res['words']:
                res_words_tags.append(self.word_to_extraction_tag(word))
            return res_words_tags
        return res

    @property
    def lines(self) -> List[List[dict]]:
        """Detects lines of the page

        :return: list of lists of dicts,
            where each list represents a line,
            and each dict in that list is a word on that line,
            with its coordinates, ocr_text and word_id_number
        """
        if self._lines is None:
            self._lines = self._create_lines()
        return self._lines

    @property
    def ocr_tags(self) -> dict:
        """
        Makes the words extraction tags in the ocr data of pages.
        :return: dict of lists of tags, where each list represents
                 formatted OCR of a page,
                 and each tag in that list is the OCR data represented as
                 an Extraction tag, with its coordinates in the document.
        """
        ocr_dict = {}
        page_ocr = self.ocr
        for page, value in page_ocr.items():
            ocr_dict[page] = [self.word_to_extraction_tag(item) for
                              item in value]
        return ocr_dict

    @property
    def line_tags(self) -> list:
        """Makes the words extraction tags in the lines of pages
        :return: list of lists of tags,
            where each list represents a line,
            and each tag in that list is a word on that line
            represented as an Extraction tag, with its coordinates
            in the document
        """
        lines_list = []
        page_lines = self.lines
        for page_line in page_lines:
            page_line_list = []
            for word_of_line in page_line:
                page_line_list.append(
                    self.word_to_extraction_tag(word_of_line))
            lines_list.append(page_line_list)
        return lines_list

    def _create_lines(
            self,
            return_tags: bool = False
    ) -> List[List[Union[dict, ExtractionTag]]]:
        """Detects lines of the page

        :param return_tags: if False returns list of lists of dicts,
            where each list represents a line, and each dict
        in that list is a word on that line. If True,
            returns list of lists of ExtractionTags, where each word of line is
        converted to tag
        """
        words_tags = []
        rows_inf, self._row_word_groups = infer_rows_from_words(
            box=dict(left=0, top=0, right=1, bottom=1),
            class_ocr_data=clean_ocr_data(self.ocr)['words'])
        rows: list = [
            int(round(abs(rows_inf[row_n]['top'] + row['bottom']) / 2))
            for row_n, row in enumerate(rows_inf)]
        bottom_coord = [
            int(max(rows_inf, key=lambda d: d['bottom'])['bottom'])
        ] if rows_inf else []

        self._row_word_groups: list = [
            i for _, i in sorted(
                zip(rows + bottom_coord, self._row_word_groups),
                key=lambda pair: pair[0])]
        rows.sort()
        temp_rows = []
        for i, (row, group) in enumerate(zip(rows + bottom_coord,
                                             self._row_word_groups)):
            if row in temp_rows:
                rows[i] = None
                orig_idx = rows.index(row)
                self._row_word_groups[orig_idx] += self._row_word_groups[i]
                self._row_word_groups[i] = None
            temp_rows.append(row)
        self._row_word_groups = [i for i in self._row_word_groups if i]
        self._row_word_groups = [
            sorted(i, key=lambda x: (x['left'], x['right']))
            for i in self._row_word_groups]
        if return_tags:
            for line in self._row_word_groups:
                new_line_tags = []
                for word in line:
                    new_line_tags.append(self.word_to_extraction_tag(word))
                words_tags.append(new_line_tags)
            return words_tags
        return self._row_word_groups

    def search_text(self, text: str,
                    case_sensitive=False,
                    sort: bool = False,
                    clean: bool = True,
                    area: dict = None,
                    cleanup_regex=REGEX_NO_ALPHANUM_CHARS,
                    return_tags: bool = False) -> list:
        """
        Detects the coordinates of the `text` in ocr of the page
            If the `text` is not found in the page return None

        :param str text:
        :param case_sensitive: If True, the search will be case-sensitive
        :param sort: If True,
            ocr_data will be ordered by `word_id_number` key before searching
        :param clean: If true,
            disregard all non-alphanumeric character from the search
        :param area: If a dict with coordinates (pixels) is given
            only search for text in specified area
        :param re._pattern_type cleanup_regex: Optional.
            Provide the regex for cleanup to be used
            (has effect only if `clean=True`)
        :param return_tags: if True, the words in found text
            are converted into tags.
        :return: List of dictionaries with word coordinates
            (keys: `left`, `right`, `top`, `bottom`, `matched_words`.
            `matched_words` includes the original word coordinate
                data for the matched words)
        :rtype: list
        """

        all_matches = []
        all_matches_tags = []
        if area:
            ocr_data = self.extract_area_words(**area)
        else:
            ocr_data = [word for line in self.lines for word in line]

        while True:
            final_coords = find_first_word_coords(
                text=text, ocr_data=ocr_data,
                case_sensitive=case_sensitive,
                sort=sort, clean=clean,
                cleanup_regex=cleanup_regex)
            if final_coords is None:
                break
            all_matches.append(final_coords)
            final_coord_word_ids = [
                i['word_id_number'] for i in final_coords['matched_words']]
            ocr_data = [word for word in ocr_data
                        if word['word_id_number'] not in final_coord_word_ids]
        if return_tags:
            for match in all_matches:
                matched_words_tags = []
                for word in match['matched_words']:
                    matched_words_tags.append(
                        self.word_to_extraction_tag(word))
                all_matches_tags.append(matched_words_tags)
            return all_matches_tags
        return all_matches

    @staticmethod
    def _validate_box_coordinates(left: [int, float],
                                  right: [int, float],
                                  top: [int, float],
                                  bottom: [int, float], ) -> None:
        """Validate coordinates of a box (with the origin on top-left corner)

        :param left: Left border of the box
        :param right: Right border of the box
        :param top: Top border of the box
        :param bottom: Bottom border of the box
        :return: Raises error if validation fails, otherwise does not return
            anything
        """

        if left < 0 or right < 0 or top < 0 or bottom < 0:
            raise ValueError('Coordinates need to be positive')
        if left > right:
            raise ValueError(
                f"Left ({left}) cannot be bigger than right ({right})")
        if top > bottom:
            raise ValueError(
                f"Top ({top}) cannot be bigger than bottom ({bottom})")
        if left == right:
            raise ValueError(
                f"Left ({left}) cannot be equal to right ({right})")
        if top == bottom:
            raise ValueError(
                f"Top ({top}) cannot be equal to bottom ({bottom})")

    @staticmethod
    def extract_words_in_tag_area(area_tag,
                                  return_tags: bool = False,
                                  line_by_line: bool = True) -> Optional[list]:
        page = area_tag.page
        left = area_tag.left * page.image_width / 100
        right = area_tag.right * page.image_width / 100
        top = area_tag.top * page.image_height / 100
        bottom = area_tag.bottom * page.image_height / 100
        return page.extract_area_words(left=left,
                                       top=top,
                                       right=right,
                                       bottom=bottom,
                                       return_tags=return_tags,
                                       line_by_line=line_by_line)

    def extract_area_words(self, left: [int, float],
                           right: [int, float],
                           top: [int, float],
                           bottom: [int, float],
                           threshold: float = 0.5,
                           return_tags: bool = False,
                           line_by_line: bool = False,
                           ) -> Optional[list]:
        """Finds the words on the page which are included in the area
            resulted from given coordinates.

        :param threshold: Threshold value as a fraction
            (value between 0 and 1), default value is 0.5
        :param left: left coordinate
        :param right: right coordinate
        :param top: top coordinate
        :param bottom: bottom coordinate
        :param return_tags: if True, returns tags of the words
            embedded in given area
        :param line_by_line: if True, returns a list of lists,
            where each nested list is a line
        :return: list of words, each element in the list is dictionary
            representing the coordinates, ocr_text of word, and word_id_number
        """
        if not 0 <= threshold <= 1:
            raise ValueError('Value of threshold must be between 0 and 1')
        self._validate_box_coordinates(
            left=left, right=right, top=top, bottom=bottom)
        word_list = []
        for line in self.lines:
            line_list = []
            for word in line:
                if intersects(word,
                              left=left,
                              right=right,
                              top=top,
                              bottom=bottom):
                    intersect_area = compute_intersection_area(
                        word,
                        left=left,
                        right=right,
                        top=top,
                        bottom=bottom)
                    word_area = (word['right'] - word['left']
                                 ) * (word['bottom'] - word['top'])
                    ratio = float(intersect_area / word_area)
                    if ratio > threshold:
                        if return_tags:
                            line_list.append(
                                self.word_to_extraction_tag(word))
                        else:
                            line_list.append(word)
            if line_by_line:
                word_list.append(line_list)
            else:
                word_list.extend(line_list)
        return word_list

    @staticmethod
    @module_not_found()
    def draw_rectangle(img: np.ndarray, left: int,
                       top: int, right: int, bottom: int) -> np.ndarray:
        """Adds a rectangle outline on the image"""
        import cv2
        return cv2.rectangle(img=img,
                             pt1=(int(left), int(top)),
                             pt2=(int(right), int(bottom)),
                             color=(0, 250, 0),
                             thickness=2)

    def draw_ocr_boxes(self, img: Optional[np.ndarray] = None) -> np.ndarray:
        """Draw boxes where text was detected and return the modified
            numpy array image

        :param img: Input image as numpy array.
            If not provided, use a copy of the instance image
        :return: numpy array of the image with word boxes
        """
        if img is None:
            img = self.image_arr.copy()
        for word in self.ocr['words']:
            img = self.draw_rectangle(img=img,
                                      left=word['left'],
                                      right=word['right'],
                                      top=word['top'],
                                      bottom=word['bottom'])

        return img

    @module_not_found()
    def draw_ocr_text(self, img: Optional[np.ndarray] = None) -> np.ndarray:
        """
        Insert corresponding OCR text above all OCR-ed words and
            return the modified numpy array image

        :param img: Input image as numpy array.
            If not provided, use a copy of the instance image
        :return: numpy array of the image with words
        """
        import cv2

        if img is None:
            img = self.image_arr.copy()
        for word in self.ocr['words']:
            img = cv2.putText(img=img, text=word['ocr_text'],
                              org=(word['left'], word['top'] - 1),
                              fontFace=cv2.FONT_HERSHEY_PLAIN,
                              fontScale=1.0, color=50, thickness=1)
        return img

    @module_not_found()
    def draw(self, fields: Optional[Iterable] = None,
             draw_ocr_boxes: bool = True,
             draw_ocr_text: bool = True,
             preview: bool = True,
             save: Optional[str] = None,
             draw_on_image: bool = False,
             size: int = 1000) -> np.ndarray:
        """
        Draw the fields and optionally draw the page image

        :param fields: List of Fields to draw
        :param draw_ocr_boxes: Whether to draw ocr boxes
        :param draw_ocr_text: Whether to draw ocr text
        :param preview: If True, show the image
        :param save: If True, the image will be saved to the given full path
        :param draw_on_image: If True, draw Tags on image instead of page
        :param size: Size of the preview image
        """
        import cv2
        if fields is None:
            fields = []
        img = self.image_arr.copy()
        if draw_ocr_boxes:
            img = self.draw_ocr_boxes(img=img)
        if draw_ocr_text:
            img = self.draw_ocr_text(img=img)
        if size <= 0:
            raise ValueError(
                f"`size` argument must have a positive integer value,"
                f" got: {size}")
        w = self.image_width
        h = self.image_height
        for field in fields:
            for tag in field.tags:
                if self.page_number != tag.page.page_number:
                    continue
                left = tag.left * w / 100
                right = tag.right * w / 100
                top = tag.top * h / 100
                bottom = tag.bottom * h / 100
                img = self.draw_rectangle(img,
                                          left=left,
                                          top=top,
                                          right=right,
                                          bottom=bottom)
        if preview:
            preview_img(img, size=size)
        if save:
            cv2.imwrite(filename=save, img=img)
        return img

    def free_form_text(self) -> str:
        """Return a text string from the ocr dictionary"""
        if self._row_word_groups is None:
            self._create_lines()
        final_text = '\n'.join([' '.join([word['ocr_text'] for word in row])
                                for row in self._row_word_groups])
        return final_text

    def word_to_extraction_tag(self, word: dict) -> ExtractionTag:
        """ Construct ExtractionTag object from word

        :type word: dict with left, right, top, bottom coordinates,
            ocr_text and word_id_number"""
        return ExtractionTag(left=word['left'] / self.image_width * 100,
                             right=word['right'] / self.image_width * 100,
                             top=word['top'] / self.image_height * 100,
                             bottom=word['bottom'] / self.image_height * 100,
                             page=self,
                             raw_value=word['ocr_text'],
                             raw_ocr_value=word['ocr_text'])


def create_dummy_page(page_n: int = 1, path: str = '/DUMMY/PATH'):
    """Used in test classes"""
    return Page(page_number=page_n, document_id='DUMMY_ID', path=path)
