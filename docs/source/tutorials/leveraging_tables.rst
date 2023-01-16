Leveraging Tables
=================

.. highlight:: python3

.. testsetup::

    from pycognaize import Snapshot
    from pycognaize.tests.resources import RESOURCE_FOLDER
    import os


    os.environ['SNAPSHOT_PATH'] = RESOURCE_FOLDER
    os.environ['SNAPSHOT_ID'] = 'snapshots'

    snapshot = Snapshot.get()
    document = snapshot.documents['60b76b3d6f3f980019105dac']
    table_field = document.x['table']
    table_1 = table_field[0]

Cognaize python SDK provides a wide functionality designed to handle
data in table forms of :term:`snapshot` in the most efficient way. Two main
concepts for accessing and representing tables in Cognaize SDK
are ``TableField`` and ``TableTag`` classes.

See corresponding documentation in API reference
:doc:`Table Field <../API/_autosummary/pycognaize.document.field.table_field>` and
:doc:`Table Tag <../API/_autosummary/pycognaize.document.tag.table_tag>`.

.. note::
    This tutorial requires understanding of the concepts of

    *  ``Snapshot``
    *  ``Document``
    *  ``Field``
    *  ``ExtractionTag``

    If you are not familiar with these concepts, please refer to the
    :doc:`Quick tutorial <quick_tutorial>`, :doc:`API reference <../API/_autosummary/pycognaize>`
    or :doc:`Glossary <../API/glossary>` first.

In the :doc:`Quick tutorial <quick_tutorial>` we read a snapshot data using ``Snapshot.get()``
and retrieved a ``TableField`` object from ``document.x``.

.. doctest::

    >>> table_1
    <TableField: table>

``TableField`` object can be used to extract the title of the table from the page,
or to convert the table to a ``JSON`` format.

To get the table's title data we use ``get_table_title()`` method
which can be called without any additional parameters or with ``margin`` and
``n_lines_above`` specified.

See the documentation of :doc:`TableField.get_table_title() <../API/_autosummary/pycognaize.document.field.table_field.TableField>`
for more details.

.. doctest::

    >>> table_1.get_table_title()
    'Sample table heading in form tutorial of Cognaize SDK'

In order to access the actual table structure, content and coordinates, we use the ``TableTag`` class.
TableTag objects can be extracted from ``document``.

.. doctest::

    >>> table_1_tags = table_1.tags[0]
    >>> table_1_tags
    <TableTag: left: 8.6, right: 92.69999999999999, top: 12.0, bottom: 64.0998>

One of the most useful properties of ``TableTag`` class is ``TableTag.df`` method.
This property returns the table annotation in a ``pandas.DataFrame`` format and afterwards we
can use the standard pandas functionality.

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


Each ``TableTag`` object consists of :term:`Cell`. Access to Cells is provided through
properties ``cells``, ``cell_data``

.. doctest::

    >>> cells = table_1_tags.cells
    >>> f"{str(cells)[:400]}..."
    '{(1, 1): <Cell: coords: (12.00000 , 61.80000 , 13.40000 , 8.60000  ) spans: (1  , 1  ) corner coords: (1  , 1  ) value: >, (2, 1): <Cell: coords: (12.00000 , 77.90000 , 13.40000 , 61.80000 ) spans: (1  , 1  ) corner coords: (2  , 1  ) value: ZZxCTGRLZeoIjx>, (3, 1): <Cell: coords: (12.00000 , 92.70000 , 13.40000 , 77.90000 ) spans: (1  , 1  ) corner coords: (3  , 1  ) value: kAMvVCPUBIACpWtZI>, (1...'
