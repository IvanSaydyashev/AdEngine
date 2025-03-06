import unittest
from unittest.mock import Mock
from sqlalchemy.orm import InstrumentedAttribute

from src.config import reset_db
from src.tools import except_null, paginate, instrumented_attribute_to_json, read_target_dict


class TestUtils(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        reset_db()

    def test_except_null(self):
        data = {"key1": "value1", "key2": None, "key3": "value3"}
        self.assertEqual(except_null(data), {"key1": "value1", "key3": "value3"})

        self.assertEqual(except_null({}), {})

        self.assertEqual(except_null({"a": None, "b": None}), {})

    def test_paginate(self):
        items = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

        self.assertEqual(paginate(items, 2, 3), [4, 5, 6])

        self.assertEqual(paginate(items, 5, 3), [])

        self.assertEqual(paginate(items, 0, 3), [1, 2, 3])

        self.assertEqual(paginate(items, -1, 3), [1, 2, 3])

        self.assertEqual(paginate(items, "invalid", None), items)

    def test_instrumented_attribute_to_json(self):
        attr = Mock(spec=InstrumentedAttribute)
        attr.expression = '{"key": "value"}'
        self.assertEqual(instrumented_attribute_to_json(attr), {"key": "value"})

        self.assertEqual(instrumented_attribute_to_json({"key": "value"}), {"key": "value"})

        self.assertEqual(instrumented_attribute_to_json('{"key": "value"}'), {"key": "value"})

        self.assertEqual(instrumented_attribute_to_json("{invalid}"), {})

        self.assertEqual(instrumented_attribute_to_json(123), {})

    def test_read_target_dict(self):
        targeting_data = '{"gender": "Male", "min_age": 25, "max_age": 35, "location": "New York"}'
        expected = {"gender": "Male", "min_age": 25, "max_age": 35, "location": "New York"}
        self.assertEqual(read_target_dict(targeting_data), expected)

        partial_data = '{"gender": "Female"}'
        expected_partial = {"gender": "Female", "min_age": 0, "max_age": 100, "location": ""}
        self.assertEqual(read_target_dict(partial_data), expected_partial)

        self.assertEqual(read_target_dict(None), {"gender": "ALL", "min_age": 0, "max_age": 100, "location": ""})
