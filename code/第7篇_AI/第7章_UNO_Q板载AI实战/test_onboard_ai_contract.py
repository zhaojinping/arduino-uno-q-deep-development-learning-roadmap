"""Offline publication and repository contracts for the UNO Q AI chapters."""

from __future__ import annotations

import re
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
CHAPTER_7 = REPOSITORY_ROOT / "book/第7篇_AI/第7章_UNO_Q板载AI实战_App_Lab_AI_Brick与本地推理.md"
CHAPTER_8 = REPOSITORY_ROOT / "book/第7篇_AI/第8章_UNO_Q接入DeepSeek_API_从云端LLM到可验证应用.md"
CHAPTER_9 = REPOSITORY_ROOT / "book/第7篇_AI/第9章_生成式AI与工具调用安全边界_从模型建议到受控执行.md"
CHAPTER_10 = REPOSITORY_ROOT / "book/第7篇_AI/第10章_AI应用综合验证_从端侧基线到云端闭环.md"
DIAGRAM_7 = REPOSITORY_ROOT / "diagrams/uno-q-onboard-ai-brick-flow.mmd"
DIAGRAM_8 = REPOSITORY_ROOT / "diagrams/uno-q-deepseek-cloud-api-flow.mmd"
DIAGRAM_9 = REPOSITORY_ROOT / "diagrams/uno-q-ai-tool-call-guard.mmd"
DIAGRAM_10 = REPOSITORY_ROOT / "diagrams/uno-q-ai-readiness-evidence-gate.mmd"
ACTIVE_ROOTS = (
    "SUMMARY.md",
    "README.md",
    "book",
    "code",
    "images",
    "diagrams",
    "resources",
)


def markdown_links(source: Path) -> list[str]:
    lines = source.read_text(encoding="utf-8").splitlines()
    prose: list[str] = []
    in_fence = False
    for line in lines:
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence:
            prose.append(line)
    return re.findall(r"(?<!!)\[[^\]]*\]\(([^)]+)\)", "\n".join(prose))


