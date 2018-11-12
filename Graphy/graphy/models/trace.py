"""
TODO: add trace.py doc
"""


class Trace(object):
    def __init__(self, id):
        self.id = id

    @property
    def id(self):
        return self.id

    @id.setter
    def id(self, value):
        self._id = value
