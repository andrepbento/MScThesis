"""
    Author: André Bento
    Date last modified: 28-02-2019
"""
from graphy.models import span as my_span


def count_trace_coverability(trace_coverability):
    """
    Counts the trace coverability for each trace.

    :param trace_coverability: A dictionary with the trace coverability data.
    :return: A dictionary with the interval trace coverability counting.
    """

    # TODO: Improve method [If else and dict creation].
    trace_coverability_count = {
        '<1%': {
            'value': 0,
            'trace_ids': set(),
            'span_ids': set()
        },
        '1-10%': {
            'value': 0,
            'trace_ids': set(),
            'span_ids': set()
        },
        '11-20%': {
            'value': 0,
            'trace_ids': set(),
            'span_ids': set()
        },
        '21-30%': {
            'value': 0,
            'trace_ids': set(),
            'span_ids': set()
        },
        '31-40%': {
            'value': 0,
            'trace_ids': set(),
            'span_ids': set()
        },
        '41-50%': {
            'value': 0,
            'trace_ids': set(),
            'span_ids': set()
        },
        '51-60%': {
            'value': 0,
            'trace_ids': set(),
            'span_ids': set()
        },
        '61-70%': {
            'value': 0,
            'trace_ids': set(),
            'span_ids': set()
        },
        '71-80%': {
            'value': 0,
            'trace_ids': set(),
            'span_ids': set()
        },
        '81-90%': {
            'value': 0,
            'trace_ids': set(),
            'span_ids': set()
        },
        '91-100%': {
            'value': 0,
            'trace_ids': set(),
            'span_ids': set()
        },
        'error': {
            'value': 0,
            'trace_ids': set(),
            'span_ids': set()
        }
    }
    for key in trace_coverability.keys():
        percentage = trace_coverability[key].get('%')
        span_ids = trace_coverability[key]['span_ids']
        if percentage < 1.0:
            trace_coverability_item = trace_coverability_count['<1%']
        elif 1.0 <= percentage < 10.0:
            trace_coverability_item = trace_coverability_count['1-10%']
        elif 11.0 <= percentage < 20.0:
            trace_coverability_item = trace_coverability_count['11-20%']
        elif 21.0 <= percentage < 30.0:
            trace_coverability_item = trace_coverability_count['21-30%']
        elif 31.0 <= percentage < 40.0:
            trace_coverability_item = trace_coverability_count['31-40%']
        elif 41.0 <= percentage < 50.0:
            trace_coverability_item = trace_coverability_count['41-50%']
        elif 51.0 <= percentage < 60.0:
            trace_coverability_item = trace_coverability_count['51-60%']
        elif 61.0 <= percentage < 70.0:
            trace_coverability_item = trace_coverability_count['61-70%']
        elif 71.0 <= percentage < 80.0:
            trace_coverability_item = trace_coverability_count['71-80%']
        elif 81.0 <= percentage < 90.0:
            trace_coverability_item = trace_coverability_count['81-90%']
        elif 91.0 <= percentage < 100.0:
            trace_coverability_item = trace_coverability_count['91-100%']
        else:
            trace_coverability_item = trace_coverability_count['error']

        if trace_coverability_item:
            trace_coverability_item['value'] += 1
            trace_coverability_item['trace_ids'].add(key)
            trace_coverability_item['span_ids'].update(span_ids)

    return trace_coverability_count


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


def trace_coverability(traces):
    # Remove duplicates
    trace_times = dict()
    span_count = 0
    for trace in traces:
        trace_id = ''
        tmp_span_parent_id = None
        for span in trace:
            span_count += 1

            trace_id = span.get('traceId')

            if trace_id not in trace_times:
                trace_times[trace_id] = {
                    't_parent': 0,
                    't_child': 0,
                    '%': 0.0,
                    'span_ids': set()
                }

            span_id = span.get('id')

            if span_id in trace_times[trace_id]['span_ids']:
                continue
            trace_times[trace_id]['span_ids'].add(span_id)

            span_parent_id = span.get('parentId', False)

            if span_parent_id and span_parent_id == tmp_span_parent_id:
                trace_times[trace_id]['t_child'] += span.get('duration')
            else:
                tmp_span_parent_id = span_id
                trace_times[trace_id]['t_parent'] = span.get('duration')
                continue

        t_child = trace_times[trace_id]['t_child']
        t_parent = trace_times[trace_id]['t_parent']
        try:
            percentage = (t_child / t_parent) * 100  # microseconds to milliseconds
            # if percentage < 0 or percentage > 100:
            #     print('percentage error:', percentage)
            # else:
            #     print('percentage ok:', percentage)
            trace_times[trace_id]['%'] = percentage
        except Exception as ex:
            print(ex)
            trace_times[trace_id]['%'] = -1
    trace_coverability = count_trace_coverability(trace_times)
    #print('span_count:', span_count)
    #print('trace_count:', len(traces))
    #print('trace_coverability:\n{}'.format(trace_coverability))
    return trace_coverability
