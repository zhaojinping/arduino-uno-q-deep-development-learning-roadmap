"""Small, bounded, report-only DeepSeek Chat Completions client.

All tests inject a transport. The default urllib transport is used only when a
caller explicitly runs the example with its two confirmation flags.
"""

from __future__ import annotations

import json
import math
import os
from collections.abc import Callable, Mapping
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


API_ENDPOINT = "https://api.deepseek.com/chat/completions"
MODEL = "deepseek-flash"
REQUEST_TIMEOUT_SECONDS = 20.0
MAX_REQUEST_BYTES = 8 * 1024
MAX_RESPONSE_BYTES = 64 * 1024
MAX_OUTPUT_TOKENS = 256
REQUIRED_READING_FIELDS = frozenset({"temperature_c", "humidity_pct", "sample_age_s"})

REPORT_ONLY_SYSTEM_PROMPT = (
    "你是实验室读数解释助手。只依据用户提供的合成读数，用简体中文给出简短说明并指出必要限制。"
    "结果仅供复核，由人工审阅；不得生成设备控制命令、声称检查过真实硬件或授权执行器动作。"
)

Transport = Callable[[Request, float], tuple[int, bytes]]


class DeepSeekError(Exception):
    """Base class for deliberately sanitized client errors."""


class ConfigurationError(DeepSeekError):
    """The local client configuration is absent or invalid."""


class InputValidationError(DeepSeekError):
    """The synthetic readings do not satisfy the small request contract."""


class APIError(DeepSeekError):
    """DeepSeek returned a non-success HTTP status; response bodies are omitted."""

    def __init__(self, status_code: int) -> None:
        self.status_code = status_code
        super().__init__(f"DeepSeek API returned HTTP {status_code}; response body was omitted")


class ResponseError(DeepSeekError):
    """The response exceeded limits or did not match the expected schema."""


class TransportError(DeepSeekError):
    """The request failed or timed out; its remote outcome may be unknown."""


def _urllib_transport(request: Request, timeout: float) -> tuple[int, bytes]:
    """Send one HTTPS request and read at most the configured response limit."""
    try:
        with urlopen(request, timeout=timeout) as response:
            return response.status, response.read(MAX_RESPONSE_BYTES + 1)
    except HTTPError as error:
        status_code = error.code
        error.close()
        return status_code, b""
    except (URLError, TimeoutError, OSError):
        raise TransportError(
            "HTTPS request failed or timed out; outcome may be unknown; no automatic retry was made"
        ) from None


class DeepSeekClient:
    """A one-request client for summarizing three bounded synthetic readings."""

    def __init__(
        self,
        api_key: str,
        *,
        transport: Transport | None = None,
        timeout: float = REQUEST_TIMEOUT_SECONDS,
    ) -> None:
        if not isinstance(api_key, str) or not api_key.strip():
            raise ConfigurationError("A non-empty local API credential is required")
        if isinstance(timeout, bool) or not isinstance(timeout, (int, float)):
            raise ConfigurationError("timeout must be a positive finite number of seconds")
        if not math.isfinite(timeout) or timeout <= 0:
            raise ConfigurationError("timeout must be a positive finite number of seconds")
        self._api_key = api_key.strip()
        self._transport = transport or _urllib_transport
        self._timeout = float(timeout)

    @classmethod
    def from_environment(
        cls,
        environ: Mapping[str, str] | None = None,
        *,
        transport: Transport | None = None,
        timeout: float = REQUEST_TIMEOUT_SECONDS,
    ) -> "DeepSeekClient":
        """Read the credential from this process's local environment only."""
        source = os.environ if environ is None else environ
        api_key = source.get("DEEPSEEK_API_KEY", "")
        if not isinstance(api_key, str) or not api_key.strip():
            raise ConfigurationError(
                "DEEPSEEK_API_KEY is not configured in the local process environment"
            )
        return cls(api_key, transport=transport, timeout=timeout)

    @staticmethod
    def _validate_readings(readings: Mapping[str, object]) -> dict[str, int | float]:
        if not isinstance(readings, Mapping) or set(readings) != REQUIRED_READING_FIELDS:
            raise InputValidationError(
                "readings must contain exactly temperature_c, humidity_pct, and sample_age_s"
            )

        bounded: dict[str, int | float] = {}
        limits = {
            "temperature_c": (-40.0, 125.0),
            "humidity_pct": (0.0, 100.0),
            "sample_age_s": (0.0, 86_400.0),
        }
        for name, (minimum, maximum) in limits.items():
            value = readings[name]
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise InputValidationError(f"{name} must be a finite number in the allowed range")
            if not math.isfinite(value) or not minimum <= value <= maximum:
                raise InputValidationError(f"{name} must be a finite number in the allowed range")
            bounded[name] = value
        return bounded

    def summarize_readings(self, readings: Mapping[str, object]) -> str:
        """Return a report-only summary; no tools or device operations are exposed."""
        bounded_readings = self._validate_readings(readings)
        user_content = json.dumps(
            bounded_readings,
            ensure_ascii=False,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        body = {
            "model": MODEL,
            "messages": [
                {"role": "system", "content": REPORT_ONLY_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": (
                        "以下是合成实验室读数，不对应真实设备，也不会触发动作。请给出仅供人工复核的摘要："
                        + user_content
                    ),
                },
            ],
            "thinking": {"type": "disabled"},
            "max_tokens": MAX_OUTPUT_TOKENS,
            "stream": False,
        }
        request_body = json.dumps(body, ensure_ascii=False, allow_nan=False).encode("utf-8")
        if len(request_body) > MAX_REQUEST_BYTES:
            raise InputValidationError("request exceeds the local byte limit")

        request = Request(
            API_ENDPOINT,
            data=request_body,
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            method="POST",
        )
        try:
            status_code, response_body = self._transport(request, self._timeout)
        except DeepSeekError:
            raise
        except Exception:
            # Transport exceptions can include request/header details; never echo them.
            raise TransportError(
                "HTTPS request failed or timed out; outcome may be unknown; no automatic retry was made"
            ) from None

        if isinstance(status_code, bool) or not isinstance(status_code, int) or not 100 <= status_code <= 599:
            raise ResponseError("transport returned an invalid HTTP status")
        if status_code < 200 or status_code >= 300:
            raise APIError(status_code)
        if not isinstance(response_body, bytes):
            raise ResponseError("transport returned a non-byte response")
        if len(response_body) > MAX_RESPONSE_BYTES:
            raise ResponseError("response exceeded the local byte limit")
        try:
            decoded = json.loads(response_body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            raise ResponseError("response was not valid UTF-8 JSON") from None

        if not isinstance(decoded, dict):
            raise ResponseError("response did not match the expected object schema")
        choices = decoded.get("choices")
        if not isinstance(choices, list) or not choices or not isinstance(choices[0], dict):
            raise ResponseError("response did not contain a completion choice")
        choice = choices[0]
        if choice.get("finish_reason") not in (None, "stop"):
            raise ResponseError("completion did not finish normally; report may be incomplete")
        message = choice.get("message")
        if not isinstance(message, dict):
            raise ResponseError("response choice did not contain a message")
        content = message.get("content")
        if not isinstance(content, str) or not content.strip():
            raise ResponseError("response message did not contain text")
        if len(content) > 16_384:
            raise ResponseError("response text exceeded the local character limit")
        return content.strip()
