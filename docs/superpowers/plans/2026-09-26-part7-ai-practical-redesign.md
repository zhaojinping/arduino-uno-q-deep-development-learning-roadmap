# 第七篇 AI 实战化改造实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Use superpowers:test-driven-development for code and contract tests. Do not start the textbook migration until the user has reviewed and approved this plan.

**Goal:** 将第七篇扩展为 10 章的 UNO Q AI 实战路线，新增板载 AI Brick/本地推理与 DeepSeek API 两章，将原工具安全与综合验证章节迁至第9、10章，并完整维护全书导航、图号、交叉引用、代码样例、来源和验证状态。

**Architecture:** 第1～6章保留现有机器学习基础；第7章介绍 UNO Q Linux 侧 App Lab AI Brick 和板载推理，第8章从 UNO Q Linux Python 调用 DeepSeek 公共 API；第9章把模型建议与工具执行权限隔离，第10章综合本地模型、云 API、Bridge/MCU 等不同证据。新章的离线主机测试与目标板/真实 API 验证严格分开。

**Tech Stack:** Markdown、Mermaid、Python 标准库；App Lab/Arduino Bricks 代码按写作时核验的官方接口编写。离线测试用固定数据和 mock HTTP，不依赖网络、密钥、板卡或费用。

**Approved structure:** `docs/superpowers/specs/2026-09-26-part7-ai-practical-redesign-proposal.md`。本计划落实已确认的方案 B：新增两章，原第7、8章改为第9、10章。

## Global constraints

- 不把云端 LLM/API 调用描述为 UNO Q 板载推理；清楚区分 QRB2210/Linux、STM32U585/MCU、App Lab Brick 与公共云服务。
- 不宣称 UNO Q 有独立 NPU；依赖型号、App Lab/Brick、运行时或模型版本的行为必须注明核验版本与目标板验证状态。
- 第7章至少使用 Arduino 官方 `object_detection` AI Brick 示例作为具体板载入口；本地 `LargeLanguageModel` 为可选路径，须说明模型、SKU、内存、运行器与版本兼容性不可先验保证。
- 第8章展示从 UNO Q Linux Python 连接 DeepSeek Chat Completions 的端到端代码形态，包含当前官方接口字段、隔离 client、超时/错误处理和完全离线 mock 测试。可评估 `CloudLLM` 作为 App Lab 集成入口，但只有在目标版本接口核验通过后才把它写成可运行代码；REST 示例作为可解释的协议基线。
- 通过环境变量/App Lab 本机 secret 读取 API key；不得把密钥写入正文示例、源代码、fixture、截图、测试输出或 Git 历史。不得要求用户在聊天中发送密钥。
- 新 API 样例默认使用合成实验室测量数据，结果仅为解释/报告，不得直接触发 GPIO、Bridge、MCU 或执行器动作。任何工具调用都需经过独立白名单、参数和身份校验、明确授权及下游硬约束。
- Mock、静态检查和本机测试只证明对应软件契约；板载 Brick、真实模型、TLS/DeepSeek、相机/传感器和 Bridge 的未运行项目一律标记 `NOT_RUN`，不得写成实测通过。
- 真正对 DeepSeek 发起请求可能产生费用并向第三方发送数据；在线目标板验证前，先让用户在设备本地配置 key，并另行征得一次实际调用授权。模型下载、系统/App Lab 更新、刷写 MCU、相机/外设接入或其他改变设备状态的操作，逐项说明后再做。
- 全书图号连续且唯一：Part 7 第1～6章 Fig-43～48；新第7章 Fig-49、新第8章 Fig-50；迁移后的第9章 Fig-51、第10章 Fig-52；Part 8 原 Fig-51～57 改为 Fig-53～59；Part 9 第1章为 Fig-60。
- 每篇章节序号从第1章重新开始；改名迁移不得把篇序当成全书连续章节号。

## Migration map

