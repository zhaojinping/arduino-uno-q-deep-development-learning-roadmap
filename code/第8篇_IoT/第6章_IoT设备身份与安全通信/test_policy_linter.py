import json
import io
import re
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock

try:
    import policy_linter
except ModuleNotFoundError as error:
    if error.name != "policy_linter":
        raise
    policy_linter = None


def valid_profile(device_id="uno-q-demo-01"):
    return {
        "profile_id": "profile-" + device_id,
        "device_id": device_id,
        "client_id": device_id,
        "principal_id": "device:" + device_id,
        "credential_ref": "synthetic://credential/" + device_id,
        "credential_type": "x509_client_certificate",
        "credential_state": "active",
        "not_before": "2026-01-01T00:00:00Z",
        "not_after": "2027-01-01T00:00:00Z",
        "rotation_due_at": "2026-10-01T00:00:00Z",
        "tls": {
            "enabled": True,
            "verify_server": True,
            "server_name": "broker.example.invalid",
            "trust_ref": "synthetic://trust/demo-root",
            "client_auth": "mutual_tls",
        },
        "authorization": {"default": "deny", "rules": []},
    }


def evaluate_one(profile):
    return policy_linter.evaluate_document(
        {"schema_version": 1, "profiles": [profile]},
        reference_time=datetime(2026, 9, 24, 12, 0, tzinfo=timezone.utc),
    )[0]


def finding_codes(report):
    return {finding["code"] for finding in report["findings"]}


class ParserBootstrapTests(unittest.TestCase):
    def test_parser_module_is_available(self):
        self.assertIsNotNone(policy_linter, "policy_linter.py has not been created")


