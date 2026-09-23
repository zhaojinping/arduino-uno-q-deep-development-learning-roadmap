# 第七篇第5章端侧推理性能评估实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在第七篇新增一章端侧推理性能评估，配套离线合成数据分析器、行为测试、图示及完整导航与来源登记。

**Architecture:** 使用 Python 标准库读取单次运行的 JSON 记录，严格校验环境元数据、预热/正式样本数量与有限数值，再输出明示采用最近秩法的 P50/P95、最大时延和观测 RSS。所有有效输入都只产生 `REPORT_ONLY`；正文讲解如何采集真实目标数据，但本次不执行模型或硬件测量。

**Tech Stack:** Markdown、Mermaid、Python 3.10+ 标准库、`unittest`、JSON。

**Spec:** `docs/superpowers/specs/2026-09-24-ai-inference-performance-design.md`（用户已确认的题目与范围及验收边界）。

## Global Constraints

- 章节保持 `draft`，`part: 7`、`chapter: 5`，事实核验日期为 `2026-09-24`。
- 不安装依赖，不加载模型，不调用 ONNX Runtime、Arduino UNO Q、网络设备、Bridge、MCU 或执行器。
- 所有数据均标记为合成教学记录；不得虚构实机/真实运行时的测量或兼容性结论。
- 所有报告均为 `REPORT_ONLY`、不应用阈值；输入问题用 `BLOCKED` 和非零退出码表达。
- 使用标准库；预热样本必须与正式时延统计隔离；分位数方法明确为最近秩法。
- 依照 `docs/writing-guidelines.md`，维护篇内编号、唯一图号、代码说明、来源登记、Mermaid 双源和相对链接。
- 依据用户持续维护本仓库、确认本章并确认验证后推送的授权，在现有 `main` 检出内工作；只在验证通过后提交与推送。

## Review Focus

- 错误的预热/正式样本边界污染分位数：用明显较大的预热值验证其被排除。
- 分位数算法或索引边界出错：用手工排序、固定 P50/P95 期望验证最近秩法。
- 把 `bool`、`NaN`、无穷大、零或负值当作有效测量：分别验证输入拒绝。
- 声明的样本数、索引、阶段顺序不一致仍输出摘要：验证阻断及非零退出码。
- 高性能数字被误读成目标验收：验证报告对全部有效输入恒为 `REPORT_ONLY` 且不应用阈值，并在章节/图示登记中重复界定。

---

### Task 1: 离线性能记录分析器

**Files:**
- Create: `code/第7篇_AI/第5章_端侧推理性能评估/test_analyze_benchmark.py`
- Create: `code/第7篇_AI/第5章_端侧推理性能评估/analyze_benchmark.py`
- Create: `code/第7篇_AI/第5章_端侧推理性能评估/benchmark.json`
- Create: `code/第7篇_AI/第5章_端侧推理性能评估/README.md`

**Interfaces:**
- Consumes: schema-version 1 JSON run object with `run_id`, environment identity, `warmup_count`, `measured_count` and ordered `samples`.
- Produces: `percentile_nearest_rank(values: Sequence[float], percentile: float) -> float` with `percentile` in `(0, 1]`, `analyze_run(run: Mapping[str, object]) -> dict[str, object]`, `load_run(path: Path) -> dict[str, object]`, `main(argv: Sequence[str] | None = None) -> int`.
- A valid report contains `status="REPORT_ONLY"`, `report_only=true`, `thresholds_applied=false`, sample counts, `latency_ms` nearest-rank P50/P95/mean/max, and `memory_mib.observed_max_rss` from measured samples only. Invalid input raises a domain `ValueError` subtype; CLI prints `BLOCKED` to stderr and returns 1.

- [x] **RED — write tests before `analyze_benchmark.py`.** Add these behavior contracts to `test_analyze_benchmark.py` (the local `make_run` helper builds only input data; expected values below are literal and hand-derived):

```python
def test_warmups_do_not_affect_measured_latency_summary():
    report = analyze_run(make_run(warmups=[999.0, 888.0], measured=[10.0, 20.0, 30.0, 40.0]))
    assert report["latency_ms"]["p50_nearest_rank"] == 20.0
    assert report["latency_ms"]["p95_nearest_rank"] == 40.0
    assert report["latency_ms"]["max"] == 40.0

def test_nearest_rank_uses_ceiling_of_percentile_times_sample_count():
    values = list(range(1, 21))
    assert percentile_nearest_rank(values, 0.50) == 10
    assert percentile_nearest_rank(values, 0.95) == 19

def test_valid_measurements_never_claim_a_threshold_pass():
    report = analyze_run(make_run(warmups=[5.0], measured=[10000.0, 20000.0]))
    assert report["status"] == "REPORT_ONLY"
    assert report["report_only"] is True
    assert report["thresholds_applied"] is False
```

  Add separate rejection cases for wrong schema, missing environment identity, count/index/phase inconsistency, empty measured data, boolean/zero/negative/NaN/infinite latency or RSS, and CLI behavior. The latter must assert valid JSON output with exit code 0, and invalid input with `BLOCKED` on stderr plus exit code 1.
