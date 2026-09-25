import json
import re
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

try:
    import aggregate_local_tests
except ModuleNotFoundError as error:
    if error.name != "aggregate_local_tests":
        raise
    aggregate_local_tests = None


SCRIPT = Path(__file__).with_name("aggregate_local_tests.py")
REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
EXPECTED_CHAPTERS = ["第1章", "第2章", "第3章", "第4章", "第5章", "第6章"]
CHAPTER_PATH = (
    "book/第8篇_IoT/第7章_IoT综合验证_从分章测试到系统级证据.md"
)
FIG57_ANCHOR = "fig-57-uno-q-iot-integration-validation"


def passing_results():
    return [
        {"chapter": "第1章", "status": "LOCAL_PASS", "returncode": 0, "tests_run": 1},
        {"chapter": "第2章", "status": "LOCAL_PASS", "returncode": 0, "tests_run": 1},
        {"chapter": "第3章", "status": "LOCAL_PASS", "returncode": 0, "tests_run": 1},
        {"chapter": "第4章", "status": "LOCAL_PASS", "returncode": 0, "tests_run": 1},
        {"chapter": "第5章", "status": "LOCAL_PASS", "returncode": 0, "tests_run": 1},
        {"chapter": "第6章", "status": "LOCAL_PASS", "returncode": 0, "tests_run": 1},
    ]


class RunnerBootstrapTests(unittest.TestCase):
    def test_aggregator_module_is_available(self):
        self.assertIsNotNone(aggregate_local_tests, "aggregate_local_tests.py is missing")


@unittest.skipIf(aggregate_local_tests is None, "aggregator implementation is not available yet")
class SummaryTests(unittest.TestCase):
    def test_six_local_passes_do_not_claim_target_acceptance(self):
        report = aggregate_local_tests.summarize_results(passing_results())

        self.assertEqual(report["decision"], "LOCAL_TESTS_PASS")
        self.assertEqual(report["scope"], "LOCAL_TESTS_ONLY")
        self.assertEqual(report["target_validation"], "NOT_RUN")
        self.assertIs(report["deployment_authorized"], False)
        self.assertEqual(
            [item["chapter"] for item in report["chapters"]], EXPECTED_CHAPTERS
        )

    def test_any_nonzero_chapter_result_blocks_local_pass(self):
        results = passing_results()
        results[2] = {
            "chapter": "第3章",
            "status": "LOCAL_FAIL",
            "returncode": 1,
            "tests_run": 4,
        }

        report = aggregate_local_tests.summarize_results(results)

        self.assertEqual(report["decision"], "LOCAL_TESTS_FAIL")
        self.assertIs(report["deployment_authorized"], False)

    def test_missing_or_reordered_chapter_is_incomplete(self):
        results = passing_results()
        results.pop(4)

        report = aggregate_local_tests.summarize_results(results)

        self.assertEqual(report["decision"], "LOCAL_TESTS_INCOMPLETE")
        self.assertIs(report["deployment_authorized"], False)

    def test_extra_malformed_record_cannot_be_ignored_as_a_full_pass(self):
        results = passing_results()
        results.append(None)

        report = aggregate_local_tests.summarize_results(results)

        self.assertEqual(report["decision"], "LOCAL_TESTS_INCOMPLETE")
        self.assertIs(report["deployment_authorized"], False)

    def test_timeout_is_recorded_for_each_fixed_suite_and_never_passes(self):
        timeout = subprocess.TimeoutExpired(cmd="python -m unittest", timeout=120)
        with patch(
            "aggregate_local_tests.subprocess.run", side_effect=timeout
        ) as run:
            report = aggregate_local_tests.run_all_suites()

        self.assertEqual(report["decision"], "LOCAL_TESTS_FAIL")
        self.assertEqual(len(report["chapters"]), 6)
        self.assertTrue(
            all(item["status"] == "LOCAL_TIMEOUT" for item in report["chapters"])
        )
        self.assertEqual(run.call_count, 6)
        for call in run.call_args_list:
            command = call.args[0]
            self.assertEqual(command[0], sys.executable)
            self.assertEqual(command[1:5], ["-B", "-m", "unittest", "discover"])
            self.assertIn("test_*.py", command)
            self.assertIs(call.kwargs["shell"], False)
            self.assertEqual(Path(call.kwargs["cwd"]), REPOSITORY_ROOT)

    def test_process_start_error_becomes_a_nonpassing_local_result(self):
        with patch(
            "aggregate_local_tests.subprocess.run",
            side_effect=OSError("simulated executable unavailable"),
        ):
            try:
                report = aggregate_local_tests.run_all_suites()
            except OSError as error:
                self.fail(f"runner leaked process-start error: {error}")

        self.assertEqual(report["decision"], "LOCAL_TESTS_FAIL")
        self.assertTrue(
            all(
                item["status"] == "LOCAL_EXECUTION_ERROR"
                for item in report["chapters"]
            )
        )


