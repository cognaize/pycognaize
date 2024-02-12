Quick Tutorial
==============

.. highlight:: python3

.. testsetup::

    from pycognaize import Snapshot
    from pycognaize.tests.resources import RESOURCE_FOLDER
    import os


    os.environ['SNAPSHOT_PATH'] = RESOURCE_FOLDER
    os.environ['SNAPSHOT_ID'] = 'snapshots'

Our main objective in this tutorial is to retrieve the balance sheet table
from a financial report, and create an excel output from it.

To start working with ``pycognaize``, first we need to retrieve the document from a
stored :term:`snapshot`.

.. code-block:: python

    from pycognaize import Snapshot

.. note::

    Snapshot uses environment variables ``SNAPSHOT_PATH`` and ``SNAPSHOT_ID``
    to load the snapshot.
    Before creating a Snapshot object using ``Snapshot.get()``,
    be sure to set the *path* and *id* in the corresponding environment
    variables.

    .. code:: python

            os.environ['SNAPSHOT_PATH'] = "PATH_TO_RESOURCE_FOLDER"
            os.environ['SNAPSHOT_ID'] = "SNAPSHOT_ID"


Now we can create the Snapshot object

.. doctest::

    >>> snapshot = Snapshot.get()
    >>> snapshot # doctest: +ELLIPSIS
    <pycognaize.document.snapshot.Snapshot object at 0x...>

Alternatively, ``Snapshot`` can be initialized with the corresponding parameters.

    .. code:: python

        snapshot = Snapshot(data_path=..., doc_path=...)

Cognaize SDK supports logging using Cognaize account, to access snapshots
from the cloud. To use this feature, you need to login using your Cognaize account.

First of all, ``API_HOST`` environment variable should be set to the Cognaize API host.

    .. code:: python

        os.environ['API_HOST'] = "https://api.cognaize.com"

    .. code:: python

        from pycognaize.login import Login

        login_instance = Login()
        login_instance.login(email=..., password=...)

Now Snapshot is enabled to access snapshots with `id` using ``get_by_id()``,
or downloading snapshot files from cloud storage using  ``download()``.

    .. code:: python

        snapshot = Snapshot.get_by_id(snapshot_id=...)
        snapshot = Snapshot.download(snapshot_id=..., destination_path=...)

    .. note::

        ``login`` function will give you access to snapshots assigned to your account.
        You only need to login once, and the login information will be available until
        end of runtime


:doc:`Snapshot <../API/_autosummary/pycognaize.document.snapshot.Snapshot>` is a
collection of multiple Document objects

.. doctest::

    >>> snapshot.documents._ids[:4]
    ['5eb8ee1c6623f200192a0651', '60215310dbf28200120e6afa', '60b76b3d6f3f980019105dac', '60f5260c7883ab0013d9c184']

As we can see our Snapshot consists of 5 documents,
let's choose one them and have a look at documents structure

.. doctest::

    >>> document = snapshot.documents['60b76b3d6f3f980019105dac']
    >>> document # doctest: +ELLIPSIS
    <pycognaize.document.document.Document object at 0x...>

Additionally, You can retrieve the Document object from the Cloud using the `recipe_id` and `document_id`.
This method allows you to access :term:`OCR` data and images associated with the specified document
after logging into your Cognaize account

.. note::
    Before creating a document object using ``Document.fetch_document(recipe_id, document_id)``
    make sure to specify the corresponding environment variables

    ``X_AUTH_TOKEN``: authentication token for API access
    ``API_HOST``: URL for the Cognaize API  .

    .. code:: python

            os.environ['API_HOST'] = "https://api.cognaize.com"
            os.environ['X_AUTH_TOKEN'] = "token"

.. code:: python

    >>> document = Document.fetch_document(recipe_id=..., doc_id=...)
    >>> document # doctest: +ELLIPSIS
    <pycognaize.document.document.Document object at 0x...>



Documents are seperated into pages, which we can access
by calling the ``document.pages`` method. Afterwards,
we can select the page we want to work with.
We will choose page 4, as it contains the table that
we need to get.

.. doctest::

    >>> document.pages
    OrderedDict([(1, <Page 1>), (2, <Page 2>), (3, <Page 3>), (4, <Page 4>), (5, <Page 5>), (6, <Page 6>)])
    >>> page_4 = document.pages[4]
    >>> page_4
    <Page 4>

