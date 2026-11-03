"""Structural checks. Mock the OS call to avoid running shell commands in tests."""
import unittest
from unittest.mock import patch
import subprocess

from app import app, make_command, ATTACK_TARGET, NORMAL_TARGET


class LabTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_index(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"VULNERABLE MODE", response.data)

    def test_normal_request_builds_ping(self):
        with patch("app.subprocess.run", return_value=subprocess.CompletedProcess([], 0, "demo-ping-output", "")) as run:
            response = self.client.post("/diagnose", data={"target": NORMAL_TARGET})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"demo-ping-output", response.data)
        self.assertTrue(run.call_args.kwargs["shell"])
        self.assertIn(NORMAL_TARGET, run.call_args.args[0])

    def test_attack_is_not_sanitized_and_inband_output_is_displayed(self):
        with patch("app.subprocess.run", return_value=subprocess.CompletedProcess([], 0, "lab\\student", "")) as run:
            response = self.client.post("/diagnose", data={"target": ATTACK_TARGET})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"whoami", response.data)
        self.assertIn(b"lab\\student", response.data)
        self.assertEqual(run.call_args.args[0], make_command(ATTACK_TARGET))
        self.assertTrue(run.call_args.kwargs["shell"])


if __name__ == "__main__":
    unittest.main()
