#!/usr/bin/env python3
"""Test for the utils module"""

import unittest
from typing import Any, Dict
from parameterized import parameterized
from unittest.mock import patch, Mock

utils = __import__("utils")
access_nested_map = utils.access_nested_map
get_json = utils.get_json
memoize = utils.memoize

nested_map = {"a": {"b": {"c": 1}}}


class TestAccessNestedMap(unittest.TestCase):
    """The class inherits from unittest.TestCase.
    Methods:
        test_access_nested_map: Test the acess_access_nested_map function
    """

    @parameterized.expand(
        [
            ({"a": 1}, ("a",), 1),
            ({"a": {"b": 2}}, ("a",), {"b": 2}),
            ({"a": {"b": 2}}, ("a", "b"), 2),
        ]
    )
    def test_access_nested_map(self, nested_map, path, expected) -> Any:
        """Test the access_nested_map() from the utils module
        to ensure that the right result is returned.
        """
        self.assertEqual(access_nested_map(nested_map, path), expected)

    @parameterized.expand(
        [
            ({}, ("a",)),
            ({"a": 1}, ("a", "b")),
        ]
    )
    def test_access_nested_map_exception(self, nested_map, path) -> Any:
        """Test that the access_nested_map() return the right exception
        when a wrong argument is passed.
        """
        with self.assertRaises(KeyError):
            access_nested_map(nested_map, path)


class TestGetJson(unittest.TestCase):
    """
    Unit test class for the get_json function.

    This test ensures that the get_json function correctly retrieves and
    returns JSON payloads from given URLs, using mocking to avoid real HTTP
    requests.
    """

    @parameterized.expand(
        [
            ("http://example.com", {"payload": True}),
            ("http://holberton.io", {"payload": False}),
        ]
    )
    @patch("utils.requests.get")
    def test_get_json(
        self, url: str, mock_data: Dict[str, Any], mock_get: Mock
    ) -> None:
        """
        Test get_json returns expected payload for given URL.

        This test mocks requests.get to return a controlled mock response.
        It checks that:
        - The returned data from get_json is equal to the mock payload.
        - The requests.get method is called once with the given URL.

        Args:
            url (str): The URL to simulate the HTTP GET request to.
            mock_data (Dict[str, Any]): The expected JSON payload to be
            returned.
            mock_get (Mock): The mocked version of requests.get.
        """

        mock_response = Mock()
        mock_response.json.return_value = mock_data
        mock_get.return_value = mock_response
        result = get_json(url)
        self.assertEqual(result, mock_data)


class TestMemoize(unittest.TestCase):
    """Test case for the `memoize` decorator.

    This test ensures that the `memoize` decorator correctly caches the
    result of a method decorated as a property, such that the original
    method is only called once, even if accessed multiple times.
    """

    def test_memoize(self):
        """Test that `memoize` caches the result and avoids repeated
        method calls.

        Defines a class with a memoized property that wraps a method.
        The method is mocked to return a fixed value. This test confirms
        that:
        - the result returned by the memoized property is as expected.
        - the underlying method is only called once, even when the property
        is accessed multiple times.`
        """

        class TestClass:
            def a_method(self):
                return 42

            @memoize
            def a_property(self):
                return self.a_method()

        with patch.object(
            TestClass,
            "a_method",
            return_value=42,
        ) as mock_method:
            test_class = TestClass()

            self.assertEqual(test_class.a_property, 42)
            self.assertEqual(test_class.a_property, 42)
            mock_method.assert_called_once()


if __name__ == "__main__":
    unittest.main()
