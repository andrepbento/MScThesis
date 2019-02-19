import logging
import time

import click
import click_log

from graphy.app import setup_logging
from graphy.graph.graph_processor import GraphProcessor
from graphy.models.span import parse_to_spans_array
from graphy.utils.json import to_json
from graphy.utils.files import get_absolute_path

logger = logging.getLogger(__name__)


@click.group()
@click.option('--info', default=False, is_flag=True, help='Logger in info level')
@click.option('--debug', default=False, is_flag=True, help='Logger in debug level')
@click.option('--error', default=False, is_flag=True, help='Logger in error level')
@click_log.simple_verbosity_option(logger)
@click.version_option()
def cli(info, debug, error):
    """ Graphy is a tool for distributed systems analysis and monitoring """
    if not info and not debug and not error:
        setup_logging(logging_level=logging.NOTSET)
        logger.info('logging_level: NOTSET')
    if info:
        setup_logging(logging_level=logging.INFO)
        logger.info('logging_level: INFO')
    if debug:
        setup_logging(logging_level=logging.DEBUG)
        logger.info('logging_level: DEBUG')
    if error:
        setup_logging(logging_level=logging.ERROR)
        logger.info('logging_level: ERROR')


@cli.command('run')
@click.argument('file', type=click.Path(exists=True))
@click.option('--print-span-tree-data', default=False, is_flag=True, help='Print span tree data to console')
@click.option('--print-graph-data', default=False, is_flag=True, help='Print graph data to console')
@click.option('--print-graph-statistics', default=False, is_flag=True, help='Print graph statistics data to console')
@click.option('--save-graph', default=False, is_flag=True, help='Saves graph image representation')
@click.option('--show-graph', default=False, is_flag=True, help='Show graph image representation')
def run(file, print_span_tree_data, print_graph_data, print_graph_statistics, save_graph, show_graph):
    """ The `run` command, executes Graphy using local data """
    start_time = time.time()

    # Print arguments data
    logger.info('file:{}'.format(file))

    # Instantiate the graph tool and runs it in standard mode
    graph_tool = GraphProcessor()
    graph_tool.generate_graph_from_spans(spans_array=parse_to_spans_array(to_json(get_absolute_path(file))))
    graph_tool.print_span_tree_data(print_span_tree_data=print_span_tree_data)
    graph_tool.print_graph_data(print_graph_data=print_graph_data)
    graph_tool.generate_graph_statistics(print_graph_statistics=print_graph_statistics)
    graph_tool.draw_graph(save=save_graph, show=show_graph)

    logger.info('executed in: {} seconds'.format(time.time() - start_time))


@cli.command('zipkin')
@click.option('--file', default='', help='JSON file')
@click.option('--print-span-tree-data', default=False, is_flag=True, help='Print span tree data to console')
@click.option('--print-graph-data', default=False, is_flag=True, help='Print graph data to console')
@click.option('--print-graph-statistics', default=False, is_flag=True, help='Print graph statistics data to console')
@click.option('--save-graph', default=False, is_flag=True, help='Saves graph image representation')
@click.option('--show-graph', default=False, is_flag=True, help='Show graph image representation')
def zipkin(file, print_span_tree_data, print_graph_data, print_graph_statistics, save_graph, show_graph):
    """ The `zipkin` command, executes Graphy using Zipkin API data """
    start_time = time.time()

    # Print arguments data
    logger.info('file:{}'.format(file))

    # Instantiate the graph tool and runs it in zipkin mode
    graph_tool = GraphProcessor()
    graph_tool.generate_graph_from_zipkin(traces_path=to_json(get_absolute_path(file)))
    graph_tool.print_graph_data(print_graph_data=print_graph_data)
    graph_tool.generate_graph_statistics(print_graph_statistics=print_graph_statistics)
    graph_tool.draw_graph(save=save_graph, show=show_graph)

    logger.info('executed in: {} seconds'.format(time.time() - start_time))
