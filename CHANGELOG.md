# Changelog

## [1.4]

## [1.4.41] - 2024-03-25
- Improve `Snapshot.download`
  - Download snapshot without login required

## [1.4.40] - 2024-03-6
- Improve `Document.fetch_document`
  - Add option to provide token and api url as parameters
  - Raise if env variables are missing
  - Raise if response is invalid
  - Handle trailing forward slashes in url
- Fix `Page.draw`

## [1.4.39] - 2024-02-27
- Handle tables in `Document.get_layout_text`

## [1.4.38] - 2024-02-25
- Add `Document.get_layout_text` method

### [1.4.37] - 2024-02-23
- Add `Genie` for easy model testing

### [1.4.36] - 2024-02-21
- Handle pandas warnings and 1.2.0 compatibility issues.
- Handle M series Mac incompatibility issues.
- Warn for missing page image/ocr information.
- Add `pyarrow` as a requirement

### [1.4.35] - 2024-02-21
- Optimize `pycognaize.common.utils.img_to_black_and_white`
- Test coverage 85%

### [1.4.34] - 2024-01-23
- Fix create_lines function in Page class
- Update docs/requirements.txt
- Update python_versions.svg

### [1.4.33] - 2024-01-16
- Remove support for python 3.8 and lower. Add support for 3.10, 3.11 and 3.12
- Use `map` instead of `applymap` in `DataFrame` objects

### [1.4.32] - 2024-01-10
- Fix load_page_ocr and load_page_images

### [1.4.31] - 2023-12-04
- Add `classes` property to fields

### [1.4.30] - 2023-11-30
- Remove `cloudstorageio` from the SDK

### [1.4.29] - 2023-11-06
- Changes os.path.join for s3 paths

### [1.4.28] - 2023-10-25
- Add support for scale output

### [1.4.27] - 2023-09-27
- Add support for s3 path resolution in Windows

### [1.4.26] - 2023-09-25k
- Add `exclude_html` to snapshot download
- Add `include` option to snapshot downloader

### [1.4.25] - 2023-09-13
- Add unit test for `span_field.py`

### [1.4.24] - 2023-09-13
- Create snapshot downloader class

### [1.4.23] - 2023-08-17
- Add tests for exclude options
- Add tests for cloudstorageio hooks usage
- Update to cloudstorageio version 1.2.14

### [1.4.22] - 2023-08-16
- Add new method for document fetching

### [1.4.21rc1] - 2023-08-08
- Use new method from cloudstorageio for big snapshot download

### [1.4.20] - 2023-07-30
- Add replacing text-span datatype with text_span in `from_dict` input_fields of Document object

### [1.4.19] - 2023-07-30
- Update `_to_dict` and `construct_from_raw` functions in `SpanField` class to set value when field does not have tag

### [1.4.18] - 2023-07-28
- Update  `_line_values` attribute in `SpanField` class in order to return sentences per lines

### [1.4.17] - 2023-07-19
- Update `__add__` function in `ExtractionTag` class in order to include the text between the two `BoxTag` objects selected

### [1.4.16] - 2023-07-14
- Add `scale` property to `NumericField` class

### [1.4.15] - 2023-07-12
- `NumericField.value` will return the calculated value if no field or tag values are available

### [1.4.14] - 2023-07-11
- Add exclude options for Snapshot download

### [1.4.13] - 2023-07-10
- Add calculated values to `NumericField`

### [1.4.12] - 2023-06-30
- Add missing function to `CloudService`

### [1.4.11] - 2023-06-28
- Ignore empty table tags in `langchain_loader.py`

### [1.4.10] - 2023-06-28
- Separate LangchainLoader text blocks with new lines

### [1.4.10] - 2023-07-13
- Add `to_text()` functionality to `Document` class that utilizes inputs from 
  `PageLayout` model to create the text version of the document

### [1.4.9] - 2023-06-27
- Add `to_string()` functionality to `table_tags`
- Add langchain_loader util to convert Pycognaize `Document` objects to Langchain `Document` objects

### [1.4.8] - 2023-06-24
- Add field value and tag value to numeric field

### [1.4.7] - 2023-06-15
- Add `ocr_tags()` and `line_tags()` to `Page`

### [1.4.6] - 2023-06-27
- Add replace_nans_with_empty_html_tags functionality in HTMLTableTag build df

### [1.4.5] - 2023-06-12
- Add re-login when AWS token is expired

### [1.4.4] - 2023-05-31
- Add `anytree` to setup-requires in `setup.cfg`

### [1.4.3] - 2023-05-31
- Fix handling of section field with no tags

### [1.4.2] - 2023-05-30
- Fix handling of section field value when field does not have tags

### [1.4.1] - 2023-05-29
- Add section field and section tag functionality

### [1.4.0] - 2023-05-25
- Add classification labels functionality to ``Field`` objects

## [1.3]

