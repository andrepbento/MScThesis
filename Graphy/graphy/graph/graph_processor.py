"""
    Author: André Bento
    Date last modified: 21-02-2019
"""
import logging
from collections import defaultdict

import matplotlib.pyplot as plt
import networkx as nx
import networkx.algorithms as nx_algorithms

from graphy.models.span_tree import SpanTree

logger = logging.getLogger(__name__)


class GraphProcessor:
    """ GraphProcessor contains a collection of methods to handle Graphs. """

    def __init__(self):
        """ Initiate a new GraphProcessor. """
        self._graph = nx.MultiDiGraph()
        self.span_tree = None

    @property
    def graph(self):
        return self._graph

    def generate_graph(self, tuple_list):
        """
        TODO: Add doc.

        :param tuple_list:
        :return:
        """
        self._graph.add_edges_from(tuple_list)

    def generate_graph_from_spans(self, spans_array):
        """
        Generates the graph using the spans array data

        :param spans_array: array of span objects
        """
        logger.info('generate_graph()')

        # Create the span tree to generate the graph
        self.span_tree = SpanTree(spans_array)
        # Generate nodes and edges
        self.__generate_nodes_and_edges()

    def generate_graph_from_zipkin(self, dependencies):
        """
        Generates the graph using the Dependencies from Zipkin.

        :param dependencies: Graph dependencies data in Zipkin format.
        :return: Generated graph.
        """
        logger.debug('generate_graph_from_zipkin()')
        self._graph.clear()
        for dependency in dependencies:
            self._graph.add_edge(dependency['parent'],
                                 dependency['child'],
                                 weight=dependency['callCount'])
        return self._graph

    def generate_graph_from_edge_list(self, edge_list):
        """
        Generates the graph using a list of edges.

        :param edge_list: A list edges in ArangoDB format.
        :return: Generated graph.
        """
        logger.debug('generate_graph_from_edge_list()')
        self._graph.clear()
        for edge in edge_list:
            node_from = edge.get('_from').split('/')[-1]
            node_to = edge.get('_to').split('/')[-1]
            call_count = edge.get('links')
            if node_from and node_to and call_count:
                self._graph.add_edge(node_from, node_to, weight=call_count)
        return self._graph

    @staticmethod
    def graphs_difference(graph_1, graph_2):
        """
        TODO: Add doc.

        :param graph_1:
        :param graph_2:
        :return:
        """
        graph_diff = nx.difference(graph_1, graph_2)
        return graph_diff

    @staticmethod
    def graphs_symmetric_difference(graph1, graph2):
        """
        TODO: Add doc.

        :param graph1:
        :param graph2:
        :return:
        """
        graph_symetric_diff = nx.symmetric_difference(graph1, graph2)
        return graph_symetric_diff

    @staticmethod
    def graphs_edges_difference(graph_1, graph_2):
        """
        TODO: Add doc.

        :param graph_1:
        :param graph_2:
        :return:
        """
        edges_diff = dict()

        graph_1_edges = graph_1.edges(data=True)
        graph_2_edges = graph_2.edges(data=True)

        # if graph_1_edges and graph_2_edges:
        #    edges_diff = {k: graph_2_edges.get('_adjdic')[k]
        #                  for k in set(graph_2_edges.get('_adjdic')) - set(graph_1_edges.get('_adjdic'))}

        return edges_diff
        # TODO: Perform difference.

    @staticmethod
    def graphs_nodes_difference(graph_1, graph_2):
        """
        TODO: Add doc.

        :param graph_1:
        :param graph_2:
        :return:
        """
        nodes_diff = dict()

        graph_1_nodes = list(graph_1.nodes)
        graph_2_nodes = list(graph_2.nodes)

        from graphy.utils import list as my_list
        nodes_diff_1 = my_list.diff(graph_1_nodes, graph_2_nodes)
        nodes_diff_2 = my_list.diff(graph_2_nodes, graph_1_nodes)
        print('List1.len:', len(graph_1_nodes))
        print('List2.len:', len(graph_2_nodes))
        print('List.diff(1-2):', nodes_diff_1)
        print('List.diff(2-1):', nodes_diff_2)

        return nodes_diff_1

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

        self._graph.add_nodes_from(graph_nodes)

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
                    # print(stack_edge)
                    self._graph.add_edge(stack_edge, stack_edge)
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
                    self._graph.add_edge(edge_aux, stack_edge)
            else:
                logger.error('invalid edge[{}]: {}'.format(len(edge), edge))

        logger.debug('attribute_exception_counter: {}'.format(attribute_exception_counter))
        logger.debug('endpoint_counter: {}'.format(endpoint_counter))
        logger.debug('trace_counter: {}'.format(self.span_tree.count_traces()))
        logger.debug('binary_annotation_endpoint_counter: {}'.format(binary_annotation_endpoint_counter))

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

    def draw_graph(self, save=False, show=False):
        """
        Draw the graph using the data presented in the graph tool.

        :param save: Save graph to a file.
        :param show: Show the image after saving.
        """
        if save is False and show is False:
            return

        logger.info('draw_graph()')

        nx.draw(self._graph, with_labels=True, font_weight='bold')
        plt.axis('off')
        if save:
            plt.savefig("graph.png")
        if show:
            plt.show()

    def log_span_tree_data(self, print_span_tree_data=True):
        """ Print span tree metadata to logger """
        if not print_span_tree_data:
            logger.info('skipping print_span_tree_data()')
            return

        logger.info('print_span_tree_data()')

        self.span_tree.print()
        logger.info('traces: {}'.format(self.span_tree.count_traces()))
        logger.info('spans: {}'.format(self.span_tree.count_spans()))
        logger.info('spans_max_depth: {}'.format(self.span_tree.span_max_depth()))

    def print_graph_data(self, print_graph_data=True):
        """ Print graph metadata to logger """
        if not print_graph_data:
            logger.info('skipping print_graph_data()')
            return

        logger.info('print_graph_data()')

        self.__print_nodes_edges()
        self.__count_edge_occurrence()

    def __print_nodes_edges(self, max_nodes=20, max_edges=100):
        """ Prints the number of edges and nodes """

        # Print nodes and edge numbers
        if self._graph.number_of_nodes() > max_nodes:
            logger.info('graph_nodes[{}]'.format(self._graph.number_of_nodes()))
        else:
            logger.info('graph_nodes[{}]: {}'.format(self._graph.number_of_nodes(), self._graph.nodes()))
        if self._graph.number_of_edges() > max_edges:
            logger.info('graph_edges[{}]'.format(self._graph.number_of_edges()))
        else:
            logger.info('graph_edges[{}]: {}'.format(self._graph.number_of_edges(), self._graph.edges()))

    def __count_edge_occurrence(self):
        """ Prints the number of edges types and their sum """
        logger.info('count_edge_occurrence()')
        # Count each edge occurrence
        edge_type_counter = {}
        for edge in self._graph.edges():
            if edge in edge_type_counter:
                edge_type_counter[edge] += 1
            else:
                edge_type_counter[edge] = 1

        logger.info('edge_type_counter[{}]: {}'.format(len(edge_type_counter.keys()), edge_type_counter))
        logger.info('edge_type_sum: {}'.format(sum(edge_type_counter.values())))

    def generate_graph_statistics(self, print_graph_statistics=True):
        """ Print graph statistics to logger """
        if not print_graph_statistics:
            logger.info('skipping generate_graph_statistics()')
            return

        logger.info('generate_graph_statistics()')

        logger.info('Assortativity Algorithms')
        logger.info('assortativity: {}'.format(self.__assortativity()))
        logger.info('average neighbor degree: {}'.format(self.__average_neighbor_degree()))
        logger.info('average degree connectivity: {}'.format(self.__average_degree_connectivity()))
        logger.info('k nearest neighbors: {}'.format(self.__mixing()))

        logger.info('Boundaries Algorithms')
        logger.info('node boundaries: {}'.format(self.__node_boundaries()))

        logger.info('Components Algorithms')
        logger.info('number of connected components: {}'.format(self.__number_connected_components()))
        logger.info('connected components: {}'.format((str(list(self.__connected_components())))))
        logger.info('number of attracting components: {}'.format(self.__number_attracting_components()))

        logger.info('Cycles Algorithms')
        logger.info('number of simple cycles: {}'.format(self.__count_simple_cycles()))
        logger.info('number of recursive simple cycles: {}'.format(self.__count_recursive_simple_cycles()))
        logger.info('graph cycle found: {}'.format(self.__find_cycle()))
        logger.info('minimum cycle basis: {}'.format(self.__minimum_cycle_basis()))

        logger.info('Directed Acyclic Graph Algorithms')
        logger.info('is directed acyclic graph: {}'.format(self.__is_directed_acyclic_graph()))

        logger.info('Distance Measures Algorithms')
        logger.info('center: {}'.format(self.__center()))
        logger.info('diameter: {}'.format(self.__diameter()))
        logger.info('periphery: {}'.format(self.__periphery()))
        logger.info('radius: {}'.format(self.__radius()))

        logger.info('Shortest Path Algorithms')
        logger.info('shortest path: {}'.format(self.__shortest_path()))
        # for path in self.__all_pairs_shortest_path():
        #    print(path)
        # logger.info('all pairs shortest path: {}'.format()
        logger.info('floyd warshall: {}'.format(self.__floyd_warshall()))

        logger.info('Other Algorithms')
        logger.info('neighbors: {}'.format(self.all_neighbors()))

        # TODO: maybe convert the GraphTool to use more than one graph
        # TODO: problem -> # Found infinite path length because the digraph is not strongly connected

    # Assortativity Algorithms -----------------------------------------------------------------------------------------

    def __assortativity(self):
        """
        Calculates the degree assortativity of graph

        :return: the degree assortativity of graph
        """
        try:
            return nx_algorithms.degree_pearson_correlation_coefficient(self._graph)
        except Exception as ex:
            logger.error('cannot calculate degree assortativity: {}'.format(ex))
        return -1

    def __average_neighbor_degree(self):
        """
        Calculates the average neighbor degree of the current graph

        :return: a dict with the average neighbor degree of each node
        """
        try:
            return nx_algorithms.average_neighbor_degree(self._graph)
        except Exception as ex:
            logger.error('cannot calculate average neighbor degree: {}'.format(ex))
        return -1

    def __average_degree_connectivity(self):
        """
        Calculates the average degree connectivity of the current graph

        :return: a dict with the average neighbor degree of each node
        """
        try:
            return nx_algorithms.average_degree_connectivity(self._graph)
        except Exception as ex:
            logger.error('cannot calculate average degree connectivity : {}'.format(ex))
        return -1

    def __mixing(self):
        """
        Calculates the mixing matrix for degree

        :return: a dict representation of mixing matrix for degree
        """
        try:
            return nx_algorithms.degree_mixing_dict(self._graph)
        except Exception as ex:
            logger.error('cannot calculate mixing matrix: {}'.format(ex))
        return -1

    # Boundary Algorithms ----------------------------------------------------------------------------------------------
    def __node_boundaries(self):
        # TODO: not finished
        node_boundaries = dict()
        for node in self._graph.nodes:
            node_boundaries[node] = nx_algorithms.node_boundary(self._graph, node)

    # Components Algorithms --------------------------------------------------------------------------------------------

    def __number_connected_components(self):
        return nx_algorithms.number_connected_components(self._graph.to_undirected())

    def __connected_components(self):
        return nx_algorithms.connected_components(self._graph.to_undirected())

    def __number_attracting_components(self):
        return nx_algorithms.number_attracting_components(self._graph)

    # Cycles Algorithms ------------------------------------------------------------------------------------------------

    def __count_simple_cycles(self):
        return len(list(nx_algorithms.simple_cycles(self._graph)))

    def __count_recursive_simple_cycles(self):
        return len(list(nx_algorithms.recursive_simple_cycles(self._graph)))

    def __find_cycle(self):
        try:
            return nx_algorithms.find_cycle(self._graph)
        except Exception as ex:
            logger.error('cannot find cycle in the current graph: {}'.format(ex))
        return -1

    def __minimum_cycle_basis(self):
        try:
            return nx_algorithms.minimum_cycle_basis(self._graph.to_undirected())
        except Exception as ex:
            logger.error('cannot calculate minimum cycle basis for this kind of graph: {}'.format(ex))
        return -1

    # Directed Acyclic Graphs Algorithms -------------------------------------------------------------------------------

    def __is_directed_acyclic_graph(self):
        """
        Checks if the graph is acyclic

        :return: the list of nodes in center or a empty list
        """
        return nx_algorithms.is_directed_acyclic_graph(self._graph)

    # Distance Measures Algorithms -------------------------------------------------------------------------------------

    def __center(self):
        """
        Calculates the center of the current graph

        :return: the list of nodes in center or a empty list
        """
        try:
            return nx_algorithms.center(self._graph.to_undirected())  # Only works with undirected graphs
        except Exception as ex:
            logger.error('cannot obtain the list of nodes in the center: {}'.format(ex))
        return []

    def __diameter(self):
        """
        Calculates the diameter of the current graph

        :return: the diameter of the graph or -1
        """
        try:
            return nx_algorithms.diameter(self._graph.to_undirected())  # Only works with undirected graphs
        except Exception as ex:
            logger.error('cannot calculate graph diameter: {}'.format(ex))
        return -1

    def __periphery(self):
        if nx_algorithms.is_strongly_connected(self._graph) is False:
            logger.error('cannot calculate graph periphery: Graph is not strongly connected')
            return []
        return nx_algorithms.periphery(self._graph)

    def __radius(self):
        if nx_algorithms.is_strongly_connected(self._graph) is False:
            logger.error('cannot calculate graph radius: Graph is not strongly connected')
            return []
        return nx_algorithms.radius(self._graph)

    # Shortest Paths Algorithms ----------------------------------------------------------------------------------------

    def __shortest_path(self):
        return nx_algorithms.shortest_path(self._graph)

    def __all_pairs_shortest_path(self):
        return nx_algorithms.all_pairs_shortest_path(self._graph)

    def __floyd_warshall(self):
        return nx_algorithms.floyd_warshall(self._graph)

    def degrees(self, sort=True):
        """
        Calculates the degree for all nodes.
        Node degree is the sum of all input and output edges.

        :param sort: sort the list by degree in reverse order.
        :return: a tuple list containing all the nodes and their corresponding degree.
        """
        # TODO: The following lines of code can be used to get the input or output degree from all nodes
        # in_degree = self.G.in_degree
        # out_degree = self.G.out_degree
        degrees = self._graph.degree
        return sorted(degrees, key=lambda tup: tup[1], reverse=sort)

    def neighbors(self, service_name=None):
        """
        Calculates the out neighbors for all nodes or for a specific node.

        :param service_name: the service node name.
        :return: a dictionary containing all the nodes and their corresponding list of neighbors.
        """
        debug_message = ''
        neighbors = defaultdict(list)

        service_nodes = self._graph.nodes
        if service_name:
            service_nodes = [service_name]

        # TODO: The following lines of code can be used to get the input and output from all nodes
        # in_edges = self.G.in_edges
        # out_edges = self.G.out_edges

        for node in service_nodes:
            debug_message += '\nNode: {}'.format(node)
            for i, neighbor in enumerate(self._graph.neighbors(node)):
                debug_message += '\n\t{}: {}'.format(i, neighbor)
                neighbors[node].append(neighbor)
        logger.debug(debug_message)
        return neighbors

    def number_of_edges(self, service_name=None):
        """
        Calculates the number of edges for all nodes or for a specific node.

        :param service_name: the service node name.
        :return:
        """
        services = self._graph.nodes
        if service_name:
            services = [service_name]

        for service in services:
            for service_neighbor in (self._graph.neighbors(service)):
                n_edges = self._graph.number_of_edges(service, service_neighbor)
                print(service, ':', service_neighbor, ':', n_edges)
