import json
import logging
import sys
import time

import requests

from graphy.utils.files import read_file

zipkin_ip = '127.0.0.1'
zipkin_port = '9411'
base_address = 'http://{}:{}'.format(zipkin_ip, zipkin_port)
api_v1_endpoint = '/api/v1/'
api_v2_endpoint = '/api/v2/'

address_v1 = base_address + api_v1_endpoint
address_v2 = base_address + api_v2_endpoint

headers = {'content-type': 'application/json'}

logger = logging.getLogger(__name__)


def get_services():
    """
    Get all the service names from the Zipkin API.

    :return: a list with all services presented in Zipkin
    """
    logger.info('get_services()')

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
    logger.info('get_spans()')

    try:
        params = {'serviceName': service_name}
        response = requests.get(address_v2 + 'spans', params)
        return json.loads(response.text)
    except ConnectionError as ex:
        logger.error('{}: {}', type(ex), ex)
        sys.exit(status=1)


def post_spans(spans_file):
    """
    Post the spans json file to the Zipkin API

    :param spans_file: spans file path
    :return: if the operation was successful (equal to HTTP code 202) or not
    """
    logger.info('post_spans()')

    try:
        spans_data = read_file(spans_file)
        response = requests.post(address_v1 + 'spans', data=spans_data, headers=headers)
        return response.status_code == 202
    except ConnectionError as ex:
        logger.error('{}: {}', type(ex), ex)
        sys.exit(status=1)


def get_traces(service_name=None, span_name=None, annotation_query=None, min_duration=None, max_duration=None,
               end_ts=None, lookback=None, limit=None):
    """
    Get all the traces from the Zipkin API.

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
    :param lookback: Only return traces where all Span.timestamp are at or after (endTs lookback) in milliseconds.
    Defaults to endTs, limited to a system parameter QUERY_LOOKBACK
    :param limit: Maximum number of traces to return. Defaults to 10
    :return: list of traces with respect to the provided parameters.
    """
    logger.info('get_trace()')

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
    logger.info('get_trace()')

    response = requests.get(address_v2 + 'trace/{}'.format(trace_id))

    return json.loads(response.text)


def get_dependencies(lookback=None):
    """
    Get all the dependencies from the Zipkin API.

    :return: the dependencies data or None
    """
    logger.info('get_dependencies()')

    try:
        end_ts = str(int(time.time()))
        params = {'endTs': end_ts, 'lookback': lookback}
        response = requests.get(address_v2 + 'dependencies', params)
        return None if response.status_code != 200 else json.loads(response.text)
    except ConnectionError as ex:
        logger.error('{}: {}', type(ex), ex)
        sys.exit(status=1)


# TODO: the following lines are only for testing purposes [REMOVE]
if __name__ == '__main__':
    # print(get_services())
    # print(get_spans('api_com'))
    # print(get_dependencies())
    # print(get_trace('236a2805784a45d10a891d8327fc58f1'))
    print(len(get_traces()))
