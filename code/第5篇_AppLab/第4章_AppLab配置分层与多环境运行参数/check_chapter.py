"""Offline publication checks for App Lab Chapter 4."""
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
PART = ROOT / "book/第5篇_AppLab"
CHAPTER = PART / "第4章_AppLab配置分层与多环境运行参数_从开发机到现场板.md"
DIAGRAM = ROOT / "diagrams/uno-q-app-lab-config-layering.mmd"
IMAGE = ROOT / "images/第5篇_AppLab/ch04-fig31-uno-q-app-lab-config-layering.svg"
REGISTRY = IMAGE.parent / "README.md"
FIGURE_ANCHOR = "fig-31-uno-q-app-lab-config-layering"
HEADINGS = [
    "学习目标", "背景与边界", "1. 配置不是一个文件", "2. 三层配置与覆盖顺序",
    "3. 运行参数与身份锁定", "4. Fig-31：从分层配置到运行快照",
    "5. 实验一：合并配置层并保留来源", "6. 实验二：生成脱敏运行配置快照",
    "7. Secret、`data/` 与 `.cache/` 的边界", "8. 与 `run_id` 和生命周期的衔接",
    "9. 多环境检查单与验证矩阵", "10. 常见问题", "11. 本章小结与下一步", "延伸阅读",
]
EXPECTED_OUTPUT = {
    "config_layers.py": (
        "SIMULATED env=staging valid=true values=APP_MODE=staging,LOG_LEVEL=debug,TARGET_BOARD=test-q\n"
        "SIMULATED overrides=APP_MODE,LOG_LEVEL\n"
        "SIMULATED invalid=UNKNOWN_KEY:environment.EXTRA\n"
        "SIMULATED locked=LOCKED_OVERRIDE:runtime.TARGET_BOARD\n"
    ),
    "run_config_snapshot.py": (
        "SIMULATED snapshot=run-042 env=staging redacted=DB_PASSWORD\n"
        "SIMULATED payload={\"environment\":\"staging\",\"run_id\":\"run-042\",\"values\":{\"APP_MODE\":\"staging\",\"DB_PASSWORD\":\"<redacted>\",\"LOG_LEVEL\":\"debug\"}}\n"
        "SIMULATED fingerprint=44da1cca1074\n"
    ),
}
EXTERNAL_URLS = {
    "https://github.com/arduino/arduino-app-cli/blob/main/docs/app-specification.md",
    "https://github.com/arduino/arduino-app-cli/blob/main/docs/user-documentation.md",
    "https://docs.arduino.cc/software/app-lab/tutorials/examples/",
    "https://docs.arduino.cc/resources/datasheets/ABX00162-datasheet.pdf",
}


def read(path: Path) -> str:
    return path.read_bytes().decode("utf-8")


def without_fences(text: str) -> str:
    result: list[str] = []
    opened: str | None = None
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
    return set(re.findall(r"https?://[^\s<>\x60)\]|]+", text))


class ChapterChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = read(CHAPTER)
        cls.docs = [
            ROOT / "README.md", ROOT / "SUMMARY.md", ROOT / "code/README.md",
            ROOT / "resources/references.md", REGISTRY, HERE / "README.md",
            PART / "README.md",
        ]

    def test_metadata(self) -> None:
        match = re.match(r"\A---\n(.*?)\n---\n", self.text, re.S)
        self.assertIsNotNone(match, "Missing chapter frontmatter")
        pairs = [line.split(": ", 1) for line in match[1].splitlines()]
        self.assertTrue(all(len(pair) == 2 for pair in pairs), "Malformed metadata")
        self.assertEqual(dict(pairs), {
            "title": "App Lab 配置分层与多环境运行参数：从开发机到现场板",
            "part": "5", "chapter": "4", "status": "draft",
            "last_verified": "2026-09-23", "updated": "2026-09-23",
            "prerequisites": "第五篇第1～3章、第三篇第8章、第四篇第1～4章",
            "tags": "App Lab, 配置分层, 多环境, 运行参数, Secret, run_id, 指纹",
        })

    def test_headings_and_anchor(self) -> None:
        prose = without_fences(self.text)
        self.assertEqual(re.findall(r"^# (.+)$", prose, re.M), [
            "第4章 App Lab 配置分层与多环境运行参数：从开发机到现场板"
        ])
        self.assertEqual(re.findall(r"^## (.+)$", prose, re.M), HEADINGS)
        self.assertEqual(prose.count(f'<a id="{FIGURE_ANCHOR}"></a>'), 1)

    def test_exact_python_blocks(self) -> None:
        blocks = re.findall(rb"^~~~python\n(.*?)^~~~$", CHAPTER.read_bytes(), re.M | re.S)
        self.assertEqual(len(blocks), 2)
        for block, name in zip(blocks, EXPECTED_OUTPUT):
            source = (HERE / name).read_bytes()
            self.assertTrue(source.endswith(b"\n"))
            self.assertEqual(block, source, f"Code block drift: {name}")

    def test_python_310_syntax(self) -> None:
        for name in EXPECTED_OUTPUT:
            ast.parse(read(HERE / name), filename=name, feature_version=(3, 10))

    def check_demo(self, name: str) -> None:
        result = subprocess.run(
            [sys.executable, "-B", str(HERE / name)], cwd=ROOT,
            capture_output=True, text=True, encoding="utf-8", timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        self.assertEqual(result.stdout, EXPECTED_OUTPUT[name])
        self.assertIn("~~~text\n" + EXPECTED_OUTPUT[name] + "~~~", self.text)

    def test_demos(self) -> None:
        for name in EXPECTED_OUTPUT:
            with self.subTest(source=name):
                self.check_demo(name)

    def test_experiment_explanations(self) -> None:
        expected = ["用途", "运行环境", "文件位置", "依赖", "操作步骤", "预期输出", "故障排查", "验证方式"]
        for title in (HEADINGS[6], HEADINGS[7]):
            section = self.text.split("## " + title + "\n", 1)[1].split("\n## ", 1)[0]
            self.assertEqual(re.findall(r"^- ([^：\n]+)：", section, re.M), expected)

    def test_mermaid_and_svg(self) -> None:
        blocks = re.findall(rb"^~~~mermaid\n(.*?)^~~~$", CHAPTER.read_bytes(), re.M | re.S)
        self.assertEqual(blocks, [DIAGRAM.read_bytes()])
        root = ET.parse(IMAGE).getroot()
        self.assertEqual(root.tag, "{http://www.w3.org/2000/svg}svg")
        self.assertRegex(root.get("style", ""), r"background-color:\s*white")
        labels = " ".join(root.itertext())
        for label in ("app.yaml", "environment", "runtime", "run_config_snapshot", "run_id", "指纹"):
            self.assertIn(label, labels)
        self.assertTrue(root.get("viewBox"))
        self.assertIn("Fig-31", read(REGISTRY))

    def test_links_and_anchors(self) -> None:
        all_local = self.docs + [CHAPTER]
        for source in all_local:
            source_text = read(source)
            for target in links(source_text):
                if target.startswith(("http://", "https://", "mailto:")):
                    continue
                path_text, _, fragment = unquote(target).partition("#")
                target_path = (source.parent / path_text).resolve() if path_text else source.resolve()
                self.assertTrue(target_path.is_file(), f"Broken link in {source.name}: {target}")
                if fragment:
                    self.assertIn(fragment, anchors(read(target_path)), f"Broken anchor: {target}")

    def test_sources_and_navigation(self) -> None:
        reference_text = read(ROOT / "resources/references.md")
        self.assertTrue(EXTERNAL_URLS <= urls(self.text))
        self.assertTrue(EXTERNAL_URLS <= urls(reference_text))
        summary = read(ROOT / "SUMMARY.md")
        root_readme = read(ROOT / "README.md")
        part_readme = read(PART / "README.md")
        code_readme = read(ROOT / "code/README.md")
        self.assertIn("book/第5篇_AppLab/第4章_AppLab配置分层与多环境运行参数_从开发机到现场板.md", summary)
        self.assertIn("./第4章_AppLab配置分层与多环境运行参数_从开发机到现场板.md", part_readme)
        self.assertIn("第5篇_AppLab/第4章_AppLab配置分层与多环境运行参数/README.md", code_readme)
        self.assertIn("第五篇第 4 章", root_readme)
        self.assertIn("全书当前共 31 章", root_readme)
        self.assertIn("ch04-fig31-uno-q-app-lab-config-layering.svg", read(REGISTRY))


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(ChapterChecks)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if result.wasSuccessful():
        print("PASS: 9 checks; metadata; headings; 2 exact examples and demos; Python 3.10 syntax; explanations; Mermaid; SVG; links; sources; navigation")
    raise SystemExit(not result.wasSuccessful())
