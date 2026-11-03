"""One-fix app tests. OS execution is always mocked in these tests."""
import subprocess
import unittest
from unittest.mock import patch

from app import app, make_command, validate_ipv4, NORMAL_TARGET, ATTACK_TARGET


class AllowlistOnlyTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_homepage_mentions_one_mitigation(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"ALLOW-LIST MODE", response.data)

    def test_normal_valid_ipv4_still_runs_ping_with_original_shell(self):
        fake = subprocess.CompletedProcess(args=[], returncode=0,
                                           stdout="NORMAL_PING_OUTPUT", stderr="")
        with patch("app.subprocess.run", return_value=fake) as run:
            response = self.client.post("/diagnose", data={"target": NORMAL_TARGET})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"NORMAL_PING_OUTPUT", response.data)
        self.assertEqual(run.call_count, 1)
        self.assertTrue(run.call_args.kwargs["shell"],
                        "shell=True is intentionally left unchanged")
        self.assertEqual(run.call_args.args[0], make_command(NORMAL_TARGET))

    def test_original_attack_blocked_before_subprocess(self):
        with patch("app.subprocess.run") as run:
            response = self.client.post("/diagnose", data={"target": ATTACK_TARGET})
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"BLOCKED", response.data)
        self.assertIn(b"No OS command was executed", response.data)
        run.assert_not_called()

    def test_more_injections_and_bad_inputs_blocked(self):
        invalid = [
            "127.0.0.1 & dir", "127.0.0.1 & type demo.txt",
            "127.0.0.1 && whoami", "127.0.0.1 | whoami",
            "127.0.0.1; whoami", "127.0.0.1 || whoami",
            "localhost", "256.256.256.256", "127.0.0.1 -n 2", "", "::1",
        ]
        for target in invalid:
            with self.subTest(target=target):
                with patch("app.subprocess.run") as run:
                    response = self.client.post("/diagnose", data={"target": target})
                self.assertEqual(response.status_code, 400)
                run.assert_not_called()

    def test_ipv4_allowlist_accepts_only_ipv4(self):
        self.assertEqual(validate_ipv4("127.0.0.1"), "127.0.0.1")
        self.assertEqual(validate_ipv4("192.0.2.1"), "192.0.2.1")
        with self.assertRaises(ValueError):
            validate_ipv4("127.0.0.1 & whoami")
        with self.assertRaises(ValueError):
            validate_ipv4("localhost")


if __name__ == "__main__":
    unittest.main()
