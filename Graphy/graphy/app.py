import sys

from graphy.controller.controller import Controller
from graphy.utils import config
from graphy.utils.files import get_absolute_path
from graphy.view.console_view import ConsoleView


class Graphy(object):

    @staticmethod
    def run():
        graphy_config = config.get('GRAPHY')

        file = get_absolute_path(graphy_config['TRACE_FILE'], graphy_config['TRACE_FILE_FROM_PROJECT'])

        view = ConsoleView()
        controller = Controller(view)
        controller.set_file(file)
        controller.set_zipkin(graphy_config['ACTIVATE_ZIPKIN'])

        controller.start()


if __name__ == '__main__':
    print('argv: {}'.format(sys.argv))

    Graphy.run()