- [x] **RED — prove the tests detect missing behavior.** From the chapter code directory run `python -m unittest -v test_analyze_benchmark.py`; expected result: failure due to absent `analyze_benchmark` module/API. If it fails for an import typo or test error, fix the test and repeat until the intended failure is visible.
- [x] **GREEN — implement the minimum interface.** Add `percentile_nearest_rank(values, percentile)` with a fractional percentile from `(0, 1]`, strict schema validation, `analyze_run(run)`, `load_run(path)`, and `main(argv=None)`; use standard-library JSON, `math.isfinite`, `statistics.fmean`, and `argparse` only. Keep errors as a `ValueError` subtype and keep input files unchanged.
- [x] Add `benchmark.json` with exactly 3 `warmup` and 20 `measured` synthetic rows. Its measured sorted values must be `[11, 12, 12.5, 12.8, 13, 13.2, 13.5, 14, 14.2, 14.5, 14.8, 15, 15.5, 16, 16.3, 17, 17.1, 18, 19, 23]`; expected nearest-rank P50 is `14.5`, P95 is `19.0`, and max is `23.0`.
- [x] Add a README with exact invocations `python -B analyze_benchmark.py --input benchmark.json` and `python -B -m unittest -v test_analyze_benchmark.py`, schema fields, sample command result and explicit “synthetic data / no model / no UNO Q” scope; `-B` prevents bytecode artifacts.
- [x] **GREEN — run the chapter tests and fixture CLI.** Expected: every chapter test passes; CLI prints valid JSON with `status=REPORT_ONLY`, `p50_nearest_rank=14.5`, `p95_nearest_rank=19.0`, `max=23.0`; no source file is changed. Run `git diff --check` as a separate check.
- [x] Commit the focused files with message `docs(ai): add offline inference performance analyzer`, test follow-up `test(ai): verify warmup RSS exclusion`, and finite-input mean follow-up `fix(ai): prevent overflow in finite latency mean`.

### Task 2: Chapter prose, Mermaid figure and sources

**Files:**
- Create: `book/第7篇_AI/第5章_端侧推理性能评估_从测量方案到资源预算.md`
- Create: `diagrams/uno-q-ai-inference-performance.mmd`
- Modify: `images/第7篇_AI/README.md`
- Modify: `diagrams/README.md`
- Modify: `resources/references.md`

**Interfaces:**
- Consumes: Task 1 schema, report fields, executable commands, fixture outputs, test behavior.
- Produces: publication-structured chapter with a transparent performance measurement protocol, the exact experiment contract, Fig-47, traceable official references, and explicit hardware/measurement limits.

- [x] Write the chapter using the approved scope and required order: five-field metadata, measurable learning goals, cold-start/warm-up/inference/end-to-end distinctions, comparable-run contract, nearest-rank and RSS limits, experiment using Task 1, verification scope, common questions and further reading.
- [x] Embed the flow `record contract → validate environment/counts → separate warmups → compute statistics → REPORT_ONLY`; include a `BLOCKED` branch and an explicit stop before claiming target acceptance. Save that same Mermaid body as `diagrams/uno-q-ai-inference-performance.mmd`.
- [x] Append source entries for `https://onnxruntime.ai/docs/performance/tune-performance/`, `https://onnxruntime.ai/docs/performance/tune-performance/profiling-tools.html`, and `https://docs.python.org/3/library/time.html`; summarize only the supported metric/profiling/clock facts and state they do not verify UNO Q support.
- [x] Register Fig-47 with a unique anchor, chapter link, content, source and “SVG 待生成并完成预览审阅” status. Run a PowerShell relative-link check on chapter Markdown, compare the inline Mermaid block with the `.mmd` file, search for duplicate `fig-47` IDs, and run `git diff --check`.
- [x] Commit the chapter, figure and sources as one document-focused change with message `docs(ai): add inference performance evaluation chapter`.

### Task 3: Navigation, progress record and whole-project verification

**Files:**
- Modify: `SUMMARY.md`
- Modify: `book/第7篇_AI/README.md`
- Modify: `code/README.md`
- Modify: `README.md`

**Interfaces:**
- Consumes: Task 1 runnable code and exact behavior; Task 2 chapter path/title, Fig-47 identity and verified source/measurement boundaries.
- Produces: consistent chapter navigation and progress records showing 46 book chapters, five chapters in the AI part, the new test count, and no real target benchmarking.

- [x] Append Chapter 5 to `SUMMARY.md` and `book/第7篇_AI/README.md`; update `code/README.md` inventory and root `README.md` progress to 46 chapters, 第七篇第1～5章 and the measured test total. Keep `draft`, real target benchmarking and SVG review explicitly outstanding.
- [x] Verify all 15 Chapter 5 relative links with a path-resolving check; verify front matter `part=7`, `chapter=5`, `status=draft`, `last_verified=2026-09-24`, one Fig-47 anchor in the chapter and resource index, Mermaid parity, and root/part/SUMMARY title/path/count agreement.
- [x] Run `python -B -m pytest -q code` from the repository root: exit 0, 191 tests passed, 135 subtests passed in 21 test modules. Run `git diff --check` separately and inspect the complete implementation, chapter, navigation and supporting-document diffs.
- [x] Complete final self-review: implementation and chapter match the confirmed scope; no blocking findings. No independent review agent was available, so this is a recorded self-review rather than a second-person review.
- [x] Commit navigation, progress record, and this plan/spec as `docs(ai): index inference performance chapter`; user-authorized push and remote SHA verification remain the final delivery step.

**Expected verification:** 21 chapter behavior tests and the full suite (191 tests, 135 subtests, 21 modules) pass; all 15 Chapter 5 relative links resolve; Fig-47 has one registered anchor in the chapter and resource index and matching Mermaid source; root/part counts agree; no renderer or real UNO Q hardware claim is made.
