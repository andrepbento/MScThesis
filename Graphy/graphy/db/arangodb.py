from pyArango.collection import Collection, Field, Edges
from pyArango.connection import Connection
from pyArango.graph import Graph, EdgeDefinition

from graphy.utils import config


class ArangoDB(object):
    class Services(Collection):
        _fields = {
            'name': Field()
        }

    class ServiceLink(Edges):
        _fields = {
        }

    class ServiceGraph(Graph):
        _edgeDefinitions = [EdgeDefinition("ServiceLink", fromCollections=["Services"], toCollections=["Services"])]
        _orphanedCollections = []

        _fields = {
            'name': Field()
        }

    def __init__(self):
        self._arangodb_config = config.get('ARANGODB')

        self._conn = Connection(arangoURL=self._arangodb_config.get('ARANGO_URL'),
                                username=self._arangodb_config.get('USERNAME'),
                                password=self._arangodb_config.get('PASSWORD'))

        db_name = self._arangodb_config.get('DB_NAME')
        if self._conn.hasDatabase(db_name):
            self._db = self._conn[db_name]
        else:
            self._db = self._conn.createDatabase(db_name)

        if not self._db.hasCollection('Services'):
            self._services = self._db.createCollection('Services')
            self._services.activateCache(self._arangodb_config.get('CACHE_VALUE'))

        if not self._db.hasCollection('ServiceLink'):
            self._service_link = self._db.createCollection('ServiceLink')

    def delete_all(self):
        """ Deletes all collections. """
        self._db.dropAllCollections()
        self.__init__()  # TODO: Starts the database structure

    def delete_graph(self, name):
        """
        Deletes a certain graph.

        :param name: The graph name.
        :return: True if graph was deleted or false if not.
        """
        if self._db.hasGraph(name):
            self._db.graphs[name].delete()
            return True
        return False

    def get_graph(self, name):
        """
        Gets a certain graph.

        :param name: The name of the graph.
        :return: The graph.
        """
        if self._db.hasGraph(name):
            return self._db.graphs[name]
        return None

    def insert_graph(self, name, node_links):
        """
        Inserts a new graph.

        :param name: The name of the graph.
        :param node_links: The links in dict data format.
        :return: The created graph.
        """
        if self._db.hasGraph(name):
            graph = self._db.graphs[name]
        else:
            graph = self._db.createGraph('ServiceGraph', name)

        for node_link in node_links:
            node_from_name = node_link[0]
            node_to_name = node_link[1]
            links = node_link[2].get('weight')

            vertex_1 = self._vertex(graph, node_from_name)
            vertex_2 = self._vertex(graph, node_to_name)

            graph.link('ServiceLink', vertex_1, vertex_2, {'links': links})

        return graph

    def _vertex(self, graph, name):
        """
        Creates or gets a node.

        :param graph: The graph where the node might be.
        :param name: The name of the node.
        :return: The fetched node or the new node.
        """
        collections = self._db.collections['Services']
        node_from = collections.fetchFirstExample({'name': name})
        if node_from:
            key = node_from.response.get('result')[0].get('_key')  # TODO: Remove hard coded gets.
            return collections.fetchDocument(key=str(key))
        else:
            return graph.createVertex('Services', {'name': name})


if __name__ == '__main__':
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

    arango_db = ArangoDB()

    import time

    timestamp1 = time.time()
    timestamp2 = time.time()
    arango_db.delete_all()
    # arango_db.delete_graph('graph')
    graph = arango_db.insert_graph(name='graph', node_links=edges)  # name='graph_{}_{}'.format(timestamp1, timestamp2))
    print(graph)
