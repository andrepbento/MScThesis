"""
    Author: André Bento
    Date last modified: 16-11-2018
"""
"""
SpanTree represents the entity for handling spans in a tree data structure.
"""
import logging

from treelib import Tree
from treelib.exceptions import NodeIDAbsentError

logger = logging.getLogger(__name__)


class SpanTree(object):
    """ SpanTree object is a representation of spans in a tree """

    def __init__(self, spans_array):
        """Initiate a new SpanTree """
        self.tree = Tree()
        self.tree.create_node()  # root node
        self.root_node = self.tree.root

        self.__generate_span_tree(spans_array)

    def print(self):
        """ Prints the tree using the default tree.show() method """
        self.tree.show(idhidden=False)

    def count_traces(self):
        """
        Counts the number of traces in the span tree

        :return: the number of traces in the span tree
        """
        return len(self.tree.children(self.root_node))

    def count_spans(self):
        """
        Counts the number of spans in the span tree

        :return: the number of spans in the span tree
        """
        return len(self.tree) - 1 - self.count_traces()  # -1: Minus root node

    def span_max_depth(self):
        return self.tree.depth(self.root_node) - 2  # -2: Minus root and trace

    def __generate_span_tree(self, spans_array):
        """ Generates the span tree using a Span array """
        logger.info('generate_span_tree()')
        for span in spans_array:
            trace_id = None
            try:
                trace_id = span.trace_id
                if not self.tree.contains(trace_id):
                    self.tree.create_node(span.timestamp, trace_id, self.root_node)
                parent_id = span.parent_id
                if parent_id is not None:
                    self.tree.create_node(span.timestamp, span.id, parent_id, data=span)
                else:
                    self.tree.create_node(span.timestamp, span.id, trace_id, data=span)
            except NodeIDAbsentError:
                self.tree.create_node(span.timestamp, span.id, trace_id, data=span)
            except Exception as ex:
                logger.error('exception: type({}) msg({})'.format(type(ex), ex))

        logger.debug('spans in tree length/spans_array_length: {}/{}'.format(self.count_spans(),
                                                                             len(spans_array)))
