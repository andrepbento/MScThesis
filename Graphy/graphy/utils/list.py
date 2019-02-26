"""
    Author: André Bento
    Date last modified: 25-02-2019
"""


def diff(list_1, list_2):
    """
    Performs the difference between two lists. In this context the difference is what is in list_1, but not in list_2.

    :param list_1: The first list.
    :param list_2: The second list.
    :return: A list with the difference between the first and second lists.
    """
    return list(set(list_1).symmetric_difference(set(list_2)))