| 内容 | 当前 | 目标 |
| --- | --- | --- |
| 新板载 AI 实战 | — | `book/第7篇_AI/第7章_UNO_Q板载AI实战_App_Lab_AI_Brick与本地推理.md`；Fig-49 |
| 新 DeepSeek 实战 | — | `book/第7篇_AI/第8章_UNO_Q接入DeepSeek_API_从云端LLM到可验证应用.md`；Fig-50 |
| 工具调用安全 | `第7章_生成式AI与工具调用_从模型建议到受控执行.md` | `第9章_生成式AI与工具调用安全边界_从模型建议到受控执行.md`；Fig-49 → Fig-51 |
| AI 综合验证 | `第8章_AI应用综合验证_从模型基线到受控工具调用.md` | `第10章_AI应用综合验证_从端侧基线到云端闭环.md`；Fig-50 → Fig-52 |
| 第八篇图示 | Fig-51～Fig-57 | Fig-53～Fig-59; update all active prose, anchors, source/asset registries, tests and references |
| 第九篇第1章图示 | pending global allocation | Fig-60 |

The corresponding code directories for the moved chapters change from `code/第7篇_AI/第7章_生成式AI与工具调用` and `.../第8章_AI应用综合验证` to `.../第9章_生成式AI与工具调用安全边界` and `.../第10章_AI应用综合验证`. Preserve implementation and test history through repository-aware moves; update all README, Markdown links and test constants. Keep existing Mermaid filenames for the two moved diagrams unless a repository audit finds a concrete collision; figure identity and registry links must still be updated.

---

### Task 1: Freeze the repository contract and the live migration inventory

**Files:**
- Read: `SUMMARY.md`, root `README.md`, `book/第7篇_AI/README.md`, `book/第8篇_IoT/README.md`, `book/第9篇_Project/README.md`
- Read: `images/README.md`, `images/第7篇_AI/README.md`, `images/第8篇_IoT/README.md`, `diagrams/README.md`, `code/README.md`, `resources/references.md`
- Read: all Part 7/8 chapter files, code READMEs/tests, active Mermaid sources, and existing Markdown/link/figure validation scripts

**Interfaces:** Consumes the approved structure and current checkout; produces a verified affected-file inventory and baseline test commands. No textbook content changes in this task.

- [ ] Identify every live reference to Part 7 Chapters 7/8, their code paths, their `#fig-49`/`#fig-50` anchors, and source sections in `resources/references.md`.
- [ ] Identify every active Fig-51–57 occurrence, including Part 8 tests asserting figure IDs, README progress entries, image/source registries and any Part 9 planned/new figure references; classify archived planning docs separately from live book navigation.
- [ ] Record current `SUMMARY.md` chapter count (56), current test modules and applicable repo-wide contract checks; do not modify old status narratives silently.
- [ ] Re-open official Arduino, Qualcomm and DeepSeek primary sources immediately before authoring; record access date, software/API versions, and which claims remain hardware-dependent. Verify current API model identifier and request field names instead of copying stale values from the proposal.

### Task 2: Define failing offline contracts for both new chapters

**Files:**
- Create: `code/第7篇_AI/第7章_UNO_Q板载AI实战/test_onboard_ai_contract.py`
- Create: `code/第7篇_AI/第8章_DeepSeek_API实战/test_deepseek_client.py`
- Modify: existing link/figure contract tests only where a repository-level helper already owns those checks

**Interfaces:** Tests consume fixed local fixtures and mockable boundaries; they must not import/run hardware-only Bricks, fetch models, access network, load secrets, or call DeepSeek.

- [ ] Specify chapter front matter/status, mandatory safety and evidence sections, concrete code references, diagram anchor/source parity, internal links, secret scanning and explicit `NOT_RUN` hardware/API state.
- [ ] For DeepSeek client tests, cover request schema, bounded input/context, successful response decoding, malformed/oversized response, timeout, HTTP/API errors and secret redaction with a mocked transport.
- [ ] Run both test files before implementation and record expected failures; ensure they never print a test API key or perform external I/O.
- [ ] Add global figure-uniqueness and active-link checks that detect both duplicated Fig IDs and stale pre-migration Part 7/8 paths.

### Task 3: Author Chapter 7 — board-local AI and AI Bricks

**Files:**
- Create: `book/第7篇_AI/第7章_UNO_Q板载AI实战_App_Lab_AI_Brick与本地推理.md`
- Create: `code/第7篇_AI/第7章_UNO_Q板载AI实战/README.md` and offline contract tests/fixtures
- Create: `diagrams/uno-q-onboard-ai-brick-flow.mmd`
- Modify: `book/第7篇_AI/README.md`, `images/第7篇_AI/README.md`, `diagrams/README.md`, `code/README.md`, `resources/references.md`

**Interfaces:** Uses only verified Arduino AI Brick/App Lab interfaces. The primary hands-on path follows the official `object_detection` sample-image example; local LLM is an optional, separately qualified path. Figure: Fig-49.

