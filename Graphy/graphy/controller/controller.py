import logging
import time

from pip._vendor.distlib.compat import raw_input

from graphy.db.opentsdb import OpenTSDB
from graphy.graph.graph_processor import GraphProcessor
from graphy.models import span
from graphy.utils import time as my_time
from graphy.utils import zipkin
from graphy.utils.convert_json import convert_json
from graphy.utils.files import get_absolute_path
from graphy.utils.logger import setup_logging

logger = logging.getLogger(__name__)

# TODO: This values are the default times, change them if you need.
start_date_time_str = "25/06/2018 00:00:00"
end_date_time_str = "30/06/2018 00:00:00"


class Controller(object):
    def __init__(self, view, model=None):
        setup_logging()

        self.model = model
        self.view = view

        self.file = ''
        self.is_zipkin_running = False

        self.graph_tool = GraphProcessor()

        self.graph_db = None

        self.time_series_db = OpenTSDB()

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
                '6': self.show_response_time_analysis,
                '7': self.show_morphology_analysis,
                '8': self.show_request_work_flow_analysis,
                '9': self.show_service_order_distribution_analysis,
                '10': self.show_load_analysis,
                '11': self.show_clients_request_analysis,
                '12': self.end
            }

            switcher_descriptions = [
                'Show service neighbours',
                'Show service neighbours in time (EXPERIMENTAL)',
                'Show most popular service',
                'Show most popular service in time (EXPERIMENTAL)',
                'Show service status code analysis',
                'Show response time analysis',
                'Show morphology analysis',
                'Show request work-flow analysis',
                'Show service order distribution analysis',
                'Show load analysis',
                'Show clients request analysis',
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

    def set_file(self, file):
        self.file = get_absolute_path(file)
        logger.info('file:{}'.format(self.file))

    def set_zipkin(self, is_zipkin_running, is_data_in_zipkin=False):
        self.is_zipkin_running = is_zipkin_running
        if not is_data_in_zipkin and self.is_zipkin_running and self.file:
            if not zipkin.post_spans(self.file):
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

            from graphy.utils import zipkin
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
        else:
            # Runs GraphProcessor in standard mode
            self.graph_tool.generate_graph(spans_array=span.parse_to_spans_array(convert_json(self.file)))
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
            self.view.display_tuple_list('Most popular services', self.graph_tool.degrees())
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
                dependencies = zipkin.get_dependencies(end_ts=timestamp_2)
                if dependencies:
                    self.graph_tool.generate_graph_from_zipkin(dependencies)
                    most_popular_service = self.graph_tool.degrees()[0]
                    self.view.display_tuple('Most popular service from {} to {}'
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

            service_names = zipkin.get_services()

            for service_name in service_names:
                service_traces = zipkin.get_traces(service_name=service_name)
                print(service_traces)

        return NotImplemented

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
