import logging

import matplotlib.pyplot as plt
import numpy

logger = logging.getLogger(__name__)


class Timestamp(object):
    def __init__(self, spans_array):
        self.span_array = spans_array

        self.timestamps_array = []
        for span in spans_array:
            timestamp = span.timestamp
            if timestamp:
                self.timestamps_array.append(timestamp)

    def create_timestamp_histogram(self, timestamps_array):
        print(len(timestamps_array))
        numpy_timestamp_array = numpy.asarray(timestamps_array)
        counts, bin_edges = plt.hist(numpy_timestamp_array, density=True)
        print('counts:', counts)
        print('bin_edges:', bin_edges)
        plt.title("Spans Timestamp Histogram")
        plt.xlabel("Span")
        plt.ylabel("Time (μs)")
        plt.show()

        # fig = plt.gcf()
        # plotly_fig = tls.mpl_to_plotly(fig)
        # py.plot(plotly_fig, filename='spans_timestamp_histogram')

    def print_timestamp_info(self):
        logger.info('print_timestamp_info()')

        logger.info('min: {}'.format(min(self.timestamps_array)))
        logger.info('max: {}'.format(max(self.timestamps_array)))
        logger.info('avg: {}'.format(sum(self.timestamps_array) / len(self.timestamps_array)))