### [1.3.14] - 2023-05-10
- Add LinkField object
- Add returning group name in to_dict functionality of Field object 

### [1.3.13] - 2023-05-01
- Add exclude folders option for ``lisdir`` in ``html_info``
- Update version cloudstorageio >= 1.2.8
### [1.3.12] - 2023-05-01
- Rename HTMLTag to HTMLTagABC
- Rename TDTag to HTMLTag
- Handle out of table tags in XBRL

### [1.3.11] - 2023-04-28
- Add interface to create directory summary hashes
- Add automatic snapshot hash creation for ``snapshot.download``

### [1.3.10] - 2023-03-31
- Add login command and code for submit to model registry

### [1.3.9] - 2023-03-30
- Refactor HTML._validate_path() to include try-except block

### [1.3.8] - 2023-03-28
- Improve html file path validation by adding a new check
in HTML._validate_path()

### [1.3.7] - 2023-03-24
- Match (xbrl) using xpath and indices in matches function of `model.py`

### [1.3.6] - 2023-03-19
- Add functionality to run Model().execute_eval given
  the ground truth document id

### [1.3.5] - 2023-03-11
- Make Confidence key lowercase.

### [1.3.4] - 2023-03-09
- Rename classConfidence key to Confidence in enums.

### [1.3.3] - 2023-03-07
- Check that the sum of confidence values is close to 1 instead of exactly 1.

### [1.3.2] - 2023-02-21
- Add is_xbrl attribute in document, to identify if document is XBRL or not
- Modify assign indices functionality to handle XBRL tables
- Modify Model.matches() to also match with HTMLTags
- Add HTML._validate_path() to get valid path of `source.html` file
- Fix reading html file from S3
- Add tag_id attribute to HTMLTag

### [1.3.1] - 2023-02-14
- Update install requirements in `setup.cfg`
- Rename environment variable `COGNAIZE_HOST` to `API_HOST`
- Raise error when trying to log in without `API_HOST` environment variable
- Add documentation and make cosmetic changes in `login.py`

### [1.3.0] - 2023-02-10
- Add XBRL support
- Add `spacy` to `model-requirements.txt`
- Add `bs4` to `requirements.txt`

## [1.2]

### [1.2.9] - 2023-01-17
- Add class confidence functionality to tag objects

### [1.2.8] - 2023-01-09
- Update Numeric parser to handle float numbers with three or more
  decimal numbers
- Add "-" character handler in numeric parser
- Change all occurrences of 'cognaize' to 'Cognaize'

### [1.2.7] - 2022-12-22
- Change PyMuPDF version to support M1

### [1.2.6] - 2022-12-06
- Update numeric parser to better handle decimal numbers

### [1.2.5] - 2022-11-28
- Read page image height/width from document.json
- Field raw value bug fix

### [1.2.4] - 2022-11-28
- Field object raw_value bug fix

### [1.2.3] - 2022-11-16
- Field object raw_value bug fix

### [1.2.3] - 2022-11-16
- Field object raw_value contains fields value

### [1.2.2] - 2022-11-11
- Add HTTP request timeout for genie model run

### [1.2.1] - 2022-11-08
- Add functionality for grouping fields by key


### [1.2.0] - 2022-10-11
- Modify assign indices functionality to correctly index tables located side by side

## [1.1]
### [1.1.4] - 2022-10-06
- Add snapshot download to specified directory
  functionality
- Add Page Section tag and field functionalities

### [1.1.3] - 2022-10-05
- Add login functionality to pycognaize

### [1.1.2] - 2022-09-12
- group_by_field returns list of fields with group_key
- Add minor improvement for NumericParser
- Tied fields now only return unique fields

### [1.1.1] - 2022-09-05
- Fix field grouping with non-existing key
- Add field grouping with given ``Field`` object

### [1.1.0] - 2022-08-25
- Added multiprocessing download of images and 
  ocr data

## [1.0]
### [1.0.3] - 2022-08-23
- Change get_tied_fields, get_tied_tags, 
  get_first_tied_field, get_first_tied_tag methods to return also python names
- Fix get_first_tied_field_value and get_first_tied_tag_value methods to work 
  properly after changes

### [1.0.2] - 2022-08-23
- Fix get_tied_tags method

### [1.0.1] - 2022-08-22
- Fix get_tied_fields method

### [1.0.0] - 2022-08-15
- Update signature of base Field class
- Update constructor of SpanField class


## [0.3]

### [0.3.66] - 2022-08-15
- Add tied_field and tied_tag functionality to document


### [0.3.65] - 2022-08-10
- Enhance numeric parser to handle strings like 0.01, add unittest

### [0.3.64] - 2022-08-09
- Add span field and span tag 

### [0.3.63] - 2022-08-04
- Add grouping functionality for input and
  output fields of document

### [0.3.62] - 2022-07-20
- Update GitHub workflow to publish documentation on release

### [0.3.61] - 2022-07-13
- Read image width and height from document.json instead of loading actual images for that

