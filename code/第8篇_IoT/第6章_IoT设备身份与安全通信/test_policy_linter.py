import json
import unittest

try:
    import policy_linter
except ModuleNotFoundError as error:
    if error.name != "policy_linter":
        raise
    policy_linter = None


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
        with self.assertRaisesRegex(ValueError, "DUPLICATE_JSON_KEY"):
            policy_linter.parse_document(
                b'{"schema_version":1,"profiles":[],"profiles":[]}'
            )

    def test_nonfinite_and_invalid_utf8_are_rejected(self):
        for raw in (b'{"schema_version":1,"profiles":[],"x":NaN}', bytes((255,))):
            with self.subTest(raw=raw), self.assertRaises(ValueError):
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
