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
from enum import Enum

from graphy.models.annotation import Annotation
from graphy.models.attributes import get_attribute, set_attribute_value
from graphy.models.binary_annotation import BinaryAnnotation


class Span(object):
    def __init__(self, data):
        self.__dict__ = json.loads(data)

    def __str__(self):
        return str(self.__dict__)

    @property
    def trace_id(self):
        attribute_key = 'traceId'
        return get_attribute(self, attribute_key)

    @property
    def name(self):
        attribute_key = 'name'
        return get_attribute(self, attribute_key)

    @property
    def timestamp(self):
        attribute_key = 'timestamp'
        fix_needed, timestamp = fix_timestamp(get_attribute(self, attribute_key))
        if fix_needed:
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
    def binary_annotations(self):
        attribute_key = 'binaryAnnotations'
        binary_annotations = []
        if attribute_key in self.__dict__:
            for _, binary_annotation in enumerate(self.__dict__[attribute_key]):
                binary_annotation = BinaryAnnotation(json.dumps(binary_annotation))
                binary_annotations.append(binary_annotation)
            return binary_annotations
        raise AttributeError(attribute_key)

    @property
    def annotations(self):
        attribute_key = 'annotations'
        annotations = []
        if attribute_key in self.__dict__:
            for _, annotation_data in enumerate(self.__dict__[attribute_key]):
                annotation = Annotation(json.dumps(annotation_data))
                annotations.append(annotation)
            return annotations
        raise AttributeError(attribute_key)


class Kind(Enum):
    CLIENT = 1,
    SERVER = 2,
    PRODUCER = 3,
    CONSUMER = 4


def fix_timestamp(timestamp):
    """
    Fix timestamp values.

    This function fixes the timestamp len issue.
    """
    if len(str(timestamp)) < 16:
        return True, int(str(timestamp) + '000')
    return False, timestamp


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
