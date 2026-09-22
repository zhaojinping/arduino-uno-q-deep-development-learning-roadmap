"""Offline publication checks for Chapter 4; standard library only."""
from __future__ import annotations

import ast
from pathlib import Path
import re
import subprocess
import sys
import unittest
from urllib.parse import unquote
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
PART = ROOT / "book/第4篇_PythonBridge"
CHAPTER = PART / "第4章_Python_Bridge结果账本与状态查询_从返回值到可验证证据.md"
DIAGRAM = ROOT / "diagrams/uno-q-python-bridge-result-ledger.mmd"
IMAGE = ROOT / "images/第4篇_PythonBridge/ch04-fig27-uno-q-python-bridge-result-ledger.svg"
REGISTRY = IMAGE.parent / "README.md"
FIGURE_ANCHOR = "fig-27-python-bridge-result-ledger"
HEADINGS = [
    "学习目标", "背景与边界", "1. 返回值为什么不是最终证据",
    "2. 请求身份、当前投影与事件历史", "3. 状态机与安全收敛",
    "4. Fig-27：结果账本与状态查询闭环", "5. SQLite 实现：把事实保存下来",
    "6. 实验一：账本持久化与事件历史", "7. 实验二：状态查询与 UNKNOWN 收敛",
    "8. 接入真实 App 的顺序", "9. 验证结果、练习与交接", "10. 常见问题",
    "11. 本章小结与下一步", "延伸阅读",
]
EXPECTED_OUTPUT = {
    "ledger.py": (
        "SIMULATED current=UNKNOWN events=3\n"
        "SIMULATED restart_state=UNKNOWN events=3\n"
        "SIMULATED applied=APPLIED events=4\n"
    ),
    "reconcile_status.py": (
        "SIMULATED not_found: KEEP_UNKNOWN\n"
        "SIMULATED applied: CLOSE_APPLIED\n"
        "SIMULATED expired_not_applied: CLOSE_NOT_APPLIED\n"
        "SIMULATED mismatch: KEEP_UNKNOWN\n"
    ),
}


def read(path: Path) -> str:
    # Decode bytes directly: newline translation would hide source/block drift.
    return path.read_bytes().decode("utf-8")


def without_fences(text: str) -> str:
    result = []
    opened = None
    for line in text.splitlines():
        fence = re.match(r"^(`{3,}|~{3,})", line)
        if fence:
            if opened is None:
                opened = fence[1]
            elif re.fullmatch(re.escape(opened[0]) + "{" + str(len(opened)) + r",}\s*", line):
                opened = None
            continue
        if opened is None:
            result.append(line)
    if opened is not None:
        raise ValueError("Unclosed Markdown fence")
    return "\n".join(result)


def anchors(text: str) -> set[str]:
    prose = without_fences(text)
    found = set(re.findall(r'<a\s+id="([^"]+)"', prose))
    occurrences: dict[str, int] = {}
    for heading in re.findall(r"^#{1,6}\s+(.+)$", prose, re.M):
        slug = re.sub(r"[^\w\- ]", "", heading.lower()).replace(" ", "-")
        number = occurrences.get(slug, 0)
        found.add(f"{slug}-{number}" if number else slug)
        occurrences[slug] = number + 1
    return found


def links(text: str) -> list[str]:
    return re.findall(r"\]\(([^)]+)\)", without_fences(text))


def urls(text: str) -> set[str]:
    # Include linked, bare and autolink URLs, including any inside code fences.
    return set(re.findall(r"https?://[^\s<>\x60)\]|]+", text))


