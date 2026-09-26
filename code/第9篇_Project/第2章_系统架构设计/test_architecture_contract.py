"""Offline structural contract for Part 9, Chapter 2."""
from __future__ import annotations

import ast
import inspect
import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CHAPTER_REL = Path(
    "book/第9篇_Project/第2章_系统架构设计_从处理器边界到可验证数据流.md"
)
CHAPTER = ROOT / CHAPTER_REL
FIGURE_SOURCE = ROOT / "diagrams/uno-q-lab-environment-architecture.mmd"
FIGURE_ANCHOR = "fig-61-uno-q-lab-environment-architecture"
CHAPTER_FILENAME = CHAPTER_REL.name
MANUAL_URL = "https://docs.arduino.cc/tutorials/uno-q/user-manual/"
DATASHEET_URL = "https://docs.arduino.cc/resources/datasheets/ABX00162-datasheet.pdf"


def _cells(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def _table_with_columns(text: str, required: set[str]) -> tuple[list[str], list[list[str]]]:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if not line.strip().startswith("|"):
            continue
        header = _cells(line)
        if not required.issubset(header):
            continue

        rows: list[list[str]] = []
        for candidate in lines[index + 1 :]:
            if not candidate.strip().startswith("|"):
                break
            cells = _cells(candidate)
            if cells and all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells):
                continue
            rows.append(cells)
        return header, rows
    return [], []


