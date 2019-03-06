"""
    Author: André Bento
    Date last modified: 01-03-2019
"""
import operator


def calc_percentage(dictionary: dict) -> dict:
    """
    Calculates the percentage of each value for every key in the dictionary.

    :param dictionary: The dictionary containing keys and the corresponding int or float values.
    :return: A dictionary containing the keys of the given dictionary and their percentage values.
    """
    result_dict = dict()
    total = sum(dictionary.values())
    for k, v in dictionary.items():
        result_dict[k] = dictionary[k] / total
    return result_dict


def filter(dictionary: dict, key) -> dict:
    """
    Filter values from a certain dictionary of dictionary.

    :param dictionary: The dictionary.
    :param key: The key to filter.
    :return: The list of filtered values.
    """
    result_dict = dict()
    for k, v in dictionary.items():
        if isinstance(v, int) or isinstance(v, float):
            if key == k:
                result_dict[k] = v
        elif isinstance(v, dict):
            if key in v:
                result_dict[k] = v.get(key)
    return result_dict


def sort(dictionary: dict) -> list:
    """
    Sorts a dictionary by their values.

    :param dictionary: The dictionary to sort.
    :return: A list with the sorted values in reverse order.
    """
    return sorted(dictionary.items(), key=operator.itemgetter(1), reverse=True)


def update(dictionary: dict, key, func):
    """
    Updates the values of a dictionary with respect to a given function.

    :param dictionary: The dictionary.
    :param key: The key.
    :param func: The function that takes the value and transforms it.
    """
    for k, v in dictionary.items():
        if k == key:
            dictionary[k] = func(v)
        elif isinstance(v, list):
            for item in v:
                update(item, key, func)