class ChapterContentContractTests(unittest.TestCase):
    def assert_chapter_metadata(self, path: Path, *, chapter: int, title: str) -> str:
        self.assertTrue(path.is_file(), f"missing chapter: {path.relative_to(REPOSITORY_ROOT)}")
        text = path.read_text(encoding="utf-8")
        self.assertTrue(text.startswith("---\n"))
        front_matter = text.split("---", 2)[1]
        self.assertIn(f"title: {title}", front_matter)
        self.assertIn("part: 7", front_matter)
        self.assertIn(f"chapter: {chapter}", front_matter)
        self.assertIn("status: draft", front_matter)
        self.assertIn("last_verified: 2026-09-26", front_matter)
        self.assertIn("## 学习目标", text)
        self.assertIn("## 验证结果", text)
        self.assertIn("## 常见问题", text)
        self.assertIn("## 延伸阅读", text)
        return text

    def test_chapter_7_teaches_a_concrete_board_local_brick_and_reports_unrun_evidence(self):
        text = self.assert_chapter_metadata(
            CHAPTER_7,
            chapter=7,
            title="第7章 UNO Q 板载 AI 实战：App Lab AI Brick 与本地推理",
        )
        for required in (
            "## 背景与边界",
            "### 实验一：用 AI Brick 对上传图片做对象检测",
            "### 实验二：把本地 LLM Brick 当作可选能力，而不是规格保证",
            "## 目标板验证记录",
            "ObjectDetection",
            "LargeLanguageModel",
            "ABX00162",
            "ABX00173",
            "CPU",
            "NOT_RUN",
        ):
            self.assertIn(required, text)
        self.assertIn("inspirational/common/object-detection", text)
        self.assertIn("QRB2210", text)
        self.assertIn("STM32U585", text)
        self.assertIn("不代表", text)

    def test_chapter_8_teaches_report_only_cloud_call_and_separates_mock_from_live_api(self):
        text = self.assert_chapter_metadata(
            CHAPTER_8,
            chapter=8,
            title="第8章 UNO Q 接入 DeepSeek API：从云端 LLM 到可验证应用",
        )
        for required in (
            "## 背景与边界",
            "凭据只留在本机",
            "DEEPSEEK_API_KEY",
            "deepseek-flash",
            "thinking",
            "max_tokens",
            "超时",
            "不自动重试",
            "MOCK",
            "NOT_RUN",
            "数据从设备经网络传出",
            "仅供复核",
        ):
            self.assertIn(required, text)
        self.assertIn("test_deepseek_client.py", text)
        self.assertNotRegex(text, r"sk-[A-Za-z0-9_-]{16,}")

    def test_new_chapter_mermaid_is_identical_to_its_registered_source(self):
        for chapter_path, source_path, anchor in (
            (CHAPTER_7, DIAGRAM_7, "fig-49-uno-q-onboard-ai-brick-flow"),
            (CHAPTER_8, DIAGRAM_8, "fig-50-uno-q-deepseek-cloud-api-flow"),
        ):
            self.assertTrue(source_path.is_file(), f"missing Mermaid source: {source_path.name}")
            text = chapter_path.read_text(encoding="utf-8")
            source = source_path.read_text(encoding="utf-8").strip()
            self.assertEqual(text.count("```mermaid"), 1)
            body = text.split("```mermaid", 1)[1].split("```", 1)[0].strip()
            self.assertEqual(body, source)
            self.assertIn(f'<a id="{anchor}"></a>', text)

    def test_migrated_chapters_keep_correct_metadata_figures_and_ai_evidence_boundaries(self):
        chapter_9 = CHAPTER_9.read_text(encoding="utf-8")
        chapter_10 = CHAPTER_10.read_text(encoding="utf-8")
        for path, text, chapter, title, figure, source in (
            (
                CHAPTER_9,
                chapter_9,
                9,
                "生成式 AI 与工具调用安全边界：从模型建议到受控执行",
                "fig-51-uno-q-ai-tool-call-guard",
                DIAGRAM_9,
            ),
            (
                CHAPTER_10,
                chapter_10,
                10,
                "AI 应用综合验证：从端侧基线到云端闭环",
                "fig-52-uno-q-ai-readiness-evidence-gate",
                DIAGRAM_10,
            ),
        ):
            self.assertTrue(path.is_file())
            self.assertTrue(text.startswith("---\n"))
            front_matter = text.split("---", 2)[1]
            self.assertIn("part: 7", front_matter)
            self.assertIn(f"chapter: {chapter}", front_matter)
            self.assertIn(f"title: {title}", front_matter)
            self.assertIn(f'<a id="{figure}"></a>', text)
            self.assertEqual(text.count("```mermaid"), 1)
            body = text.split("```mermaid", 1)[1].split("```", 1)[0].strip()
            self.assertEqual(body, source.read_text(encoding="utf-8").strip())

        for required in (
            "UNO Q 板载 AI Brick",
            "板载本地 LLM",
            "DeepSeek 公共 API",
            "图像/相机输入",
            "Bridge/MCU 通信",
            "安全动作验证",
            "不由本章八门示例程序逐项解析或验证",
        ):
            self.assertIn(required, chapter_10)

    def test_new_chapter_local_links_resolve(self):
        for source in (CHAPTER_7, CHAPTER_8):
            for destination in markdown_links(source):
                if destination.startswith(("https://", "http://", "mailto:")):
                    continue
                path_text, _, _fragment = destination.partition("#")
                if not path_text:
                    continue
                target = (source.parent / path_text).resolve()
                self.assertTrue(
                    target.exists(),
                    f"broken local link in {source.name}: {destination}",
                )

    def test_migrated_chapter_local_reference_anchors_resolve(self):
        for source in (CHAPTER_9, CHAPTER_10):
            for destination in markdown_links(source):
                if destination.startswith(("https://", "http://", "mailto:")):
                    continue
                path_text, separator, fragment = destination.partition("#")
                if not separator:
                    continue
                target = (source.parent / path_text).resolve() if path_text else source
                self.assertTrue(target.is_file(), f"missing fragment target for {destination}")
                self.assertIn(
                    f'<a id="{fragment}"></a>',
                    target.read_text(encoding="utf-8"),
                    f"broken explicit anchor in {source.name}: {destination}",
                )

    def test_part_7_directory_registers_ten_chapters_and_58_total(self):
        summary = (REPOSITORY_ROOT / "SUMMARY.md").read_text(encoding="utf-8")
        self.assertEqual(len(re.findall(r"^- \[第\d+章", summary, re.MULTILINE)), 58)
        for chapter in range(1, 11):
            pattern = re.compile(rf"^- \[第{chapter}章[^\n]*\]\(book/第7篇_AI/[^)]+\)", re.MULTILINE)
            self.assertRegex(summary, pattern)
        for old_path in (
            "第7章_生成式AI与工具调用_从模型建议到受控执行.md",
            "第8章_AI应用综合验证_从模型基线到受控工具调用.md",
            "第7章_生成式AI与工具调用/",
            "第8章_AI应用综合验证/",
        ):
            for root_name in ACTIVE_ROOTS:
                root = REPOSITORY_ROOT / root_name
                sources = [root] if root.is_file() else list(root.rglob("*.md")) if root.exists() else []
                for source in sources:
                    if source.resolve() == Path(__file__).resolve():
                        continue
                    text = source.read_text(encoding="utf-8")
                    self.assertNotIn(old_path, text, f"stale active path in {source.relative_to(REPOSITORY_ROOT)}")

    def test_image_registry_has_unique_contiguous_figure_ids_from_existing_baseline_through_59(self):
        chapter_numbers: list[int] = []
        for chapter in (REPOSITORY_ROOT / "book").rglob("*.md"):
            chapter_numbers.extend(
                int(number)
                for number in re.findall(r'<a id="fig-(\d+)-[^\"]+"></a>', chapter.read_text(encoding="utf-8"))
            )
        self.assertEqual(sorted(chapter_numbers), list(range(4, 60)))

        registry_numbers: list[int] = []
        for registry in (REPOSITORY_ROOT / "images").glob("*/README.md"):
            registry_numbers.extend(
                int(number)
                for number in re.findall(r'<a id="fig-(\d+)-[^\"]+"></a>', registry.read_text(encoding="utf-8"))
            )
        self.assertEqual(sorted(registry_numbers), list(range(26, 60)))

    def test_part_8_active_figures_are_53_through_59(self):
        part_8 = REPOSITORY_ROOT / "book/第8篇_IoT"
        for chapter in part_8.glob("第*章*.md"):
            numbers = [int(value) for value in re.findall(r"Fig-(\d+)", chapter.read_text(encoding="utf-8"))]
            self.assertTrue(numbers, f"no figure reference in {chapter.name}")
            self.assertTrue(all(53 <= value <= 59 for value in numbers), f"old/wrong figure number in {chapter.name}: {numbers}")

    def test_active_part_9_plan_keeps_figure_60(self):
        plan = REPOSITORY_ROOT / "docs/superpowers/plans/2026-09-26-part9-chapter1-implementation-plan.md"
        self.assertIn("Fig-60", plan.read_text(encoding="utf-8"))

    def test_active_markdown_local_link_targets_exist(self):
        files: list[Path] = []
        for root_name in ACTIVE_ROOTS:
            root = REPOSITORY_ROOT / root_name
            files.extend([root] if root.is_file() else root.rglob("*.md") if root.is_dir() else [])
        for source in files:
            for destination in markdown_links(source):
                if destination.startswith(("https://", "http://", "mailto:")):
                    continue
                target_text = destination.split(">", 1)[0][1:] if destination.startswith("<") else destination.split()[0]
                path_text, _, _fragment = target_text.partition("#")
                if not path_text:
                    continue
                target = (source.parent / path_text).resolve()
                self.assertTrue(
                    target.exists(),
                    f"broken active link in {source.relative_to(REPOSITORY_ROOT)}: {destination}",
                )

    def test_new_content_contains_no_credential_shaped_strings(self):
        paths = (CHAPTER_7, CHAPTER_8, DIAGRAM_7, DIAGRAM_8)
        for path in paths:
            if path.is_file():
                self.assertNotRegex(path.read_text(encoding="utf-8"), r"sk-[A-Za-z0-9_-]{16,}")


if __name__ == "__main__":
    unittest.main()
