"""
    Author: André Bento
    Date last modified: 13-02-2019
"""
"""
Fields:
-------
* traceId - unique id of a trace, 128-bit string
* name - human-readable title of instrumented function
* timestamp - UNIX epoch in milliseconds
* id - unique id of a span, 64-bit string
* parentId - reference to id of parent span
* duration - span duration in microseconds
* binaryAnnotations:
  ** protocol - `HTTP` or `function` for RPC calls
  ** http.url - HTTP endpoint
  ** http.status_code - result of HTTP operation
* annotations:
  ** value - describes the position in trace (based on Zipkin format):
     `cs` - client send
     `cr` - client receive
     `ss` - server send
     `sr` - server receive
  ** timestamp - UNIX epoch in microseconds
  ** endpoint - which endpoint generated a trace event

Notes:
1. Time units are not consistent, some fields are in milliseconds and some are in microseconds
2. Trace spans may contain more fields, except those mentioned here
"""
import json
import logging
from enum import Enum

from graphy.models.annotation import Annotation
from graphy.models.attributes import get_attribute, set_attribute_value
from graphy.models.binary_annotation import BinaryAnnotation
from graphy.utils import dict as my_dict

logger = logging.getLogger(__name__)


class Span(object):
    def __init__(self, data):
        """ Span initialization using JSON data. """
        self.__dict__ = json.loads(data)

    def __str__(self):
        """
        Span string representation containing all the object property values.

        :return: the span as a string
        """
        return str(self.__dict__)

    @property
    def trace_id(self):
        """
        Span trace id, present in all spans.

        :return: the trace id value
        """
        attribute_key = 'traceId'
        return get_attribute(self, attribute_key)

    @property
    def name(self):
        """
        Span name in lowercase, rpc method for example.

        :return: the span name value
        """
        attribute_key = 'name'
        return get_attribute(self, attribute_key)

    @property
    def timestamp(self):
        """
        Epoch microseconds of the start of this span, possibly absent if this an incomplete span.

        :return: the span timestamp value
        """
        attribute_key = 'timestamp'
        attribute = get_attribute(self, attribute_key)
        if attribute is None:
            return None
        timestamp = fix_timestamp(attribute)
        set_attribute_value(self, attribute_key, timestamp)
        return timestamp

    @property
    def parent_id(self):
        attribute_key = 'parentId'
        return get_attribute(self, attribute_key)

    @property
    def id(self):
        attribute_key = 'id'
        return get_attribute(self, attribute_key)

    @property
    def kind(self):
        attribute_key = 'kind'
        return Kind.CLIENT

    @property
    def local_service_name(self):
        """
        Local service name property

        :return: the local service name
        """
        return 'lpn'

    @property
    def remote_service_name(self):
        """
        Remote service name property

        :return: the remote service name
        """
        return 'rpn'

    @property
    def tags(self):
        """
        Spans tags are presented with all the binary annotations

        :return: a dictionary containing all binary annotations
        """
        i = iter(self.binary_annotations)
        tags = dict(zip(i, i))
        return tags

    @property
    def binary_annotations(self):
        attribute_key = 'binaryAnnotations'
        binary_annotations = []
        if attribute_key in self.__dict__:
            for _, binary_annotation in enumerate(self.__dict__[attribute_key]):
                binary_annotation = BinaryAnnotation(json.dumps(binary_annotation))
                binary_annotations.append(binary_annotation)
            return binary_annotations
        return None

    @property
    def annotations(self):
        attribute_key = 'annotations'
        annotations = []
        if attribute_key in self.__dict__:
            for _, annotation_data in enumerate(self.__dict__[attribute_key]):
                annotation = Annotation(json.dumps(annotation_data))
                annotations.append(annotation)
            return annotations
        return None


class Kind(Enum):
    CLIENT = 1,
    SERVER = 2,
    PRODUCER = 3,
    CONSUMER = 4


def fix_timestamps(spans):
    if type(spans) is not list:
        return

    timestamp = 'timestamp'

    for span in spans:
        my_dict.update(span, timestamp, fix_timestamp)


def fix_timestamp(timestamp):
    """
    Fix timestamp values.

    This function fixes the timestamp len issue.
    """
    default_timestamp_len = 16
    if len(str(timestamp)) < default_timestamp_len:
        miss_len = default_timestamp_len - len(str(timestamp))
        timestamp = str(timestamp) + ''.join(['0' for _ in range(miss_len)])
        return int(timestamp)
    return timestamp


def get_status_code(span):
    try:
        tags = span.get('tags', False)
        if tags:
            http_status_code = tags.get('http.status_code', False)
            return http_status_code
        return span['tags']['http.status_code']
    except Exception as e:
        logger.error(e)
        return False


def parse_to_spans_array(spans_json_path):
    """
    Parses JSON data to Span Object Array.

    Returns Span Array.
    """
    with open(spans_json_path) as fp:
        span_json = fp.read()
    loaded_json = json.loads(span_json)
    spans_array = []
    for _, json_obj in enumerate(loaded_json):
        spans_array.append(Span(str(json_obj).replace('\'', '\"')))
    return spans_array
