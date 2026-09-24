"""Behavior tests for the local, synthetic IoT health observer."""

import unittest

from health_observer import evaluate_snapshot, load_jsonl


NOW = "2026-09-24T10:00:00Z"
DEVICE = "uno-q-demo-01"


def snapshot(**changes):
    value = {
        "device_id": DEVICE,
        "boot_id": "boot-demo-a",
        "observed_at_utc": "2026-09-24T10:00:00Z",
        "last_publish_at_utc": "2026-09-24T09:59:50Z",
        "queue_depth": 2,
        "queue_capacity": 20,
        "oldest_event_age_seconds": 10,
        "retries_5m": 0,
        "rejected_5m": 0,
    }
    value.update(changes)
    return value


class HealthObserverTests(unittest.TestCase):
    def test_fresh_normal_snapshot_is_healthy(self):
        report = evaluate_snapshot(snapshot(), now_utc=NOW, expected_device_id=DEVICE)

        self.assertEqual(report["health"], "HEALTHY")
        self.assertEqual(report["findings"], [])
        self.assertEqual(report["action"], "CONTINUE_MONITORING")

    def test_queue_pressure_threshold_is_inclusive(self):
        report = evaluate_snapshot(
            snapshot(queue_depth=16), now_utc=NOW, expected_device_id=DEVICE
        )

        self.assertEqual(report["health"], "DEGRADED")
        self.assertIn("QUEUE_PRESSURE", {item["code"] for item in report["findings"]})

    def test_oldest_queued_event_age_has_an_independent_threshold(self):
        at_threshold = evaluate_snapshot(
            snapshot(queue_depth=1, oldest_event_age_seconds=600),
            now_utc=NOW,
            expected_device_id=DEVICE,
        )
        over_threshold = evaluate_snapshot(
            snapshot(queue_depth=1, oldest_event_age_seconds=601),
            now_utc=NOW,
            expected_device_id=DEVICE,
        )

        self.assertEqual(at_threshold["health"], "HEALTHY")
        self.assertEqual(over_threshold["health"], "DEGRADED")
        self.assertIn(
            "OLDEST_EVENT_DELAYED",
            {item["code"] for item in over_threshold["findings"]},
        )

    def test_retry_threshold_is_inclusive_without_rejected_events(self):
        report = evaluate_snapshot(
            snapshot(retries_5m=3),
            now_utc=NOW,
            expected_device_id=DEVICE,
        )

        codes = {item["code"] for item in report["findings"]}
        self.assertEqual(report["health"], "DEGRADED")
        self.assertEqual(report["action"], "INVESTIGATE_AND_PRESERVE_QUEUE")
        self.assertIn("RETRIES_ELEVATED", codes)
        self.assertNotIn("EVENTS_REJECTED", codes)

    def test_rejected_events_are_reported_without_retries(self):
        report = evaluate_snapshot(
            snapshot(rejected_5m=1),
            now_utc=NOW,
            expected_device_id=DEVICE,
        )

        codes = {item["code"] for item in report["findings"]}
        self.assertEqual(report["health"], "DEGRADED")
        self.assertIn("EVENTS_REJECTED", codes)
        self.assertNotIn("RETRIES_ELEVATED", codes)

    def test_publish_freshness_is_separate_from_snapshot_freshness(self):
        report = evaluate_snapshot(
            snapshot(last_publish_at_utc="2026-09-24T09:54:59Z"),
            now_utc=NOW,
            expected_device_id=DEVICE,
        )

        self.assertEqual(report["health"], "DEGRADED")
        self.assertIn("PUBLISH_STALE", {item["code"] for item in report["findings"]})

    def test_old_snapshot_is_stale_and_metrics_are_not_evaluated(self):
        report = evaluate_snapshot(
            snapshot(
                observed_at_utc="2026-09-24T09:58:29Z",
                last_publish_at_utc="2026-09-24T09:58:00Z",
                queue_depth=20,
            ),
            now_utc=NOW,
            expected_device_id=DEVICE,
        )

        self.assertEqual(report["health"], "STALE")
        self.assertEqual([item["code"] for item in report["findings"]], ["SNAPSHOT_STALE"])

    def test_future_snapshot_is_unknown(self):
        report = evaluate_snapshot(
            snapshot(observed_at_utc="2026-09-24T10:00:01Z"),
            now_utc=NOW,
            expected_device_id=DEVICE,
        )

        self.assertEqual(report["health"], "UNKNOWN")
        self.assertEqual(report["findings"][0]["code"], "FUTURE_SNAPSHOT")

    def test_identity_mismatch_is_unknown(self):
        report = evaluate_snapshot(
            snapshot(device_id="another-device"),
            now_utc=NOW,
            expected_device_id=DEVICE,
        )

        self.assertEqual(report["health"], "UNKNOWN")
        self.assertEqual(report["findings"][0]["code"], "IDENTITY_MISMATCH")

    def test_queue_depth_above_capacity_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "queue_depth"):
            evaluate_snapshot(
                snapshot(queue_depth=21), now_utc=NOW, expected_device_id=DEVICE
            )

    def test_boolean_is_not_accepted_as_an_integer_signal(self):
        with self.assertRaisesRegex(ValueError, "retries_5m"):
            evaluate_snapshot(
                snapshot(retries_5m=True), now_utc=NOW, expected_device_id=DEVICE
            )

    def test_empty_queue_cannot_claim_an_oldest_event(self):
        with self.assertRaisesRegex(ValueError, "oldest_event_age_seconds"):
            evaluate_snapshot(
                snapshot(queue_depth=0, oldest_event_age_seconds=1),
                now_utc=NOW,
                expected_device_id=DEVICE,
            )

    def test_duplicate_json_keys_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
            load_jsonl('{"device_id":"a","device_id":"b"}\n')

    def test_jsonl_row_count_is_bounded(self):
        with self.assertRaisesRegex(ValueError, "maximum row count"):
            load_jsonl("{}\n" * 101)


if __name__ == "__main__":
    unittest.main()
