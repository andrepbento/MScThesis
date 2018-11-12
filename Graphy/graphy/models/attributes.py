"""
TODO: add attributes.py doc
"""


def get_attribute(self, attribute_key):
    if attribute_key in self.__dict__:
        return self.__dict__[attribute_key]
    raise AttributeError(attribute_key)


def set_attribute_value(self, attribute_key, value):
    if attribute_key in self.__dict__:
        self.__dict__[attribute_key] = value
        return self.__dict__[attribute_key]
    raise AttributeError(attribute_key)