### [0.3.60] - 2022-07-03
- Fix seaborn issue

### [0.3.59] - 2022-07-03
- Remove opencv and seaborn from setup.cfg requirements

### [0.3.58] - 2022-06-20
- Deprecation decorator chooses version automatically

### [0.3.57] - 2022-06-20
- Fix _post_response_eval() method of Model

### [0.3.56] - 2022-06-20
- Remove OpenCV from main requirements (now in model-requirements)
- Add deprecation and module not found warning decorators
- Get rid of opencv dependencies
- Update GitHub workflow to use model-requirements

### [0.3.55] - 2022-06-18
- Set logging level to debug for missing OCR or image files

### [0.3.54] - 2022-06-18
- Added for running workflows

### [0.3.53] - 2022-06-18
- Exclude tests from the package distro
- Include white pixel in the distro
- Remove MANIFEST.in
- Add virtualenv to dev-requirements.txt
- Publish in main pypi repository when running setup.sh

### [0.3.52] - 2022-06-15
- Integrate evaluation driver

### [0.3.51] - 2022-06-11
- Fix get_matching_table_cells_for_tag

### [0.3.50] - 2022-06-10
- Update documentation (logo, badges, etc.)) 

### [0.3.49] - 2022-06-06
- Add names to GitHub actions 

### [0.3.48] - 2022-06-06
- Remove redundant information from README.md 

### [0.3.47] - 2022-06-06
- Update setup.sh to create wheel and upload to pypi
- Setup.sh performs doctests as part of the build process

### [0.3.46] - 2022-06-03
- Added tutorial about working with tags, and PDF
- Made updates to documentation

### [0.3.45] - 2022-06-03
- Obfuscate data in pycognaize tests
- Update names in GitHub actions

### [0.3.44] - 2022-05-31
- Create tutorial about leveraging tables in cognaize SDK
- Add logo and favicon to documentation
- Add supported python version badge to readme
- Add logo to readme


### [0.3.43] - 2022-05-28
- Remove outdated modules (ocr.py and recipe.py)
- Remove Dockerfile and outdated build scripts
- Add dev-requirements.txt, update badges

### [0.3.42] - 2022-05-27
- Add badge generating script to show in Readme
- Update Readme to show badge, documentation and tutorials
- Add sphinx doctests to GitHub actions

### [0.3.41] - 2022-05-25
- Updated homepage of the documentation
- Added versioning to RTD. (NOT FINAL. CHECKS VERSIONS FROM GIT WHICH…)
- Added blank tutorial pages
- Updated sidebar toc tree structure 
- Added doctests to quick tutorial
- dded sphinx.ext.doctest
- Updated create_docs to include new `_autosummary` directory and create doctest

### [0.3.40] - 2022-05-20
- Fix styling and refactor in order to pass flake8 checks

### [0.3.39] - 2022-05-20
- Add backquotes in changelog 
- Group changelog entries
- Changelog ordered from the latest version to first
- Add script to deploy the docs
- Add `quick_tutorial.rst` file
- Update index.rst to include links to general sections
- Add myst-parser to docs `requirements.txt`
- Change Markdown parser to myst-parser
- Add `quickstart.rst`
- Add reading `.md` files for changelog
- Separate `installation.rst`

### [0.3.38] - 2022-05-19
- Configure sphinx for generating proper API reference
- Create general docs outline, add generated `autosummary` rst files in ignore files

### [0.3.37] - 2022-05-16
- Added docstrings and type hints to modules

### [0.3.36] - 2022-05-16
- Rename the package to pycognaize

### [0.3.35] - 2022-05-13
- Added GitHub workflows for linting and testing
- Changed docstrings in snapshot.py and lazy_dict.py

### [0.3.34] - 2022-05-12
- Fix all tests

### [0.3.33] - 2022-05-11
- Fix requirements and setup.sh

### [0.3.32] - 2022-04-11
- Add opencv-python-headless==4.0.1.23 in requirements for avoiding ImportError: cannot import name
  '_registerMatType' (only for usage in table_detection)

### [0.3.31] - 2022-04-11
- Bring back using opencv in bytes_to_array, string_to_array, img_to_black_and_white for 
  stick_word_boxes functionality (only for usage in table_detection)

### [0.3.30] - 2022-04-11
- Change TableTag to take cell data, not use table dividers
- Add tests corresponding to changed TableTag 

### [0.3.29.a0] - 2022-04-06
- Fix in get_table_title to give not first 8 rows of page while 8 rows above table

### [0.3.29] - 2022-04-06
- Add numeric parser in common

### [0.3.28] - 2022-03-04
- Remove opencv from requirements, add some utils

### [0.3.27] - 2022-02-10
- Set requirement pymupdf<=1.19.4 in setup.cfg

### [0.3.26] - 2022-02-04
- Fix pymupdf conflicting version issue(1.19.4)

