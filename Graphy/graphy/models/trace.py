"""
TODO: add trace.py doc
"""
from graphy.models import span as my_span


def get_status_codes(trace_list):
    status_codes_dict = dict()
    for trace in trace_list:
        for span in trace:
            status_code = my_span.get_status_code(span)
            if status_code:
                if status_code in status_codes_dict:
                    status_codes_dict[status_code] += 1
                else:
                    status_codes_dict[status_code] = 1
    return status_codes_dict
