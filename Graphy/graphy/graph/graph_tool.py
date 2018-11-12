"""
TODO: add graph_tool.py doc
"""
import logging

import matplotlib.pyplot as plt
import networkx as nx

from graphy.structures.span_tree import SpanTree

logger = logging.getLogger(__name__)


class GraphTool:
    def __init__(self):
        # Create a MultiGraph instance
        self.G = nx.MultiDiGraph()
        self.span_tree = None

    def draw_graph(self, save=False, show=True):
        logger.info('draw_graph()')

        nx.draw(self.G, with_labels=True, font_weight='bold')
        plt.axis('off')
        if save:
            plt.savefig("graph.png")
        if show:
            plt.show()

    def generate_graph(self, spans_array, print_span_tree=False):
        logger.info('generate_graph()')

        logger.info('spans_array length: {}'.format(len(spans_array)))

        self.span_tree = SpanTree(spans_array)

        if print_span_tree:
            self.span_tree.print()

        self.__generate_nodes_and_edges()

        if self.G.number_of_nodes() > 20:
            logger.info('graph_nodes[{}]'.format(self.G.number_of_nodes()))
        else:
            logger.info('graph_nodes[{}]: {}'.format(self.G.number_of_nodes(), self.G.nodes()))
        if self.G.number_of_edges() > 20:
            logger.info('graph_edges[{}]'.format(self.G.number_of_edges()))
        else:
            logger.info('graph_edges[{}]: {}'.format(self.G.number_of_edges(), self.G.edges()))

    def count_edge_occurrence(self):
        logger.info('count_edge_occurrence()')
        # Count each edge occurrence
        edge_type_counter = {}
        for edge in self.G.edges():
            if edge in edge_type_counter:
                edge_type_counter[edge] += 1
            else:
                edge_type_counter[edge] = 1

        logger.info('edge_type_counter[{}]: {}'.format(len(edge_type_counter.keys()), edge_type_counter))
        logger.info('edge_type_sum: {}'.format(sum(edge_type_counter.values())))

    def __generate_nodes_and_edges(self):
        """
        Generates the nodes and edges using the span tree.

        :return: tuple with nodes and edges
        """
        logger.info('generate_nodes_and_edges()')

        attribute_exception_counter = 0

        graph_nodes = set()  # graph_nodes
        graph_edges = []
        graph_arc = set()
        # graph_arc = []

        endpoint_counter = 0
        binary_annotation_endpoint_counter = 0

        value_stack_array = []

        annotation_values = [['sr', 'ss'], ['cs', 'cr']]

        evs_counter = 0
        span_annotations_len_array = []
        endpoints_len_array = []

        for node in self.span_tree.tree.all_nodes():
            span = node.data
            # root or trace node
            if span is None:
                continue
            try:
                value_stack = set()
                endpoint_service_name = None
                annotation_aux = None
                span_annotations_len_array.append(len(span.annotations))
                for i, annotation in enumerate(span.annotations):
                    print(i, str(annotation))
                    # print(index2, ':', str(span.annotation))
                    annotation_aux = annotation
                    timestamp = annotation.timestamp
                    value = annotation.value
                    value_stack.add(value)
                    endpoints = annotation.endpoints
                    endpoints_len_array.append(len(endpoints))
                    printed = False
                    for _, endpoint in enumerate(endpoints):
                        endpoint_counter += 1
                        endpoint_service_name = endpoint.service_name
                        # graph_arc.append(endpoint.get_service_name())
                        graph_arc.add(endpoint.service_name)
                    if i == len(span.annotations) - 1 and list(value_stack) in [annotation_value for annotation_value
                                                                                in annotation_values]:
                        graph_nodes.add(endpoint_service_name)
                # for _, binary_annotation in enumerate(span.binary_annotations):
                value_stack_array.append(value_stack)
            except AttributeError:
                # logger.error('annotation: {}'.format(annotation_aux))
                attribute_exception_counter += 1
                graph_edges.append(graph_arc)
                graph_arc = set()
                continue

        self.G.add_nodes_from(graph_nodes)

        print('Smax', max(span_annotations_len_array))
        print('Smin', min(span_annotations_len_array))
        print('Savg', sum(span_annotations_len_array) / len(span_annotations_len_array))

        print('Tmax', max(endpoints_len_array))
        print('Tmin', min(endpoints_len_array))
        print('Tavg', sum(endpoints_len_array) / len(endpoints_len_array))

        try:
            lens = [len(i) for i in graph_edges]
            print('max', max(lens))
            print('min', min(lens))
            print('avg', sum(lens) / len(lens))
            print('len', len(graph_edges))
        except Exception as ex:
            logging.error('Exception[{}]: {}'.format(type(ex), ex))

        # self.G.add_edges_from(graph_edges)

        for edge in graph_edges:
            if len(edge) == 1:
                # TODO: do something
                continue
            if len(edge) >= 2:
                if len(edge) > 2:
                    # print('>2: ', edge)
                    continue
                edge_aux = None
                for i, stack_edge in enumerate(edge):
                    if i == 0:
                        edge_aux = stack_edge
                        continue
                    self.G.add_edge(edge_aux, stack_edge)
            else:
                logger.error('invalid edge[{}]: {}'.format(len(edge), edge))

        logger.info('attribute_exception_counter: {}'.format(attribute_exception_counter))
        logger.info('endpoint_counter: {}'.format(endpoint_counter))
        logger.info('trace_counter: {}'.format(self.span_tree.count_traces()))
        print('binary_annotation_endpoint_counter:', binary_annotation_endpoint_counter)