### [0.3.25] - 2021-11-13
- Add raw_value to TextField

### [0.3.24] - 2021-11-13
- call build_df in `TableTag.__init__` to skip corrupted table tags

### [0.3.23] - 2021-11-13
- call TableTag._build_df in init so that corrupt table tags are not created on snapshot read

### [0.3.22] - 2021-11-13
- Implement `TableTag.__getitem__`
- Define TableTag.raw_df
- Cache property TableTag.df on access
- Do not build_df in `TableTag.__init__`

### [0.3.21] - 2021-11-12
- Fix Document.get_table_cell_overlap (look both in input and output fields, fix the iou page check issue)

### [0.3.20] - 2021-11-10
- Add Document.metadata attribute

### [0.3.19] - 2021-11-10
- Remove assertion tests for fields and tags where applicable
- Set all warnings to debug level in tag.py
- Do not fail on invalid tag json data, but skip the tag (all logs are on debug level)

### [0.3.18] - 2021-11-02
- Enforce utf-8 encoding when reading document.json locally

### [0.3.17] - 2021-10-29
- Add Document.to_pdf() feature
- Add annotate_pdf() function in document.py
- Add Unittests for Document.to_pdf()
- Fix requirement (fitz to pymupdf)

### [0.3.16] - 2021-10-22
- Make evaluate method of Model class abstract

### [0.3.15] - 2021-10-21
- Add handling repeating field and group cases in evaluate functionality of model

### [0.3.14] - 2021-10-20
- Rename Model.predict_based_on abstract method to `Model.copy` method
- Remove predict_based_on method from test_model ExampleModel class

### [0.3.13] - 2021-10-12
- Add Model.execute_based_on_match, Model.predict_based_on, and Model._post_response methods
- Add separate `Index._store` method
- Add `response_to_dict` method to index class for transformation of the response to needed format - {doc_id: encoding}
- Update `execute_based_on_match` method in model class to get document object for matched base document"
- Remove INDEX from Model
- Change Index to create fields for matched document ID and confidence

### [0.3.12] - 2021-10-11
- Remove ssl verification from GET/POST requests

### [0.3.11] - 2021-10-04
- Add tests for pycognaize.common.utils.intersects

### [0.3.10] - 2021-10-03
- Fix pycognaize.common.utils.intersects

### [0.3.9a24] - 2021-09-06
- Fixed the issue of local running the tests

### [0.3.9a23] - 2021-09-01
- `LаzyDict.__getitem__` returns None, if reading the document fails
- Define the return value type 

### [0.3.9a22] - 2021-08-31
- Add Index class for document-index abstraction
- Add unittests for Index (93% coverage)
  
### [0.3.9a21] - 2021-08-31
- add return_tags functionality in get_ocr_formatted, _create_lines,
search_text, extract_area_words of Page
- add image_bytes property
- remove assigning results of get_image() ang get_ocr() to hidden attributes

### [0.3.9a20] - 2021-08-26
- Added test for execute_genie_v2

### [0.3.9a19] - 2021-08-24
- sorted `self._ids` for lazy_dict.py in line 18 

### [0.3.9a18] - 2021-08-24
- Added test_lazy_dict.py

### [0.3.9a17] - 2021-08-24
- Added tests for document.ocr.py.

### [0.3.9a16] - 2021-08-20
- Added missing tests for table_tag.

### [0.3.9a15] - 2021-08-20
- Added tests for draw. Corrected an issue in page.py.

### [0.3.9a14] - 2021-08-20
- Corrected the issue in test_utils.py. Changed the writen code that relies on the ordering of os.listdir.

### [0.3.9a13] - 2021-08-20
- Add tests for Page (90% coverage)

### [0.3.9a12] - 2021-08-20
- Correct tag Euclidean distance method by changing the private variables into public

### [0.3.9a11] - 2021-08-18
- Added missing test methods for Tag, utils, Cell, AreaField, Document, and Field (89% coverage). 

### [0.3.9a10] - 2021-08-16
- Fix tag Euclidean distance method

### [0.3.9a9] - 2021-08-13
- Added area argument to page.search_text() to specify scope

### [0.3.9a8] - 2021-08-13
- Add image_arr, image_height, image_width, ocr_raw properties

### [0.3.9a7] - 2021-08-11
- Added getter and setter for field group_key

### [0.3.9a6] - 2021-08-10
- Add an option for image size in page.draw() and set a larger size as default
- Add OS specific behavior for preview_img
- Remove unnecessary exceptions

### [0.3.9a5] - 2021-08-10
- Add tag euclidean distance method

### [0.3.9a4] - 2021-08-09
- Add evaluation and unittests including content only metrics
- Add ConfusionMatrix and heatmap drawing function

### [0.3.9a3] - 2021-08-08
- Add EnvConfigEnum.SNAPSHOT_ID
- get snapshot_path using snapshot_id
- refactor LOCAL_SNAPSHOT_PATH to SNAPSHOT_PATH
- Update snapshot.py tests

