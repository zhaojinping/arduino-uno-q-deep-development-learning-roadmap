# 第八篇第7章 IoT 综合验证实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 编写第八篇第7章，并提供一个只汇总本机第1～6章固定标准库测试的离线验证工具。

**Architecture:** 验证工具只允许访问仓库中六个已登记的 IoT 章节测试目录，以独立 Python 子进程串行执行 `unittest discover`，输出固定 JSON 汇总。章节把本地单元测试与目标板观察、独立证据复核和部署授权分开；所有自动汇总结果都固定不授权部署。

**Tech Stack:** Python 3.10+ 标准库（`json`、`pathlib`、`subprocess`、`sys`、`unittest`）；Markdown；Mermaid。

**Spec:** 已获用户确认的第八篇第7章设计：`第7章 IoT 综合验证：从分章测试到系统级证据`；本机固定目录测试聚合、逐章证据矩阵、Fig-57；禁止任意路径、网络、Broker、硬件或部署授权。

## Global Constraints

- 仅运行第八篇第1～6章的固定测试目录，不接受路径、命令或目标地址参数。
- 子进程使用参数数组，不经 shell；不访问网络、Broker、传感器、Bridge/RPC、执行器或 UNO Q。
- 汇总只描述本机测试进程结果；证据真实性、目标环境验收和部署授权始终需要独立责任人。
- 保持教程代码使用 Python 标准库，并沿用本篇的合成数据和明确验证边界。
- 每篇从第1章重新编号；本章为第八篇第7章，图号顺延为 Fig-57。

## Review Focus

- 固定范围被扩展到外部目录或任意命令；测试需核验 CLI 不接受额外参数，实际报告只含六个固定章节。
- 非零退出、超时或缺失章节被误报为通过；测试需覆盖失败/不完整汇总以及真实六目录运行。
- 本机全绿被误写成设备验收或部署批准；单元测试和 CLI 测试均断言目标验收未执行、部署授权为 `false`。
- 证据矩阵把合成模拟、目标观察、独立复核和未知状态混为一谈；章节需逐项标明证据类别及阻断条件。
- Fig-57 正文与独立 Mermaid 源、注册表和导航链接发生漂移；验证需解析本地链接并逐字比较 Mermaid 正文与源文件。

---

### Task 1: 补足第六章独立审阅指出的回归覆盖

**Files:**
- Modify: `code/第8篇_IoT/第6章_IoT设备身份与安全通信/test_policy_linter.py`
- Read: `resources/references.md`
- Read: `images/第8篇_IoT/README.md`
- Read: `book/第8篇_IoT/第6章_IoT设备身份与安全通信_从连接信任到最小权限.md`

**Interfaces:**
- Consumes: 第六章现有参考表、Fig-56 图片登记和锚点。
- Produces: 测试逐行校验七列来源元数据；校验 Fig-56 在章节与图登记中的锚点各唯一一次，且反向链接指向该章节的同名 fragment。

- [x] **Step 1: 写出回归断言。** 已扩展 `test_chapter_six_sources_are_registered_with_versions_and_boundaries` 与 `test_fig56_registry_anchor_and_local_links_resolve`，不改章节正文内容。
- [x] **Step 2: 运行第六章测试。** 在 `code/第8篇_IoT/第6章_IoT设备身份与安全通信` 执行 `python -B -m unittest -v test_policy_linter.py`，45 项通过；新增七列逐行非空/核验日期检查与唯一锚点/fragment 回链检查均通过。

### Task 2: 先测试后实现固定范围的本地测试聚合器

**Files:**
- Create: `code/第8篇_IoT/第7章_IoT综合验证/test_aggregate_local_tests.py`
- Create: `code/第8篇_IoT/第7章_IoT综合验证/aggregate_local_tests.py`
- Create: `code/第8篇_IoT/第7章_IoT综合验证/README.md`

**Interfaces:**
- Consumes: 第1～6章既有 `test_*.py` 文件夹。
- Produces: `summarize_results(results)` 纯函数；无参数 `run_all_suites()`；无参数 CLI 输出含 `scope`、`decision`、六条逐章结果、`target_validation` 与 `deployment_authorized` 的 JSON。

- [x] **Step 1: 写失败测试。** 为全通过、任一失败、结果缺项/额外无效记录、子进程超时/启动错误、额外 CLI 参数及六个真实目录均被执行等行为编写测试。初次运行按预期因模块尚不存在而失败。

```python
self.assertEqual(report["decision"], "LOCAL_TESTS_PASS")
self.assertEqual(report["target_validation"], "NOT_RUN")
self.assertIs(report["deployment_authorized"], False)
self.assertEqual([item["chapter"] for item in report["chapters"]], EXPECTED_CHAPTERS)
```

