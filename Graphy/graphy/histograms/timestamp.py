import matplotlib.pyplot as plt
import numpy

"""
for span in spans_array:
    print('traceId:', span.traceId)
    print('id:', span.id)
    print('timestamp:', span.timestamp)
    if hasattr(span, 'parentId'):
        print('parentId:', span.parentId)
"""


class Timestamp(object):
    def __init__(self, spans_array):
        self.spans_array = spans_array

    def create_timestamp_histogram(self):
        timestamps_array = []
        for span in self.spans_array:
            timestamps_array.append(span.timestamp)
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
