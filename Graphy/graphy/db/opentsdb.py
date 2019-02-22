"""
    Author: André Bento
    Date last modified: 20-02-2019
"""
import logging

import potsdb

from graphy.utils import config

logger = logging.getLogger(__name__)

opentsdb_config = config.get('OPENTSDB')


def send_numeric_metrics(pre_label, metrics, metric_timestamp):
    """
    Sends a collection of metrics to the Time-Series database.

    :param pre_label: The pre label of the metric in string format. Ex.: degree or status_code
    :param metrics: The list of the metrics. Each metric must be a tuple. Ex.: service: value.
    :param metric_timestamp: The metric unix timestamp.
    :return: True if success, False otherwise.
    """
    if isinstance(metrics, list):
        for tuple_item in metrics:
            x, y = tuple_item
            send_numeric_metric('{}.{}'.format(pre_label, x), y, metric_timestamp)
    elif isinstance(metrics, dict):
        for k, v in metrics.items():
            send_numeric_metric('{}.{}'.format(pre_label, k), v, metric_timestamp)
    else:
        return False
    return True


def send_numeric_metric(metric_name, metric_value, metric_timestamp):
    """
    Sends a single metric to the Time-Series database.

    :param metric_name: The metric name in string format.
    :param metric_value: The metric value in float, integer, or string (convertible to float or integer) format.
    :param metric_timestamp: The metric unix timestamp.
    :return: True if success, False otherwise.
    """
    try:
        client = potsdb.Client(host=opentsdb_config['IP'], port=opentsdb_config['PORT'], check_host=True)
        client.log(name=metric_name, val=metric_value, timestamp=metric_timestamp)
        client.close()
        return True
    except Exception as e:
        logger.error(e)
        return False
