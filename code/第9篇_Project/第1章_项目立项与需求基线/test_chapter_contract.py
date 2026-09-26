"""Offline structural contract for Part 9, Chapter 1."""
from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CHAPTER_REL = Path(
    "book/第9篇_Project/第1章_项目立项与需求基线_从场景到可验收目标.md"
)
CHAPTER = ROOT / CHAPTER_REL
FIGURE_SOURCE = ROOT / "diagrams/uno-q-lab-environment-project-baseline.mmd"
FIGURE_ANCHOR = "fig-60-uno-q-lab-environment-project-baseline"
SUMMARY_LINK = CHAPTER_REL.as_posix()


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

    def test_chapter_metadata_and_order_match_part_nine(self) -> None:
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
        self.assertEqual(metadata.get("chapter"), "1")
        self.assertEqual(metadata.get("status"), "draft")
        self.assertRegex(metadata.get("last_verified", ""), r"^\d{4}-\d{2}-\d{2}$")
        self.assertEqual(metadata.get("title"), "项目立项与需求基线：从场景到可验收目标")
        self.assertIn(f"# 第1章 {metadata['title']}", text)

    def test_requirements_have_unique_ids_and_verifiable_acceptance_fields(self) -> None:
        text = self._read_required(CHAPTER)
        required = {"需求 ID", "类型", "需求描述", "验收条件", "验证方法", "证据级别"}
        header, rows = _table_with_columns(text, required)
        self.assertTrue(header, "chapter must provide the agreed requirements matrix")
        self.assertGreaterEqual(len(rows), 8, "matrix must cover functional and non-functional requirements")

        positions = {name: header.index(name) for name in required}
        ids: list[str] = []
        for row in rows:
            self.assertEqual(len(row), len(header), f"malformed requirement row: {row}")
            item = {name: row[position] for name, position in positions.items()}
            self.assertTrue(item["需求描述"])
            self.assertTrue(item["验收条件"])
            self.assertTrue(item["验证方法"])
            self.assertTrue(item["证据级别"])
            self.assertRegex(item["需求 ID"], r"^LEM-(?:FR|NFR)-\d{3}$")
            expected_prefix = "LEM-FR-" if item["类型"] == "功能" else "LEM-NFR-"
            self.assertTrue(item["需求 ID"].startswith(expected_prefix))
            ids.append(item["需求 ID"])

        self.assertEqual(len(ids), len(set(ids)), "requirement IDs must be stable and unique")
        self.assertIn("功能", {row[positions["类型"]] for row in rows})
        self.assertIn("非功能", {row[positions["类型"]] for row in rows})

    def test_scope_table_keeps_unconfirmed_hardware_and_actuators_out_of_assumptions(self) -> None:
        text = self._read_required(CHAPTER)
        required = {"范围类别", "事项", "当前决定"}
        header, rows = _table_with_columns(text, required)
        self.assertTrue(header, "chapter must state explicit in-scope, out-of-scope, and undecided items")
        positions = {name: header.index(name) for name in required}
        categories = {row[positions["范围类别"]] for row in rows}
        self.assertTrue({"范围内", "范围外", "未决"}.issubset(categories))
        undecided = " ".join(row[positions["事项"]] for row in rows if row[positions["范围类别"]] == "未决")
        excluded = " ".join(row[positions["事项"]] for row in rows if row[positions["范围类别"]] == "范围外")
        self.assertIn("传感器", undecided)
        self.assertIn("执行器", excluded)

    def test_fig60_inline_mermaid_matches_traceable_source(self) -> None:
        text = self._read_required(CHAPTER)
        source = self._read_required(FIGURE_SOURCE)
        blocks = re.findall(r"(?ms)^```mermaid\s*\n(.*?)^```\s*$", text)
        self.assertEqual(len(blocks), 1, "chapter must contain one Mermaid figure")
        self.assertEqual(blocks[0].strip(), source.strip())
        self.assertEqual(text.count(f'<a id="{FIGURE_ANCHOR}"></a>'), 1)

    def test_fig60_is_registered_once_and_links_to_chapter_and_source(self) -> None:
        chapter_text = self._read_required(CHAPTER)
        registry_path = ROOT / "images/第9篇_Project/README.md"
        registry = self._read_required(registry_path)
        self.assertIn(FIGURE_ANCHOR, registry)
        self.assertIn("uno-q-lab-environment-project-baseline.mmd", registry)
        self.assertIn(f"../../{SUMMARY_LINK}#{FIGURE_ANCHOR}", registry)

        registrations = [
            line.strip()
            for path in (ROOT / "images").rglob("README.md")
            for line in path.read_text(encoding="utf-8").splitlines()
            if re.fullmatch(r"- 图号：\s*Fig-60", line.strip())
        ]
        self.assertEqual(registrations, ["- 图号：Fig-60"])
        self.assertIn("Fig-60", chapter_text)

    def test_summary_and_part_readme_each_link_the_chapter_once(self) -> None:
        summary = self._read_required(ROOT / "SUMMARY.md")
        part_readme = self._read_required(ROOT / "book/第9篇_Project/README.md")
        images_index = self._read_required(ROOT / "images/README.md")
        diagram_index = self._read_required(ROOT / "diagrams/README.md")
        self.assertEqual(summary.count(SUMMARY_LINK), 1)
        self.assertEqual(part_readme.count("第1章_项目立项与需求基线_从场景到可验收目标.md"), 1)
        self.assertIn("第九篇 Project 图示登记", images_index)
        self.assertIn("uno-q-lab-environment-project-baseline.mmd", diagram_index)

        chapter_links = re.findall(r"^- \[第\d+章", summary, re.M)
        root_readme = self._read_required(ROOT / "README.md")
        count = re.search(r"全书当前共\s+(\d+)\s+章", root_readme)
        self.assertIsNotNone(count)
        self.assertEqual(int(count.group(1)), len(chapter_links))

    def test_local_markdown_links_in_chapter_resolve(self) -> None:
        text = self._read_required(CHAPTER)
        text_without_fences = re.sub(r"(?ms)^```.*?^```\s*$", "", text)
        for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text_without_fences):
            if target.startswith(("https://", "http://", "mailto:", "#")):
                continue
            local_path = target.split("#", 1)[0]
            if not local_path:
                continue
            self.assertFalse(local_path.startswith("/"), f"link must be repository-relative: {target}")
            resolved = (CHAPTER.parent / local_path).resolve()
            self.assertTrue(resolved.is_file(), f"broken local link: {target}")

    def test_current_hardware_evidence_stays_not_run(self) -> None:
        text = self._read_required(CHAPTER)
        self.assertRegex(text, r"(?m)^\|\s*UNO Q 实机与传感器采集\s*\|\s*NOT_RUN\s*\|")
        self.assertIn("SYNTHETIC", text)
        self.assertIn("默认关闭", text)

    def test_required_chapter_sections_follow_the_book_template(self) -> None:
        text = self._read_required(CHAPTER)
        headings = [
            "## 学习目标",
            "## 1. 背景与项目章程",
            "## 2. 范围边界与假设",
            "## 6. 本章实验",
            "## 7. 验证结果与当前证据",
            "## 8. 常见问题",
            "## 9. 延伸阅读与交接下一章",
        ]
        positions = [text.find(heading) for heading in headings]
        self.assertTrue(all(position >= 0 for position in positions), "chapter omits a required book section")
        self.assertEqual(positions, sorted(positions), "chapter sections must follow the repository template")


if __name__ == "__main__":
    unittest.main()
