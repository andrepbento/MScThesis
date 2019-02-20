import logging
import time

from pip._vendor.distlib.compat import raw_input

from graphy.db import opentsdb
from graphy.graph.graph_processor import GraphProcessor
from graphy.models import trace as my_trace
from graphy.utils import dict as my_dict
from graphy.utils import files
from graphy.utils import json as my_json
from graphy.utils import time as my_time
from graphy.utils import zipkin

logger = logging.getLogger(__name__)

# TODO: This values are the default times, change them if you need.
start_date_time_str = "25/06/2018 00:00:00"
end_date_time_str = "30/06/2018 00:00:00"


class Controller(object):
    def __init__(self, view, model=None):
        self.model = model
        self.view = view

        self.trace_file = ''

        self.is_zipkin_running = False
        self.zipkin_limit = 1000000  # TODO: Check if is enough

        self.graph_tool = GraphProcessor()

        self.graph_db = None

        self.time_series_db = opentsdb

    def start(self):
        self.view.start_view()

        user_input = ''
        while user_input != '0':
            switcher = {
                '1': self.show_service_neighbours,
                '2': self.show_service_neighbours_in_time,
                '3': self.show_most_popular_service,
                '4': self.show_most_popular_service_in_time,
                '5': self.show_service_status_code_analysis,
                '6': self.show_service_status_code_analysis_in_time,
                '7': self.show_response_time_analysis,
                '8': self.show_morphology_analysis,
                '9': self.show_request_work_flow_analysis,
                '10': self.show_service_order_distribution_analysis,
                '11': self.show_load_analysis,
                '12': self.show_clients_request_analysis,
                '13': self.end
            }

            switcher_descriptions = [
                'Show service neighbours',
                'Show service neighbours in time (EXPERIMENTAL)',
                'Show most popular service',
                'Show most popular service in time (EXPERIMENTAL)',
                'Show service status code analysis',
                'Show service status code analysis in time (EXPERIMENTAL)',
                'Show response time analysis (NOT IMPLEMENTED)',
                'Show morphology analysis (NOT IMPLEMENTED)',
                'Show request work-flow analysis (NOT IMPLEMENTED)',
                'Show service order distribution analysis (NOT IMPLEMENTED)',
                'Show load analysis (NOT IMPLEMENTED)',
                'Show clients request analysis (NOT IMPLEMENTED)',
                'Exit'
            ]

            self.show_options('Graphy options', switcher_descriptions)
            user_input = raw_input('>>> ')
            execute_selected = switcher.get(user_input, lambda: 'Invalid option!' if user_input is not '0' else '')
            try:
                execute_selected()
            except Exception as ex:
                self.view.display_exception(ex)

        self.end()

    def end(self):
        self.view.end_view()
        exit(1)

    def set_trace_file(self, file):
        absolute_path = files.get_absolute_path(file)
        if not my_json.is_json(absolute_path):
            self.view.display_message('Converting file to JSON', 'file: {}'.format(absolute_path))
            absolute_path = my_json.to_json(absolute_path)
            self.view.display_message('File converted to JSON', 'file: {}'.format(absolute_path))
        self.trace_file = absolute_path
        logger.debug('using file: {}'.format(self.trace_file))

    def set_zipkin(self, is_zipkin_running, is_data_in_zipkin=False):
        self.is_zipkin_running = is_zipkin_running
        if not is_data_in_zipkin and self.is_zipkin_running and self.trace_file:
            if not zipkin.post_spans(self.trace_file):
                logger.error('error posting data to zipkin')
                exit(1)

    def show_options(self, item_type, options):
        self.view.show_number_point_list(item_type, options)

    def show_service_neighbours(self):
        if self.is_zipkin_running:
            start_time = time.time()

            start_timestamp = my_time.to_unix_time_millis(start_date_time_str)
            end_timestamp = my_time.to_unix_time_millis(end_date_time_str)

            self.view.display_time('start_time', my_time.from_str_to_datetime(start_date_time_str), start_timestamp)
            self.view.display_time('end_time', my_time.from_str_to_datetime(end_date_time_str), end_timestamp)

            dependencies = zipkin.get_dependencies(end_ts=end_timestamp, lookback=end_timestamp - start_timestamp)
            self.graph_tool.generate_graph_from_zipkin(dependencies)
            self.view.display_dictionary('All service neighbors from {} to {}'
                                         .format(my_time.from_str_to_datetime(start_date_time_str),
                                                 my_time.from_str_to_datetime(end_date_time_str)),
                                         self.graph_tool.neighbors())
            service_name = 'api_com'
            self.view.display_dictionary('{} service neighbors'.format(service_name),
                                         self.graph_tool.neighbors(service_name))

            self.view.display_message('Time processing', '\nfinish in {} seconds'.format(time.time() - start_time))
        # else:
        # Runs GraphProcessor in standard mode
        # self.graph_tool.generate_graph(spans_array=span.parse_to_spans_array(my_json.to_json(self.trace_file)))
        # graph_tool.print_span_tree_data(print_span_tree_data=print_span_tree_data)
        # graph_tool.print_graph_data(print_graph_data=print_graph_data)
        # graph_tool.generate_graph_statistics(print_graph_statistics=print_graph_statistics)
        # graph_tool.draw_graph(save=save_graph, show=show_graph)

    def show_service_neighbours_in_time(self):
        if self.is_zipkin_running:
            start_time = time.time()

            start_timestamp = my_time.to_unix_time_millis(start_date_time_str)
            end_timestamp = my_time.to_unix_time_millis(end_date_time_str)

            self.view.display_time('start_time', my_time.from_str_to_datetime(start_date_time_str), start_timestamp)
            self.view.display_time('end_time', my_time.from_str_to_datetime(end_date_time_str), end_timestamp)

            timestamps = my_time.timestamp_millis_split(start_timestamp, end_timestamp)

            for i, timestamp in enumerate(timestamps):
                if i + 1 >= len(timestamps):
                    break
                timestamp_1 = timestamp
                timestamp_2 = timestamps[i + 1]
                dependencies = zipkin.get_dependencies(end_ts=timestamp_2)
                if dependencies:
                    self.graph_tool.generate_graph_from_zipkin(dependencies)
                    self.view.display_dictionary('All neighbors from {} to {}'
                                                 .format(my_time.from_timestamp_to_datetime(timestamp_1),
                                                         my_time.from_timestamp_to_datetime(timestamp_2)),
                                                 self.graph_tool.neighbors())
                else:
                    self.view.display_message('No services from {} to {}'
                                              .format(my_time.from_timestamp_to_datetime(timestamp_1),
                                                      my_time.from_timestamp_to_datetime(timestamp_2)),
                                              None)

            self.view.display_message('Time processing', '\nfinish in {} seconds'.format(time.time() - start_time))

    def show_most_popular_service(self):
        if self.is_zipkin_running:
            start_time = time.time()

            start_timestamp = my_time.to_unix_time_millis(start_date_time_str)
            end_timestamp = my_time.to_unix_time_millis(end_date_time_str)

            self.view.display_time('start_time:', my_time.from_timestamp_to_datetime(start_timestamp), start_timestamp)
            self.view.display_time('end_time:', my_time.from_timestamp_to_datetime(end_timestamp), end_timestamp)

            dependencies = zipkin.get_dependencies(end_ts=end_timestamp, lookback=end_timestamp - start_timestamp)
            self.graph_tool.generate_graph_from_zipkin(dependencies)
            self.view.display_tuple_list('Most popular services (Degrees)', self.graph_tool.degrees())
            # self.graph_tool.number_of_edges()

            self.view.display_message('Time processing', '\nfinish in {} seconds'.format(time.time() - start_time))

    def show_most_popular_service_in_time(self):
        if self.is_zipkin_running:
            start_time = time.time()

            start_timestamp = my_time.to_unix_time_millis(start_date_time_str)
            end_timestamp = my_time.to_unix_time_millis(end_date_time_str)

            self.view.display_time('start_time:', my_time.from_timestamp_to_datetime(start_timestamp), start_timestamp)
            self.view.display_time('end_time:', my_time.from_timestamp_to_datetime(end_timestamp), end_timestamp)

            timestamps = my_time.timestamp_millis_split(start_timestamp, end_timestamp)

            for i, timestamp in enumerate(timestamps):
                if i + 1 >= len(timestamps):
                    break
                timestamp_1 = timestamp
                timestamp_2 = timestamps[i + 1]
                dependencies = zipkin.get_dependencies(end_ts=timestamp_2, lookback=timestamp_2 - timestamp_1)
                if dependencies:
                    self.graph_tool.generate_graph_from_zipkin(dependencies)
                    service_degrees = self.graph_tool.degrees()

                    self.time_series_db.send_numeric_metrics('degree', service_degrees,
                                                             int((timestamp_1 + timestamp_2) / 2))

                    most_popular_service = service_degrees[0]
                    self.view.display_tuple('Most popular service from {} to {} (Degrees)'
                                            .format(my_time.from_timestamp_to_datetime(timestamp_1),
                                                    my_time.from_timestamp_to_datetime(timestamp_2)),
                                            most_popular_service)
                else:
                    self.view.display_message('No services from {} to {}'
                                              .format(my_time.from_timestamp_to_datetime(timestamp_1),
                                                      my_time.from_timestamp_to_datetime(timestamp_2)),
                                              None)

            self.view.display_message('Time processing', '\nfinish in {} seconds'.format(time.time() - start_time))

    def show_service_status_code_analysis(self):
        if self.is_zipkin_running:
            start_time = time.time()

            start_timestamp = my_time.to_unix_time_millis(start_date_time_str)
            end_timestamp = my_time.to_unix_time_millis(end_date_time_str)

            self.view.display_time('start_time:', my_time.from_timestamp_to_datetime(start_timestamp), start_timestamp)
            self.view.display_time('end_time:', my_time.from_timestamp_to_datetime(end_timestamp), end_timestamp)

            service_names = zipkin.get_services()

            for service_name in service_names:
                traces = zipkin.get_traces(service_name=service_name, end_ts=end_timestamp,
                                           lookback=end_timestamp - start_timestamp, limit=self.zipkin_limit)

                if len(traces) > self.zipkin_limit:
                    self.view.display_message('Zipkin Trace Limit', 'traces limit exceeded: {}'.format(len(traces)))

                status_codes = my_trace.get_status_codes(traces)
                status_codes_percentage = my_dict.calc_percentage(status_codes)
                self.view.display_message(
                    'Status Codes from {} to {}'.format(my_time.from_timestamp_to_datetime(start_timestamp),
                                                        my_time.from_timestamp_to_datetime(end_timestamp)),
                    '\nservice_name: {}'
                    '\nstatus_codes: {}'
                    '\nstatus_codes_percentage: {}'.format(service_name, my_dict.sort(status_codes),
                                                           my_dict.sort(status_codes_percentage)))

            self.view.display_message('Time processing', '\nfinish in {} seconds'.format(time.time() - start_time))

    def show_service_status_code_analysis_in_time(self):
        if self.is_zipkin_running:
            start_time = time.time()

            start_timestamp = my_time.to_unix_time_millis(start_date_time_str)
            end_timestamp = my_time.to_unix_time_millis(end_date_time_str)

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
                    traces = zipkin.get_traces(service_name=service_name, end_ts=timestamp_2,
                                               lookback=timestamp_2 - timestamp_1, limit=self.zipkin_limit)
                    if len(traces) > self.zipkin_limit:
                        self.view.display_message('Zipkin Trace Limit', 'traces limit exceeded: {}'.format(len(traces)))

                    if traces:
                        status_codes = my_trace.get_status_codes(traces)
                        status_codes_percentage = my_dict.calc_percentage(status_codes)

                        self.time_series_db.send_numeric_metrics('status_code.{}'.format(service_name),
                                                                 status_codes_percentage,
                                                                 int((timestamp_1 + timestamp_2) / 2))

                        self.view.display_message(
                            'Status Codes from {} to {}'.format(my_time.from_timestamp_to_datetime(timestamp_1),
                                                                my_time.from_timestamp_to_datetime(timestamp_2)),
                            '\nservice_name: {}'
                            '\nstatus_codes: {}'
                            '\nstatus_codes_percentage: {}'.format(service_name, my_dict.sort(status_codes),
                                                                   my_dict.sort(status_codes_percentage)))
                    else:
                        self.view.display_message('No traces from {} to {} for service {}'
                                                  .format(my_time.from_timestamp_to_datetime(timestamp_1),
                                                          my_time.from_timestamp_to_datetime(timestamp_2),
                                                          service_name),
                                                  None)

            self.view.display_message('Time processing', '\nfinish in {} seconds'.format(time.time() - start_time))

    def show_response_time_analysis(self):
        return NotImplemented

    def show_morphology_analysis(self):
        return NotImplemented

    def show_request_work_flow_analysis(self):
        return NotImplemented

    def show_service_order_distribution_analysis(self):
        return NotImplemented

    def show_load_analysis(self):
        return NotImplemented

    def show_clients_request_analysis(self):
        return NotImplemented
