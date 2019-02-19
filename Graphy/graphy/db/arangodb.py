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
        self._db.dropAllCollections()

    def get_graphs(self, name=None):
        if name and self._db.hasGraph(name):
            self._db.graph(name)
        else:
            self._db_conn.graphs()

    def delete_graphs(self, names=None):
        if not names:
            names = self._db_conn.graphs()

        for name in names:
            self._db_conn.delete_graph(name)

    def insert_graph(self, name, node_links):
        if self._db.hasGraph(name):
            graph = self._db.graphs[name]
        else:
            graph = self._db.createGraph('ServiceGraph', name)

        for node_link in node_links:
            node_from = node_link[0]
            node_to = node_link[1]
            links = node_link[2].get('weight')
            collections = self._db.collections['Services']
            example = collections.fetchFirstExample({'name': node_from})
            v1 = graph.createVertex('Services', {'name': node_from})
            v2 = graph.createVertex('Services', {'name': node_to})
            graph.link('ServiceLink', v1, v2, {'links': links})

    def update_node(self, vertex_collection):
        vertex_collection.update({'_key': 'service_name_1', 'data': '0.8'})


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
    # arango_db.delete_all()
    arango_db.insert_graph(name='graph', node_links=edges)  # name='graph_{}_{}'.format(timestamp1, timestamp2))

    # var = arango_db.get_graphs().
