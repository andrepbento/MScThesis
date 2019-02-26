"""
    Author: André Bento
    Date last modified: 25-02-2019
"""
from unittest import TestCase

from graphy.utils import json as my_json


class TestJson(TestCase):

    def test_is_json(self):
        """ Tests is_json function. """
        self.assertTrue(my_json.is_json('test.json'))
        self.assertTrue(my_json.is_json('test.json'))
        self.assertFalse(my_json.is_json('test.not_json'))
        self.assertTrue(my_json.is_json('dir/test.json'))
        self.assertFalse(my_json.is_json('dir/test.not_json'))

    def test_to_json(self):
        """ Tests to_json function. """
        json_file = '.json'
        not_json_file = '.jsonl'
        self.assertEqual(my_json.to_json(json_file), json_file)
