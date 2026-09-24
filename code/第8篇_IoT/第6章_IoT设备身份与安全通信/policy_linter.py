import json
from datetime import datetime, timezone


MAX_PROFILE_BYTES = 32768
MAX_PROFILES = 32


def _unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("DUPLICATE_JSON_KEY")
        result[key] = value
    return result


def _reject_constant(_value: str) -> None:
    raise ValueError("JSON_CONSTANT_INVALID")


def parse_document(raw: bytes) -> dict[str, object]:
    if not isinstance(raw, bytes):
        raise ValueError("INPUT_TYPE_INVALID")
    if len(raw) > MAX_PROFILE_BYTES:
        raise ValueError("INPUT_SIZE_INVALID")

    try:
        text = raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError:
        raise ValueError("UTF8_INVALID") from None

    try:
        document = json.loads(
            text,
            object_pairs_hook=_unique_object,
            parse_constant=_reject_constant,
        )
    except json.JSONDecodeError:
        raise ValueError("JSON_INVALID") from None

    if not isinstance(document, dict):
        raise ValueError("ROOT_TYPE_INVALID")
    if set(document) != {"schema_version", "profiles"}:
        raise ValueError("ROOT_KEYS_INVALID")
    if type(document["schema_version"]) is not int or document["schema_version"] != 1:
        raise ValueError("SCHEMA_VERSION_INVALID")

    profiles = document["profiles"]
    if not isinstance(profiles, list) or not 1 <= len(profiles) <= MAX_PROFILES:
        raise ValueError("PROFILES_INVALID")

    return document


def parse_utc_timestamp(value: object) -> datetime:
    if not isinstance(value, str):
        raise ValueError("TIMESTAMP_INVALID")

    timestamp_format = "%Y-%m-%dT%H:%M:%SZ"
    try:
        parsed = datetime.strptime(value, timestamp_format)
    except ValueError:
        raise ValueError("TIMESTAMP_INVALID") from None

    if parsed.strftime(timestamp_format) != value:
        raise ValueError("TIMESTAMP_INVALID")

    return parsed.replace(tzinfo=timezone.utc)
