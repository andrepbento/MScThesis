"""
    Author: André Bento
    Date last modified: 08-11-2018
"""
import json

from graphy.models.attributes import get_attribute


class BinaryAnnotation(object):
    def __init__(self, data):
        self.__dict__ = json.loads(data)

    def __str__(self):
        return str(self.__dict__)

    @property
    def protocol(self):
        attribute_key = 'protocol'
        return get_attribute(self, attribute_key)

    @property
    def http_url(self):
        attribute_key = 'http.url'
        return get_attribute(self, attribute_key)

    @property
    def http_status_code(self):
        attribute_key = 'http.status_code'
        return get_attribute(self, attribute_key)

    @property
    def endpoint(self):
        attribute_key = 'enpoint'
        return get_attribute(self, attribute_key)
