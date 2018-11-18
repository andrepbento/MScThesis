import logging.config
import sys
import time

from graphy.graph.graph_tool import GraphTool
from graphy.models.span import parse_to_spans_array
from graphy.utils.files import get_data_path, get_absolute_path
from graphy.utils.logger import setup_logging
from graphy.utils.profile import profile

logger = logging.getLogger(__name__)


@profile
def main():
    setup_logging()

    logger.info('Graphy started')

    # CHANGE THIS VARIABLES IF YOU WANT [True|False] -----
    from_zipkin = sys.argv[1]

    print_span_tree_data = True
    print_graph_data = True
    print_graph_statistics = True
    save_graph = False
    show_graph = False

    # file_name = '28_06.json'
    # file_name = "28_06_simplified_100_spans.json"
    # file_name = "28_06_simplified_1000_spans.json"
    # file_name = "28_06_simplified_10000_spans.json"
    # file_name = "28_06_simplified_100000_spans.json"
    file_name = "29_06.json"
    # file_name = "29_06_simplified_100_spans.json"
    # file_name = "29_06_simplified_1000_spans.json"
    # file_name = "29_06_simplified_10000_spans.json"
    # file_name = "29_06_simplified_100000_spans.json"
    # ----------------------------------------------------

    file = get_data_path(file_name)

    if from_zipkin:
        start_time = time.time()

        # Print arguments data
        logger.info('file:{}'.format(file))

        # Instantiate the graph tool and runs it in zipkin mode
        graph_tool = GraphTool()
        graph_tool.generate_graph_from_zipkin(traces_path=get_absolute_path(file))
        # TODO: remove because when getting from Zipkin, Span Tree doesnt exists
        # graph_tool.print_span_tree_data(print_span_tree_data=print_span_tree_data)
        graph_tool.print_graph_data(print_graph_data=print_graph_data)
        graph_tool.generate_graph_statistics(print_graph_statistics=print_graph_statistics)
        graph_tool.draw_graph(save=save_graph, show=show_graph)

        logger.info('executed in: {} seconds'.format(time.time() - start_time))
    else:
        start_time = time.time()

        # Print arguments data
        logger.info('file:{}'.format(file))

        # Instantiate the graph tool and runs it in standard mode
        graph_tool = GraphTool()
        graph_tool.generate_graph(spans_array=parse_to_spans_array(get_absolute_path(file)))
        graph_tool.print_span_tree_data(print_span_tree_data=print_span_tree_data)
        graph_tool.print_graph_data(print_graph_data=print_graph_data)
        graph_tool.generate_graph_statistics(print_graph_statistics=print_graph_statistics)
        graph_tool.draw_graph(save=save_graph, show=show_graph)

        logger.info('executed in: {} seconds'.format(time.time() - start_time))


if __name__ == '__main__':
    main()