### [0.3.9a2] - 2021-08-08
- page.search_text() did not find certain substrings present in page.free_form_text(). Found two reasons for this behavior.
  * The list of ocr-data passed to `find_frirst_word_coord` was page.ocr('words'), which has the entries sorted by word_id. This makes the sort flag of the function obsolete, and second it leads to cases in which the coordinates of sub-strings from page.free_form_text() cannot be found using the function the order of the words in page.free_form_text() is unrelated to word_id. 
    For example a sub-string of page.free_form_text() might be “brown fox” with the word_id of “brown” being equal to 3 and “fox” being equal to 8. In this case find_first_word_coords would not find the coordinates, as it would break the for-loop as the word with word_id 4 is not “fox”.
    This behavior was fixed by passing the ocr data in the same order as in page.free_form_text(), still giving the option to sort it by word_id using the sort-flag.
  * Inside the find_first_word_coord function the words of the sub-string were always put through a cleanup regex before being compared to the ocr_text (which was not cleaned up if the clean-flag was set to false). This leads to cases in which a sub-string such as “Phone: 12345” would not be found as “Phone:” would be cleaned up to “Phone”. 
    This was fixed by either putting the words of the sub-string as well as the values for ocr_text through a cleanup regex or neither of them, depending on the clean-flag.

### [0.3.9a1] - 2021-08-06
- Implement and/or update all tests for 0.3.7 versions (ALL TESTS PASS)
- Optimize imports

### [0.3.8a5] - 2021-08-03 (0.3.8 versions do not include the changes in 0.3.7 versions)
- Fix page.search_text()

### [0.3.8a4] - 2021-07-18 (0.3.8 versions do not include the changes in 0.3.7 versions)
- Add `Model.evaluate`
- Fix changelog wrong years (Incorrect 2020 years changed to 2021)

### [0.3.8a3] - 2021-06-24 (0.3.8 versions do not include the changes in 0.3.7 versions)
- Fix table divider offsets and interruption coordinates (FIXES THE BUG FROM 0.3.8a2)

### [0.3.8a2] - 2021-06-24 (0.3.8 versions do not include the changes in 0.3.7 versions)
- Fix table divider offsets and interruption coordinates (BUGGED VERSION)

### [0.3.8a1] - 2021-05-23 (0.3.8 versions do not include the changes in 0.3.7 versions)
- Fix `Tag.intersects` method

### [0.3.7a9] - 2021-07-07
- AreaField will raise a warning if the input value field is not a string and set it to empty string (if the field has no tags)

### [0.3.7a8] - 2021-05-30
- Fix `AreaField.value`

### [0.3.7a7] - 2021-05-26
- Fix get item in lazy_dict (required path)

### [0.3.7a6] - 2021-05-23
- Fix `Tag.intersects` method

### [0.3.7a5] - 2021-05-13
- Fix NaN issue in execute_genie_v2 post request json

### [0.3.7a4] - 2021-05-10
- Fix table cell value population issue

### [0.3.7a3] - 2021-05-09
- If page image or ocr files cannot be found, use an empty ocr/ 1 white pixel image instead

### [0.3.7a2] - 2021-05-08
- Add execute_genie_v2 for executing genie with airflow

### [0.3.7a1] - 2021-05-08
- Page object uses absolute path and allows lazy-loading from cloud (all tests pass)
- Adjust all filename conventions to work with original image/ocr storage name conventions

### [0.3.6] - 2021-03-29
- Adjust tests to count for the Range margin (all tests pass)

### [0.3.6a4] - 2021-03-05
- Modify the margin in Range.to_dict, set margin to 0.15

### [0.3.6a3] - 2021-03-05
- Add margin to table cells in TableTag._build_cell
- Fix ordering information in digester
- Fix typing annotation for OrderedDict output
- Change document.x and document.y into OrderedDict, use global ordering in digester

### [0.3.6a2] - 2021-02-24
- Add tests for Tag/ExtractionTag (coverage 87%)

### [0.3.6a1] - 2021-02-24
- Fox group_key typing annotation in Field objects

### [0.3.5] - 2021-02-23
- Store pdf in the snapshot

### [0.3.4] - 2021-02-22
- Add group_key optional argument to Field objects

### [0.3.3] - 2021-02-16
- All tests pass (84% coverage)
- Snapshot creator with threading
- Use mongomock for DB tests

### [0.3.2] - 2021-02-09
- Update tests for storage

### [0.3.1a4] - 2021-02-03
- Add threading to `SnaphotBuilder`

### [0.3.1a3] - 2021-02-02
- Fix `test_digestor.py` to work with the correct document bson file
- All tests pass (82% coverage)

### [0.3.1a2] - 2021-02-02
- Set DB.find call arguments no_cursor_timeout=True, batch_size=10 in SnapshotBuilder in order to avoid CursorNotFound timeout errors

