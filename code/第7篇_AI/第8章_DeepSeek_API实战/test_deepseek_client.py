"""Fully offline contract tests for the DeepSeek report-only client."""

from __future__ import annotations

import json
import io
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from urllib.request import Request


sys.path.insert(0, str(Path(__file__).resolve().parent))
from deepseek_client import (  # noqa: E402
    APIError,
    ConfigurationError,
    DeepSeekClient,
    InputValidationError,
    ResponseError,
    TransportError,
)
from summarize_readings import main as run_example  # noqa: E402


SYNTHETIC_CREDENTIAL = "SYNTHETIC-CREDENTIAL-DO-NOT-USE"
READINGS = {
    "temperature_c": 23.4,
    "humidity_pct": 47.0,
    "sample_age_s": 2,
}
SUCCESS_RESPONSE = {
    "choices": [
        {"message": {"role": "assistant", "content": "合成读数正常；此说明仅供复核。"}}
    ]
}


class RecordingTransport:
    def __init__(self, response: tuple[int, bytes] | Exception):
        self.response = response
        self.calls: list[tuple[Request, float]] = []

    def __call__(self, request: Request, timeout: float) -> tuple[int, bytes]:
        self.calls.append((request, timeout))
        if isinstance(self.response, Exception):
            raise self.response
        return self.response


class DeepSeekClientTests(unittest.TestCase):
    def make_client(self, response: tuple[int, bytes] | Exception = (200, json.dumps(SUCCESS_RESPONSE).encode())):
        transport = RecordingTransport(response)
        return DeepSeekClient(SYNTHETIC_CREDENTIAL, transport=transport, timeout=3.0), transport

    def test_request_uses_current_bounded_report_only_schema(self):
        client, transport = self.make_client()
        result = client.summarize_readings(READINGS)

        self.assertEqual(result, "合成读数正常；此说明仅供复核。")
        self.assertEqual(len(transport.calls), 1)
        request, timeout = transport.calls[0]
        self.assertEqual(request.full_url, "https://api.deepseek.com/chat/completions")
        self.assertEqual(request.method, "POST")
        self.assertEqual(timeout, 3.0)
        self.assertEqual(request.get_header("Authorization"), f"Bearer {SYNTHETIC_CREDENTIAL}")
        self.assertEqual(request.get_header("Content-type"), "application/json")
        body = json.loads(request.data)
        self.assertEqual(body["model"], "deepseek-flash")
        self.assertEqual(body["thinking"], {"type": "disabled"})
        self.assertEqual(body["max_tokens"], 256)
        self.assertIs(body["stream"], False)
        self.assertEqual([item["role"] for item in body["messages"]], ["system", "user"])
        self.assertIn("temperature_c", body["messages"][1]["content"])
        self.assertIn("仅供复核", body["messages"][0]["content"])

    def test_environment_factory_fails_closed_without_local_credential(self):
        with self.assertRaises(ConfigurationError) as raised:
            DeepSeekClient.from_environment({}, transport=RecordingTransport((200, b"{}")))
        self.assertNotIn(SYNTHETIC_CREDENTIAL, str(raised.exception))

    def test_readings_reject_extra_fields_and_out_of_range_or_nonfinite_values(self):
        client, transport = self.make_client()
        invalid = (
            {**READINGS, "command": "turn on actuator"},
            {**READINGS, "temperature_c": float("nan")},
            {**READINGS, "humidity_pct": 101},
            {**READINGS, "sample_age_s": -1},
        )
        for readings in invalid:
            with self.subTest(readings=readings):
                with self.assertRaises(InputValidationError):
                    client.summarize_readings(readings)
        self.assertEqual(transport.calls, [])

    def test_rejects_http_api_errors_without_echoing_body_or_credential(self):
        api_body = json.dumps({"error": {"message": SYNTHETIC_CREDENTIAL}}).encode()
        client, _transport = self.make_client((429, api_body))
        with self.assertRaises(APIError) as raised:
            client.summarize_readings(READINGS)
        self.assertIn("429", str(raised.exception))
        self.assertNotIn(SYNTHETIC_CREDENTIAL, str(raised.exception))

    def test_rejects_malformed_or_unexpected_response_schema(self):
        cases = ((200, b"not-json"), (200, b'{"choices":[]}'))
        for response in cases:
            with self.subTest(response=response):
                client, _transport = self.make_client(response)
                with self.assertRaises(ResponseError) as raised:
                    client.summarize_readings(READINGS)
                self.assertNotIn(SYNTHETIC_CREDENTIAL, str(raised.exception))

    def test_rejects_oversized_response_before_json_decode(self):
        client, _transport = self.make_client((200, b" " * (64 * 1024 + 1)))
        with self.assertRaises(ResponseError):
            client.summarize_readings(READINGS)

    def test_timeout_is_sanitized_and_never_automatically_replayed(self):
        client, transport = self.make_client(TimeoutError(SYNTHETIC_CREDENTIAL))
        with self.assertRaises(TransportError) as raised:
            client.summarize_readings(READINGS)
        self.assertEqual(len(transport.calls), 1)
        self.assertNotIn(SYNTHETIC_CREDENTIAL, str(raised.exception))

    def test_non_text_completion_is_rejected_without_exposing_payload(self):
        response = {"choices": [{"message": {"content": None}}]}
        client, _transport = self.make_client((200, json.dumps(response).encode()))
        with self.assertRaises(ResponseError):
            client.summarize_readings(READINGS)

    def test_cli_defaults_to_dry_run_without_constructing_a_client(self):
        factory_calls: list[bool] = []

        def unexpected_client_factory():
            factory_calls.append(True)
            raise AssertionError("dry-run must not read credentials or construct a client")

        output = io.StringIO()
        with redirect_stdout(output):
            exit_code = run_example([], client_factory=unexpected_client_factory)

        self.assertEqual(exit_code, 0)
        self.assertIn("DRY_RUN", output.getvalue())
        self.assertEqual(factory_calls, [])

    def test_cli_requires_both_flags_before_constructing_a_client(self):
        for arguments in (
            ["--send-request"],
            ["--confirm-network-and-cost"],
        ):
            factory_calls: list[bool] = []
            output = io.StringIO()
            with self.subTest(arguments=arguments), redirect_stdout(output):
                exit_code = run_example(
                    arguments,
                    client_factory=lambda: factory_calls.append(True),
                )
            self.assertEqual(exit_code, 0)
            self.assertIn("DRY_RUN", output.getvalue())
            self.assertEqual(factory_calls, [])


if __name__ == "__main__":
    unittest.main()
