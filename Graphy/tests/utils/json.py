from graphy.utils import json as my_json


def test_is_json():
    assert my_json.is_json('test.json') == True
    assert my_json.is_json('test.not_json') == False
