"""
TODO: add endpoint.py doc
"""
import json

from graphy.models.attributes import get_attribute


class Endpoint(object):
    def __init__(self, data):
        self.__dict__ = json.loads(data)

    def __str__(self):
        return str(self.__dict__)

    @property
    def service_name(self):
        attribute = 'serviceName'
        return get_attribute(self, attribute)

    @property
    def ipv4(self):
        attribute = 'ipv4'
        return get_attribute(self, attribute)
