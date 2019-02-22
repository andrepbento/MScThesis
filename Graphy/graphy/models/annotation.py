"""
    Author: André Bento
    Date last modified: 12-11-2018
"""
import json

from graphy.models.attributes import get_attribute
from graphy.models.endpoint import Endpoint


class Annotation(object):
    def __init__(self, data):
        self.__dict__ = json.loads(data)

    def __str__(self):
        return str(self.__dict__)

    @property
    def timestamp(self):
        attribute = 'timestamp'
        return get_attribute(self, attribute)

    @property
    def value(self):
        attribute = 'value'
        return get_attribute(self, attribute)

    @property
    def endpoints(self):
        attribute = 'endpoint'
        endpoints = []
        endpoint_data = get_attribute(self, attribute)
        if endpoint_data is None:
            return None
        endpoints.append(Endpoint(json.dumps(endpoint_data)))
        return endpoints
