import time

import requests

from graphy.utils.files import read_file

base_address = "http://127.0.0.1:9411"
api_v1_endpoint = "/api/v1/"
api_v2_endpoint = "/api/v2/"

address_v1 = base_address + api_v1_endpoint
address_v2 = base_address + api_v2_endpoint


def post_spans(spans_file):
    """
    Post the spans json file to the Zipkin API.

    :param spans_file: spans file path
    :return: if the operation was successful (equal to HTTP code 202)
    """
    spans_data = read_file(spans_file)

    headers = {'content-type': 'application/json'}
    response = requests.post(address_v1 + 'spans', data=spans_data, headers=headers)

    return response.status_code == 202


def get_dependencies():
    """
    Gets the dependencies from the Zipkin API.

    :return: the dependencies data in JSON format or None
    """
    end_ts_param = str(int(time.time()))
    response = requests.get(address_v2 + 'dependencies?endTs=' + end_ts_param)

    if response.status_code == 200:
        return response.text
    return None
