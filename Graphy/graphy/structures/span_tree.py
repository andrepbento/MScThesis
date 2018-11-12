"""
SpanTree represents the entity for handling spans in a tree data structure.
"""
import logging

from treelib import Tree
from treelib.exceptions import NodeIDAbsentError

logger = logging.getLogger(__name__)


class SpanTree(object):
    def __init__(self, spans_array):
        self.tree = Tree()
        self.tree.create_node()  # root node
        self.root_node = self.tree.root

        self.__generate_span_tree(spans_array)

    def print(self):
        result = self.tree.show(idhidden=False)
        if result:
            print(result)

    def count_traces(self):
        return len(self.tree.children(self.root_node))

    def __count_spans(self):
        return len(self.tree) - 1 - self.count_traces()  # -1: Minus root node

    def __generate_span_tree(self, spans_array):
        logger.info('generate_span_tree()')
        # node_absent_exception = 0
        # absent_span_array = []
        for span in spans_array:
            trace_id = None
            try:
                trace_id = span.trace_id
                if not self.tree.contains(trace_id):
                    self.tree.create_node(span.timestamp, trace_id, self.root_node)
                parent_id = span.parent_id
                self.tree.create_node(span.timestamp, span.id, parent_id, data=span)
            except AttributeError:
                self.tree.create_node(span.timestamp, span.id, trace_id, data=span)
            except NodeIDAbsentError:
                # node_absent_exception += 1
                # absent_span_array.append(span)
                self.tree.create_node(span.timestamp, span.id, trace_id, data=span)
            except Exception as ex:
                logger.error('exception: type({}) msg({})'.format(type(ex), ex))

        # absent_span_trace_id_stack = Stack()
        # for absent_span in absent_span_array:
        #    absent_span_trace_id_stack.push(absent_span.trace_id)
        # logger.debug(
        #    'absent_span_trace_id_stack[{}]: {}'.format(len(absent_span_trace_id_stack), absent_span_trace_id_stack))

        logger.debug('spans in tree length/spans_array_length: {}/{}'.format(self.__count_spans(),
                                                                             len(spans_array)))
        # logger.debug('node_absent_exception: {}'.format(node_absent_exception))
