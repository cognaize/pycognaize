import logging
from itertools import groupby
from typing import Optional

from pycognaize.document.tag.html_tag import HTMLTableTag, HTMLTag


def filter_out_invalid_tables(tables):
    """
    Filters tables that have tag.
    """
    valid_tables = []
    for table in tables:
        if not table.tags:
            logging.warning('removing table with no tags')
            continue
        valid_tables.append(table)
    return valid_tables


def _sort_table_horizontally(tables, threshold: float):
    """
    Given tables are sorted first horizontally, then vertically.
    """
    groups = []
    for table in tables:
        if not groups:
            groups.append([table])
            continue
        latest_group = groups[-1]
        group_left = min([table.tags[0].left for table in latest_group])
        group_right = max([table.tags[0].right for table in latest_group])
        table_tag = table.tags[0]
        if group_left < table_tag.right and group_right > table_tag.left:
            iou = (
                    (min((table_tag.right, group_right)) -
                     max((table_tag.left, group_left))) /
                    (min(table_tag.right - table.tags[0].left,
                         group_right - group_left)))
            if iou > threshold:
                latest_group.append(table)
                continue
        groups.append([table])

    sorted_tables = []
    for group in groups:
        for table in sorted(group, key=lambda x: x.tags[0].top):
            sorted_tables.append(table)
    return sorted_tables


def assign_indices_to_tables(tables, all_tables: Optional[list] = None,
                             threshold: float = 0.4) -> dict:
    """
    If the document is an XBRL document,
        the function matches the tables based on the ordering of all tables.
    If it's not an XBRL document,
        the tables are grouped by pages and for each page,
        the tables are left sorted and ordered horizontally and vertically.

    Return dict where the keys are indices based above-mentioned ordering
        and the values are the corresponding tables.

    :param tables: a list of tables that need to be indexed
    :param all_tables: a list of all tables in the document.
        This parameter is required if the tables are from an XBRL document
    :param threshold: intersection threshold
    """
    tables_dict = {}
    valid_tables = filter_out_invalid_tables(tables)
    if not valid_tables:
        return tables_dict
    if all(isinstance(table.tags[0], HTMLTableTag) or
           isinstance(table.tags[0], HTMLTag) for table in valid_tables):
        if not all_tables:
            logging.error('Missing argument: list of all table fields')
            return tables_dict
        all_valid_tables = filter_out_invalid_tables(all_tables)
        tables_html_id_idx_mapping = {
            table.tags[0].html_id: (idx, 0)
            for idx, table in enumerate(all_valid_tables, start=1)}
        tables_dict = {
            tables_html_id_idx_mapping[table.tags[0].html_id]: table
            for table in valid_tables}
    else:
        sorted_tables = sorted(valid_tables,
                               key=lambda x: x.tags[0].page.page_number)
        grouped_tables = {page: list(table) for page, table in
                          groupby(sorted_tables,
                                  key=lambda x: x.tags[0].page.page_number)}
        for page, page_tables in grouped_tables.items():
            sorted_page_tables = sorted(page_tables,
                                        key=lambda x: x.tags[0].left)
            final_ordered_tables = _sort_table_horizontally(
                sorted_page_tables, threshold=threshold)
            tables_dict.update({(page, idx): table
                                for idx, table in
                                enumerate(final_ordered_tables)})
    return tables_dict
