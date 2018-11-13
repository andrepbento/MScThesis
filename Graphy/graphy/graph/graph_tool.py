"""
TODO: add graph_tool.py doc
"""
import json
import logging

import matplotlib.pyplot as plt
import networkx as nx
import networkx.algorithms as nx_algorithms

from graphy.structures.span_tree import SpanTree
from graphy.utils.zipkin import post_spans, get_dependencies

logger = logging.getLogger(__name__)


class GraphTool:
    """ GraphTool contains a collection of methods to handle SpanTree's and Graphs """

    def __init__(self):
        """Initiate a new GraphTool """
        # Create a MultiGraph instance
        self.G = nx.MultiDiGraph()
        self.span_tree = None

    def draw_graph(self, save=False, show=True):
        """

        :param save: True if
        :param show:
        :return:
        """
        logger.info('draw_graph()')

        nx.draw(self.G, with_labels=True, font_weight='bold')
        plt.axis('off')
        if save:
            plt.savefig("graph.png")
        if show:
            plt.show()

    def generate_graph(self, spans_array, print_span_tree=False, print_graph_data=True):
        logger.info('generate_graph()')

        logger.info('spans_array length: {}'.format(len(spans_array)))

        self.span_tree = SpanTree(spans_array)

        if print_span_tree:
            self.span_tree.print()

        self.__generate_nodes_and_edges()

        if print_graph_data:
            self.print_graph_data()

    def generate_graph_from_zipkin(self, spans_json_path='', print_graph_data=True):
        logger.info('generate_graph_from_zipkin()')

        if spans_json_path:
            if not post_spans(spans_json_path):
                return False
        json_dependencies = get_dependencies()
        dependencies = json.loads(json_dependencies)
        for dependency in dependencies:
            for count in range(dependency['callCount']):
                self.G.add_edge(dependency['parent'], dependency['child'])

        if print_graph_data:
            self.print_graph_data()

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
                span_annotations_len_array.append(len(span.annotations))
                for i, annotation in enumerate(span.annotations):
                    timestamp = annotation.timestamp
                    value = annotation.value
                    value_stack.add(value)
                    endpoints = annotation.endpoints
                    if endpoints is None:
                        raise AttributeError('endpoints not found')
                    endpoints_len_array.append(len(endpoints))
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
            except Exception as ex:
                print(ex)

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
                for i, stack_edge in enumerate(edge):
                    print(stack_edge)
                    self.G.add_edge(stack_edge, stack_edge)
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

        """
        for node in self.span_tree.tree.all_nodes():
            span = node.data
            # root or trace node
            if span is None:
                continue
            kind = span.kind
            if kind == Kind.CLIENT and node.is_leaf():
                print('deferring link to rpc child span')
                continue
            service_name = span.local_service_name
            remote_service_name = span.remote_service_name
            if kind is None:
                if service_name is not None and remote_service_name is not None:
                    kind = Kind.CLIENT
                else:
                    print('non-rpc span; skipping')
                    continue

            if kind is Kind.SERVER or kind is Kind.CONSUMER:
                child = service_name
                parent = remote_service_name
                # if (current == tree)
                if parent is None:
                    print('root\'s peer is unknown; skippin')
                    continue
            elif kind is Kind.CLIENT or kind is Kind.PRODUCER:
                parent = service_name
                child = remote_service_name
            else:
                print('unknown kind; skipping')
                continue

            is_error = True if 'error' in span.tags else False
            if kind == Kind.PRODUCER or kind == Kind.CONSUMER:
                if parent is None or child is None:
                    print("cannot link messaging span to its broker; skipping")
                else:
                    self.__addLink(parent, child, is_error)
                continue

            rpc_ancestor = self.__findRpcAncestor(node)
            rpc_service_name = ''
            if rpc_ancestor is not None:
                rpc_ancestor_name = rpc_ancestor.local_service_name
                if rpc_ancestor_name is not None:
                    if kind == Kind.CLIENT and service_name is not None and rpc_ancestor_name == rpc_service_name:
                        print("detected missing link to client span")
                        self.__addLink(rpc_ancestor_name, service_name, False)  # we don't know if there's an error here
                    if parent is None:
                        parent = rpc_ancestor_name
                    if not is_error and Kind.CLIENT == rpc_ancestor.kind and span.parent_id is not None \
                            and span.parent_id == rpc_ancestor.id:
                        is_error = rpc_ancestor.tags().containsKey("error")

            if parent is None and child is None:
                print("cannot find server ancestor; skipping")
                continue

            self.__addLink(parent, child, is_error)
        """

    def __addLink(self, parent, child, isError):
        if isError is True:
            print('Error')
        else:
            print('!Error')
        self.G.add_edge(parent, child)
        pass

    def __findRpcAncestor(self, node):
        return node

    def diameters(self):
        """
        TODO: convert the GraphTool to use more than one graph

        :return: a list with the diameters of every graph
        """
        return nx_algorithms.diameter(self.G)

    def print_graph_data(self):
        if self.G.number_of_nodes() > 20:
            logger.info('graph_nodes[{}]'.format(self.G.number_of_nodes()))
        else:
            logger.info('graph_nodes[{}]: {}'.format(self.G.number_of_nodes(), self.G.nodes()))
        if self.G.number_of_edges() > 100:
            logger.info('graph_edges[{}]'.format(self.G.number_of_edges()))
        else:
            logger.info('graph_edges[{}]: {}'.format(self.G.number_of_edges(), self.G.edges()))
