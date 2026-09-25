"""Run the fixed local test suites for IoT Chapters 1 through 6."""

import json
import re
import subprocess
import sys
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
TIMEOUT_SECONDS = 120
TEST_COUNT_PATTERN = re.compile(r"Ran\s+(\d+)\s+tests?\s+in\s+")

CHAPTER_SUITES = (
    ("第1章", Path("code/第8篇_IoT/第1章_IoT开发基础")),
    ("第2章", Path("code/第8篇_IoT/第2章_MQTT消息上报与幂等消费")),
    ("第3章", Path("code/第8篇_IoT/第3章_离线缓存与补传")),
    ("第4章", Path("code/第8篇_IoT/第4章_IoT可观测性与告警")),
    ("第5章", Path("code/第8篇_IoT/第5章_IoT远程命令与受控维护")),
    ("第6章", Path("code/第8篇_IoT/第6章_IoT设备身份与安全通信")),
)


def _test_count(output: str) -> int | None:
    match = TEST_COUNT_PATTERN.search(output)
    if match is None:
        return None
    return int(match.group(1))


def summarize_results(results: list[dict[str, object]]) -> dict[str, object]:
    """Summarize six fixed suite outcomes without inferring target readiness."""
    expected_chapters = [chapter for chapter, _ in CHAPTER_SUITES]
    chapters = [dict(item) for item in results if isinstance(item, dict)]
    received_names = [item.get("chapter") for item in chapters]
    complete = (
        len(results) == len(expected_chapters)
        and len(chapters) == len(expected_chapters)
        and received_names == expected_chapters
    )
    all_passed = complete and all(
        item.get("status") == "LOCAL_PASS"
        and type(item.get("returncode")) is int
        and item.get("returncode") == 0
        and type(item.get("tests_run")) is int
        and item.get("tests_run") > 0
        for item in chapters
    )

    if all_passed:
        decision = "LOCAL_TESTS_PASS"
    elif any(item.get("status") != "LOCAL_PASS" for item in chapters):
        decision = "LOCAL_TESTS_FAIL"
    else:
        decision = "LOCAL_TESTS_INCOMPLETE"

    return {
        "schema_version": 1,
        "scope": "LOCAL_TESTS_ONLY",
        "decision": decision,
        "target_validation": "NOT_RUN",
        "deployment_authorized": False,
        "chapters": chapters,
    }


def _run_suite(chapter: str, directory: Path) -> dict[str, object]:
    test_directory = REPOSITORY_ROOT / directory
    if not test_directory.is_dir() or not any(test_directory.glob("test_*.py")):
        return {
            "chapter": chapter,
            "status": "LOCAL_NO_TESTS",
            "returncode": None,
            "tests_run": 0,
        }

    command = [
        sys.executable,
        "-B",
        "-m",
        "unittest",
        "discover",
        "-s",
        str(directory),
        "-p",
        "test_*.py",
    ]
    try:
        completed = subprocess.run(
            command,
            cwd=REPOSITORY_ROOT,
            shell=False,
            capture_output=True,
            text=True,
            timeout=TIMEOUT_SECONDS,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return {
            "chapter": chapter,
            "status": "LOCAL_TIMEOUT",
            "returncode": None,
            "tests_run": 0,
        }
    except OSError:
        return {
            "chapter": chapter,
            "status": "LOCAL_EXECUTION_ERROR",
            "returncode": None,
            "tests_run": 0,
        }

    tests_run = _test_count(completed.stdout + "\n" + completed.stderr)
    if completed.returncode != 0:
        status = "LOCAL_FAIL"
    elif tests_run is None or tests_run == 0:
        status = "LOCAL_NO_TESTS"
    else:
        status = "LOCAL_PASS"

    return {
        "chapter": chapter,
        "status": status,
        "returncode": completed.returncode,
        "tests_run": tests_run or 0,
    }


def run_all_suites() -> dict[str, object]:
    """Run the six repository-owned suites in a deterministic order."""
    results = [_run_suite(chapter, directory) for chapter, directory in CHAPTER_SUITES]
    return summarize_results(results)


def main() -> int:
    if len(sys.argv) != 1:
        sys.stderr.write("usage: python -B aggregate_local_tests.py\n")
        return 2

    report = run_all_suites()
    sys.stdout.write(
        json.dumps(report, ensure_ascii=False, separators=(",", ":")) + "\n"
    )
    return 0 if report["decision"] == "LOCAL_TESTS_PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