class ChapterChecks(unittest.TestCase):
    link_count = 0
    source_count = 0

    @classmethod
    def setUpClass(cls) -> None:
        cls.text = read(CHAPTER)
        cls.docs = [
            ROOT / "README.md", ROOT / "SUMMARY.md", ROOT / "code/README.md",
            ROOT / "resources/references.md", REGISTRY, HERE / "README.md",
            ROOT / "docs/superpowers/plans/2026-09-22-python-bridge-chapter4-plan.md",
            *sorted(PART.glob("*.md")),
        ]

    def test_metadata(self) -> None:
        """Exact frontmatter, including prerequisites, tags and both dates."""
        match = re.match(r"\A---\n(.*?)\n---\n", self.text, re.S)
        self.assertIsNotNone(match, "Missing LF-delimited chapter frontmatter")
        pairs = [line.split(": ", 1) for line in match[1].splitlines()]
        self.assertTrue(all(len(pair) == 2 for pair in pairs), "Malformed metadata field")
        metadata = dict(pairs)
        self.assertEqual(len(pairs), len(metadata), "Duplicate metadata field")
        self.assertEqual(metadata, {
            "title": "Python Bridge 结果账本与状态查询：从返回值到可验证证据",
            "part": "4", "chapter": "4", "status": "draft",
            "last_verified": "2026-09-22", "updated": "2026-09-22",
            "prerequisites": "第四篇第1～3章、第三篇第8章",
            "tags": "Python Bridge, 结果账本, 状态查询, UNKNOWN, SQLite, 证据",
        }, "Chapter 4 metadata drift")

    def test_heading_sequence_and_anchor(self) -> None:
        """Local Chapter 4 heading sequence and one Fig-27 anchor."""
        prose = without_fences(self.text)
        self.assertEqual(re.findall(r"^# (.+)$", prose, re.M), [
            "第4章 Python Bridge 结果账本与状态查询：从返回值到可验证证据"
        ])
        self.assertEqual(re.findall(r"^## (.+)$", prose, re.M), HEADINGS)
        self.assertEqual(prose.count(f'<a id="{FIGURE_ANCHOR}"></a>'), 1,
                         "Fig-27 chapter anchor must occur exactly once")

    def test_exact_python_blocks(self) -> None:
        """Both complete Python blocks match source bytes and final newline."""
        blocks = re.findall(rb"^~~~python\n(.*?)^~~~$", CHAPTER.read_bytes(), re.M | re.S)
        self.assertEqual(len(blocks), 2, "Expected exactly two complete Python blocks")
        for block, name in zip(blocks, EXPECTED_OUTPUT):
            with self.subTest(source=name):
                source = (HERE / name).read_bytes()
                self.assertTrue(source.endswith(b"\n"), f"Missing final newline: {name}")
                self.assertEqual(block, source, f"Byte-for-byte example drift: {name}")

    def test_python_310_syntax(self) -> None:
        """Parse both current sources with the Python 3.10 AST grammar."""
        for name in EXPECTED_OUTPUT:
            with self.subTest(source=name):
                ast.parse(read(HERE / name), filename=name, feature_version=(3, 10))

    def check_demo(self, name: str) -> None:
        result = subprocess.run(
            [sys.executable, "-B", str(HERE / name)], cwd=ROOT,
            capture_output=True, text=True, encoding="utf-8", timeout=30,
        )
        self.assertEqual(result.returncode, 0, f"{name} failed: {result.stderr}")
        self.assertEqual(result.stderr, "", f"Unexpected stderr from {name}")
        self.assertEqual(result.stdout, EXPECTED_OUTPUT[name], f"Demo output drift: {name}")
        self.assertIn("~~~text\n" + EXPECTED_OUTPUT[name] + "~~~", self.text,
                      f"Documented expected output drift: {name}")

    def test_ledger_demo(self) -> None:
        """Ledger direct demo produces its exact three SIMULATED lines."""
        self.check_demo("ledger.py")

    def test_reconciliation_demo(self) -> None:
        """Reconciliation direct demo produces its exact four SIMULATED lines."""
        self.check_demo("reconcile_status.py")

    def test_experiment_explanations(self) -> None:
        """Each experiment contains all eight explanation fields, in order."""
        expected = ["用途", "运行环境", "文件位置", "依赖", "操作步骤", "预期输出", "故障排查", "验证方式"]
        for index in (7, 8):
            with self.subTest(experiment=HEADINGS[index]):
                section = self.text.split("## " + HEADINGS[index] + "\n", 1)[1]
                section = section.split("\n## ", 1)[0]
                self.assertEqual(re.findall(r"^- ([^：\n]+)：", section, re.M), expected)

    def test_mermaid(self) -> None:
        """One inline Mermaid block equals the standalone source bytes."""
        blocks = re.findall(rb"^~~~mermaid\n(.*?)^~~~$", CHAPTER.read_bytes(), re.M | re.S)
        self.assertEqual(len(blocks), 1, "Expected exactly one Mermaid block")
        self.assertEqual(blocks[0], DIAGRAM.read_bytes(), "Mermaid byte drift")

    def test_svg_and_render_registry(self) -> None:
        """SVG XML, state labels and Fig-27 rendering/preview record exist."""
        self.assertTrue(IMAGE.is_file(), f"Missing SVG: {IMAGE}")
        root = ET.parse(IMAGE).getroot()
        self.assertEqual(root.tag, "{http://www.w3.org/2000/svg}svg")
        self.assertRegex(root.get("style", ""), r"background-color:\s*white")
        labels = " ".join(root.itertext())
        for label in ("PENDING", "SENT", "UNKNOWN", "APPLIED", "REJECTED", "EXPIRED",
                      "NOT_APPLIED_FINAL", "Decision boundary, not a ledger state."):
            self.assertIn(label, labels, f"Missing SVG label: {label}")
        registry = read(REGISTRY)
        self.assertEqual(len(re.findall(r"^- 图号：Fig-27$", registry, re.M)), 1)
        entry = registry.split("- 图号：Fig-27\n", 1)[1]
        for required in (DIAGRAM.name, IMAGE.name, CHAPTER.name + "#" + FIGURE_ANCHOR,
                         "11.12.0", "2026-09-22", "预览"):
            self.assertIn(required, entry, f"Missing Fig-27 registry field: {required}")

    def test_internal_links_and_text(self) -> None:
        """All local Markdown links/anchors in chapter and shared indexes resolve."""
        count = 0
        for path in self.docs:
            content = read(path)
            self.assertNotIn("\ufffd", content, f"Replacement character: {path}")
            self.assertTrue(all(line == line.rstrip() for line in content.splitlines()),
                            f"Trailing whitespace: {path}")
            for target in links(content):
                if target.startswith(("https://", "http://", "mailto:")):
                    continue
                with self.subTest(document=str(path.relative_to(ROOT)), target=target):
                    relative, _, fragment = unquote(target.strip("<>")).partition("#")
                    resolved = (path.parent / relative).resolve() if relative else path
                    self.assertTrue(resolved.is_relative_to(ROOT), "Link escapes repository")
                    self.assertTrue(resolved.is_file(), f"Missing local target: {resolved}")
                    if fragment:
                        if resolved.suffix == ".md":
                            self.assertIn(fragment, anchors(read(resolved)), "Missing Markdown anchor")
                        elif resolved.suffix == ".svg":
                            self.assertIn(fragment, {e.get("id") for e in ET.parse(resolved).iter()},
                                          "Missing SVG anchor")
                        else:
                            self.fail(f"Unsupported local anchor target: {resolved}")
                count += 1
        type(self).link_count = count

    def test_source_registration(self) -> None:
        """Every external chapter URL has an exact reference-index registration."""
        chapter_urls = urls(self.text)
        self.assertTrue(chapter_urls, "No chapter sources found")
        registered = urls(read(ROOT / "resources/references.md"))
        self.assertEqual(chapter_urls - registered, set(), "Unregistered external chapter URLs")
        type(self).source_count = len(chapter_urls)

    def test_navigation(self) -> None:
        """Summary, part/code entries, backlink and root progress/list stay synchronized."""
        summary = read(ROOT / "SUMMARY.md")
        fourth_part = summary.split("## 第四篇：Python Bridge\n", 1)[1].split("\n## ", 1)[0]
        self.assertEqual(links(fourth_part).count(CHAPTER.relative_to(ROOT).as_posix()), 1)
        part = read(PART / "README.md")
        self.assertEqual(links(part).count("./" + CHAPTER.name), 1)
        for token in ("第 1～4 章", "draft", "Fig-27"):
            self.assertIn(token, part, f"Missing part progress: {token}")
        self.assertIn((HERE / "README.md").relative_to(ROOT / "code").as_posix(),
                      links(read(ROOT / "code/README.md")))
        self.assertIn("../../../" + CHAPTER.relative_to(ROOT).as_posix(),
                      links(read(HERE / "README.md")), "Incorrect code README backlink")
        root_readme = read(ROOT / "README.md")
        self.assertIn("第四篇第 4 章", root_readme, "Missing root progress paragraph")
        for path in (CHAPTER, HERE / "README.md", HERE / "ledger.py", HERE / "reconcile_status.py",
                     HERE / "test_ledger.py", HERE / "check_chapter.py", DIAGRAM, IMAGE):
            self.assertIn(path.relative_to(ROOT).as_posix(), root_readme,
                          f"Missing root validation-list entry: {path}")


def main() -> int:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(ChapterChecks)
    result = unittest.TextTestRunner(verbosity=2, stream=sys.stdout).run(suite)
    if not result.wasSuccessful():
        print(f"FAIL: {len(result.failures)} failures; {len(result.errors)} errors")
        return 1
    print(f"PASS: {result.testsRun} checks; metadata; headings; 2 exact examples and demos; "
          f"Python 3.10 syntax; explanations; Mermaid; SVG; {ChapterChecks.link_count} internal links; "
          f"{ChapterChecks.source_count} registered sources; navigation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