@unittest.skipIf(policy_linter is None, "parser implementation is not available yet")
class ParserTests(unittest.TestCase):
    def test_root_profile_and_byte_limits(self):
        valid = json.dumps({
            "schema_version": 1,
            "profiles": [{}] * 32,
        }).encode("utf-8")
        self.assertEqual(len(policy_linter.parse_document(valid)["profiles"]), 32)
        at_limit = b'{"schema_version":1,"profiles":[{}]}'
        at_limit += b" " * (32768 - len(at_limit))
        self.assertEqual(len(at_limit), 32768)
        self.assertEqual(len(policy_linter.parse_document(at_limit)["profiles"]), 1)
        invalid = (
            b"[]",
            b'{"schema_version":1,"profiles":null}',
            b'{"schema_version":1,"profiles":[]}',
            b'{"schema_version":1,"profiles":[{}],"extra":0}',
            json.dumps({"schema_version": 1, "profiles": [{}] * 33}).encode("utf-8"),
        )
        for raw in invalid:
            with self.subTest(raw_length=len(raw)), self.assertRaises(ValueError):
                policy_linter.parse_document(raw)
        with self.assertRaisesRegex(ValueError, "INPUT_SIZE_INVALID"):
            policy_linter.parse_document(b" " * 32769)

    def test_duplicate_member_is_rejected(self):
        samples = (
            b'{"schema_version":1,"profiles":[],"profiles":[]}',
            b'{"schema_version":1,"profiles":[{"x":1,"x":2}]}',
        )
        for raw in samples:
            with self.subTest(raw_length=len(raw)), self.assertRaisesRegex(
                ValueError, "DUPLICATE_JSON_KEY"
            ):
                policy_linter.parse_document(raw)

    def test_nonfinite_and_invalid_utf8_are_rejected(self):
        nonfinite = (
            b'{"schema_version":1,"profiles":[],"x":NaN}',
            b'{"schema_version":1,"profiles":[Infinity]}',
            b'{"schema_version":1,"profiles":[-Infinity]}',
        )
        for raw in nonfinite:
            with self.subTest(raw=raw), self.assertRaisesRegex(
                ValueError, "JSON_CONSTANT_INVALID"
            ):
                policy_linter.parse_document(raw)
        with self.assertRaisesRegex(ValueError, "UTF8_INVALID"):
            policy_linter.parse_document(bytes((255,)))

    def test_long_integer_uses_stable_decoder_error(self):
        set_limit = getattr(sys, "set_int_max_str_digits", None)
        if set_limit is None:
            self.skipTest("runtime has no configurable JSON integer digit limit")
        previous_limit = sys.get_int_max_str_digits()
        try:
            set_limit(640)
            raw = b'{"schema_version":' + b"9" * 1000 + b',"profiles":[{}]}'
            with self.assertRaisesRegex(ValueError, "^JSON_INVALID$"):
                policy_linter.parse_document(raw)
        finally:
            set_limit(previous_limit)

    def test_decoder_recursion_error_uses_stable_code(self):
        raw = b'{"schema_version":1,"profiles":[{}]}'
        with mock.patch.object(
            policy_linter.json, "loads", side_effect=RecursionError
        ):
            with self.assertRaisesRegex(ValueError, "^JSON_INVALID$"):
                policy_linter.parse_document(raw)

    def test_bool_is_not_schema_version_one(self):
        with self.assertRaisesRegex(ValueError, "SCHEMA_VERSION_INVALID"):
            policy_linter.parse_document(b'{"schema_version":true,"profiles":[]}')

    def test_timestamp_requires_zulu_seconds(self):
        self.assertEqual(
            policy_linter.parse_utc_timestamp("2026-09-24T12:00:00Z").utcoffset().total_seconds(),
            0,
        )
        for value in ("2026-09-24", "2026-09-24T12:00:00+08:00", 1):
            with self.subTest(value=value), self.assertRaises(ValueError):
                policy_linter.parse_utc_timestamp(value)

    def test_timestamp_requires_zero_padded_fields(self):
        with self.assertRaises(ValueError):
            policy_linter.parse_utc_timestamp("2026-9-24T12:00:00Z")

    def test_valid_identity_tls_profile_has_stable_report_shape(self):
        report = policy_linter.evaluate_document(
            {"schema_version": 1, "profiles": [valid_profile()]},
            reference_time=datetime(2026, 9, 24, 12, 0, tzinfo=timezone.utc),
        )
        self.assertEqual(
            report,
            [{
                "profile_id": "profile-uno-q-demo-01",
                "decision": "PASS",
                "findings": [],
            }],
        )
        self.assertEqual(set(report[0]), {"profile_id", "decision", "findings"})

    def test_identity_fields_must_be_unique_across_profiles(self):
        duplicate_cases = (
            ("profile_id", "PROFILE_ID_REUSED"),
            ("device_id", "DEVICE_ID_REUSED"),
            ("principal_id", "DEVICE_PRINCIPAL_REUSED"),
            ("client_id", "CLIENT_ID_REUSED"),
            ("credential_ref", "CREDENTIAL_REF_REUSED"),
        )
        for field, expected_code in duplicate_cases:
            first = valid_profile("uno-q-demo-01")
            second = valid_profile("uno-q-demo-02")
            second[field] = first[field]
            with self.subTest(field=field):
                reports = policy_linter.evaluate_document(
                    {"schema_version": 1, "profiles": [first, second]},
                    reference_time=datetime(2026, 9, 24, 12, 0, tzinfo=timezone.utc),
                )
                findings = reports[1]["findings"]
                self.assertIn(expected_code, {finding["code"] for finding in findings})
                self.assertTrue(all(set(finding) == {"code", "path"} for finding in findings))
                self.assertNotIn(first[field], repr(findings))

    def test_client_and_principal_must_match_device_mapping(self):
        profile = valid_profile()
        profile["client_id"] = "some-other-client"
        profile["principal_id"] = "some-other-principal"
        report = policy_linter.evaluate_document(
            {"schema_version": 1, "profiles": [profile]},
            reference_time=datetime(2026, 9, 24, 12, 0, tzinfo=timezone.utc),
        )[0]
        codes = {finding["code"] for finding in report["findings"]}
        self.assertIn("CLIENT_ID_MISMATCH", codes)
        self.assertIn("DEVICE_PRINCIPAL_MISMATCH", codes)

    def test_tls_baseline_is_enforced(self):
        profile = valid_profile()
        profile["tls"].update({
            "enabled": False,
            "verify_server": False,
            "server_name": "*.example.invalid",
            "trust_ref": "",
            "client_auth": "none",
        })
        report = policy_linter.evaluate_document(
            {"schema_version": 1, "profiles": [profile]},
            reference_time=datetime(2026, 9, 24, 12, 0, tzinfo=timezone.utc),
        )[0]
        codes = {finding["code"] for finding in report["findings"]}
        self.assertTrue({
            "TLS_DISABLED",
            "TLS_SERVER_VERIFY_DISABLED",
            "TLS_SERVER_NAME_INVALID",
            "TLS_TRUST_REF_INVALID",
            "TLS_CLIENT_AUTH_INVALID",
        }.issubset(codes))

    def test_nested_profile_tls_and_authorization_shapes_are_exact(self):
        cases = []
        profile = valid_profile()
        del profile["credential_ref"]
        cases.append((profile, "PROFILE_FIELDS_INVALID"))
        profile = valid_profile()
        profile["unexpected"] = "synthetic"
        cases.append((profile, "PROFILE_FIELDS_INVALID"))
        profile = valid_profile()
        del profile["tls"]["trust_ref"]
        cases.append((profile, "TLS_FIELDS_INVALID"))
        profile = valid_profile()
        profile["tls"]["unexpected"] = "synthetic"
        cases.append((profile, "TLS_FIELDS_INVALID"))
        profile = valid_profile()
        del profile["authorization"]["rules"]
        cases.append((profile, "AUTHORIZATION_FIELDS_INVALID"))
        for profile, expected_code in cases:
            with self.subTest(expected_code=expected_code, keys=tuple(profile)):
                report = policy_linter.evaluate_document(
                    {"schema_version": 1, "profiles": [profile]},
                    reference_time=datetime(2026, 9, 24, 12, 0, tzinfo=timezone.utc),
                )[0]
                self.assertIn(expected_code, {f["code"] for f in report["findings"]})

    def test_exact_own_device_acl_pairs_are_allowed(self):
        profile = valid_profile()
        device_id = profile["device_id"]
        profile["authorization"]["rules"] = [
            {"effect": "allow", "operation": "publish", "topic": f"demo/v1/devices/{device_id}/telemetry"},
            {"effect": "allow", "operation": "publish", "topic": f"demo/v1/devices/{device_id}/state"},
            {"effect": "allow", "operation": "subscribe", "topic": f"demo/v1/devices/{device_id}/commands"},
        ]
        report = evaluate_one(profile)
        self.assertEqual(report["decision"], "PASS")
        self.assertFalse(finding_codes(report))

    def test_default_must_deny_and_wrong_topic_directions_are_rejected(self):
        profile = valid_profile()
        profile["authorization"] = {
            "default": "allow",
            "rules": [
                {"effect": "allow", "operation": "subscribe", "topic": "demo/v1/devices/uno-q-demo-01/telemetry"},
                {"effect": "allow", "operation": "publish", "topic": "demo/v1/devices/uno-q-demo-01/commands"},
            ],
        }
        report = evaluate_one(profile)
        codes = finding_codes(report)
        self.assertIn("ACL_DEFAULT_NOT_DENY", codes)
        self.assertIn("ACL_RULE_NOT_ALLOWED", codes)
        self.assertEqual(report["decision"], "DENY")

    def test_wildcards_and_cross_device_topics_are_rejected(self):
        profile = valid_profile()
        profile["authorization"]["rules"] = [
            {"effect": "allow", "operation": "subscribe", "topic": "demo/v1/devices/+/commands"},
            {"effect": "allow", "operation": "subscribe", "topic": "demo/v1/devices/#"},
            {"effect": "allow", "operation": "subscribe", "topic": "demo/v1/devices/uno-q-demo-02/commands"},
            {"effect": "allow", "operation": "publish", "topic": "demo/v1/devices/uno-q-demo-02"},
        ]
        codes = finding_codes(evaluate_one(profile))
        self.assertIn("ACL_WILDCARD_TOO_BROAD", codes)
        self.assertIn("ACL_CROSS_DEVICE_TOPIC", codes)

    def test_unknown_duplicate_and_malformed_rules_are_rejected(self):
        profile = valid_profile()
        permitted = {
            "effect": "allow",
            "operation": "publish",
            "topic": "demo/v1/devices/uno-q-demo-01/state",
        }
        profile["authorization"]["rules"] = [
            permitted,
            dict(permitted),
            {"effect": "allow", "operation": "execute", "topic": "demo/v1/devices/uno-q-demo-01/state"},
            {"effect": "deny", "operation": "publish", "topic": "demo/v1/devices/uno-q-demo-01/state"},
            {"effect": "allow", "operation": "publish"},
            {"effect": "allow", "operation": "publish", "topic": "demo/v1/devices/uno-q-demo-01/state", "qos": 1},
            {"effect": "allow", "operation": "publish", "topic": None},
        ]
        report = evaluate_one(profile)
        codes = finding_codes(report)
        self.assertTrue({
            "ACL_DUPLICATE_RULE",
            "ACL_OPERATION_INVALID",
            "ACL_RULE_NOT_ALLOWED",
            "ACL_RULE_FIELDS_INVALID",
        }.issubset(codes))
        self.assertTrue(all(set(finding) == {"code", "path"} for finding in report["findings"]))

    def test_acl_rule_limit_is_sixteen(self):
        profile = valid_profile()
        profile["authorization"]["rules"] = [
            {
                "effect": "allow",
                "operation": "publish",
                "topic": f"demo/v1/devices/uno-q-demo-01/custom/{index}",
            }
            for index in range(16)
        ]
        codes_at_limit = finding_codes(evaluate_one(profile))
        self.assertNotIn("ACL_RULE_LIMIT_EXCEEDED", codes_at_limit)
        profile["authorization"]["rules"].append({
            "effect": "allow",
            "operation": "publish",
            "topic": "demo/v1/devices/uno-q-demo-01/custom/16",
        })
        self.assertIn("ACL_RULE_LIMIT_EXCEEDED", finding_codes(evaluate_one(profile)))

    def test_acl_findings_do_not_echo_topic_values(self):
        profile = valid_profile()
        marker = "synthetic-topic-marker"
        profile["authorization"]["rules"] = [
            {"effect": "allow", "operation": "publish", "topic": marker}
        ]
        report = evaluate_one(profile)
        self.assertNotIn(marker, json.dumps(report, sort_keys=True))

    def test_device_id_must_be_a_single_literal_mqtt_topic_level(self):
        for invalid_device_id in (
            "uno-q/demo",
            "uno-q+demo",
            "uno-q#demo",
            "uno-q\x00demo",
        ):
            with self.subTest(device_id=invalid_device_id):
                report = evaluate_one(valid_profile(invalid_device_id))
                self.assertEqual(report["decision"], "DENY")
                self.assertIn(
                    "DEVICE_ID_TOPIC_SEGMENT_INVALID",
                    finding_codes(report),
                )
                self.assertNotIn(invalid_device_id, repr(report["findings"]))

    def test_identity_tls_and_timestamp_types_are_checked(self):
        profile = valid_profile()
        profile["device_id"] = None
        profile["tls"]["enabled"] = 1
        profile["tls"]["verify_server"] = 1
        profile["tls"]["server_name"] = 12
        profile["tls"]["trust_ref"] = False
        profile["credential_type"] = "other"
        profile["not_before"] = "2026-9-1T00:00:00Z"
        report = policy_linter.evaluate_document(
            {"schema_version": 1, "profiles": [profile]},
            reference_time=datetime(2026, 9, 24, 12, 0, tzinfo=timezone.utc),
        )[0]
        codes = {finding["code"] for finding in report["findings"]}
        self.assertTrue({
            "IDENTITY_FIELD_INVALID",
            "TLS_ENABLED_INVALID",
            "TLS_SERVER_VERIFY_INVALID",
            "TLS_SERVER_NAME_INVALID",
            "TLS_TRUST_REF_INVALID",
            "CREDENTIAL_TYPE_INVALID",
            "TIMESTAMP_INVALID",
        }.issubset(codes))

    def test_profile_order_and_malformed_profile_are_preserved(self):
        reports = policy_linter.evaluate_document(
            {"schema_version": 1, "profiles": [valid_profile("demo-1"), None, valid_profile("demo-2")]},
            reference_time=datetime(2026, 9, 24, 12, 0, tzinfo=timezone.utc),
        )
        self.assertEqual(
            [report["profile_id"] for report in reports],
            ["profile-demo-1", None, "profile-demo-2"],
        )
        self.assertEqual(reports[1]["decision"], "DENY")
        self.assertEqual(reports[1]["findings"], [{"code": "PROFILE_SHAPE_INVALID", "path": "profiles[1]"}])

    def test_malformed_document_and_nested_containers_do_not_crash(self):
        reference_time = datetime(2026, 9, 24, 12, 0, tzinfo=timezone.utc)
        invalid_documents = (
            ({"schema_version": True, "profiles": [valid_profile()]}, "DOCUMENT_SHAPE_INVALID"),
            ({"schema_version": 1, "profiles": None}, "PROFILES_INVALID"),
        )
        for document, expected_code in invalid_documents:
            with self.subTest(expected_code=expected_code):
                report = policy_linter.evaluate_document(
                    document, reference_time=reference_time
                )[0]
                self.assertEqual(report["decision"], "DENY")
                self.assertEqual(report["findings"][0]["code"], expected_code)

        for field, invalid_value, expected_code in (
            ("tls", [], "TLS_FIELDS_INVALID"),
            ("authorization", None, "AUTHORIZATION_FIELDS_INVALID"),
        ):
            profile = valid_profile()
            profile[field] = invalid_value
            with self.subTest(field=field):
                report = policy_linter.evaluate_document(
                    {"schema_version": 1, "profiles": [profile]},
                    reference_time=reference_time,
                )[0]
                self.assertIn(expected_code, {f["code"] for f in report["findings"]})

    def test_credential_lifecycle_uses_strict_reference_time_boundaries(self):
        lifecycle_codes = {
            "CREDENTIAL_NOT_YET_VALID",
            "CREDENTIAL_EXPIRED",
            "CREDENTIAL_ROTATION_OVERDUE",
            "CREDENTIAL_VALIDITY_INTERVAL_INVALID",
        }
        cases = (
            ("not_before", "2026-09-24T12:00:00Z", None),
            ("not_before", "2026-09-24T12:00:01Z", "CREDENTIAL_NOT_YET_VALID"),
            ("not_after", "2026-09-24T12:00:00Z", "CREDENTIAL_EXPIRED"),
            ("not_after", "2026-09-23T12:00:00Z", "CREDENTIAL_EXPIRED"),
            ("rotation_due_at", "2026-09-24T12:00:00Z", "CREDENTIAL_ROTATION_OVERDUE"),
        )
        for field, value, expected_code in cases:
            profile = valid_profile()
            profile[field] = value
            with self.subTest(field=field, value=value):
                codes = finding_codes(evaluate_one(profile))
                if expected_code is None:
                    self.assertFalse(codes.intersection(lifecycle_codes))
                else:
                    self.assertIn(expected_code, codes)

    def test_revoked_unknown_state_and_invalid_interval_are_rejected(self):
        cases = (
            ("credential_state", "revoked", "CREDENTIAL_REVOKED"),
            ("credential_state", "pending", "CREDENTIAL_STATE_INVALID"),
            ("not_after", "2026-01-01T00:00:00Z", "CREDENTIAL_VALIDITY_INTERVAL_INVALID"),
        )
        for field, value, expected_code in cases:
            profile = valid_profile()
            profile[field] = value
            if field == "not_after":
                profile["not_before"] = "2026-01-01T00:00:00Z"
            with self.subTest(field=field, value=value):
                self.assertIn(expected_code, finding_codes(evaluate_one(profile)))

    def test_parser_secret_screening_precedes_json_and_schema_errors(self):
        malformed = (
            b'{"schema_version":1,"profiles":[{"private_key":"-----BEGIN RSA PRIVATE KEY----- fake"}',
        )
        for raw in malformed:
            with self.subTest(raw_length=len(raw)), self.assertRaisesRegex(
                ValueError, "^SECRET_LITERAL_REJECTED$"
            ):
                policy_linter.parse_document(raw)

        for key in (
            b'"PASSWORD"',
            b'"access-token"',
            b'"client_secret"',
            b'"API KEY"',
            b'"private key"',
        ):
            raw = b'{"schema_version":1,"profiles":[{' + key + b':"fake"}]}'
            with self.subTest(key=key), self.assertRaisesRegex(
                ValueError, "^SECRET_LITERAL_REJECTED$"
            ):
                policy_linter.parse_document(raw)

    def test_parser_secret_screening_finds_escaped_field_names(self):
        raw = b'{"schema_version":1,"profiles":[{"\\u0070assword":"synthetic-secret-marker"}]}'
        with self.assertRaisesRegex(ValueError, "^SECRET_LITERAL_REJECTED$") as error:
            policy_linter.parse_document(raw)
        self.assertNotIn("synthetic-secret-marker", str(error.exception))

    def test_direct_evaluation_rejects_secret_fields_and_redacts_profile_id(self):
        profile = valid_profile()
        marker = "synthetic-private-key-marker"
        profile["client_secret"] = marker
        report = evaluate_one(profile)
        self.assertEqual(report["decision"], "DENY")
        self.assertIn("SECRET_LITERAL_REJECTED", finding_codes(report))
        self.assertNotIn(marker, json.dumps(report, sort_keys=True))

        profile = valid_profile()
        marker = "-----BEGIN PRIVATE KEY----- synthetic-marker"
        profile["profile_id"] = marker
        report = evaluate_one(profile)
        self.assertIsNone(report["profile_id"])
        self.assertIn("SECRET_LITERAL_REJECTED", finding_codes(report))
        self.assertNotIn(marker, json.dumps(report, sort_keys=True))

    def test_secret_screening_fails_closed_at_depth_and_node_limits(self):
        deep_value = None
        for _ in range(257):
            deep_value = [deep_value]
        profile = valid_profile()
        profile["unexpected"] = deep_value
        self.assertIn("SECRET_LITERAL_REJECTED", finding_codes(evaluate_one(profile)))

        profile = valid_profile()
        profile["unexpected"] = [None] * 50001
        self.assertIn("SECRET_LITERAL_REJECTED", finding_codes(evaluate_one(profile)))

        profile = valid_profile()
        repeated = {"safe": None}
        profile["unexpected"] = [repeated] * 50001
        self.assertIn("SECRET_LITERAL_REJECTED", finding_codes(evaluate_one(profile)))