@unittest.skipIf(aggregate_local_tests is None, "aggregator implementation is not available yet")
class CLITests(unittest.TestCase):
    def test_cli_rejects_extra_arguments_instead_of_accepting_paths(self):
        completed = subprocess.run(
            [sys.executable, "-B", str(SCRIPT), "--directory", "C:/outside"],
            cwd=REPOSITORY_ROOT,
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )

        self.assertEqual(completed.returncode, 2)
        self.assertEqual(completed.stdout, "")
        self.assertIn("usage:", completed.stderr)

    def test_cli_runs_exactly_six_fixed_suites_and_reports_local_scope(self):
        completed = subprocess.run(
            [sys.executable, "-B", str(SCRIPT)],
            cwd=REPOSITORY_ROOT,
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        report = json.loads(completed.stdout)
        self.assertEqual(report["decision"], "LOCAL_TESTS_PASS")
        self.assertEqual(report["scope"], "LOCAL_TESTS_ONLY")
        self.assertEqual(report["target_validation"], "NOT_RUN")
        self.assertIs(report["deployment_authorized"], False)
        self.assertEqual(
            [item["chapter"] for item in report["chapters"]], EXPECTED_CHAPTERS
        )
        self.assertTrue(
            all(item["status"] == "LOCAL_PASS" for item in report["chapters"])
        )
        self.assertTrue(all(item["tests_run"] > 0 for item in report["chapters"]))


class ChapterBootstrapTests(unittest.TestCase):
    def test_chapter_and_diagram_assets_exist(self):
        self.assertTrue((REPOSITORY_ROOT / CHAPTER_PATH).is_file())
        self.assertTrue(
            (REPOSITORY_ROOT / "diagrams/uno-q-iot-integration-validation.mmd").is_file()
        )


@unittest.skipUnless(
    (REPOSITORY_ROOT / CHAPTER_PATH).is_file(), "chapter documentation is not available yet"
)
class ChapterContractTests(unittest.TestCase):
    def test_chapter_has_expected_metadata_and_publication_sections(self):
        chapter_path = REPOSITORY_ROOT / CHAPTER_PATH
        chapter = chapter_path.read_text(encoding="utf-8")
        front_matter = chapter.split("---", 2)[1]

        self.assertIn("title: IoT 综合验证：从分章测试到系统级证据", front_matter)
        self.assertIn("part: 8", front_matter)
        self.assertIn("chapter: 7", front_matter)
        self.assertIn("status: draft", front_matter)
        self.assertIn("# 第7章 IoT 综合验证：从分章测试到系统级证据", chapter)
        for heading in (
            "## 学习目标",
            "## 背景与边界",
            "## 端到端证据矩阵",
            "## 操作与实验",
            "## 目标环境验证与证据交接",
            "## 验证结果与范围",
            "## 常见问题",
            "## 本章小结",
            "## 延伸阅读",
        ):
            with self.subTest(heading=heading):
                self.assertIn(heading, chapter)

    def test_summary_part_readme_and_root_readme_register_chapter_seven(self):
        summary = (REPOSITORY_ROOT / "SUMMARY.md").read_text(encoding="utf-8")
        part_readme = (
            REPOSITORY_ROOT / "book/第8篇_IoT/README.md"
        ).read_text(encoding="utf-8")
        root_readme = (REPOSITORY_ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn(CHAPTER_PATH, summary)
        self.assertIn("第7章 IoT 综合验证", part_readme)
        self.assertIn("第八篇第1～7章", root_readme)
        self.assertIn("全书当前共 56 章", root_readme)

    def test_fig57_anchor_is_unique_and_mermaid_source_matches(self):
        chapter_path = REPOSITORY_ROOT / CHAPTER_PATH
        registry_path = REPOSITORY_ROOT / "images/第8篇_IoT/README.md"
        source_path = REPOSITORY_ROOT / "diagrams/uno-q-iot-integration-validation.mmd"
        chapter = chapter_path.read_text(encoding="utf-8")
        registry = registry_path.read_text(encoding="utf-8")
        anchor_line = rf'^<a id="{re.escape(FIG57_ANCHOR)}"></a>$'

        self.assertEqual(len(re.findall(anchor_line, chapter, re.MULTILINE)), 1)
        self.assertEqual(len(re.findall(anchor_line, registry, re.MULTILINE)), 1)
        figure_section = chapter.split(f'<a id="{FIG57_ANCHOR}"></a>', 1)[1]
        match = re.search(r"```mermaid\r?\n(.*?)\r?\n```", figure_section, re.DOTALL)
        self.assertIsNotNone(match)
        self.assertEqual(match.group(1).strip(), source_path.read_text(encoding="utf-8").strip())
        self.assertIn("Fig-57", registry)

    def test_chapter_registered_local_links_resolve(self):
        chapter_path = REPOSITORY_ROOT / CHAPTER_PATH
        registry_path = REPOSITORY_ROOT / "images/第8篇_IoT/README.md"
        sources = [chapter_path, registry_path]
        for source_path in sources:
            text = source_path.read_text(encoding="utf-8")
            for target in re.findall(r"!?\[[^\]]*\]\(([^)]+)\)", text):
                if target.startswith(("http://", "https://", "mailto:")):
                    continue
                target_path = target.split("#", 1)[0]
                if not target_path:
                    resolved = source_path
                else:
                    resolved = (source_path.parent / target_path).resolve()
                with self.subTest(source=source_path.name, target=target):
                    self.assertTrue(resolved.is_file(), f"unresolved local link: {target}")
        registry = registry_path.read_text(encoding="utf-8")
        self.assertIn(f"{CHAPTER_PATH}#{FIG57_ANCHOR}", registry.replace("../", ""))

    def test_unittest_official_reference_is_registered_with_use_and_limit(self):
        references = (REPOSITORY_ROOT / "resources/references.md").read_text(
            encoding="utf-8"
        )
        marker = "## 第八篇第7章补充核验"
        self.assertIn(marker, references)
        section = references.split(marker, 1)[1].split("\n## ", 1)[0]
        self.assertIn("Python `unittest`", section)
        self.assertIn("https://docs.python.org/3.14/library/unittest.html", section)
        self.assertIn("用途与边界", section)
        self.assertIn("版本基线", section)
        self.assertIn("Python 3.14.7", section)
        self.assertIn("2026-09-25", section)


if __name__ == "__main__":
    unittest.main()
