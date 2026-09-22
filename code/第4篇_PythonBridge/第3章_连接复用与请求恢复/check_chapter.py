"""Read-only checks for chapter 3 links, examples, metadata, and figures."""
from __future__ import annotations

import ast
from pathlib import Path
import re
from urllib.parse import unquote
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
PART = ROOT / "book/第4篇_PythonBridge"
CHAPTER = PART / "第3章_Python_Bridge连接复用与请求恢复_从断线到可判定结果.md"


def read(path: Path) -> str:
    text = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    assert "\ufffd" not in text, f"Replacement character in {path}"
    assert all(line == line.rstrip() for line in text.splitlines()), path
    return text


def without_fences(text: str) -> str:
    result = []
    opened = None
    for line in text.splitlines():
        fence = re.match(r"^([\x60~]{3,})", line)
        if fence:
            if opened is None:
                opened = fence[1]
            elif line.strip() == opened:
                opened = None
            continue
        if opened is None:
            result.append(line)
    assert opened is None, "Unclosed Markdown fence"
    return "\n".join(result)


def anchors(text: str) -> set[str]:
    found = set(re.findall(r'<a\s+id="([^"]+)"', text))
    for heading in re.findall(r"^#{1,6}\s+(.+)$", text, re.M):
        heading = re.sub(r"[^\w\- ]", "", heading.lower())
        found.add(heading.replace(" ", "-"))
    return found


def main() -> None:
    text = read(CHAPTER)
    assert text.startswith("---\n")
    metadata = dict(line.split(": ", 1) for line in text.split("---\n", 2)[1].splitlines())
    for field, expected in {
        "title": "Python Bridge 连接复用与请求恢复：从断线到可判定结果",
        "part": "4", "chapter": "3", "status": "draft", "last_verified": "2026-09-22",
    }.items():
        assert metadata[field] == expected, (field, metadata.get(field))
    examples = re.findall(r"^~~~python\n(.*?)^~~~$", text, re.M | re.S)
    assert len(examples) == 2
    for block, name in zip(examples, ("connection_owner.py", "recovery_policy.py")):
        assert block == read(HERE / name), f"Example drift: {name}"
        ast.parse(block, feature_version=(3, 10))
    for field in ("用途", "运行环境", "文件位置", "依赖", "操作步骤", "预期输出", "故障排查", "验证方式"):
        assert len(re.findall(rf"^- {field}：", text, re.M)) == 2, field
    diagram = re.search(r"^~~~mermaid\n(.*?)^~~~$", text, re.M | re.S)
    assert diagram is not None
    assert diagram[1] == read(ROOT / "diagrams/uno-q-python-bridge-connection-recovery.mmd")
    image = ROOT / "images/第4篇_PythonBridge/ch03-fig26-uno-q-python-bridge-connection-recovery.svg"
    assert ET.parse(image).getroot().tag.endswith("svg")
    registry = read(ROOT / "images/第4篇_PythonBridge/README.md")
    assert len(re.findall(r"^- 图号：Fig-26$", registry, re.M)) == 1
    docs = [
        ROOT / "README.md", ROOT / "SUMMARY.md", ROOT / "code/README.md",
        ROOT / "resources/references.md", ROOT / "images/第4篇_PythonBridge/README.md",
        ROOT / "docs/superpowers/plans/2026-09-22-python-bridge-chapter3-plan.md",
        HERE / "README.md", *sorted(PART.glob("*.md")),
    ]
    count = 0
    for path in docs:
        for target in re.findall(r"\]\(([^)]+)\)", without_fences(read(path))):
            if target.startswith(("https://", "http://", "mailto:")):
                continue
            relative, _, fragment = unquote(target.strip("<>")).partition("#")
            resolved = (path.parent / relative).resolve() if relative else path
            assert resolved.is_relative_to(ROOT), (path, target)
            assert resolved.is_file(), (path, target)
            if fragment and resolved.suffix == ".md":
                assert fragment in anchors(read(resolved)), (path, fragment)
            count += 1
    references = read(ROOT / "resources/references.md")
    for url in re.findall(r"\]\((https?://[^)]+)\)", without_fences(text)):
        assert url.split("#", 1)[0] in references, f"Unregistered source: {url}"
    assert CHAPTER.name in read(ROOT / "SUMMARY.md")
    print(f"PASS: metadata; 2 exact examples; Python 3.10 syntax; Mermaid; SVG; {count} internal links")


if __name__ == "__main__":
    main()