### [0.3.1a1] - 2021-01-29
- Add lines, search_text, extract_area_words methods to Page
- Add unittests for lines, search_text and extract_area_words methods
- Add infer_rows_from_words, clean_ocr_data, find_first_word_coords, intersects, compute_intersection_area methods in utils.py

### [0.3.1a0] - 2021-01-28
- Add unittest for Document.from_dict
- Optimize digester output_fields lookup
- Add stick_coords option to Page.get_ocr_formatted
- Add opencv requirement

### [0.3.0b20] - 2021-01-16
- Assign document in `execute_genie` when calling `model.predict`

### [0.3.0b19] - 2021-01-12
- Assigning recipe output fields in digester for better performance

### [0.3.0b18] - 2021-01-06
- Update digester to set id-s of the original fields from the blueprint 
- Change `document.tag` imports to relative

### [0.3.0b17] - 2021-01-03
- Model.predict in Model.execute_genie uses positional arguments

### [0.3.0b16] - 2021-01-03
- Load LazyDocumentDicts as bson
- Make sure page numbers are integers

### [0.3.0b15] - 2021-01-03
- Fix SnapshotBuilder.save_doc_json_to_snapshot document_id key

### [0.3.0b14] - 2021-01-03
- Update Document.to_dict document_id key in metadata

### [0.3.0b13] - 2021-01-03
- Add field name and ID in Field.to_dict implementations

### [0.3.0b12] - 2021-01-03
- Add pages argument to construct_from_raw

### [0.3.0b11] - 2021-01-03
- Fix Document.from_dict typo (construct_from_raw method call)

### [0.3.0b10] - 2021-01-03
- Define Field data_types in to_dict methods
- Add area to IqDataTypesEnum David A minute ago

### [0.3.0b9] - 2021-01-03
- Move FieldMapping to `field.__init__`
- Fix circular import in fields
- Use super().to_dict() in Field objects

### [0.3.0b8] - 2021-01-03
- Fix Document.from_dict page iteration
- Add field types to Field.to_dict methods
- TableField allows no tags when calling to_dict method

### [0.3.0b7] - 2021-01-02
- Update Dockerfile entrypoint to pycognaize.app.rest
- Fix SnapshotBuilder.create_document_zip cls.DB assignment expression

### [0.3.0b6] - 2021-01-02
- Update changelog, fix all versions to 0.3.0b6