class CLIBootstrapTests(unittest.TestCase):
    def test_cli_entrypoint_is_available(self):
        self.assertTrue(callable(getattr(policy_linter, "run_cli", None)))


@unittest.skipIf(
    policy_linter is None or not callable(getattr(policy_linter, "run_cli", None)),
    "offline CLI is not implemented yet",
)
class CLITests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        self.profile_file = Path(self.tempdir.name) / "profiles.json"

    def write_profiles(self, profiles):
        document = {"schema_version": 1, "profiles": profiles}
        self.profile_file.write_text(json.dumps(document), encoding="utf-8")
        return self.profile_file

    def invoke_cli(self, argv):
        stdout = io.StringIO()
        stderr = io.StringIO()
        with mock.patch.object(policy_linter, "PROFILE_FILE", self.profile_file):
            status = policy_linter.run_cli(argv, stdout=stdout, stderr=stderr)
        return status, stdout.getvalue(), stderr.getvalue()

    def test_all_pass_profiles_return_zero(self):
        self.write_profiles([valid_profile()])
        status, stdout, stderr = self.invoke_cli(
            ["--now", "2026-09-24T12:00:00Z"]
        )
        self.assertEqual(status, 0)
        self.assertEqual(stderr, "")
        self.assertIn('"decision":"PASS"', stdout)
        self.assertEqual(len(stdout.splitlines()), 1)

    def test_policy_denial_returns_one(self):
        profile = valid_profile()
        profile["tls"]["verify_server"] = False
        self.write_profiles([profile])
        status, stdout, stderr = self.invoke_cli(
            ["--now", "2026-09-24T12:00:00Z"]
        )
        self.assertEqual(status, 1)
        self.assertEqual(stderr, "")
        self.assertIn('"decision":"DENY"', stdout)
        self.assertIn("TLS_SERVER_VERIFY_DISABLED", stdout)

    def test_missing_and_unreadable_files_return_stable_error(self):
        self.profile_file = Path(self.tempdir.name) / "missing.json"
        cases = (self.profile_file, Path(self.tempdir.name))
        for profile_file in cases:
            with self.subTest(profile_file_is_directory=profile_file.is_dir()):
                self.profile_file = profile_file
                status, stdout, stderr = self.invoke_cli(
                    ["--now", "2026-09-24T12:00:00Z"]
                )
                self.assertEqual(status, 2)
                self.assertEqual(stdout, "")
                self.assertEqual(stderr, "INPUT_READ_FAILED\n")

    def test_invalid_time_missing_now_and_path_options_are_rejected(self):
        self.write_profiles([valid_profile()])
        cases = (
            ([], "CLI_ARGUMENTS_INVALID"),
            (["--now", "not-a-time"], "TIMESTAMP_INVALID"),
            (["--now", "2026-09-24T12:00:00Z", "--profile-file", "elsewhere.json"],
             "CLI_ARGUMENTS_INVALID"),
        )
        for argv, expected_code in cases:
            with self.subTest(argv=argv):
                status, stdout, stderr = self.invoke_cli(argv)
                self.assertEqual(status, 2)
                self.assertEqual(stdout, "")
                self.assertEqual(stderr, expected_code + "\n")

    def test_parse_and_secret_errors_are_stable_and_never_echo_input(self):
        samples = (
            (b"{malformed", "JSON_INVALID", ""),
            (
                b'{"schema_version":1,"profiles":[{"private_key":"synthetic-fake-marker"}]}',
                "SECRET_LITERAL_REJECTED",
                "synthetic-fake-marker",
            ),
        )
        for raw, expected_code, marker in samples:
            with self.subTest(expected_code=expected_code):
                self.profile_file.write_bytes(raw)
                status, stdout, stderr = self.invoke_cli(
                    ["--now", "2026-09-24T12:00:00Z"]
                )
                self.assertEqual(status, 2)
                self.assertEqual(stdout, "")
                self.assertEqual(stderr, expected_code + "\n")
                if marker:
                    self.assertNotIn(marker, stdout + stderr)

    def test_jsonl_is_deterministic_and_keeps_profile_order(self):
        profiles = [valid_profile("uno-q-order-a"), valid_profile("uno-q-order-b")]
        self.write_profiles(profiles)
        args = ["--now", "2026-09-24T12:00:00Z"]
        first = self.invoke_cli(args)
        second = self.invoke_cli(args)
        self.assertEqual(first, second)
        reports = [json.loads(line) for line in first[1].splitlines()]
        self.assertEqual(
            [report["profile_id"] for report in reports],
            ["profile-uno-q-order-a", "profile-uno-q-order-b"],
        )

    def test_synthetic_fixture_and_readme_match_cli_contract(self):
        chapter_dir = Path(__file__).resolve().parent
        fixture_path = chapter_dir / "profiles.json"
        readme_path = chapter_dir / "README.md"
        document = policy_linter.parse_document(fixture_path.read_bytes())
        reports = policy_linter.evaluate_document(
            document,
            reference_time=datetime(2026, 9, 24, 12, 0, tzinfo=timezone.utc),
        )
        decisions = {
            report["profile_id"]: report["decision"] for report in reports
        }
        self.assertEqual(sum(value == "PASS" for value in decisions.values()), 1)
        for profile_id in (
            "shared-principal",
            "tls-verification-disabled",
            "wildcard-acl",
            "cross-device-acl",
            "expired-credential",
            "revoked-credential",
        ):
            self.assertEqual(decisions[profile_id], "DENY")
        shared_report = next(
            report for report in reports if report["profile_id"] == "shared-principal"
        )
        self.assertIn("DEVICE_PRINCIPAL_REUSED", finding_codes(shared_report))

        readme = readme_path.read_text(encoding="utf-8")
        self.assertIn(
            'python -B policy_linter.py --now "2026-09-24T12:00:00Z"', readme
        )
        for field in (
            "用途：",
            "运行环境：",
            "文件位置：",
            "依赖：",
            "操作步骤：",
            "预期输出：",
            "故障排查：",
            "验证方式：",
        ):
            self.assertIn(field, readme)
        for limitation in (
            "证书验证",
            "密码学证明",
            "真实 TLS",
            "Broker",
            "生产秘密发现",
            "硬件验证",
        ):
            self.assertIn(limitation, readme)


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
CHAPTER_PATH = (
    REPOSITORY_ROOT
    / "book/第8篇_IoT/第6章_IoT设备身份与安全通信_从连接信任到最小权限.md"
)
FIGURE_PATH = REPOSITORY_ROOT / "diagrams/uno-q-iot-device-identity-secure-communication.mmd"


