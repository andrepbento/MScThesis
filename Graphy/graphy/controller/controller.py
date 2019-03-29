"""
    Author: André Bento
    Date last modified: 22-03-2019
"""
import os
import sys
import time

from graphy.db import opentsdb
from graphy.db.arangodb import ArangoDB
from graphy.graph.graph_processor import GraphProcessor
from graphy.models import trace as my_trace
from graphy.utils import dict as my_dict, config
from graphy.utils import json as my_json
from graphy.utils import logger as my_logger
from graphy.utils import plots as my_plots
from graphy.utils import time as my_time
from graphy.utils import zipkin

logger = my_logger.setup_logging(__name__)

graphy_config = config.get('GRAPHY')


class Controller(object):
    def __init__(self, view, model=None):
        self.model = model
        self.view = view

        self.__graph_processor = GraphProcessor()

        self.__graph_db = ArangoDB()

        self.__time_series_db = opentsdb

        self.__start_date_time_str = graphy_config.get('DEFAULT_START_TIME')
        self.__end_date_time_str = graphy_config.get('DEFAULT_END_TIME')

        self.__zipkin_limit = graphy_config.get('ZIPKIN_TRACES_LIMIT')
        self.__is_zipkin = graphy_config.get('ACTIVATE_ZIPKIN')

    def start(self):
        """ Starts the controller. """
        self.view.start_view()

        while True:
            switcher = {
                'Show service neighbours':
                    self.show_service_neighbours,
                'Show service neighbours in time (EXPERIMENTAL)':
                    self.show_service_neighbours_in_time,
                'Show most popular service [degree]':
                    self.show_most_popular_service,
                'Show most popular service [degree] in time (EXPERIMENTAL)':
                    self.show_most_popular_service_degree_in_time,
                'Show most popular service [call count]':
                    self.show_most_popular_service_call_count,
                'Show most popular service [call count] in time (EXPERIMENTAL)':
                    self.show_most_popular_service_call_count_in_time,
                'Show service status code analysis':
                    self.show_service_status_codes_analysis,
                'Show service status code analysis in time (EXPERIMENTAL)':
                    self.show_service_status_code_analysis_in_time,
                'Show trace quality analysis (EXPERIMENTAL)':
                    self.show_trace_quality_analysis,
                'Show response time analysis (NOT IMPLEMENTED)':
                    self.show_response_time_analysis,
                'Show morphology analysis (EXPERIMENTAL)':
                    self.show_morphology_analysis_in_time,
                'Show request work-flow analysis (NOT IMPLEMENTED)':
                    self.show_request_work_flow_analysis,
                'Show service order distribution analysis (NOT IMPLEMENTED)':
                    self.show_service_order_distribution_analysis,
                'Show load analysis (NOT IMPLEMENTED)':
                    self.show_load_analysis,
                'Show clients request analysis (NOT IMPLEMENTED)':
                    self.show_clients_request_analysis,
                'Gather and show all metrics in time (EXPERIMENTAL) [neighbours, degree, call count, status codes]':
                    self.show_all_metrics,
                'Exit':
                    self.__end
            }

            self.__show_options('Graphy options', switcher)
            user_input = input('>>> ')

            if user_input in range(1, len(switcher)):
                self.view.display_message('Invalid option!', 'Option not valid, please try again.')
                continue
            else:
                try:
                    execute_selected = list(switcher.items())[int(user_input) - 1]
                    execute_selected[1]()
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    file_name = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                    logger.error(e)
                    self.view.display_exception('{} {} {}'.format(exc_type, file_name, exc_tb.tb_lineno))

    def __end(self):
        """ Terminates the controller. """
        self.view.end_view()
        exit(1)

    def __show_options(self, title: str, options: dict) -> None:
        """
        Shows options using the view.

        :param title: The title of the options menu.
        :param options: The list of options.
        """
        self.view.show_number_point_list(title, options)

    def setup_zipkin(self, trace_file_path: str):
        """
        Setup Zipkin with a certain trace file, if data is not already in it.

        :param trace_file_path: The trace file absolute path.
        """
        if not my_json.is_json(trace_file_path):
            self.view.display_message('Converting file to JSON', 'file: {}'.format(trace_file_path))
            trace_file_path = my_json.to_json(trace_file_path)
            self.view.display_message('File converted to JSON', 'file: {}'.format(trace_file_path))

        if trace_file_path:
            logger.debug('Using file: {}'.format(trace_file_path))

            if not zipkin.post_spans(trace_file_path):
                logger.error('error posting data to zipkin')
                exit(1)

    def show_service_neighbours(self):
        if self.__is_zipkin:
            start_time = time.time()

            start_timestamp = my_time.to_unix_time_millis(self.__start_date_time_str)
            end_timestamp = my_time.to_unix_time_millis(self.__end_date_time_str)

            self.view.display_time('start_time', my_time.from_str_to_datetime(self.__start_date_time_str),
                                   start_timestamp)
            self.view.display_time('end_time', my_time.from_str_to_datetime(self.__end_date_time_str),
                                   end_timestamp)

            dependencies = zipkin.get_dependencies(end_ts=end_timestamp, lookback=end_timestamp - start_timestamp)

            self.__service_neighbours(dependencies, start_timestamp, end_timestamp)

            self.view.display_message('Time processing', 'finish in {} seconds'.format(time.time() - start_time))

    def show_service_neighbours_in_time(self):
        if self.__is_zipkin:
            start_time = time.time()

            start_timestamp = my_time.to_unix_time_millis(self.__start_date_time_str)
            end_timestamp = my_time.to_unix_time_millis(self.__end_date_time_str)

            self.view.display_time('start_time', my_time.from_str_to_datetime(self.__start_date_time_str),
                                   start_timestamp)
            self.view.display_time('end_time', my_time.from_str_to_datetime(self.__end_date_time_str),
                                   end_timestamp)

            timestamps = my_time.timestamp_millis_split(start_timestamp, end_timestamp)

            for i, timestamp in enumerate(timestamps):
                if i + 1 >= len(timestamps):
                    break
                timestamp_1 = timestamp
                timestamp_2 = timestamps[i + 1]
                dependencies = zipkin.get_dependencies(end_ts=timestamp_2)

                self.__service_neighbours(dependencies, timestamp_1, timestamp_2)

            self.view.display_message('Time processing', 'finish in {} seconds'.format(time.time() - start_time))

    def __service_neighbours(self, dependencies, start_timestamp, end_timestamp):
        if dependencies:
            self.__graph_processor.generate_graph_from_zipkin(dependencies, start_timestamp, end_timestamp)
            self.view.display_dictionary('All service neighbors from {} to {}'
                                         .format(my_time.from_timestamp_to_datetime(start_timestamp),
                                                 my_time.from_timestamp_to_datetime(end_timestamp)),
                                         self.__graph_processor.neighbors())
        else:
            self.view.display_message('No services from {} to {}'
                                      .format(my_time.from_timestamp_to_datetime(start_timestamp),
                                              my_time.from_timestamp_to_datetime(end_timestamp)),
                                      'Can\'t calculate service neighbours')

    def show_most_popular_service(self):
        if self.__is_zipkin:
            start_time = time.time()

            start_timestamp = my_time.to_unix_time_millis(self.__start_date_time_str)
            end_timestamp = my_time.to_unix_time_millis(self.__end_date_time_str)

            self.view.display_time('start_time:', my_time.from_timestamp_to_datetime(start_timestamp),
                                   start_timestamp)
            self.view.display_time('end_time:', my_time.from_timestamp_to_datetime(end_timestamp), end_timestamp)

            dependencies = zipkin.get_dependencies(end_ts=end_timestamp, lookback=end_timestamp - start_timestamp)

            self.__service_degree(dependencies, start_timestamp, end_timestamp)

            self.view.display_message('Time processing', 'finish in {} seconds'.format(time.time() - start_time))

    def show_most_popular_service_degree_in_time(self):
        if self.__is_zipkin:
            start_time = time.time()

            start_timestamp = my_time.to_unix_time_millis(self.__start_date_time_str)
            end_timestamp = my_time.to_unix_time_millis(self.__end_date_time_str)

            self.view.display_time('start_time:', my_time.from_timestamp_to_datetime(start_timestamp),
                                   start_timestamp)
            self.view.display_time('end_time:', my_time.from_timestamp_to_datetime(end_timestamp), end_timestamp)

            timestamps = my_time.timestamp_millis_split(start_timestamp, end_timestamp)

            for i, timestamp in enumerate(timestamps):
                if i + 1 >= len(timestamps):
                    break
                timestamp_1 = timestamp
                timestamp_2 = timestamps[i + 1]
                dependencies = zipkin.get_dependencies(end_ts=timestamp_2, lookback=timestamp_2 - timestamp_1)

                self.__service_degree(dependencies, timestamp_1, timestamp_2)

            self.view.display_message('Time processing', 'finish in {} seconds'.format(time.time() - start_time))

    def __service_degree(self, dependencies, start_timestamp, end_timestamp):
        if dependencies:
            self.__graph_processor.generate_graph_from_zipkin(dependencies, start_timestamp, end_timestamp)
            service_degrees = self.__graph_processor.degrees()
            service_in_degrees = self.__graph_processor.degrees('in')
            service_out_degrees = self.__graph_processor.degrees('out')

            self.__time_series_db.send_numeric_metrics('degree', service_degrees,
                                                       int((start_timestamp + end_timestamp) / 2))
            self.__time_series_db.send_numeric_metrics('degree_in', service_in_degrees,
                                                       int((start_timestamp + end_timestamp) / 2))
            self.__time_series_db.send_numeric_metrics('degree_out', service_out_degrees,
                                                       int((start_timestamp + end_timestamp) / 2))

            most_popular_service = service_degrees[0]
            self.view.display_tuple('Most popular service from {} to {} (Degrees)'
                                    .format(my_time.from_timestamp_to_datetime(start_timestamp),
                                            my_time.from_timestamp_to_datetime(end_timestamp)),
                                    most_popular_service)
        else:
            self.view.display_message('No services from {} to {}'
                                      .format(my_time.from_timestamp_to_datetime(start_timestamp),
                                              my_time.from_timestamp_to_datetime(end_timestamp)),
                                      'Can\'t calculate service degree')

    def show_most_popular_service_call_count(self):
        if self.__is_zipkin:
            start_time = time.time()

            start_timestamp = my_time.to_unix_time_millis(self.__start_date_time_str)
            end_timestamp = my_time.to_unix_time_millis(self.__end_date_time_str)

            self.view.display_time('start_time:', my_time.from_timestamp_to_datetime(start_timestamp),
                                   start_timestamp)
            self.view.display_time('end_time:', my_time.from_timestamp_to_datetime(end_timestamp), end_timestamp)

            dependencies = zipkin.get_dependencies(end_ts=end_timestamp, lookback=end_timestamp - start_timestamp)

            self.__service_call_count(dependencies, start_timestamp, end_timestamp)

            self.view.display_message('Time processing', 'finish in {} seconds'.format(time.time() - start_time))

    def show_most_popular_service_call_count_in_time(self):
        if self.__is_zipkin:
            start_time = time.time()

            start_timestamp = my_time.to_unix_time_millis(self.__start_date_time_str)
            end_timestamp = my_time.to_unix_time_millis(self.__end_date_time_str)

            self.view.display_time('start_time:', my_time.from_timestamp_to_datetime(start_timestamp),
                                   start_timestamp)
            self.view.display_time('end_time:', my_time.from_timestamp_to_datetime(end_timestamp), end_timestamp)

            timestamps = my_time.timestamp_millis_split(start_timestamp, end_timestamp)

            for i, timestamp in enumerate(timestamps):
                if i + 1 >= len(timestamps):
                    break
                timestamp_1 = timestamp
                timestamp_2 = timestamps[i + 1]
                dependencies = zipkin.get_dependencies(end_ts=timestamp_2, lookback=timestamp_2 - timestamp_1)

                self.__service_call_count(dependencies, timestamp_1, timestamp_2)

            self.view.display_message('Time processing', 'finish in {} seconds'.format(time.time() - start_time))

    def __service_call_count(self, dependencies, start_timestamp, end_timestamp):
        if dependencies:
            self.__graph_processor.generate_graph_from_zipkin(dependencies, start_timestamp, end_timestamp)
            service_edge_call_count = self.__graph_processor.edges_call_count()

            self.__time_series_db.send_numeric_metrics('call_count', service_edge_call_count,
                                                       int((start_timestamp + end_timestamp) / 2))

            service_in_edge_call_count = self.__graph_processor.in_edges_call_count()

            self.__time_series_db.send_numeric_metrics('call_count_in', service_in_edge_call_count,
                                                       int((start_timestamp + end_timestamp) / 2))

            service_out_edge_call_count = self.__graph_processor.out_edges_call_count()

            self.__time_series_db.send_numeric_metrics('call_count_out', service_out_edge_call_count,
                                                       int((start_timestamp + end_timestamp) / 2))

            most_popular_service = service_edge_call_count[0]
            self.view.display_tuple('Most popular service from {} to {} (Call Count)'
                                    .format(my_time.from_timestamp_to_datetime(start_timestamp),
                                            my_time.from_timestamp_to_datetime(end_timestamp)),
                                    most_popular_service)
        else:
            self.view.display_message('No services from {} to {}'
                                      .format(my_time.from_timestamp_to_datetime(start_timestamp),
                                              my_time.from_timestamp_to_datetime(end_timestamp)),
                                      'Can\'t calculate service call count')

    def show_service_status_codes_analysis(self):
        if self.__is_zipkin:
            start_time = time.time()

            start_timestamp = my_time.to_unix_time_millis(self.__start_date_time_str)
            end_timestamp = my_time.to_unix_time_millis(self.__end_date_time_str)

            self.view.display_time('start_time:', my_time.from_timestamp_to_datetime(start_timestamp),
                                   start_timestamp)
            self.view.display_time('end_time:', my_time.from_timestamp_to_datetime(end_timestamp), end_timestamp)

            service_names = zipkin.get_services()

            for service_name in service_names:
                traces = zipkin.get_traces(service_name=service_name, end_ts=end_timestamp,
                                           lookback=end_timestamp - start_timestamp, limit=self.__zipkin_limit)

                self.__service_status_codes(service_name, traces, start_timestamp, end_timestamp)

            self.view.display_message('Time processing', 'finish in {} seconds'.format(time.time() - start_time))

    def show_service_status_code_analysis_in_time(self):
        if self.__is_zipkin:
            start_time = time.time()

            start_timestamp = my_time.to_unix_time_millis(self.__start_date_time_str)
            end_timestamp = my_time.to_unix_time_millis(self.__end_date_time_str)

            self.view.display_time('start_time:', my_time.from_timestamp_to_datetime(start_timestamp),
                                   start_timestamp)
            self.view.display_time('end_time:', my_time.from_timestamp_to_datetime(end_timestamp), end_timestamp)

            timestamps = my_time.timestamp_millis_split(start_timestamp, end_timestamp)

            service_names = zipkin.get_services()

            for i, timestamp in enumerate(timestamps):
                if i + 1 >= len(timestamps):
                    break
                timestamp_1 = timestamp
                timestamp_2 = timestamps[i + 1]

                for service_name in service_names:
                    traces = zipkin.get_traces(service_name=service_name, end_ts=end_timestamp,
                                               lookback=end_timestamp - start_timestamp, limit=self.__zipkin_limit)

                    self.__service_status_codes(service_name, traces, timestamp_1, timestamp_2)

            self.view.display_message('Time processing', 'finish in {} seconds'.format(time.time() - start_time))

    def __service_status_codes(self, service_name, traces, start_timestamp, end_timestamp):
        if traces:
            if len(traces) >= self.__zipkin_limit:
                raise zipkin.ZipkinTraceLimit(len(traces))

            status_codes = my_trace.get_status_codes(traces)
            status_codes_percentage = my_dict.calc_percentage(status_codes)

            self.__time_series_db.send_numeric_metrics('status_code.{}'.format(service_name),
                                                       status_codes_percentage,
                                                       int((start_timestamp + end_timestamp) / 2))

            self.view.display_message(
                'Status Codes from {} to {}'.format(my_time.from_timestamp_to_datetime(start_timestamp),
                                                    my_time.from_timestamp_to_datetime(end_timestamp)),
                '\nservice_name: {}'
                '\nstatus_codes: {}'
                '\nstatus_codes_percentage: {}'.format(service_name, my_dict.sort(status_codes),
                                                       my_dict.sort(status_codes_percentage)))
        else:
            self.view.display_message('No traces found from {} to {} for service {}'
                                      .format(my_time.from_timestamp_to_datetime(start_timestamp),
                                              my_time.from_timestamp_to_datetime(end_timestamp),
                                              service_name),
                                      'Can\'t calculate service status codes')

    def show_trace_quality_analysis(self):
        if self.__is_zipkin:
            start_time = time.time()

            start_timestamp = my_time.to_unix_time_millis(self.__start_date_time_str)
            end_timestamp = my_time.to_unix_time_millis(self.__end_date_time_str)

            service_names = zipkin.get_services()

            for i, service_name in enumerate(service_names):
                traces = zipkin.get_traces(service_name=service_name, end_ts=end_timestamp,
                                           lookback=end_timestamp - start_timestamp, limit=self.__zipkin_limit)

                if traces:
                    span_trees = my_trace.generate_span_trees(traces)
                    trace_metrics_data = my_trace.extract_metrics(span_trees)

                    self.view.display_message(
                        'Trace quality analysis from {} to {} for service {}'.format(
                            my_time.from_timestamp_to_datetime(start_timestamp),
                            my_time.from_timestamp_to_datetime(end_timestamp),
                            service_name),
                        'Analysing...')

                    file_path = self.__trace_quality_analysis(service_name, trace_metrics_data)

                    self.view.display_message(
                        'Analysis completed!',
                        'Please check file: {}'.format(file_path))
                else:
                    self.view.display_message(
                        'No traces found from {} to {} for service {}'.format(
                            my_time.from_timestamp_to_datetime(start_timestamp),
                            my_time.from_timestamp_to_datetime(end_timestamp),
                            service_name),
                        '\nCan\'t calculate service status codes')

            self.view.display_message('Time processing', 'finish in {} seconds'.format(time.time() - start_time))

    def __trace_quality_analysis(self, service_name: str, trace_metrics_data: my_trace.TraceMetricsData):
        del trace_metrics_data.coverability_count['error']
        return my_plots.plot_service_trace_cov(service_name, trace_metrics_data, True)

    def show_response_time_analysis(self):
        if self.__is_zipkin:
            start_time = time.time()

            start_timestamp = my_time.to_unix_time_millis(self.__start_date_time_str)
            end_timestamp = my_time.to_unix_time_millis(self.__end_date_time_str)

            timestamps = my_time.timestamp_millis_split(start_timestamp, end_timestamp)

            service_names = zipkin.get_services()

            for i, timestamp in enumerate(timestamps):
                if i + 1 >= len(timestamps):
                    break
                timestamp_1 = timestamp
                timestamp_2 = timestamps[i + 1]

                # TODO: IMPROVE DATA USAGE.
                for service_name in service_names:
                    traces = zipkin.get_traces(service_name=service_name, end_ts=end_timestamp,
                                               lookback=end_timestamp - start_timestamp, limit=self.__zipkin_limit)

                    span_trees = my_trace.generate_span_trees(traces)
                    trace_metrics_data = my_trace.extract_metrics(span_trees)

                    self.__service_response_time_analysis(service_name, trace_metrics_data, timestamp_1, timestamp_2)

            self.view.display_message('Time processing', 'finish in {} seconds'.format(time.time() - start_time))

    def __service_response_time_analysis(self, service_name: str, trace_metrics_data, start_timestamp, end_timestamp):
        if trace_metrics_data.response_time_avg is not -1:
            self.view.display_message(
                'Response time analysis from {} to {} for service {}'.format(
                    my_time.from_timestamp_to_datetime(start_timestamp),
                    my_time.from_timestamp_to_datetime(end_timestamp),
                    service_name),
                'Analysing...')

            response_time_avg = trace_metrics_data.response_time_avg

            self.__time_series_db.send_numeric_metric(['response_time_avg', service_name],
                                                      response_time_avg,
                                                      int((start_timestamp + end_timestamp) / 2))

            self.view.display_message('Response time analysis from {} to {} for service {}\nAVG: {}'.format(
                my_time.from_timestamp_to_datetime(start_timestamp),
                my_time.from_timestamp_to_datetime(end_timestamp),
                service_name,
                response_time_avg),
                'Analysis completed!')
        else:
            self.view.display_message(
                'No data found from {} to {} for service {}'.format(
                    my_time.from_timestamp_to_datetime(start_timestamp),
                    my_time.from_timestamp_to_datetime(end_timestamp),
                    service_name),
                '\nCan\'t perform response time analysis')

    def show_morphology_analysis_in_time(self):
        if self.__is_zipkin:
            start_time = time.time()

            start_timestamp = my_time.to_unix_time_millis(self.__start_date_time_str)
            end_timestamp = my_time.to_unix_time_millis(self.__end_date_time_str)

            self.view.display_time('start_time:', my_time.from_timestamp_to_datetime(start_timestamp),
                                   start_timestamp)
            self.view.display_time('end_time:', my_time.from_timestamp_to_datetime(end_timestamp), end_timestamp)

            timestamps = my_time.timestamp_millis_split(start_timestamp, end_timestamp)

            previous_graph = None
            for i, timestamp in enumerate(timestamps):
                if i + 1 >= len(timestamps):
                    break
                timestamp_1 = timestamp
                timestamp_2 = timestamps[i + 1]

                dependencies = zipkin.get_dependencies(end_ts=timestamp_2, lookback=timestamp_2 - timestamp_1)

                previous_graph = self.__service_morphology(dependencies, timestamp_1, timestamp_2, previous_graph)

            self.view.display_message('Time processing', 'finish in {} seconds'.format(time.time() - start_time))

    def __service_morphology(self, dependencies, start_timestamp, end_timestamp, previous_graph):
        if dependencies:
            current_graph = self.__graph_processor.generate_graph_from_zipkin(dependencies, start_timestamp,
                                                                              end_timestamp)
            current_graph.name = '{}_{}'.format(start_timestamp, end_timestamp)

            self.__graph_db.insert_graph(start_timestamp, end_timestamp, list(current_graph.edges(data=True)),
                                         self.__graph_db.graph_db)

            if previous_graph:
                graph_diff = self.__graph_processor.graphs_difference(previous_graph, current_graph)

                self.__graph_db.insert_graph(start_timestamp, end_timestamp, list(graph_diff.edges(data=True)),
                                             self.__graph_db.graph_diff_db)

                graph_variance = self.__graph_processor.graphs_variance(previous_graph, current_graph)

                self.__time_series_db.send_numeric_metric(['graph_gain_variance'], graph_variance.get('gain'),
                                                          int((start_timestamp + end_timestamp) / 2))
                self.__time_series_db.send_numeric_metric(['graph_loss_variance'], graph_variance.get('loss'),
                                                          int((start_timestamp + end_timestamp) / 2))
                self.__time_series_db.send_numeric_metric(['graph_variance'],
                                                          graph_variance.get('gain') - graph_variance.get('loss'),
                                                          int((start_timestamp + end_timestamp) / 2))

                self.view.display_message('System Morphology from {} to {}'
                                          .format(my_time.from_timestamp_to_datetime(start_timestamp),
                                                  my_time.from_timestamp_to_datetime(end_timestamp)),
                                          '\nprevious_graph.Nodes:{}\nprevious_graph.Edges:{}'
                                          '\nprevious_graph.NodesLen:{}\nprevious_graph.EdgesLen:{}'
                                          '\ncurrent_graph.Nodes:{}\ncurrent_graph.Edges:{}'
                                          '\ncurrent_graph.NodesLen:{}\ncurrent_graph.EdgesLen:{}'
                                          '\ngraph_diff.Nodes:{}\ngraph_diff.Edges:{}'
                                          '\ngraph_diff.NodesLen:{}\ngraph_diff.EdgesLen:{}'
                                          .format(previous_graph.nodes, previous_graph.edges(data=True),
                                                  len(previous_graph.nodes), len(previous_graph.edges),
                                                  current_graph.nodes, current_graph.edges(data=True),
                                                  len(current_graph.nodes), len(current_graph.edges),
                                                  graph_diff.nodes, graph_diff.edges(data=True),
                                                  len(graph_diff.nodes), len(graph_diff.edges)))

            previous_graph = current_graph.copy()
            return previous_graph
        else:
            self.view.display_message('No system graph from {} to {}'
                                      .format(my_time.from_timestamp_to_datetime(start_timestamp),
                                              my_time.from_timestamp_to_datetime(end_timestamp)),
                                      'Can\'t calculate service morphology')
            return None

    def show_request_work_flow_analysis(self):
        # TODO: Analise the requests from the graphs || spans (How?)
        return NotImplemented

    def show_service_order_distribution_analysis(self):
        return NotImplemented

    def show_load_analysis(self):
        return NotImplemented

    def show_clients_request_analysis(self):
        return NotImplemented

    def show_all_metrics(self):
        if self.__is_zipkin:
            start_time = time.time()

            start_timestamp = my_time.to_unix_time_millis(self.__start_date_time_str)
            end_timestamp = my_time.to_unix_time_millis(self.__end_date_time_str)

            self.view.display_time('start_time:', my_time.from_timestamp_to_datetime(start_timestamp),
                                   start_timestamp)
            self.view.display_time('end_time:', my_time.from_timestamp_to_datetime(end_timestamp), end_timestamp)

            timestamps = my_time.timestamp_millis_split(start_timestamp, end_timestamp)

            previous_graph = None
            service_names = zipkin.get_services()

            for i, timestamp in enumerate(timestamps):
                if i + 1 >= len(timestamps):
                    break
                timestamp_1 = timestamp
                timestamp_2 = timestamps[i + 1]

                dependencies = zipkin.get_dependencies(end_ts=timestamp_2, lookback=timestamp_2 - timestamp_1)

                self.__service_neighbours(dependencies, timestamp_1, timestamp_2)
                self.__service_degree(dependencies, timestamp_1, timestamp_2)
                self.__service_call_count(dependencies, timestamp_1, timestamp_2)
                previous_graph = self.__service_morphology(dependencies, timestamp_1, timestamp_2, previous_graph)

                for service_name in service_names:
                    traces = zipkin.get_traces(service_name=service_name, end_ts=timestamp_2,
                                               lookback=timestamp_2 - timestamp_1, limit=self.__zipkin_limit)

                    span_trees = my_trace.generate_span_trees(traces)
                    trace_metrics_data = my_trace.extract_metrics(span_trees)

                    self.__service_status_codes(service_name, traces, timestamp_1, timestamp_2)
                    # self.__trace_quality_analysis(service_name, trace_metrics_data)
                    self.__service_response_time_analysis(service_name, trace_metrics_data, timestamp_1, timestamp_2)

            self.view.display_message('Time processing', 'finish in {} seconds'.format(time.time() - start_time))