### [0.3.0b4] - 2021-01-02
- Update all tests (75% coverage)
- Merge branch 'master' into major_refactor
- Add Snapshot to `pycognaize.__init__`
- Use scandir in DocumentBuilder._populate_pages
- Update import statement for Mapping
- Fix SnapshotBuilder to work with new Snapshot class
- Remove FieldMapping from DocumentBuilder, use a separate module instead
- Snapshot uses lazy_dict for reading individual documents
- Use `tempfile` module in model.py
- Add doc_file (document.json) to SnapStorageEnum
- Add AreaField to `field.__init__`
- Add to_dict and from_dict methods to Document class
- Add test coverage in tox
- Merged in add_test_for_overwriting_snapshot_in_s3 (pull request #47)
- pull updates from major refactor and merge with current branch, remove test_service, add test_store_snapshot_with_same_name
- Merge branch 'major_refactor' into add_test_for_overwriting_snapshot_in_s3
- add unittests to test snapshot overwriting, change overwriting log message
- Allow 'from pycognaize import Model'
- Add doctests to text_field module
- Update sphynx conf.py
- Update build_docs.sh to also build pdf documentation file
- Update setup.sh logs
- Move all setup configurations from setup.py to setup.cfg
- build_docs.sh generated html and pdf documentations
- Add doc/source/generated/ to .*ignore files

### [0.3.0b3] - 2020-12-28
- Add script for building sphinx docs
- Minor docstring changes to Tag `hshift` and `vshift` methods
- SnapshotBuilder.DB added only on function call, to speed up module imports
- Add a single doctest to TextField constructor
- Add simplejson to requirements 
- Add Model.execute_genie method

### [0.3.0b1] - 2020-12-27
- Major refactored version
- Document > DocumentBuilder
  (DocumentBuilder has no instance, only methods for creating Documents,
  which are now equivalent to DocumentDataclass objects)
- DocumentDataclass > Document
- SnapshotProcessor > SnapshotBuilder
- Changed folder structure (no services package)
- DataSnapshot > Snapshot, DataRecipe > Recipe
- Add tox configuration for py36, py37, py38, py39, pypy
- Add 'MANIFEST.in' (required for 'TOX' to run properly)
- Add 'setup.cfg' for 'pytest'
- './setup.sh' builds and pushes a version, only if no tests fail
- Update README.md
- All tests pass on py36, py37, py38, py39, pypy

## [0.2]

### [0.2.5a4] - 2020-12-18
- Add docker push command in build.sh

### [0.2.5a3] - 2020-12-17
- Change rest service to threaded=False

### [0.2.5a2] - 2020-12-15
- Checkpoint version

### [0.2.5a1] - 2020-12-15
- Delete numpy from req-s

### [0.2.5a0] - 2020-12-04
- Update _build_df method in TableTag

### [0.2.4] - 2020-11-27
- Fix srcFieldId log in Document.get_fields_by_id to print field id instead of the whole field

### [0.2.3] - 2020-11-27
- Fix src_field_id issue in `digestor.py`

### [0.2.2.a7] - 2020-11-27
- All tests are fixed and running

### [0.2.2.a6] - 2020-11-18
- Fix issue in get_ocr_formatted

### [0.2.2.a5] - 2020-11-13
- Add setup.sh script
- Use cloudstorageio>=1.1.2 which supports uploading 5GB+ files to s3
- Do not store TableTag ocr (makes the pickle dumps way too big for documents with many tables)

### [0.2.2.a4] - 2020-11-07
- Fix typing annotation for `DocumentDataclass._pages`
- Add property `AreaField.value`
- Change `super().tags` to `self.tags`

### [0.2.2.a3] - 2020-11-01
- Do not store `TableTag.df`, build it on call
- Update Range unittest (remove unnecessary error raising test cases)

### [0.2.2.a2] - 2020-11-01
- Add area, height, width to (Cell)Range objects
- Add support for comparing Tag and (Cell)Range objects in magic methods of Tag
- In create_document_zip, if the recipe retrieved from DB is empty, through a ConnectionError Add get_table_cell_overlap to DocumentDataclass

### [0.2.2.a1] - 2020-10-31
- Initiate database_setup on function call instead of import statement

### [0.2.2.a0] - 2020-10-14
- Adjust problematic OCR in Page.get_ocr_formatted (if left >= right, right = left + 1, same for top/bottom)

### [0.2.1.a3] - 2020-10-28
-Optionally build df for TableTag using ocr data

### [0.2.1.a2] - 2020-10-22
- Add _build_df method in TableTag 

### [0.2.1.a1] - 2020-10-08
- Catch validation errors for TableTag

### [0.2.1.a0] - 2020-09-23
- Adjust coordinates smaller than 0 and bigger than 100

### [0.2.0.a12] - 2020-09-14
- Always remove snapshot zip before creating a new one

### [0.2.0.a11] - 2020-09-06
- Update digester template check

### [0.2.0.a10] - 2020-08-20
- Use proper relative_path in populate_pages
- Add to_dict in AreaField

### [0.2.0.a9] - 2020-08-20
- Include data_recipe in DataSnapshot

### [0.2.0.a8] - 2020-08-20
- Add value argument in construct_from_raw method in DateField

### [0.2.0.a7] - 2020-07-30
- Filter fields with repeat_parent instead of source field id

### [0.2.0.a6] - 2020-07-28
- SnapshotProcessor raises error in create_document_zip if document not found in the DB

### [0.2.0.a5] - 2020-07-28
- Attribute value of TextField and DateField are strings

### [0.2.0.a4] - 2020-07-27
- Add to_dict method to DateField

### [0.2.0.a3] - 2020-07-24
- Fix construct_from_raw in ExtractionTag
- Implement to_dict for numeric_field

### [0.2.0.a2] - 2020-07-24
- Add generated ObjectId-s in to_dict methods, update readme

### [0.2.0.a1] - 2020-07-23
- Add additional include-services argument to `setup.py`

### [0.2.0.a0] - 2020-07-23
- Add make_document_snap endpoint
- Implement DbStorage
- database_setup raises an error if failed
- Rename `rest.app` to `service.rest`
- Implement to_dict method for TableField TableTag and cell Range objects
- Add template_ids property in DataRecipe
- Add IqTableDividerEnum and update fields of other enums, including IqTableTagEnum
- Change cloudstorageio to version 1.0.10 in requirements
- Add digest_results function
- Add Storage abstract class
- Add to_dict methods in ExtractionTag and TextField
- Add IqFieldKeyEnum and add to_dict `abstractmethods` in Tag and Field abstract classes
- Update readme to use `nosetests` command
- Add abstract method decorators to methods in Tag, Field and Model abstract classes
- Make package exclusion dynamic in setup.py

## [0.1]

### [0.1.9.alpha1] - 2020-07-16
- Fix get_ocr_formatted in Page class
- Model object's predict method takes document_dataclass as input
- Major cosmetic change, full PEP8 compliance, except max line length
- Remove spreading_document, build and tag_utils modules

### [0.1.9.alpha] - 2020-07-15
- Add Model abstract class
- Update README.md packaging instructions and setup.py
- Update tests, comment DocumentDataclass tests, until proper setUp/tearDown is implemented
- Update SnapshotProcessor import in the rest.app
- Remove unnecessary methods from Document, remove outdated tests
- Add AreaField
- Adjustments after renaming an IqTableEnum to IqCollectionEnum
- TableTag optionally uses raw cell data to construct cell ranges, change keys to 1-based index
- Change __repr__ and __str__ methods in TableField
- Add IqCellKeyEnum and IqTableFieldEnum

### [0.1.8.alpha] - 2020-07-15
- Update make_snap endpoint to work with SnapshotProcessor, add fetch_document_zip endpoint
- Add SnapshotProcessor
- Add instruction for pushing to fury and pip install
- Minor cosmetic changes in ocr.py
- Remove source_id from Document object constructor
- Make tag parameter optional in TableField
- Remove raw parameter from DataSnapshot constructor
- Add collections to IqDatasetKeyEnum
- Remove CellTag

### [0.1.7.alpha] - 2020-07-14
- repr for Range includes the value
- Add methods for constructing tags and fields from raw dictionaries
- Add OCRData and modify build_cell function using dividers
- Implement build ranges
- Cell ranges added
- Remove an outdated comment from DocumentDataclas
- Add TableDivider object
- Add test for DocumentDataclass
- Modify constructors for Field and Tag objects
- Add IqTagKeyEnum to enums
- Document.get_y returns a list of fields instead of a single field
- Add get_ocr_formatted method in Page
- add src_field_id to IqDocumentKeysEnum
- Move database_setup into a separate module

### [0.1.6.alpha] - 2020-07-03
- Store relative path in page objects, remove SNAP_STORAGE_PATH constant and use env variable everywhere, fix some typos in TODOs
- Add document_src, document_id and pages as properties in DocumentDataClass
- Improve DataSnapshot api, add document_dataclasses and get methods
- Images and ocr folders are document ids instead of document src
- Pickled snapshot is saved as `snap.pickle` instead of `snap..pickle`
- Add StoredSnapshotException
- Add src attribute in document, put NoneField in a separate module
- Fix Page repr

### [0.1.4.alpha] - 2020-07-02
- Improve log format
- Redefine Snapshot, return traceback if rest.app fails
- Store images and ocr with snapshot
- Change pymongo to pymongo[srv] in requirements, fix DB name splitting in `iq.__init__`
- Remove db dependency from documents
- Rename Snapshot to DataSnapshot, Pipeline to DataPipeline, Recipe to DataRecipe
- Add test for DocumentDataclass
- add load_bson_by_path in utils
- Add document and recipe `bsons` to test resources

### [0.1.2.alpha] - 2020-06-10
 - Use rest endpoint for get_data in DataSnap
 - Change defaults for SNAP_STORAGE_PATH and DEFAULT_DB_URL, add back DEFAULT_DATASNAP_ENDPOINT
 - Fix TypeError message in `DataPipe.update`
 - Add IQ_SNAP_STORAGE_PATH back to EnvConfigEnum
 - Add pydrive to requirements in order to solve issue with cloudstorageio, should be changed once cloudstorageio is updated
 
 ### [0.1.3.alpha] - 2020-06-26
- Add DocumentDataclass
- Add get_x, get_y methods to Document
- Rename DataRecipe to Recipe, add input_fields, output_fields attributes to Recipe
- Rename snap to snapshot
- Add raw_field_type in IqRecipeEnum
- Cosmetic changes in DateField
- Add NoneField

### [0.1.1] - 2020-06-08
- Modify rest.app to make snapshots through a shared volume
- Implement `DataSnap.create` and DataSnap initialization through a shared volume
- Modify DataPipe in order to be inherited by DataSnap
- Add cloudstorageio to requirements
- Add SnapshotPathMissingException and SnapshotExistsException
- Remove IQ_DATASNAP_URL and add IQ_SNAP_STORAGE_PATH to EnvConfigEnum
- Remove igraph dependencies from Dockerfile
- Add DATASET_TYPE to DataSnap

### [0.1.0] - 2020-05-28
- Allow to import dataset types from `pycognaize.datasets`
- Add DataSnap
- Refactor the package structure

## [0.0]

### [0.0.9] - 2020-05-26
- Add Dockerfile and build.sh for building docker image with hash

### [0.0.8] - 2020-05-24
- Fix DEFAULT_DB error handling, add rest API for snap

### [0.0.7] - 2020-05-23
- Add raw and construct_from_raw methods
- Add data snap serialization and deserialization

### [0.0.6] - 2020-05-22
- Fix parse_periods in SpreadingDocument

### [0.0.5] - 2020-05-22
- Change df property to return CellTag objects

### [0.0.4] - 2020-05-22
- Add get_document_periods method
- Add df property to TableTag
- Inherit SpreadingDocument class from Document

### [0.0.3] - 2020-05-17
- Change `__repr__` in Field object, add TODO for document name column in DataRecipe
- Define a DEFAULT_DB object, with a single env variable - IQ_DB_URL

### [0.0.2] - 2020-05-15
- Created DataRecipe

### [0.0.1]
- Created Tag, Field, Page and Document abstractions for pycognaize
