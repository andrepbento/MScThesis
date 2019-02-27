"""
    Author: André Bento
    Date last modified: 27-02-2019
"""
from collections import defaultdict

import matplotlib.pyplot as plt
import networkx as nx
import networkx.algorithms as nx_algorithms

from graphy.models.span_tree import SpanTree
from graphy.utils import logger as my_logger

logger = my_logger.setup_logging(__name__)


class GraphProcessor:
    """ GraphProcessor contains a collection of methods to handle Graphs. """

    def __init__(self):
        """ Initiate a new GraphProcessor. """
        self.__graph = nx.MultiDiGraph()

        self.__start_timestamp = None
        self.__end_timestamp = None

        self.span_tree = None

    @property
    def graph(self):
        return self.__graph

    def generate_graph(self, tuple_list):
        """
        Generates the graph using the tuple list.

        :param tuple_list: The tuple list with the from and to nodes.
        :return: Generated graph.
        """
        self.__graph.add_edges_from(tuple_list)
        return self.__graph

    def generate_graph_from_spans(self, spans_array):
        """
        Generates the graph using the spans array data.

        :param spans_array: Array of span objects.
        """
        # TODO: Check if it is needed or should be removed.
        self.span_tree = SpanTree(spans_array)
        # Generate nodes and edges
        self.__generate_nodes_and_edges()

    def generate_graph_from_zipkin(self, dependencies, start_timestamp, end_timestamp):
        """
        Generates the graph using the Dependencies from Zipkin.

        :param dependencies: Graph dependencies data in Zipkin format.
        :param start_timestamp: Start unix timestamp of the graph.
        :param end_timestamp: End unix timestamp of the graph.
        :return: Generated graph.
        """
        if start_timestamp == self.__start_timestamp and end_timestamp == self.__end_timestamp:
            return self.__graph

        self.__graph.clear()
        for dependency in dependencies:
            self.__graph.add_edge(dependency['parent'],
                                  dependency['child'],
                                  weight=dependency['callCount'])
        return self.__graph

    def generate_graph_from_edge_list(self, edge_list, start_timestamp, end_timestamp):
        """
        Generates the graph using a list of edges.

        :param edge_list: A list edges in ArangoDB format.
        :param start_timestamp: Start unix timestamp of the graph.
        :param end_timestamp: End unix timestamp of the graph.
        :return: Generated graph.
        """
        if start_timestamp == self.__start_timestamp and end_timestamp == self.__end_timestamp:
            return self.__graph

        self.__graph.clear()
        for edge in edge_list:
            node_from = edge.get('_from').split('/')[-1]
            node_to = edge.get('_to').split('/')[-1]
            call_count = edge.get('links')
            if node_from and node_to and call_count:
                self.__graph.add_edge(node_from, node_to, weight=call_count)
        return self.__graph

    @staticmethod
    def graphs_difference(first_graph, second_graph, graph_name=None):
        """
        Performs the difference between two graphs.

        :param first_graph: The first named Graph in NetworkX MultiDiGraph format.
        :param second_graph: The second named Graph in NetworkX MultiDiGraph format.
        :param graph_name: The name of the resulting graph.
        :return: The resulting difference between the graphs.
        """
        g_diff = nx.MultiDiGraph()
        graph_1 = first_graph.copy()  # Copy to preserve values.
        graph_2 = second_graph.copy()

        # Cycle through all edges in G.
        for n in graph_1.edges:
            if n not in graph_2.edges:
                edge_weight = graph_1.get_edge_data(n[0], n[1])[0].get('weight')
                edge_weight = str(int(edge_weight) * -1)  # Lost node.
                g_diff.add_edge(n[0], n[1], weight=edge_weight)
            else:
                first_edge_weight = graph_1.get_edge_data(n[0], n[1])[0].get('weight')
                second_edge_weight = graph_2.get_edge_data(n[0], n[1])[0].get('weight')
                if first_edge_weight != second_edge_weight:
                    g_diff.add_edge(n[0], n[1], weight=second_edge_weight - first_edge_weight)
                graph_2.remove_edge(n[0], n[1])  # Remove edge to reduce size.

        # Cycle through all remaining edges in second_graph.
        for n in graph_2.edges:
            if n not in graph_1.edges:
                edge_weight = graph_2.get_edge_data(n[0], n[1])[0].get('weight')
                g_diff.add_edge(n[0], n[1], weight=edge_weight)

        if graph_name is None:
            start_timestamp = graph_1.name.split('_')[1]
            end_timestamp = graph_2.name.split('_')[-1]
            graph_name = 'graph_{}_{}'.format(start_timestamp, end_timestamp)
        g_diff.name = graph_name

        return g_diff

    def draw_graph(self, save=False, show=False):
        """
        Draw the graph using the data presented in the graph tool.

        :param save: Save graph to a file.
        :param show: Show the image after saving.
        """
        if save is False and show is False:
            return

        logger.info('draw_graph()')

        nx.draw(self.__graph, with_labels=True, font_weight='bold')
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
        """ Print graph data. """
        if not print_graph_data:
            logger.info('skipping print_graph_data()')
            return

        logger.info('print_graph_data()')

        self.__print_nodes_edges()
        self.__count_edge_occurrence()

    def __print_nodes_edges(self, max_nodes=20, max_edges=100):
        """ Prints the number of edges and nodes """

        # Print nodes and edge numbers
        if self.__graph.number_of_nodes() > max_nodes:
            logger.info('graph_nodes[{}]'.format(self.__graph.number_of_nodes()))
        else:
            logger.info('graph_nodes[{}]: {}'.format(self.__graph.number_of_nodes(), self.__graph.nodes()))
        if self.__graph.number_of_edges() > max_edges:
            logger.info('graph_edges[{}]'.format(self.__graph.number_of_edges()))
        else:
            logger.info('graph_edges[{}]: {}'.format(self.__graph.number_of_edges(), self.__graph.edges()))

    def __count_edge_occurrence(self):
        """ Prints the number of edges types and their sum """
        logger.info('count_edge_occurrence()')
        # Count each edge occurrence
        edge_type_counter = {}
        for edge in self.__graph.edges():
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
            return nx_algorithms.degree_pearson_correlation_coefficient(self.__graph)
        except Exception as ex:
            logger.error('cannot calculate degree assortativity: {}'.format(ex))
        return -1

    def __average_neighbor_degree(self):
        """
        Calculates the average neighbor degree of the current graph

        :return: a dict with the average neighbor degree of each node
        """
        try:
            return nx_algorithms.average_neighbor_degree(self.__graph)
        except Exception as ex:
            logger.error('cannot calculate average neighbor degree: {}'.format(ex))
        return -1

    def __average_degree_connectivity(self):
        """
        Calculates the average degree connectivity of the current graph

        :return: a dict with the average neighbor degree of each node
        """
        try:
            return nx_algorithms.average_degree_connectivity(self.__graph)
        except Exception as ex:
            logger.error('cannot calculate average degree connectivity : {}'.format(ex))
        return -1

    def __mixing(self):
        """
        Calculates the mixing matrix for degree

        :return: a dict representation of mixing matrix for degree
        """
        try:
            return nx_algorithms.degree_mixing_dict(self.__graph)
        except Exception as ex:
            logger.error('cannot calculate mixing matrix: {}'.format(ex))
        return -1

    # Boundary Algorithms ----------------------------------------------------------------------------------------------
    def __node_boundaries(self):
        # TODO: not finished
        node_boundaries = dict()
        for node in self.__graph.nodes:
            node_boundaries[node] = nx_algorithms.node_boundary(self.__graph, node)

    # Components Algorithms --------------------------------------------------------------------------------------------

    def __number_connected_components(self):
        return nx_algorithms.number_connected_components(self.__graph.to_undirected())

    def __connected_components(self):
        return nx_algorithms.connected_components(self.__graph.to_undirected())

    def __number_attracting_components(self):
        return nx_algorithms.number_attracting_components(self.__graph)

    # Cycles Algorithms ------------------------------------------------------------------------------------------------

    def __count_simple_cycles(self):
        return len(list(nx_algorithms.simple_cycles(self.__graph)))

    def __count_recursive_simple_cycles(self):
        return len(list(nx_algorithms.recursive_simple_cycles(self.__graph)))

    def __find_cycle(self):
        try:
            return nx_algorithms.find_cycle(self.__graph)
        except Exception as ex:
            logger.error('cannot find cycle in the current graph: {}'.format(ex))
        return -1

    def __minimum_cycle_basis(self):
        try:
            return nx_algorithms.minimum_cycle_basis(self.__graph.to_undirected())
        except Exception as ex:
            logger.error('cannot calculate minimum cycle basis for this kind of graph: {}'.format(ex))
        return -1

    # Directed Acyclic Graphs Algorithms -------------------------------------------------------------------------------

    def __is_directed_acyclic_graph(self):
        """
        Checks if the graph is acyclic

        :return: the list of nodes in center or a empty list
        """
        return nx_algorithms.is_directed_acyclic_graph(self.__graph)

    # Distance Measures Algorithms -------------------------------------------------------------------------------------

    def __center(self):
        """
        Calculates the center of the current graph

        :return: the list of nodes in center or a empty list
        """
        try:
            return nx_algorithms.center(self.__graph.to_undirected())  # Only works with undirected graphs
        except Exception as ex:
            logger.error('cannot obtain the list of nodes in the center: {}'.format(ex))
        return []

    def __diameter(self):
        """
        Calculates the diameter of the current graph

        :return: the diameter of the graph or -1
        """
        try:
            return nx_algorithms.diameter(self.__graph.to_undirected())  # Only works with undirected graphs
        except Exception as ex:
            logger.error('cannot calculate graph diameter: {}'.format(ex))
        return -1

    def __periphery(self):
        if nx_algorithms.is_strongly_connected(self.__graph) is False:
            logger.error('cannot calculate graph periphery: Graph is not strongly connected')
            return []
        return nx_algorithms.periphery(self.__graph)

    def __radius(self):
        if nx_algorithms.is_strongly_connected(self.__graph) is False:
            logger.error('cannot calculate graph radius: Graph is not strongly connected')
            return []
        return nx_algorithms.radius(self.__graph)

    # Shortest Paths Algorithms ----------------------------------------------------------------------------------------

    def __shortest_path(self):
        return nx_algorithms.shortest_path(self.__graph)

    def __all_pairs_shortest_path(self):
        return nx_algorithms.all_pairs_shortest_path(self.__graph)

    def __floyd_warshall(self):
        return nx_algorithms.floyd_warshall(self.__graph)

    def degrees(self, sort: bool = True) -> list:
        """
        Calculates the degree for all nodes.
        Node degree is the sum of all input and output edges.

        :param sort: sort the list by degree in reverse order.
        :return: a tuple list containing all the nodes and their corresponding degree.
        """
        # TODO: The following lines of code can be used to get the input or output degree from all nodes
        # in_degree = self.G.in_degree
        # out_degree = self.G.out_degree
        return sorted(self.__graph.degree, key=lambda tup: tup[1], reverse=sort)

    def edges_call_count(self, service_name: str = None, sort: bool = True) -> list:
        """
        Calculates the number of calls for all nodes or for a specific node.

        :param service_name: the service node name.
        :param sort:
        :return:
        """
        # TODO: The following lines of code can be used to get the input and output from all edges
        # in_edges = list(self.__graph.in_edges(data=True))
        # out_edges = list(self.__graph.out_edges(data=True))

        edges_call_count = dict()

        if service_name:
            edges = list(self.__graph.edges(service_name, data=True))
        else:
            edges = list(self.__graph.edges(data=True))

        for edge in edges:
            service_from = edge[0]
            call_count = edge[2].get('weight')
            if service_from in edges_call_count:
                edges_call_count[service_from] += call_count
            else:
                edges_call_count[service_from] = call_count

        return sorted(edges_call_count.items(), key=lambda x: x[1], reverse=sort)

    def neighbors(self, service_name: str = None) -> dict:
        """
        Calculates the out neighbors for all nodes or for a specific node.

        :param service_name: the service node name.
        :return: a dictionary containing all the nodes and their corresponding list of neighbors.
        """
        debug_message = ''
        neighbors = defaultdict(list)

        service_nodes = self.__graph.nodes
        if service_name:
            service_nodes = [service_name]

        for node in service_nodes:
            debug_message += '\nNode: {}'.format(node)
            for i, neighbor in enumerate(self.__graph.neighbors(node)):
                debug_message += '\n\t{}: {}'.format(i, neighbor)
                neighbors[node].append(neighbor)
        logger.debug(debug_message)
        return neighbors
