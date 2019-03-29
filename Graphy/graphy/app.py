"""
    Author: André Bento
    Date last modified: 26-02-2019
"""

from graphy.controller.controller import Controller
from graphy.utils import config
from graphy.utils import files
from graphy.view.console_view import ConsoleView


class Graphy(object):

    @staticmethod
    def run():
        graphy_config = config.get('GRAPHY')

        trace_files = graphy_config.get('TRACE_FILES')

        view = ConsoleView()
        controller = Controller(view)

        for trace_file in trace_files:
            trace_file_path = files.get_absolute_path(trace_file, graphy_config.get('TRACE_FILE_FROM_PROJECT'))
            print('Posting file: {} to Zipkin'.format(trace_file_path))
            controller.setup_zipkin(trace_file_path)

        controller.start()
