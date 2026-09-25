import json
from datetime import datetime, timezone


MAX_PROFILE_BYTES = 32768
MAX_PROFILES = 32


class _ParserInputError(ValueError):
    """A deliberate parser rejection with a stable public problem code."""


def _unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise _ParserInputError("DUPLICATE_JSON_KEY")
        result[key] = value
    return result


def _reject_constant(_value: str) -> None:
    raise _ParserInputError("JSON_CONSTANT_INVALID")


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
    except _ParserInputError:
        raise
    except (RecursionError, ValueError):
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


_PROFILE_FIELDS = frozenset({
    "profile_id",
    "device_id",
    "client_id",
    "principal_id",
    "credential_ref",
    "credential_type",
    "credential_state",
    "not_before",
    "not_after",
    "rotation_due_at",
    "tls",
    "authorization",
})
_TLS_FIELDS = frozenset({
    "enabled",
    "verify_server",
    "server_name",
    "trust_ref",
    "client_auth",
})
_AUTHORIZATION_FIELDS = frozenset({"default", "rules"})
_IDENTITY_FIELDS = {
    "profile_id": "PROFILE_ID_REUSED",
    "device_id": "DEVICE_ID_REUSED",
    "client_id": "CLIENT_ID_REUSED",
    "principal_id": "DEVICE_PRINCIPAL_REUSED",
    "credential_ref": "CREDENTIAL_REF_REUSED",
}


def _add_finding(
    findings: list[dict[str, str]], code: str, path: str
) -> None:
    finding = {"code": code, "path": path}
    if finding not in findings:
        findings.append(finding)


def _report(
    profile_id: str | None,
    findings: list[dict[str, str]],
) -> dict[str, object]:
    return {
        "profile_id": profile_id,
        "decision": "DENY" if findings else "PASS",
        "findings": findings,
    }


def _invalid_document_report(code: str, path: str) -> list[dict[str, object]]:
    findings: list[dict[str, str]] = []
    _add_finding(findings, code, path)
    return [_report(None, findings)]