class ChapterBootstrapTests(unittest.TestCase):
    def test_chapter_and_figure_assets_exist(self):
        self.assertTrue(CHAPTER_PATH.is_file(), "Task 6 chapter has not been created")
        self.assertTrue(FIGURE_PATH.is_file(), "Fig-56 source has not been created")


@unittest.skipUnless(
    CHAPTER_PATH.is_file() and FIGURE_PATH.is_file(),
    "chapter and Fig-56 assets are not implemented yet",
)
class ChapterContractTests(unittest.TestCase):
    def test_chapter_metadata_headings_and_cli_contract(self):
        chapter = CHAPTER_PATH.read_text(encoding="utf-8")
        front_matter = chapter.split("---", 2)[1]
        self.assertIn("title: 第6章 IoT 设备身份与安全通信：从连接信任到最小权限", front_matter)
        self.assertIn("part: 8", front_matter)
        self.assertIn("chapter: 6", front_matter)
        self.assertIn("status: draft", front_matter)
        self.assertIn("last_verified: 2026-09-25", front_matter)
        self.assertIn("# 第6章 IoT 设备身份与安全通信：从连接信任到最小权限", chapter)
        for heading in (
            "## 学习目标",
            "## 背景与边界",
            "## 操作与实验",
            "## 验证结果",
            "## 常见问题",
            "## 延伸阅读",
        ):
            self.assertIn(heading, chapter)

        command_fragment = '--now "2026-09-24T12:00:00Z"'
        self.assertIn(command_fragment, chapter)
        code_readme = (
            REPOSITORY_ROOT
            / "code/第8篇_IoT/第6章_IoT设备身份与安全通信/README.md"
        ).read_text(encoding="utf-8")
        self.assertIn(command_fragment, code_readme)
        self.assertIn("PASS", chapter)
        self.assertIn("DENY", chapter)
        self.assertIn("Fig-56", chapter)

    def test_mermaid_block_is_identical_to_fig56_source_and_has_fail_closed_paths(self):
        chapter = CHAPTER_PATH.read_text(encoding="utf-8")
        diagram = FIGURE_PATH.read_text(encoding="utf-8").strip()
        marker = "```mermaid"
        self.assertEqual(chapter.count(marker), 1)
        body = chapter.split(marker, 1)[1].split("```", 1)[0].strip()
        self.assertEqual(body, diagram)
        self.assertIn("拒绝", diagram)
        self.assertIn("审计", diagram)
        self.assertIn("轮换", diagram)
        self.assertIn("吊销", diagram)
        self.assertIn("明文", diagram)

    def test_local_markdown_links_resolve_to_repository_files(self):
        chapter = CHAPTER_PATH.read_text(encoding="utf-8")
        targets = re.findall(r"!?\[[^\]]*\]\(([^)]+)\)", chapter)
        local_targets = []
        for target in targets:
            path_part = target.split("#", 1)[0]
            if not path_part or path_part.startswith(("http://", "https://", "mailto:")):
                continue
            local_targets.append((target, (CHAPTER_PATH.parent / path_part).resolve()))
        self.assertGreaterEqual(len(local_targets), 5)
        for source, target in local_targets:
            with self.subTest(link=source):
                self.assertTrue(target.is_file(), f"unresolved local link: {source}")

        code_readme_path = (
            REPOSITORY_ROOT
            / "code/第8篇_IoT/第6章_IoT设备身份与安全通信/README.md"
        )
        code_readme = code_readme_path.read_text(encoding="utf-8")
        code_links = re.findall(r"!?\[[^\]]*\]\(([^)]+)\)", code_readme)
        for source in code_links:
            path_part = source.split("#", 1)[0]
            if not path_part or path_part.startswith(("http://", "https://", "mailto:")):
                continue
            target = (code_readme_path.parent / path_part).resolve()
            with self.subTest(code_readme_link=source):
                self.assertTrue(target.is_file(), f"unresolved local link: {source}")

    def test_summary_and_part_readme_register_chapter_six_in_order(self):
        target = (
            "book/第8篇_IoT/第6章_IoT设备身份与安全通信_从连接信任到最小权限.md"
        )
        summary = (REPOSITORY_ROOT / "SUMMARY.md").read_text(encoding="utf-8")
        part_readme = (
            REPOSITORY_ROOT / "book/第8篇_IoT/README.md"
        ).read_text(encoding="utf-8")
        root_readme = (REPOSITORY_ROOT / "README.md").read_text(encoding="utf-8")
        chapter_five = "第5章 IoT 远程命令与受控维护"
        chapter_six = "第6章 IoT 设备身份与安全通信"

        self.assertIn(target, summary)
        summary_five = summary.find(chapter_five)
        summary_six = summary.find(chapter_six)
        part_five = part_readme.find(chapter_five)
        part_six = part_readme.find(chapter_six)
        self.assertGreaterEqual(summary_six, 0)
        self.assertGreaterEqual(part_six, 0)
        if summary_five >= 0 and summary_six >= 0:
            self.assertLess(summary_five, summary_six)
        if part_five >= 0 and part_six >= 0:
            self.assertLess(part_five, part_six)
        self.assertTrue((REPOSITORY_ROOT / target).is_file())
        self.assertIn("第八篇第1～7章已建立为初稿", root_readme)
        self.assertIn("全书当前共 56 章", root_readme)

    def test_chapter_six_sources_are_registered_with_versions_and_boundaries(self):
        references = (REPOSITORY_ROOT / "resources/references.md").read_text(
            encoding="utf-8"
        )
        marker = "## 第八篇第6章补充核验"
        self.assertIn(marker, references)
        section = references.split(marker, 1)[1].split("\n## ", 1)[0]
        for source in (
            "NIST IR 8259 Rev. 1",
            "https://csrc.nist.gov/pubs/ir/8259/r1/final",
            "NISTIR 8259A",
            "https://csrc.nist.gov/pubs/ir/8259/a/final",
            "IoT Device Cybersecurity Requirement Catalogs",
            "https://pages.nist.gov/IoT-Device-Cybersecurity-Requirement-Catalogs/technical/",
            "RFC 9846",
            "https://datatracker.ietf.org/doc/rfc9846/",
            "RFC 9525",
            "https://datatracker.ietf.org/doc/html/rfc9525",
            "OASIS MQTT Version 5.0",
            "https://docs.oasis-open.org/mqtt/mqtt/v5.0/mqtt-v5.0.html",
        ):
            with self.subTest(source=source):
                self.assertIn(source, section)
        for field in ("用途与边界", "版本基线", "版权处理", "2026-09-25"):
            self.assertIn(field, section)
        self.assertIn("仅链接", section)

        table_lines = [
            line.strip()
            for line in section.splitlines()
            if line.strip().startswith("|")
            and not all(
                re.fullmatch(r":?-{3,}:?", cell.strip())
                for cell in line.strip().strip("|").split("|")
            )
        ]
        headers = [cell.strip() for cell in table_lines[0].strip("|").split("|")]
        self.assertEqual(
            headers,
            ["类型", "来源", "地址", "用途与边界", "版本基线", "版权处理", "核验日期"],
        )
        rows = [
            [cell.strip() for cell in line.strip("|").split("|")]
            for line in table_lines[1:]
        ]
        self.assertEqual(len(rows), 6)
        for row in rows:
            with self.subTest(source=row[1] if len(row) > 1 else "missing"):
                self.assertEqual(len(row), len(headers))
                self.assertTrue(all(row))
                self.assertEqual(row[6], "2026-09-25")

    def test_fig56_registry_anchor_and_local_links_resolve(self):
        registry_path = REPOSITORY_ROOT / "images/第8篇_IoT/README.md"
        registry = registry_path.read_text(encoding="utf-8")
        chapter_path = (
            REPOSITORY_ROOT
            / "book/第8篇_IoT/第6章_IoT设备身份与安全通信_从连接信任到最小权限.md"
        )
        chapter = chapter_path.read_text(encoding="utf-8")
        anchor = "fig-56-uno-q-iot-device-identity-secure-communication"
        anchor_line = rf'^<a id="{re.escape(anchor)}"></a>$'
        self.assertEqual(len(re.findall(anchor_line, registry, re.MULTILINE)), 1)
        self.assertEqual(len(re.findall(anchor_line, chapter, re.MULTILINE)), 1)
        self.assertIn("Fig-56", registry)
        self.assertIn("SVG 待生成并完成预览审阅", registry)

        targets = re.findall(r"!?\[[^\]]*\]\(([^)]+)\)", registry)
        chapter_targets = [target for target in targets if anchor in target]
        self.assertTrue(chapter_targets, "Fig-56 chapter backlink is missing")
        for target in chapter_targets:
            path_part, fragment = target.split("#", 1)
            resolved = (registry_path.parent / path_part).resolve()
            self.assertEqual(fragment, anchor)
            self.assertEqual(resolved, chapter_path.resolve())
        self.assertTrue(
            any("uno-q-iot-device-identity-secure-communication.mmd" in target
                for target in targets),
            "Fig-56 Mermaid source link is missing",
        )
        for source in chapter_targets + [
            target for target in targets
            if "uno-q-iot-device-identity-secure-communication.mmd" in target
        ]:
            path_part = source.split("#", 1)[0]
            resolved = (registry_path.parent / path_part).resolve()
            with self.subTest(link=source):
                self.assertTrue(resolved.is_file(), f"unresolved local link: {source}")
