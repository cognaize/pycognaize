Working with ExtractionTags and AI interface
============================================

.. highlight:: python3

.. testsetup::

    from pycognaize import Snapshot
    from pycognaize.tests.resources import RESOURCE_FOLDER
    import os

    from pycognaize.document.tag import ExtractionTag
    from pycognaize.document import Document, Page
    from pycognaize.document.field import NumericField, TextField


    os.environ['SNAPSHOT_PATH'] = RESOURCE_FOLDER
    os.environ['SNAPSHOT_ID'] = 'snapshots'

    snapshot = Snapshot.get()
    document = snapshot.documents['60b76b3d6f3f980019105dac']
    table_field = document.x['table']
    table_1 = table_field[0]


The objective of this tutorial is to show how to extract some general information and create a highlighted
PDF from a document. to do that. We will also
introduce concepts such as ``ExtractionTag`` and ``Field``.

To begin with, we will check if the table on page 4 of the document is unaudited and if
the report is for the "Test" company.

.. note::
    This tutorial requires an understanding of the following concepts of

    *  ``Snapshot``
    *  ``Document``
    *  ``Field``
    *  ``ExtractionTag``
    *  ``NumericField``
    *  ``TextField``

    If you are not familiar with these concepts, please refer to the
    :doc:`Quick tutorial <quick_tutorial>`, :doc:`API reference <../API/_autosummary/pycognaize>`
    or :doc:`Glossary <../API/glossary>` first.

Repeating the steps of loading the :term:`snapshot` and :term:`document`
from the :doc:`Quick Tutorial <quick_tutorial>` we get a document object

.. doctest::

    >>> document # doctest: +ELLIPSIS
    <pycognaize.document.document.Document object at 0x...>

In our case, we want to check if the table on page 4 is an unaudited
statement of operations of "CRESTWOOD PERMIAN BASIN HOLDINGS LLC".
First of all, we can do a text search on the page using ``search_text``
method of ``Page`` class.

First of all we have to get the page 4. After we can call ``search_text``
and get coordinates of marched text.

.. doctest::

    >>> page = document.pages[4]
    >>> matched_name = page.search_text('Test')
    >>> matched_name
    [{'top': 1168, 'bottom': 1198, 'left': 1295, 'right': 1339, 'matched_words': [{'left': 1295, 'right': 1339, 'top': 1168, 'bottom': 1198, 'ocr_text': 'Test', 'word_id_number': 73}]}]



As we can see all the words we needed have been matched and now we have their
coordinates which will allow us to create tags in the future. Now we can check
if the table is unaudited. By repeating the operations above we get

.. doctest::

    >>> matched_unaudited = page.search_text('(unaudited)')
    >>> matched_unaudited
    [{'top': 1106, 'bottom': 1135, 'left': 1299, 'right': 1338, 'matched_words': [{'left': 1299, 'right': 1338, 'top': 1106, 'bottom': 1135, 'ocr_text': '(unaudited)', 'word_id_number': 72}]}]

In the meantime we store the data of matched words in a dictionary for easy
access in later steps.

.. doctest::

    >>> search_results = dict()
    >>> search_results['matched_unaudited'] = matched_unaudited[0]['matched_words'][0]
    >>> search_results['matched_name'] = matched_name[0]['matched_words'][0]


Now we have to fill this data into ``document.y``. For this we need to
create Fields depending on their types, create
:doc:`TextField <../API/_autosummary/pycognaize.document.field.text_field.TextField>`,
:doc:`NumericField <../API/_autosummary/pycognaize.document.field.numeric_field.NumericField>`
or :doc:`TableField <../API/_autosummary/pycognaize.document.field.table_field.TableField>`.
For example we create empty output fields for name and type of the table.

.. doctest::

    >>> document.y['company_name'], document.y['table_type'] = [], []
    >>> print(document.y['company_name'], document.y['table_type'])
    [] []

To create ``Field``, we must have tags. For tags, we need coordinates
which we already saved in ``matched_name`` and ``matched_unaudited`` beforehand.

Import required modules

.. code-block::

    from pycognaize.document.tag import ExtractionTag
    from pycognaize.document import Document, Page
    from pycognaize.document.field import NumericField, TextField

Now we can create ``ExtractionTag`` for the name and type of the table.
For creating a tag, we must specify coordinates of text converted to percentages, that is why
we need the height and width of the image.

.. doctest::

    >>> name_type_tags = dict()
    >>> # take height and width of image from OCR
    >>> h = page.get_ocr()['image']['height']
    >>> w = page.get_ocr()['image']['width']
    >>> for name, coords in search_results.items():
    ...     name_type_tags[name] = ExtractionTag(left=coords['left'] / w * 100,
    ...                                         right=coords['right'] / w * 100,
    ...                                         top=coords['top'] / h * 100,
    ...                                         bottom=coords['bottom'] / h * 100,
    ...                                         page=page,
    ...                                         raw_value=coords['ocr_text'],
    ...                                         raw_ocr_value=coords['ocr_text'])
    >>> name_type_tags
    {'matched_unaudited': <ExtractionTag: left: 76.41176470588236, right: 78.70588235294119, top: 50.272727272727266, bottom: 51.590909090909086>, 'matched_name': <ExtractionTag: left: 76.17647058823529, right: 78.76470588235294, top: 53.090909090909086, bottom: 54.45454545454545>}

Using extraction tags that we have just created, we can create two ``TextFields`` and add them
to ``document.y`` (``document.x`` and``document.y`` are part of :term:`AI Interface`).

.. doctest::

    >>> table_type_field = TextField(name='table_type', tags=[name_type_tags['matched_unaudited']])
    >>> table_name_field = TextField(name='table_name', tags=[name_type_tags['matched_name']])
    >>> print(table_type_field, table_name_field)
    (unaudited) Test

    >>> document.y['company_name'].append(table_name_field)
    >>> document.y['table_type'].append(table_type_field)
    >>> document.y
    OrderedDict([('company_name', [<TextField: table_name: Test>]), ('table_type', [<TextField: table_type: (unaudited)>])])

After extraction tags have been added to the document output, we can create a pdf with
annotated fields by specifying them in ``to_pdf`` method.

.. doctest::

    >>> annotated_pdf = document.to_pdf(output_fields=['company_name', 'table_type'])

.. note::

    ``to_pdf`` method returns bytes of the pdf. It has to be written to file to
    be able to view it.

    .. code-block::

        with open('annotated_pdf.pdf', 'wb') as f:
            f.write(annotated_pdf)