Page object contains :term:`OCR` data and the image of the page. It also
has a lot of useful functionality that you can learn more about
:doc:`here <../API/_autosummary/pycognaize.document.page.Page>`.
The page OCR and image data can be loaded using multiprocessing
in order to speed up the process. To use this functionality functions
``document.load_page_images()`` and ``document.load_page_ocr()`` are available.
For example, to load all page images parallel, we can do

.. code-block::

    >>> document.get_page_images()
        ...
Optionally, you can add a filter function to these methods which take the page
object and download only the pages that return true when passed to the filter
function.
For example, to download the OCR only for the odd pages you can call

.. code-block::

    >>> document.load_page_ocr(lambda page: page.page_number%2)


Moreover in ``page`` objects, you can search for a text in page object
and get its coordinates.

.. doctest::

    >>> page_4.search_text('Month')
    [{'top': 500, 'bottom': 529, 'left': 1254, 'right': 1361, 'matched_words': [{'left': 1254, 'right': 1361, 'top': 500, 'bottom': 529, 'ocr_text': 'Month', 'word_id_number': 60}]}]


You can also generate an image with the annotations.

.. code-block::

    image = page1.draw_ocr_boxes()

In order to access the table data we need to access the fields which are in
the document object. The document object contains all tagged fields.
Input ``Fields`` are accessed using ``document.x`` and output ``Fields``
are accessed using ``document.y``.
The output of ``document.x`` is an Ordered Dictionary
that has *names* (defined in the :term:`AI Interface`) as keys and ``list`` of
:doc:`Field <../API/_autosummary/pycognaize.document.field>`
objects as values. We can select all table fields using
``document.x['table']``.

.. doctest::

    >>> fields = document.x
    >>> fields
    FieldCollection([('table', [<TableField: table>])])

    >>> table_field = document.x['table']
    >>> table_field
    [<TableField: table>]

.. note::

    There are 5 types of ``field`` objects
        * Numeric Field
        * Text Field
        * Date Field
        * Table Field
        * Area Field

Now, as we have accessed tables, we can select the only table on this page,
and get tags. Tags provide a lot more functionality that will be covered
:doc:`Tag <../API/_autosummary/pycognaize.document.tag>`

.. doctest::

    >>> table_1 = table_field[0]
    >>> table_1
    <TableField: table>

Let's select the table on page 4, and convert it to a pandas dataframe.

``TableTag`` can output a ``pandas.DataFrame`` using ``table_tag.df`` method.


.. doctest::

    >>> table_1_tags = table_1.tags[0]
    >>> table_1_tags
    <TableTag: left: 8.6, right: 92.69999999999999, top: 12.0, bottom: 64.0998>

.. code-block:: python

    >>> table_1_tags.df
                                                0               1                  2
    0                                           March 31, 2021  December 31, 2020
    1                                              (unaudited)
    2                                   Assets
    3                          Current assets:
    4                                     Cash          $ 10.9                $ —
    5                      Accounts receivable            11.6                8.6
    6      Accounts receivable - related party             5.0                5.7
    7                         Prepaid expenses             0.3                0.4
    8                     Total current assets            27.8               14.7
    9            Property, plant and equipment           377.6              371.8
    10          Less: accumulated depreciation            51.1               46.5
    11      Property, plant and equipment, net           326.5              325.3
    12  Investment in unconsolidated affiliate            80.2               80.3
    13                            Other assets             0.5                0.6
    14                            Total assets         $ 435.0            $ 420.9
    15         Liabilities and members' equity
    16                    Current liabilities:
    17                        Accounts payable          $ 29.2              $ 6.8
    18        Accounts payable - related party             6.4                2.1
    19  Accrued expenses and other liabilities             2.4                4.4
    20        Accrued expenses - related party             0.1                0.3
    21               Total current liabilities            38.1               13.6
    22                          Long-term debt           100.0              109.3
    23                       Deferred revenues             1.6                1.2
    24             Other long-term liabilities             2.5                2.5
    25                         Members' equity           292.8              294.3
    26   Total liabilities and members' equity         $ 435.0            $ 420.9