class ChapterContractTests(unittest.TestCase):
    def _read_required(self, path: Path) -> str:
        self.assertTrue(path.is_file(), f"required artifact is missing: {path.relative_to(ROOT)}")
        return path.read_text(encoding="utf-8")

    def test_metadata_and_required_sections_match_part_nine(self) -> None:
        text = self._read_required(CHAPTER)
        match = re.match(r"\A---\r?\n(.*?)\r?\n---\r?\n", text, re.S)
        self.assertIsNotNone(match, "chapter must start with YAML front matter")
        metadata = {
            key.strip(): value.strip().strip("\"'")
            for line in match.group(1).splitlines()
            if ":" in line
            for key, value in [line.split(":", 1)]
        }
        self.assertEqual(metadata.get("part"), "9")
        self.assertEqual(metadata.get("chapter"), "2")
        self.assertEqual(metadata.get("status"), "draft")
        self.assertRegex(metadata.get("last_verified", ""), r"^\d{4}-\d{2}-\d{2}$")
        self.assertEqual(
            metadata.get("title"), "系统架构设计：从处理器边界到可验证数据流"
        )
        self.assertIn(f"# 第2章 {metadata['title']}", text)

        ordered_headings = [
            "## 学习目标",
            "## 1. 架构目标与项目约束",
            "## 2. 候选方案比较",
            "## 3. 分层组件与数据流",
            "## 4. 版本化测量与告警契约",
            "## 5. 失效、恢复与安全边界",
            "## 6. 本章实验",
            "## 7. 验证结果与当前证据",
            "## 8. 常见问题",
            "## 9. 延伸阅读与交接下一章",
        ]
        positions = [text.index(heading) for heading in ordered_headings]
        self.assertEqual(positions, sorted(positions), "required sections are out of order")

    def test_architecture_and_open_decisions_are_explicit(self) -> None:
        text = self._read_required(CHAPTER)
        for phrase in (
            "STM32U585",
            "Linux",
            "Bridge/RPC",
            "分层混合",
            "MCU 单体",
            "Linux 直连",
            "传感器型号",
            "采样周期",
            "规则阈值",
            "存储介质",
            "缓存容量",
            "未决",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_data_contract_and_failure_matrix_preserve_unknown_states(self) -> None:
        text = self._read_required(CHAPTER)
        for field in (
            "schema_version",
            "device_id",
            "source_id",
            "event_id",
            "event_time",
            "received_at",
            "unit",
            "quality",
            "quality_reason",
            "provenance",
        ):
            with self.subTest(field=field):
                self.assertIn(f"`{field}`", text)

        json_examples = re.findall(r"```json\s*\n(.*?)\n```", text, re.S)
        self.assertEqual(len(json_examples), 1, "chapter must have one explicit JSON teaching example")
        synthetic_record = json.loads(json_examples[0])
        self.assertEqual(synthetic_record["provenance"], "SYNTHETIC")
        self.assertEqual(synthetic_record["schema_version"], 1)
        python_examples = re.findall(r"```python\s*\n(.*?)\n```", text, re.S)
        self.assertEqual(len(python_examples), 1, "chapter must have one Python logic example")
        ast.parse(python_examples[0])

        required_columns = {"失效条件", "系统处理与可观察状态", "禁止的错误表现"}
        header, rows = _table_with_columns(text, required_columns)
        self.assertTrue(header, "chapter must include a structured failure matrix")
        positions = {name: header.index(name) for name in required_columns}
        conditions = [row[positions["失效条件"]] for row in rows]
        actions = [row[positions["系统处理与可观察状态"]] for row in rows]
        matrix = "\n".join(" | ".join(row) for row in rows)

        for condition in (
            "重复",
            "乱序",
            "Bridge",
            "Linux",
            "时钟",
            "存储",
            "规则",
        ):
            with self.subTest(condition=condition):
                self.assertTrue(any(condition in row for row in conditions), condition)

        critical_conditions = ("Bridge", "Linux", "时钟", "存储", "规则")
        for condition in critical_conditions:
            row_index = next(i for i, row in enumerate(conditions) if condition in row)
            with self.subTest(degraded_condition=condition):
                self.assertRegex(actions[row_index], r"UNKNOWN|未知|等待|退化|未配置")

        self.assertRegex(matrix, r"重复.*(?:去重|不更新|不覆盖|不作为新测量)")
        self.assertRegex(matrix, r"乱序.*(?:不更新|不覆盖|迟到|排序)")

    def test_security_and_evidence_boundaries_stay_closed(self) -> None:
        text = self._read_required(CHAPTER)
        self.assertIn("SYNTHETIC", text)
        self.assertIn("默认关闭", text)
        self.assertRegex(text, r"(?:不连接|不控制|排除).{0,30}执行器|执行器.{0,30}(?:不连接|不控制|排除|无路径)")

        required_columns = {"验证项", "状态", "证据与限制"}
        header, rows = _table_with_columns(text, required_columns)
        self.assertTrue(header, "chapter must include a current-evidence table")
        positions = {name: header.index(name) for name in required_columns}
        board_rows = [
            row for row in rows if "UNO Q" in row[positions["验证项"]] and "实机" in row[positions["验证项"]]
        ]
        self.assertTrue(board_rows, "board validation state must be explicit")
        self.assertEqual(board_rows[0][positions["状态"]].strip("`"), "NOT_RUN")
        self.assertNotIn("TARGET_OBSERVED", board_rows[0][positions["证据与限制"]])

    def test_state_gate_refuses_normal_without_clock_and_persistence_health(self) -> None:
        text = self._read_required(CHAPTER)
        python_examples = re.findall(r"```python\s*\n(.*?)\n```", text, re.S)
        self.assertEqual(len(python_examples), 1)
        namespace: dict[str, object] = {}
        exec(compile(python_examples[0], str(CHAPTER), "exec"), namespace)
        classify = namespace["classify_measurement"]
        parameters = set(inspect.signature(classify).parameters)
        self.assertTrue(
            {"source_clock_trusted", "host_clock_trusted", "record_persisted"}.issubset(parameters)
        )

        record = {"source_id": "synthetic-source", "event_id": "synthetic-event", "quality": "valid"}
        healthy = {
            "fresh": True,
            "rule_approved": True,
            "rule_result": False,
            "source_clock_trusted": True,
            "host_clock_trusted": True,
            "record_persisted": True,
        }
        cases = (
            ("all gates healthy", {}, ("NORMAL", "APPROVED_RULE_NO_MATCH")),
            ("source clock untrusted", {"source_clock_trusted": False}, ("UNKNOWN", "SOURCE_CLOCK_UNTRUSTED")),
            ("host clock untrusted", {"host_clock_trusted": False}, ("UNKNOWN", "HOST_CLOCK_UNTRUSTED")),
            ("record not persisted", {"record_persisted": False}, ("UNKNOWN", "PERSISTENCE_UNCONFIRMED")),
        )
        for label, overrides, expected in cases:
            inputs = {**healthy, **overrides}
            with self.subTest(case=label):
                self.assertEqual(classify(record, **inputs), expected)

    def test_fig61_inline_mermaid_matches_independent_source(self) -> None:
        text = self._read_required(CHAPTER)
        source = self._read_required(FIGURE_SOURCE)
        blocks = re.findall(r"```mermaid\s*\n(.*?)\n```", text, re.S)
        self.assertEqual(len(blocks), 1, "chapter must contain exactly one Mermaid block")
        self.assertIn(f'id="{FIGURE_ANCHOR}"', text)
        self.assertIn("Fig-61", text)
        self.assertEqual(blocks[0].strip(), source.strip())

    def test_summary_part_readmes_and_root_count_link_chapter_once(self) -> None:
        summary = self._read_required(ROOT / "SUMMARY.md")
        part_readme = self._read_required(ROOT / "book/第9篇_Project/README.md")
        code_index = self._read_required(ROOT / "code/README.md")
        code_part = self._read_required(ROOT / "code/第9篇_Project/README.md")
        root_readme = self._read_required(ROOT / "README.md")

        self.assertEqual(summary.count(CHAPTER_REL.as_posix()), 1)
        self.assertEqual(part_readme.count(CHAPTER_FILENAME), 1)
        self.assertEqual(code_index.count("第9篇_Project/README.md"), 1)
        self.assertEqual(code_part.count("第2章_系统架构设计/README.md"), 1)
        self.assertTrue(CHAPTER.is_file())
        self.assertTrue((ROOT / "code/第9篇_Project/第2章_系统架构设计/README.md").is_file())

        chapter_links = re.findall(
            r"(?m)^- \[第\s*\d+章[^\]]*\]\(book/[^)]+\.md\)$", summary
        )
        count_match = re.search(r"全书当前共\s+(\d+)\s+章", root_readme)
        self.assertIsNotNone(count_match, "root README must publish the actual chapter count")
        self.assertEqual(int(count_match.group(1)), len(chapter_links))

    def test_fig61_has_one_global_registration_and_backlinks(self) -> None:
        image_readmes = list((ROOT / "images").rglob("README.md"))
        registrations = [
            line.strip()
            for path in image_readmes
            for line in path.read_text(encoding="utf-8").splitlines()
            if re.fullmatch(r"- 图号：\s*Fig-61", line.strip())
        ]
        self.assertEqual(registrations, ["- 图号：Fig-61"])

        index_path = ROOT / "images/第9篇_Project/README.md"
        index = self._read_required(index_path)
        self.assertIn(FIGURE_ANCHOR, index)
        self.assertIn(CHAPTER_FILENAME, index)
        self.assertIn("uno-q-lab-environment-architecture.mmd", index)
        self.assertIn("本书原创", index)
        self.assertIn("尚未生成 SVG", index)
        for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", index):
            if target.startswith(("https://", "http://", "mailto:")):
                continue
            local_path = target.split("#", 1)[0]
            if local_path:
                resolved = (index_path.parent / local_path).resolve()
                with self.subTest(figure_index_link=target):
                    self.assertTrue(resolved.is_file(), f"broken image-index link: {target}")

    def test_official_sources_are_registered_and_local_links_resolve(self) -> None:
        chapter = self._read_required(CHAPTER)
        references = self._read_required(ROOT / "resources/references.md")
        self.assertIn(MANUAL_URL, chapter)
        self.assertIn(DATASHEET_URL, chapter)
        self.assertIn(MANUAL_URL, references)
        manual_rows = [line for line in references.splitlines() if MANUAL_URL in line]
        self.assertEqual(len(manual_rows), 1, "reuse the existing manual source entry")
        self.assertIn(DATASHEET_URL, references)

        markdown_links = re.findall(r"(?<!!)\[[^\]]+\]\(([^)]+)\)", chapter)
        for target in markdown_links:
            destination = target.split()[0].strip("<>")
            if destination.startswith(("https://", "http://", "mailto:")):
                continue
            local_path = destination.split("#", 1)[0]
            if not local_path:
                continue
            resolved = (CHAPTER.parent / local_path).resolve()
            with self.subTest(link=destination):
                self.assertTrue(resolved.is_file(), f"broken chapter link: {destination}")


if __name__ == "__main__":
    unittest.main()