def evaluate_document(
    document: object,
    *,
    reference_time: datetime,
) -> list[dict[str, object]]:
    """Evaluate identity and TLS declarations without I/O or mutable state."""
    if (
        not isinstance(document, dict)
        or set(document) != {"schema_version", "profiles"}
        or type(document.get("schema_version")) is not int
        or document.get("schema_version") != 1
    ):
        return _invalid_document_report("DOCUMENT_SHAPE_INVALID", "$")

    profiles = document["profiles"]
    if not isinstance(profiles, list) or not 1 <= len(profiles) <= MAX_PROFILES:
        return _invalid_document_report("PROFILES_INVALID", "profiles")

    seen_values = {field: set() for field in _IDENTITY_FIELDS}
    reports: list[dict[str, object]] = []

    for index, profile in enumerate(profiles):
        profile_path = f"profiles[{index}]"
        if not isinstance(profile, dict):
            findings: list[dict[str, str]] = []
            _add_finding(findings, "PROFILE_SHAPE_INVALID", profile_path)
            reports.append(_report(None, findings))
            continue

        raw_profile_id = profile.get("profile_id")
        profile_id = (
            raw_profile_id
            if isinstance(raw_profile_id, str) and raw_profile_id.strip()
            else None
        )
        findings = []
        if set(profile) != _PROFILE_FIELDS:
            _add_finding(findings, "PROFILE_FIELDS_INVALID", profile_path)

        valid_identity: dict[str, str] = {}
        for field, reused_code in _IDENTITY_FIELDS.items():
            value = profile.get(field)
            path = f"{profile_path}.{field}"
            if not isinstance(value, str) or not value.strip():
                _add_finding(findings, "IDENTITY_FIELD_INVALID", path)
                continue
            valid_identity[field] = value
            if value in seen_values[field]:
                _add_finding(findings, reused_code, path)
            else:
                seen_values[field].add(value)

        device_id = valid_identity.get("device_id")
        client_id = valid_identity.get("client_id")
        principal_id = valid_identity.get("principal_id")
        if device_id is not None and client_id is not None and client_id != device_id:
            _add_finding(
                findings,
                "CLIENT_ID_MISMATCH",
                f"{profile_path}.client_id",
            )
        if (
            device_id is not None
            and principal_id is not None
            and principal_id != f"device:{device_id}"
        ):
            _add_finding(
                findings,
                "DEVICE_PRINCIPAL_MISMATCH",
                f"{profile_path}.principal_id",
            )

        credential_type = profile.get("credential_type")
        if credential_type != "x509_client_certificate":
            _add_finding(
                findings,
                "CREDENTIAL_TYPE_INVALID",
                f"{profile_path}.credential_type",
            )

        credential_state = profile.get("credential_state")
        if not isinstance(credential_state, str) or not credential_state.strip():
            _add_finding(
                findings,
                "CREDENTIAL_STATE_INVALID",
                f"{profile_path}.credential_state",
            )

        for field in ("not_before", "not_after", "rotation_due_at"):
            try:
                parse_utc_timestamp(profile.get(field))
            except ValueError:
                _add_finding(
                    findings,
                    "TIMESTAMP_INVALID",
                    f"{profile_path}.{field}",
                )

        tls = profile.get("tls")
        if not isinstance(tls, dict):
            _add_finding(findings, "TLS_FIELDS_INVALID", f"{profile_path}.tls")
        else:
            tls_path = f"{profile_path}.tls"
            if set(tls) != _TLS_FIELDS:
                _add_finding(findings, "TLS_FIELDS_INVALID", tls_path)

            enabled = tls.get("enabled")
            if type(enabled) is not bool:
                _add_finding(
                    findings,
                    "TLS_ENABLED_INVALID",
                    f"{tls_path}.enabled",
                )
            elif not enabled:
                _add_finding(findings, "TLS_DISABLED", f"{tls_path}.enabled")

            verify_server = tls.get("verify_server")
            if type(verify_server) is not bool:
                _add_finding(
                    findings,
                    "TLS_SERVER_VERIFY_INVALID",
                    f"{tls_path}.verify_server",
                )
            elif not verify_server:
                _add_finding(
                    findings,
                    "TLS_SERVER_VERIFY_DISABLED",
                    f"{tls_path}.verify_server",
                )

            server_name = tls.get("server_name")
            if (
                not isinstance(server_name, str)
                or not server_name.strip()
                or "*" in server_name
            ):
                _add_finding(
                    findings,
                    "TLS_SERVER_NAME_INVALID",
                    f"{tls_path}.server_name",
                )

            trust_ref = tls.get("trust_ref")
            if not isinstance(trust_ref, str) or not trust_ref.strip():
                _add_finding(
                    findings,
                    "TLS_TRUST_REF_INVALID",
                    f"{tls_path}.trust_ref",
                )

            if tls.get("client_auth") != "mutual_tls":
                _add_finding(
                    findings,
                    "TLS_CLIENT_AUTH_INVALID",
                    f"{tls_path}.client_auth",
                )

        authorization = profile.get("authorization")
        if not isinstance(authorization, dict):
            _add_finding(
                findings,
                "AUTHORIZATION_FIELDS_INVALID",
                f"{profile_path}.authorization",
            )
        else:
            authorization_path = f"{profile_path}.authorization"
            if set(authorization) != _AUTHORIZATION_FIELDS:
                _add_finding(
                    findings,
                    "AUTHORIZATION_FIELDS_INVALID",
                    authorization_path,
                )
            default = authorization.get("default")
            if not isinstance(default, str) or not default.strip():
                _add_finding(
                    findings,
                    "AUTHORIZATION_DEFAULT_INVALID",
                    f"{authorization_path}.default",
                )
            if not isinstance(authorization.get("rules"), list):
                _add_finding(
                    findings,
                    "AUTHORIZATION_RULES_INVALID",
                    f"{authorization_path}.rules",
                )

        reports.append(_report(profile_id, findings))

    return reports
