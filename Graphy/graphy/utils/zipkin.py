import json as json
import logging
import sys
import time

import requests

from graphy.utils import config
from graphy.utils.files import read_file

logger = logging.getLogger(__name__)

zipkin_config = config.get('ZIPKIN')

zipkin_ip = zipkin_config['IP']
zipkin_port = zipkin_config['PORT']
base_address = 'http://{}:{}'.format(zipkin_ip, zipkin_port)
api_v1_endpoint = zipkin_config['API_V1']
api_v2_endpoint = zipkin_config['API_V2']

address_v1 = base_address + api_v1_endpoint
address_v2 = base_address + api_v2_endpoint

headers = {'content-type': 'application/json'}


def get_services():
    """
    Get all the service names from the Zipkin API.

    :return: a list with all services presented in Zipkin
    """
    logger.debug('get_services()')

    try:
        response = requests.get(address_v2 + 'services')
        return json.loads(response.text)
    except ConnectionError as ex:
        logger.error('{}: {}', type(ex), ex)
        sys.exit(status=1)


def get_spans(service_name):
    """
    Get all the span names recorded by a particular service from the Zipkin API.

    :param service_name: Ex api_com (required) - Lower-case label of a node in the service graph. The /services endpoint
    enumerates possible input values.
    :return: the spans data
    """
    logger.debug('get_spans()')

    try:
        params = {'serviceName': service_name}
        response = requests.get(address_v2 + 'spans', params)
        return json.loads(response.text)
    except ConnectionError as ex:
        logger.error('{}: {}', type(ex), ex)
        sys.exit(status=1)


def post_spans(spans_file):
    """
    Post the spans utils file to the Zipkin API

    :param spans_file: spans file path
    :return: if the operation was successful (equal to HTTP code 202) or not
    """
    logger.debug('post_spans()')

    try:
        spans_data = read_file(spans_file)
        response = requests.post(address_v1 + 'spans', data=spans_data, headers=headers)
        return response.status_code == 202
    except ConnectionError as ex:
        logger.error('{}: {}', type(ex), ex)
        sys.exit(status=1)


def get_traces(lookback=365 * 24 * 60 * 60 * 1000, service_name=None, span_name=None, annotation_query=None,
               min_duration=None, max_duration=None, end_ts=None, limit=10):
    """
    Get all the traces from the Zipkin API.

    :param lookback: Only return traces where all Span.timestamp are at or after (endTs lookback) in milliseconds.
    Defaults to endTs, limited to a system parameter QUERY_LOOKBACK. Default 1 year in milliseconds.
    :param service_name: Ex api_com (required) - Lower-case label of a node in the service graph. The /services endpoint
    enumerates possible input values.
    :param span_name: Ex get - name of a span in a trace. Only return traces that contains spans with this name.
    :param annotation_query: Ex. http.uri=/foo and retried - If key/value (has an =), constrains against Span.tags
    entries. If just a word, constrains against Span.annotations[].value or Span.tags[].key. Any values are AND against
    each other. This means a span in the trace must match all of these.
    :param min_duration: Ex. 100000 (for 100ms). Only return traces whose Span.duration is greater than or equal to
    minDuration microseconds.
    :param max_duration: Only return traces whose Span.duration is less than or equal to maxDuration microseconds. Only
    valid with minDuration.
    :param end_ts: Only return traces where all Span.timestamp are at or before this time in epoch milliseconds.
    Defaults to current time.
    :param limit: Maximum number of traces to return. Defaults to 10
    :return: list of traces with respect to the provided parameters.
    """
    logger.debug('get_trace()')

    try:
        params = {
            'serviceName': service_name,
            'spanName': span_name,
            'annotationQuery': annotation_query,
            'minDuration': min_duration,
            'maxDuration': max_duration,
            'endTs': int(time.time()) if end_ts is None else end_ts,
            'lookback': lookback,
            'limit': limit
        }
        response = requests.get(address_v2 + 'traces', params)
        return json.loads(response.text)
    except ConnectionError as ex:
        logger.error('{}: {}', type(ex), ex)
        sys.exit(status=1)


def get_trace(trace_id):
    """
    Get the trace with the provided trace id.

    :param trace_id: Trace identifier, set on all spans within it
    :return: the trace data
    """
    logger.debug('get_trace()')

    response = requests.get(address_v2 + 'trace/{}'.format(trace_id))

    return json.loads(response.text)


def get_dependencies(end_ts, lookback=60 * 60 * 1000):
    """
    Get all the dependencies from the Zipkin API.
    :param end_ts: End timestamp in milliseconds.
    :param lookback: Timestamp in milliseconds of lookback, 1 hour default.
    :return: the dependencies data or None
    """
    logger.debug('get_dependencies()')

    try:
        params = {'endTs': end_ts, 'lookback': lookback}
        response = requests.get(address_v2 + 'dependencies', params)
        return None if response.status_code != 200 else json.loads(response.text)
    except ConnectionError as ex:
        logger.error('{}: {}', type(ex), ex)
        sys.exit(status=1)


if __name__ == '__main__':
    start_date_time_str = "01/01/2018 00:00:00"
    end_date_time_str = "30/12/2018 00:00:00"

    from graphy.utils import time as my_time

    start_timestamp = my_time.to_unix_time_millis(start_date_time_str)
    end_timestamp = my_time.to_unix_time_millis(end_date_time_str)

    # TODO: the following lines are only for testing purposes [REMOVE]
    # print('\nServices:\n{}'.format(get_services()))

    # print('\nSpans:\n{}'.format(get_spans('api_com')))

    # print('\nDependencies:\n'.format(get_dependencies(1530227280000)))

    # print(get_trace('236a2805784a45d10a891d8327fc58f1'))

    traces = get_traces(end_ts=end_timestamp, lookback=start_timestamp, limit=100000)
    min_timestamp = None
    max_timestamp = None
    trace_count = 0
    span_count = 0
    for trace in traces:
        trace_count += 1
        for span in trace:
            span_count += 1
            if min_timestamp is None:
                min_timestamp = span['timestamp']
            if max_timestamp is None:
                max_timestamp = span['timestamp']
            if min_timestamp > span['timestamp']:
                min_timestamp = span['timestamp']
            if max_timestamp < span['timestamp']:
                max_timestamp = span['timestamp']

    print('trace_count: {}'.format(trace_count))
    print('span_count: {}'.format(span_count))
    print('min_timestamp: {}'.format(min_timestamp))
    print('max_timestamp: {}'.format(max_timestamp))
