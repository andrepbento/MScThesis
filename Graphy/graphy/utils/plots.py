"""
    Author: André Bento
    Date last modified: 21-03-2019
"""
import os

from matplotlib import pyplot as plt

from graphy.utils import dict as my_dict
from graphy.utils import files as my_files


def __plot(plot_title: str, x_values: list, y_values: list, show_plot: bool, file_name: str):
    fig = plt.gcf()

    plt.bar(x_values, y_values, color='b')
    plt.title(plot_title)

    if show_plot:
        plt.show()

    # plt.draw()

    if file_name:
        path = os.path.join(my_files.DATA_PROJECT_DIRECTORY, file_name)
        fig.savefig(path)  # , dpi=100)


def plot_service_trace_cov(service_name: str, trace_coverability, show_plot):
    x_values = list(trace_coverability.coverability_count.keys())
    y_values = my_dict.filter(trace_coverability.coverability_count, 'value').values()

    if not x_values or all(value == 0 for value in y_values):
        return None

    plot_title = 'Trace coverability for service {}'.format(service_name)
    file_name = '/trace_cov_service_{}.png'.format(service_name)

    __plot(plot_title, x_values, y_values, show_plot, '')

    return file_name
