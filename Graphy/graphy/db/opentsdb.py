import potsdb

from graphy.utils import config


class OpenTSDB(object):
    def __init__(self):
        opentsdb_config = config.get('OPENTSDB')

        self._metrics = potsdb.Client(host=opentsdb_config['IP'], port=opentsdb_config['PORT'], check_host=True)

    def send_numeric_metric(self, name, metric_data):
        for metric_timestamp, metric_value in metric_data.items():
            self._metrics.send(name, metric_value, timestamp=metric_timestamp)
        self._metrics.wait()

    def send_string_metric(self, name, metric_data):
        for metric_timestamp, metric_value in metric_data.items():
            self._metrics.send(name, 0, timestamp=metric_timestamp, extratag1=metric_value)
        self._metrics.wait()


if __name__ == '__main__':
    opentsdb = OpenTSDB()

    timestamp = 1546300800000
    data = dict()
    for i in range(0, 100):
        value = 'one' if i % 2 == 0 else 'two'
        data[timestamp] = value
        timestamp += 60 * 60 * 1000

    opentsdb.send_string_metric('test_2', data)
