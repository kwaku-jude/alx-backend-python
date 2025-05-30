#!/usr/bin/env python3
"""Test file to test client.py"""

from typing import Any
import unittest
from parameterized import parameterized
from unittest.mock import patch, Mock, PropertyMock
import client


class TestGithubOrgClient(unittest.TestCase):
    """A class to Test GithubClient from client module"""

    @parameterized.expand(["google", "abc"])
    @patch("client.get_json")
    def test_org(self, org_name, mock_get):
        mock_get.return_value = {"login": org_name}

        obj = client.GithubOrgClient(org_name)
        result = obj.org
        self.assertEqual(result, {"login": org_name})
        mock_get.assert_called_once_with(
            f"https://api.github.com/orgs/{org_name}",
        )

    def test_public_repos_url(self):
        """A method that test the _public_repos_url"""
        payload = {
            "login": "google",
            "id": 12345,
            "url": "www.example.com",
            "description": "Google ❤️ Open Source",
            "repos_url": "https://api.github.com/orgs/google/repos",
        }
        with patch.object(
            client.GithubOrgClient,
            "org",
            new_callable=PropertyMock,
        ) as mock_org:
            mock_org.return_value = payload

            obj = client.GithubOrgClient("google")
            result = obj._public_repos_url

            self.assertEqual(result, payload["repos_url"])

    @patch("client.get_json")
    def test_public_repos(self, mock_get: Mock) -> Any:
        """A method to test the public_repos method"""

        repos = [
            {"name": "repo1"},
            {"name": "repo2"},
            {"name": "repo3"},
        ]
        with patch.object(
            client.GithubOrgClient,
            "_public_repos_url",
            new_callable=PropertyMock,
        ) as mock_public:
            mock_public.return_value = "http://www.example.com"
            mock_get.return_value = repos

            obj = client.GithubOrgClient("google")
            result = [repo["name"] for repo in repos]

            self.assertEqual(obj.public_repos(), result)
            mock_get.assert_called_once()
            mock_public.assert_called_once()


if __name__ == "__main__":
    unittest.main()