- [ ] Explain the dual-brain responsibility split: QRB2210 Linux executes Python/Brick workloads; STM32U585 remains deterministic MCU control; Bridge transports explicitly scoped data rather than granting model authority.
- [ ] Show environment/app layout, dependency/version assumptions, Brick import and input/output flow for object detection based on the then-current official sample. Label source image and result as example/mock if not executed on the user's board.
- [ ] Include setup/run/cleanup guidance, expected result shape, common import/model/input failures, and a target-board evidence table for board SKU, OS/App Lab/Brick versions, model identity, warm-up, latency, CPU/RSS and `NOT_RUN` status.
- [ ] Describe `LargeLanguageModel`/runtime/model availability only to the extent supported by current official source; explicitly distinguish CPU/GPU/runtime capability from an unverified NPU claim.
- [ ] Add Mermaid, chapter placeholder, independent source, image registration, citations and offline contract tests; do not claim target-board execution.

### Task 4: Author Chapter 8 — DeepSeek API from UNO Q Linux

**Files:**
- Create: `book/第7篇_AI/第8章_UNO_Q接入DeepSeek_API_从云端LLM到可验证应用.md`
- Create: `code/第7篇_AI/第8章_DeepSeek_API实战/README.md`, client module, example app and tests
- Create: `diagrams/uno-q-deepseek-cloud-api-flow.mmd`
- Modify: Part 7 navigation, figure/diagram/source indexes and `resources/references.md`

**Interfaces:** Main conceptual boundary is standard HTTPS Chat Completions; code may use Python standard library or verified App Lab `CloudLLM`. The concrete example summarizes synthetic lab readings as a report-only response. Figure: Fig-50.

- [ ] Revalidate the official DeepSeek base URL, endpoint, model name, required headers/body, error semantics, rate/cost notes and data-handling caveats; record the checked date in references and chapter.
- [ ] Implement an injectable HTTP transport/client so host tests use mocks only. Use explicit timeout, bounded payload/context, strict response parsing, sanitized errors and no automatic retry after an ambiguous outcome.
- [ ] Read credentials only from a local environment/App Lab secret and fail clearly when absent. Include only a placeholder variable name in examples; add tests proving no key appears in formatted errors/logs.
- [ ] Explain clearly that prompt/data leave the device for the public service. Keep model output as explanation/summary only; no tool or actuator side effect in the chapter's baseline example.
- [ ] Evaluate the current Arduino `CloudLLM` interface. If compatibility cannot be verified for the documented UNO Q target, present it as a candidate integration and make the standard-library REST path the runnable protocol example.
- [ ] Add Mermaid, source registry, chapter cross-references, examples and fully offline unit tests. Mark actual board/API checks `NOT_RUN`; a mock response is not a real DeepSeek result.

### Task 5: Move the existing safety and synthesis chapters to Chapters 9/10

**Files:**
- Move/rename the two existing Part 7 chapter Markdown files to the paths in the migration map.
- Move/rename their code directories to `code/第7篇_AI/第9章_生成式AI与工具调用安全边界/` and `code/第7篇_AI/第10章_AI应用综合验证/`.
- Modify: both chapter bodies, code READMEs/tests, Part 7 handoff references, Part 8 Chapter 5 cross-reference and every active navigation path.

**Interfaces:** Preserve the established offline policy simulator and evidence gate behavior, then connect Chapters 7/8 as evidence sources without making cloud/API status imply local inference or tool permission.

- [ ] Perform repository-aware moves; update all chapter/code relative links, heading anchors, part/chapter front matter, registry backlinks and commands used to run tests.
- [ ] Renumber existing safety/evidence Mermaid anchors/placeholders/registrations from Fig-49/50 to Fig-51/52; update associated tests and `resources/references.md` sections/headings.
- [ ] Update Chapter 10's evidence matrix to distinguish host tests, UNO Q Brick execution, local-model inference, actual DeepSeek call, image/camera, Bridge/MCU and safety-action validation. Default unperformed evidence to `NOT_RUN`; retain report-only/no-deployment semantics.
- [ ] Update Chapter 10 links to new Chapters 7–9 and update Part 8 Chapter 5's link to the relocated Chapter 9 safety boundary.

### Task 6: Renumber Part 8 and Part 9 figures; synchronize whole-book navigation

