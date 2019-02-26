"""
    Author: André Bento
    Date last modified: 25-02-2019
"""
from graphy.models import span as my_span


def get_status_codes(trace_list):
    """
    Gets the status codes presented in a trace list.

    :param trace_list: The trace list in Zipkin format.
    :return: A dictionary containing the grouped status codes counting.
    """

    status_codes_dict = dict()
    for trace in trace_list:
        for span in trace:
            status_code = my_span.get_status_code(span)
            if status_code and len(status_code) > 1:
                status_code_group = status_code[0]
                status_code = status_code_group + 'XX'
                if status_code in status_codes_dict:
                    status_codes_dict[status_code] += 1
                else:
                    status_codes_dict[status_code] = 1
    return status_codes_dict
