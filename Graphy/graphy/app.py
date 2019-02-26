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

        file = files.get_absolute_path(graphy_config.get('TRACE_FILE'), graphy_config.get('TRACE_FILE_FROM_PROJECT'))

        view = ConsoleView()
        controller = Controller(view)
        controller.setup_zipkin(file)

        controller.start()