**Files:**
- Modify: Part 8 Chapters 1–7, any exact figure assertions in `code/第8篇_IoT`, `book/第8篇_IoT/README.md`, `images/第8篇_IoT/README.md`, `diagrams/README.md`, `images/README.md`, `resources/references.md`, root `README.md`, `SUMMARY.md`, `book/第7篇_AI/README.md`, `code/README.md`
- Modify as required: the Part 9 Chapter 1 design/implementation plan to identify Fig-60 consistently

**Interfaces:** The registry remains one global, unique sequence, and chapter numbering remains local to each part.

- [ ] Change only active Part 8 figure references 51–57 to 53–59, including test expectations and chapter-local HTML/Markdown anchors, while preserving unrelated numbers such as test counts, protocol versions or historical notes when they are not figure IDs.
- [ ] Register new Part 7 Fig-49/50 and moved Fig-51/52 in every source/image registry; verify each chapter placeholder, heading ID, source filename and registry backlink agree.
- [ ] Set Part 9 Chapter 1's planned figure to Fig-60 and check there is no duplicate or gap inconsistent with existing global registry policy.
- [ ] Update `SUMMARY.md` with 10 Part 7 chapters and 58 total existing chapters (59 only after Part 9 Chapter 1 is separately authored); update root README's live chapter count, links and current status to reflect this work accurately.
- [ ] Revise superseded progress statements in the root README instead of leaving both “before” and “after” states presented as current. Preserve a dated history only if the repository convention explicitly treats it as a changelog.

### Task 7: Full editorial, source, link and code verification

**Files:** All affected content and registries from Tasks 1–6.

**Interfaces:** Consumes the completed migration; produces reproducible host-only test evidence and an accurate list of target checks still awaiting the physical board.

- [ ] Run new Chapter 7 and 8 tests, moved Chapter 9 and 10 tests, relevant Part 8 chapter tests, and the whole-book Python regression suite.
- [ ] Run `git diff --check`, all existing Markdown relative-link/anchor checks, figure-ID uniqueness scan, all Mermaid body/source parity checks and source/image registry consistency tests.
- [ ] Review claims against current primary Arduino, Qualcomm and DeepSeek sources; confirm no NPU overclaim, cloud/local conflation, stale API model ID, committed secret or mock-as-real claim.
- [ ] Render diagrams if the repository's renderer is available; otherwise state precisely that SVG/rendered visual review remains outstanding.
- [ ] Record actual test counts only from the run; do not update a count from estimates. Keep `draft` status and hardware/API evidence `NOT_RUN` until truly verified.
- [ ] Ask for independent read-only technical/editorial review if an available review mechanism exists; resolve significant findings before any release claim.

### Task 8: Board and live API validation — explicit later checkpoint

**Files:** None until the user connects the board and the live-test scope is agreed; any evidence log must exclude secrets.

**Interfaces:** Requires a connected UNO Q and user-side setup. Public API request requires a separately confirmed billable network call.

- [ ] Ask the user to connect the board before claiming the App Lab Brick/local model or TLS/API path works on their specific hardware.
- [ ] First inspect board SKU, OS/App Lab/Brick versions and available resources read-only. Ask before downloading a model, updating software, flashing MCU or enabling a camera/peripheral.
- [ ] Have the user configure the API key locally; never request or display the key. Before sending actual prompt data to DeepSeek, confirm the exact synthetic payload and that the user approves a possible charge and third-party transfer.
- [ ] Record only sanitized result metadata, timings and error category. Keep failures/untested paths visible rather than rewriting them as success.

## Review focus

- Does each chapter make the Linux/MCU/local/cloud boundaries obvious to a reader building with this exact board?
- Are vendor-specific APIs and model identifiers versioned and directly source-linked, with a clear fallback if App Lab changes?
- Can all Chapter 8 unit tests pass with networking disabled and no secret configured?
- Are the new two chapters substantial applied tutorials, not merely expanded architecture summaries?
- Is every figure ID unique and every moved/renumbered cross-reference navigable?
- Does any wording imply a cloud call is local inference, a model response has execution authority, a mock is a board run, or a readiness checklist is deployment approval?

## Stop point

This file is a plan, not implementation approval. Present it for review after verifying the paths and migration inventory. Until the plan is approved, do not move old chapters, renumber Part 8 figures, or write/commit/push the two new chapters. Physical board validation and a billable DeepSeek request remain separate user-controlled checkpoints even after the writing plan is approved.
