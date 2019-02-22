"""
    Author: André Bento
    Date last modified: 20-02-2019
"""
import sys

from graphy.controller.controller import Controller
from graphy.utils import config
from graphy.utils import files
from graphy.view.console_view import ConsoleView


class Graphy(object):

    @staticmethod
    def run():
        graphy_config = config.get('GRAPHY')

        file = files.get_absolute_path(graphy_config['TRACE_FILE'], graphy_config['TRACE_FILE_FROM_PROJECT'])

        view = ConsoleView()
        controller = Controller(view)
        controller.set_trace_file(file)
        controller.set_zipkin(graphy_config['ACTIVATE_ZIPKIN'])

        controller.start()


if __name__ == '__main__':
    print('argv: {}'.format(sys.argv))

    Graphy.run()
