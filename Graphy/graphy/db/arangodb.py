"""
    Author: André Bento
    Date last modified: 21-02-2019
"""
from arango import ArangoClient
from profilehooks import profile

from graphy.utils import config

arango_db_config = config.get('ARANGODB')


class ArangoDB(object):
    def __init__(self):
        self._ip = arango_db_config.get('IP')
        self._port = arango_db_config.get('PORT')

        self._username = arango_db_config.get('USERNAME')
        self._password = arango_db_config.get('PASSWORD')

        self._client = ArangoClient(host=self._ip, port=self._port)

        self._db = self._sys_db()

    def _sys_db(self):
        """ Obtain the system database. """
        return self._client.db(name='_system', username=self._username, password=self._password)

    def create_database(self, db_name=arango_db_config.get('DB_NAME')):
        """
        Creates a new database.

        :param db_name: The name of the database.
        :return:
        """
        if not self._sys_db().has_database(db_name):
            self._sys_db().create_database(db_name)

    def delete_database(self, db_name=arango_db_config.get('DB_NAME')):
        """
        Deletes a certain database database.

        :param db_name: The name of the database.
        :return: True if success, False otherwise.
        """
        if self._sys_db().has_database(db_name):
            return self._sys_db().delete_database(db_name)
        return False

    def connect_database(self, name=arango_db_config.get('DB_NAME')):
        """
        Connects to a database.

        :param name: The name of the database.
        :return: The database if exists, None otherwise.
        """
        self._db = self._client.db(name, self._username, self._password)
        return self._db

    def get_graph(self, name):
        """
        Gets a certain graph.

        :param name: The name of the graph.
        :return: The graph or None if it hasn't been found.
        """
        return self._db.graph(name)

    def get_graphs(self):
        """
        Gets all graph names stored in the database.

        :return: A list of graph names.
        """
        graph_names_list = list()
        for graph_dict in self._db.graphs():
            if isinstance(graph_dict, dict):
                graph_names_list.append(graph_dict.get('name'))
        return graph_names_list

    def delete_graph(self, name):
        """
         Deletes a certain graph.

         :param name: The graph name.
         :return: True if graph was deleted or false if not.
         """
        return self._db.delete_graph(name)

    def insert_graph(self, timestamp_start, timestamp_end, node_links):
        """
        Inserts a new graph.

        :param timestamp_end: The start timestamp, in unix timestamp format, of the graph.
        :param timestamp_start: The end timestamp, in unix timestamp format, of the graph.
        :param node_links: The links in dict data format.
        :return: The created graph.
        """
        graph_name = 'graph_{}_{}'.format(timestamp_start, timestamp_end)
        if self._db.has_graph(graph_name):
            graph = self._db.graph(graph_name)
        else:
            graph = self._db.create_graph(graph_name)

        vertex_collection_name = 'Services'  # TODO: Remove hard coded string
        if graph.has_vertex_collection(vertex_collection_name):
            vertex_collection = graph.vertex_collection(vertex_collection_name)
        else:
            vertex_collection = graph.create_vertex_collection(vertex_collection_name)

        edge_collection = self._edge_collection(graph, vertex_collection, timestamp_start, timestamp_end)

        for node_link in node_links:
            node_from_name = node_link[0]
            node_to_name = node_link[1]
            links = node_link[2].get('weight')

            vertex_1 = self._vertex(vertex_collection, node_from_name, {'name': node_from_name})
            vertex_2 = self._vertex(vertex_collection, node_to_name, {'name': node_to_name})

            collection_name = vertex_collection.name
            edge_collection.insert({'_from': '{}/{}'.format(collection_name, vertex_1.get('_key')),
                                    '_to': '{}/{}'.format(collection_name, vertex_2.get('_key')),
                                    'links': links})

        return graph

    def get_graph_edges(self, graph_name):
        """
        Gets the graph edges.

        :param graph_name: The graph name.
        :return: A list of graph edges.
        """
        edge_list = list()
        graph = self.get_graph(graph_name)

        graph_vertex_collections = graph.vertex_collections()
        graph_vertex_collection_name = graph_vertex_collections[0]  # TODO: Try to remove hard coded integer.

        graph_edge_collection = graph.edge_definitions()
        graph_edge_collection_name = graph_edge_collection[0] \
            .get('edge_collection')  # TODO: Try to remove hard coded string and integer.

        for vertex_item in self._db.collection(graph_vertex_collection_name):
            if graph.has_vertex(vertex_item.get('_id')):
                edges = graph.edges(graph_edge_collection_name, vertex_item.get('_id'), direction='out').get('edges')
                edge_list.extend(edges)

        return edge_list

    @staticmethod
    def _edge_collection(graph, vertex_collection, start_timestamp, end_timestamp):
        """
        Gets or creates a edge collection.

        :param graph: The graph where the edge collection might be or should be.
        :param vertex_collection: The vertex collection
        :param start_timestamp: The start timestamp of the collection, in unix timestamp format.
        :param end_timestamp: The end timestamp of the collection, in unix timestamp format.
        :return: The edge collection.
        """
        service_links_edge_collection_name = 'ServiceLinks_{}_{}'.format(start_timestamp, end_timestamp)
        if graph.has_edge_collection(service_links_edge_collection_name):
            return graph.edge_collection(service_links_edge_collection_name)
        else:
            return graph.create_edge_definition(
                edge_collection=service_links_edge_collection_name,
                from_vertex_collections=[vertex_collection.name],
                to_vertex_collections=[vertex_collection.name]
            )

    @staticmethod
    def _vertex(vertex_collection, vertex_key, vertex_attributes):
        """
        Gets or creates a vertex in a certain vertex collection.

        :param vertex_collection: The vertex collection.
        :param vertex_key: The vertex key identifier.
        :param vertex_attributes: The vertex attributes.
        :return:
        """
        if vertex_collection.has({'_key': vertex_key}):
            return vertex_collection.get({'_key': vertex_key})
        else:
            vertex = {'_key': vertex_key}
            vertex.update(vertex_attributes)
            return vertex_collection.insert(vertex)


@profile
def main():
    from graphy.graph.graph_processor import GraphProcessor
    from graphy.utils import zipkin
    from graphy.utils import time as my_time

    graph_processor = GraphProcessor()

    start_date_time_str = "25/06/2018 00:00:00"
    end_date_time_str = "30/06/2018 00:00:00"

    start_timestamp = my_time.to_unix_time_millis(start_date_time_str)
    end_timestamp = my_time.to_unix_time_millis(end_date_time_str)

    dependencies = zipkin.get_dependencies(end_ts=end_timestamp, lookback=end_timestamp - start_timestamp)
    graph_processor.generate_graph_from_zipkin(dependencies)

    nodes = list(graph_processor.graph.nodes(data=True))
    edges = list(graph_processor.graph.edges(data=True))
    print('nodes: {}'.format(nodes))
    print('edges: {}'.format(edges))

    timestamp1 = start_timestamp
    timestamp2 = end_timestamp

    arango_db = ArangoDB()
    arango_db.delete_database()
    arango_db.create_database()
    arango_db.connect_database()
    graph = arango_db.insert_graph(start_timestamp, end_timestamp,
                                   edges)  # name='graph_{}_{}'.format(timestamp1, timestamp2))
    graph_edge_list = arango_db.get_graph_edges(graph.name)
    edges1 = list(graph_processor.generate_graph_from_edge_list(graph_edge_list).edges(data=True))


if __name__ == '__main__':
    main()