- [x] **Step 2: 运行新测试观察预期失败。** 初次执行 `python -B -m unittest -v test_aggregate_local_tests.py` 得到缺少 `aggregate_local_tests.py` 的断言失败；随后增加的畸形记录/子进程启动错误测试也各自出现预期失败。
- [x] **Step 3: 实现最小聚合器。** 固定六个相对目录；命令为 `[sys.executable, "-B", "-m", "unittest", "discover", "-s", fixed_directory, "-p", "test_*.py"]`；使用 `cwd=REPOSITORY_ROOT`、`shell=False` 和有界超时；失败、超时、启动错误及空测试目录只产出非通过状态；CLI 额外参数返回用法错误。
- [x] **Step 4: 重跑新测试观察通过。** 执行 `python -B -m unittest -q test_aggregate_local_tests.py`，15 项测试全部通过；其中一项实际运行六个固定目录，报告 16/5/11/14/30/45 项并固定不授权部署。
- [x] **Step 5: 编写运行说明。** README 记录目录、命令、JSON 字段、逐章测试边界、失败语义、无网络/硬件限制和“本机通过不等于目标验收”。

### Task 3: 编写章节、证据矩阵和 Fig-57

**Files:**
- Create: `book/第8篇_IoT/第7章_IoT综合验证_从分章测试到系统级证据.md`
- Create: `diagrams/uno-q-iot-integration-validation.mmd`
- Modify: `code/第8篇_IoT/第7章_IoT综合验证/test_aggregate_local_tests.py`
- Modify: `SUMMARY.md`
- Modify: `README.md`
- Modify: `book/第8篇_IoT/README.md`
- Modify: `images/第8篇_IoT/README.md`
- Modify: `resources/references.md`

**Interfaces:**
- Consumes: 第八篇第1～6章的程序、测试与限制说明；Python 3.14 `unittest` 官方命令文档。
- Produces: 第八篇第7章；逐章证据矩阵；Fig-57 正文锚点、登记项和独立 Mermaid 源；可运行示例与清晰的验收/授权分界。

- [x] **Step 1: 写失败的文档契约测试。** 在 `test_aggregate_local_tests.py` 验证章节 front matter/必要标题、导航链接、代码 README/来源登记、本章 Fig-57 锚点唯一、正文 Mermaid 与独立源文件一致，并确认本地链接存在。
- [x] **Step 2: 运行新契约测试观察预期失败。** 第7章正文/图源尚不存在时，bootstrap 断言按预期失败；章节、导航、代码和登记完成后 15 项测试通过。
- [x] **Step 3: 写章节初稿并建立 Fig-57。** 章节按目标与范围、六章证据矩阵、本地聚合器、目标环境证据、失败/阻断、Fig-57、交接和验证边界编写；正文与 `.mmd` 完全一致，成功报告明确不自动触发目标板或部署动作。
- [x] **Step 4: 同步导航与登记。** 新章已追加到 `SUMMARY.md` 和本篇地图；根 README 更新为56章和最新验证计数；图片登记含 Fig-57 唯一锚点、正文回链、源文件链接及未渲染说明；来源索引已登记 Python `unittest` 官方文档。

### Task 4: 全书验证、独立复核与推送

**Files:**
- Verify: `code/第8篇_IoT/第7章_IoT综合验证/`
- Verify: 所有受影响 Markdown 与 Fig-57 Mermaid 源。
- Commit: 本次修复与第7章工作树变更。

**Interfaces:**
- Consumes: Task 1–3 交付物。
- Produces: 可复现测试/链接/锚点检查结果；提交；经远端确认的推送状态。

- [x] **Step 1: 跑章节聚合器与全书测试。** Python 3.14.6；聚合器报告六章 121 项全通过；全书 pytest 362 项及 298 个子测试通过；明确未作硬件验收。
- [x] **Step 2: 验证文档。** 新章/图登记链接和双源契约测试通过；排除 fenced code 的全仓 Git 跟踪/未跟踪 Markdown 行内链接扫描为 140 份 Markdown、1067 个本地目标、0 缺失；`git diff --check` 通过。
- [x] **Step 3: 更新测试计数和验证边界。** 根 README 已更新总章数、测试和链接计数；IoT README/参考索引已更新为15项本章测试；SVG 未渲染与实机未测边界保留。
- [x] **Step 4: 请求独立审阅并处理发现。** 独立只读审阅未发现 Critical/Important 项；一项 Minor 提醒执行环境变量会继承且该工具不是沙箱，已在章节和运行 README 明确标示边界，并复跑全书测试。另一项 Minor 指出旧链接统计未区分 fenced code；已用排除 fenced code 的全仓扫描重新核验并把正式计数更新为 1067 个目标、0 缺失。
- [x] **Step 5: 提交并尝试推送。** 主交付提交 `fd8e170`（`docs: add IoT integration validation chapter`）已推送成功；受限网络中的首次尝试未能连接 `github.com:443`，经授权重试后远端 `main` 从 `f9c4e6a` 更新到 `fd8e170`。
