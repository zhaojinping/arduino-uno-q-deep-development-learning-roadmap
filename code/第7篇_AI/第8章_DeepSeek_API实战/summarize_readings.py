"""Explicitly gated CLI example; default invocation performs no network I/O."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Callable, Sequence

from deepseek_client import DeepSeekClient, DeepSeekError


SYNTHETIC_READINGS = {
    "temperature_c": 23.4,
    "humidity_pct": 47.0,
    "sample_age_s": 2,
}


def main(
    argv: Sequence[str] | None = None,
    *,
    client_factory: Callable[[], DeepSeekClient] | None = None,
) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--send-request",
        action="store_true",
        help="send one paid HTTPS request containing only the fixed synthetic readings",
    )
    parser.add_argument(
        "--confirm-network-and-cost",
        action="store_true",
        help="confirm the possible charge and transfer to the public DeepSeek service",
    )
    args = parser.parse_args(argv)
    if not (args.send_request and args.confirm_network_and_cost):
        print("DRY_RUN: no credential was read and no network request was made.")
        print("To send one request, both explicit flags are required.")
        return 0

    make_client = client_factory or DeepSeekClient.from_environment
    try:
        result = make_client().summarize_readings(SYNTHETIC_READINGS)
    except DeepSeekError as error:
        print(f"REQUEST_FAILED: {error}", file=sys.stderr)
        return 1
    print("REPORT_ONLY: model text is untrusted and must be reviewed by a person.")
    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
