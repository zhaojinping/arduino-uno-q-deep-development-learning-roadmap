import json
import sys
import unittest
from datetime import datetime, timezone
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
