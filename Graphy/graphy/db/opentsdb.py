import logging

import potsdb

from graphy.utils import config

logger = logging.getLogger(__name__)

opentsdb_config = config.get('OPENTSDB')


def send_numeric_metrics(pre_label, metrics, metric_timestamp):
    if isinstance(metrics, list):
        for tuple_item in metrics:
            x, y = tuple_item
            send_numeric_metric('{}.{}'.format(pre_label, x), y, metric_timestamp)
    elif isinstance(metrics, dict):
        for k, v in metrics.items():
            send_numeric_metric('{}.{}'.format(pre_label, k), v, metric_timestamp)


def send_numeric_metric(metric_name, metric_value, metric_timestamp):
    try:
        client = potsdb.Client(host=opentsdb_config['IP'], port=opentsdb_config['PORT'], check_host=True)
        client.log(name=metric_name, val=metric_value, timestamp=metric_timestamp)
        client.close()
    except Exception as e:
        logger.error(e)


if __name__ == '__main__':
    timestamp = 1546300800000
    data = dict()
    for i in range(0, 100):
        value = 'one' if i % 2 == 0 else 'two'
        data[timestamp] = value
        timestamp += 60 * 60 * 1000

    send_numeric_metric('test_2.dot', 100, timestamp)
    send_numeric_metric('test_2', 110, timestamp)
