import logging
from itertools import groupby


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


def assign_indices_to_tables(tables, threshold: float = 0.4):
    """
    Given tables are grouped by pages,
        then for each page, tables are left sorted then
            ordered horizontally and vertically.
    Return dict where keys are indices based above-mentioned ordering
        and values are corresponding tables.
    """
    tables_dict = {}
    valid_tables = filter_out_invalid_tables(tables)
    sorted_tables = sorted(valid_tables,
                           key=lambda x: x.tags[0].page.page_number)
    grouped_tables = {page: list(table) for page, table in
                      groupby(sorted_tables,
                              key=lambda x: x.tags[0].page.page_number)}
    for page, page_tables in grouped_tables.items():
        sorted_page_tables = sorted(page_tables,
                                    key=lambda x: x.tags[0].left)
        final_ordered_tables = _sort_table_horizontally(sorted_page_tables,
                                                        threshold=threshold)
        tables_dict.update({(page, idx): table
                            for idx, table in
                            enumerate(final_ordered_tables)})
    return tables_dict
