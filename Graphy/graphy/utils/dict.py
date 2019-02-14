import operator


def calc_percentage(dictionary):
    result_dict = dict()
    total = sum(dictionary.values())
    for k, v in dictionary.items():
        result_dict[k] = dictionary[k] / total
    return result_dict


def sort(dictionary):
    return sorted(dictionary.items(), key=operator.itemgetter(1), reverse=True)


def update(dictionary, key, func=None):
    if not isinstance(dictionary, dict) and func is None:
        return

    for k, v in dictionary.items():
        if k == key:
            dictionary[k] = func(v)
        elif isinstance(v, list):
            for item in v:
                update(item, key, func)
