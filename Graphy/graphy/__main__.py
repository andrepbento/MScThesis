import logging
import logging.config
import os
import time

import yaml

from graphy.graph.graph_tool import GraphTool
from graphy.models.span import parse_to_spans_array
from graphy.utils.files import get_data_path
from graphy.utils.profile import profile

logger = logging.getLogger(__name__)


@profile
def main():
    setup_logging()

    start_time = time.time()

    logger.info('Graphy started')

    graph_tool = GraphTool()

    # Open spans JSON file and reads its contents to span_json
    # spans_file_name = '28_06.json'
    spans_file_name = "28_06_simplified_100_spans.json"
    spans_file_name = "28_06_simplified_1000_spans.json"
    spans_file_name = "28_06_simplified_10000_spans.json"
    spans_file_name = "28_06_simplified_100000_spans.json"
    spans_file_name = "29_06.json"
    spans_file_name = "29_06_simplified_100_spans.json"
    spans_file_name = "29_06_simplified_1000_spans.json"
    spans_file_name = "29_06_simplified_10000_spans.json"
    spans_file_name = "29_06_simplified_100000_spans.json"
    spans_json_path = get_data_path(spans_file_name)

    logger.debug('spans_json_path: {}'.format(spans_json_path))

    from_zipkin = False  # CHANGE THIS VARIABLE IF YOU WANT

    if from_zipkin:
        graph_tool.generate_graph_from_zipkin(spans_json_path)
        # print(graph_tool.diameters()) # Found infinite path length because the digraph is not strongly connected
        # graph_tool.draw_graph(save=True, show=False)
    else:
        spans_array = parse_to_spans_array(spans_json_path)

        graph_tool.generate_graph(spans_array, print_span_tree=False)
        graph_tool.count_edge_occurrence()
        # graph_tool.draw_graph(save=True, show=False)

        logger.info('total time: {} seconds'.format(time.time() - start_time))


def setup_logging(default_path='logging.yaml', default_level=logging.INFO, env_key='LOG_CFG'):
    """ Setup logging configuration """
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)


if __name__ == '__main__':
    main()
