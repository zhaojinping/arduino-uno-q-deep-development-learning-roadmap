# 第九篇第2章《系统架构设计》实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 完成第九篇第2章《系统架构设计：从处理器边界到可验证数据流》，将已批准的混合架构写成可审查的教学参考章节，并同步图示、导航和来源登记。

**Architecture:** 以 STM32U585 采集、Linux 本地接纳/持久化/规则与展示、Bridge/RPC 传递版本化事件为候选参考架构。章节不锁定传感器、接口参数、采样周期、阈值、存储介质或缓存容量；远程遥测默认关闭，且没有物理执行器路径。

**Tech Stack:** 中文 Markdown；Mermaid `.mmd`；Python 标准库 `unittest` 文档契约测试；现有全仓 pytest 回归。不增加第三方依赖，不连接网络或硬件。

**Spec:** `docs/superpowers/specs/2026-09-26-part9-chapter2-architecture-design.md`

## Global Constraints

- 教学架构为 `DESIGN_ONLY`，合成输入标记为 `SYNTHETIC`，不得声称已完成 UNO Q 实机验证。
- 未决事项包括物理量、传感器型号、接口/引脚、采样周期、量程、校准、陈旧窗口、规则阈值、存储介质、缓存容量及部署参数；不得猜测补齐。
- UNO Q 实机验证状态保持 `NOT_RUN`；目标证据只能来自另行批准并保留原始证据的真实验证。
- 监测、记录、告警和展示不连接或控制继电器、电机、门锁、加热器或其他物理执行器。
- 远程遥测/云端外发默认关闭；章节契约测试和全仓验证不发起网络请求或访问凭据。
- 使用篇内编号 `part: 9`、`chapter: 2`；新图号为经仓库盘点确认的唯一 Fig-61。
- 在当前已同步 worktree 分支 `codex/part9-project-chapter1` 上工作；保留现存的第1章本地计划文件。
- 用户已明确要求提交并推送：仅在全部测试和独立审阅通过后，将本计划范围内文件与本章规格/计划一起提交并推送当前分支；不创建 PR。

## Review Focus

- 测量时间与 Linux 接收时间是否分别保留，且不可信的来源时钟是否保持未知；契约测试须检查这三个字段/边界。
- 重复与乱序事件是否可能覆盖当前状态或重复触发告警；契约测试须检查失效表和去重说明同时涵盖这两类输入。
- Bridge 中断、Linux 重启或没有新鲜数据时是否会把最后一次有效值误显为当前正常；契约测试须检查这三种退化场景及 `UNKNOWN`/等待状态。
- 本地存储失败、空间不足或规则未批准是否仍可能显示无条件正常；契约测试须检查存储失败和规则缺失均映射到可见退化/未知状态。
- 未确认的传感器/阈值、默认关闭的遥测及无执行器边界是否在正文、图示和目录描述中一致；契约测试须分别核对正文和 Fig-61 源文件。

---

## 文件职责

- `code/第9篇_Project/第2章_系统架构设计/test_architecture_contract.py`：离线检查本章元数据、必需语义、Fig-61 源/正文一致、唯一登记、导航、来源和实测声明；在主机进程内执行正文的无 I/O 纯分类函数以验证健康门禁（`HOST_TEST`）；使用篇内唯一模块名以兼容默认 pytest 导入模式，不模拟 UNO Q、Bridge 或持久化后端。
- `book/第9篇_Project/第2章_系统架构设计_从处理器边界到可验证数据流.md`：本章完整正文，按仓库写作规范组织学习目标、架构背景、实验、验证、常见问题和交接。
- `diagrams/uno-q-lab-environment-architecture.mmd`：Fig-61 唯一架构图源；与正文 Mermaid 区块逐字一致。
- `code/第9篇_Project/第2章_系统架构设计/README.md`：本章契约测试入口、运行命令和离线/非实机边界。
- `code/README.md` 与新建的 `code/第9篇_Project/README.md`：代码/测试资源目录导航。
- `SUMMARY.md` 与 `book/第9篇_Project/README.md`：全书与篇内阅读入口及篇章状态。
- `images/第9篇_Project/README.md`、`images/README.md`、`diagrams/README.md`：Fig-61 锚点、来源、许可、状态和源文件登记。
- `resources/references.md`：登记本章实际引用的 Arduino 官方用户手册与数据表；复用已有记录或补充准确条目，不制造重复项。
- 根目录 `README.md`：更新第九篇进度和从 `SUMMARY.md` 实际读取的章节计数，不沿用过期计数。

### Task 1: 先写章节契约测试，再完成正文与 Fig-61

**Files:**
- Create: `code/第9篇_Project/第2章_系统架构设计/test_architecture_contract.py`
- Create: `book/第9篇_Project/第2章_系统架构设计_从处理器边界到可验证数据流.md`
- Create: `diagrams/uno-q-lab-environment-architecture.mmd`
- Create: `code/第9篇_Project/第2章_系统架构设计/README.md`

**Interfaces:**
- Consumes: 经用户审阅的 Chapter 2 设计规格、第1章 `LEM-FR-*`/`LEM-NFR-*` 需求和仓库写作规范。
- Produces: 一篇 `draft` 正文；一份与正文一致的 Fig-61 Mermaid 源；一组离线文档契约测试及纯函数状态门禁 `HOST_TEST`，不承诺目标板或真实后端行为。

- [x] **Step 1: 写失败的正文契约测试。** 使用 `unittest` 和 `pathlib`，测试模块根目录取 `Path(__file__).resolve().parents[3]`。至少实现以下测试：
  - `test_metadata_and_required_sections_match_part_nine`：要求 YAML `part: 9`、`chapter: 2`、`status: draft`、日期格式 `YYYY-MM-DD`，且标题、H1 与篇内编号一致；必需章节按“学习目标→背景/架构→实验→验证→常见问题→延伸阅读/交接”排序。
  - `test_architecture_and_open_decisions_are_explicit`：要求正文同时说明 STM32 采集、Linux 本地应用、Bridge/RPC、方案取舍，并明确传感器、采样周期、阈值和存储/缓存参数未定。
  - `test_data_contract_and_failure_matrix_preserve_unknown_states`：要求出现 `event_time`、`received_at`、来源、单位、质量、事件 ID；失效表逐项覆盖重复、乱序、Bridge 中断、Linux 重启、时钟不可信、存储失败和规则未批准。
  - `test_security_and_evidence_boundaries_stay_closed`：要求正文明确遥测默认关闭、无执行器控制、合成数据标签、UNO Q 实机 `NOT_RUN`；不允许正文把设计/主机测试写成目标板实测。
  - `test_fig61_inline_mermaid_matches_independent_source`：要求只有一个本章 Mermaid 图块、固定锚点 `fig-61-uno-q-lab-environment-architecture`，且其内容与 `.mmd` 源完全一致。
- [x] **Step 2: 运行测试并确认按预期失败。**

  Run: `python -B -m unittest discover -s "code/第9篇_Project/第2章_系统架构设计" -p "test_*.py" -v`

  Expected: 测试模块可导入，但因正文、图源尚不存在而出现断言失败；不得出现语法错误、网络调用或硬件访问。

- [x] **Step 3: 按规格撰写正文。** 采用下列章节序列：学习目标；1. 架构目标与项目约束；2. 候选方案比较；3. 分层组件与数据流；4. 版本化测量/告警契约；5. 失效、恢复与安全边界；6. 本章实验；7. 验证结果与当前证据；8. 常见问题；9. 延伸阅读与交接下一章。所有 JSON 只作为显式 `SYNTHETIC` 示例数据，并声明不是最终 RPC 编码或真实测量。
- [x] **Step 4: 写 Fig-61 Mermaid。** 采用 `flowchart LR` 展示传感器（待选）→ STM32 采集/质量标记→ Bridge/RPC→ Linux 校验/去重/本地记录→规则与告警→本地 UI；加入 Bridge/存储/规则失败转 `UNKNOWN`/降级的路径；将默认关闭的遥测画为虚线可选出口，并显式排除执行器路径。只表达这一条架构关系，不画未确认的接线或云服务。
- [x] **Step 5: 运行正文契约测试并确认通过。**

  Run: `python -B -m unittest discover -s "code/第9篇_Project/第2章_系统架构设计" -p "test_*.py" -v`

  Expected: Task 1 的本章正文/图示契约测试全部通过；尚未覆盖的导航检查在 Task 2 单独新增。

### Task 2: 测试并同步导航、来源与 Fig-61 登记

**Files:**
- Modify: `code/第9篇_Project/第2章_系统架构设计/test_architecture_contract.py`
- Modify: `SUMMARY.md`
- Modify: `book/第9篇_Project/README.md`
- Modify: `code/README.md`
- Create: `code/第9篇_Project/README.md`
- Modify: `images/第9篇_Project/README.md`
- Modify: `images/README.md`
- Modify: `diagrams/README.md`
- Modify: `resources/references.md`
- Modify: `README.md`

**Interfaces:**
- Consumes: Task 1 的正文路径、图号/锚点、来源和证据边界。
- Produces: SUMMARY、篇内入口、资源导航、来源索引和根 README 对同一章/图号的唯一一致登记。

- [x] **Step 1: 先增加导航/登记契约测试。** 新增：
  - `test_summary_part_readmes_and_root_count_link_chapter_once`：要求 `SUMMARY.md`、第九篇 README、代码篇入口各出现一次正确章节链接；根 README 的章节总数等于 SUMMARY 实际章节链接数。
  - `test_fig61_has_one_global_registration_and_backlinks`：扫描全部 `images/**/README.md`，要求恰有一条 `- 图号：Fig-61`，并核验图示锚点、章节回链、源文件、许可及“未渲染”状态。
  - `test_official_sources_are_registered_and_local_links_resolve`：正文引用的官方手册/数据表须能在 `resources/references.md` 找到；本章 Markdown 相对链接目标均存在。
- [x] **Step 2: 运行新增测试并确认导航缺项导致的预期失败。**

  Run: `python -B -m unittest discover -s "code/第9篇_Project/第2章_系统架构设计" -p "test_*.py" -v`

  Expected: Task 1 测试保持通过；新导航/登记断言仅因链接或 Fig-61 尚未登记而失败，不得因测试本身异常失败。
- [x] **Step 3: 同步全书入口。** 在第九篇 README 与 SUMMARY 各追加一条第2章链接；创建代码篇 README 并将其链接加入 `code/README.md`；在根 README 更新第九篇进展及由 SUMMARY 计算的章节总数。
- [x] **Step 4: 同步图示与来源索引。** 在第九篇图片索引登记 Fig-61 唯一锚点、章节链接、Mermaid 源、原创许可和未渲染状态；更新全局图片/图示索引。先复核 `resources/references.md` 中现有官方数据表条目并复用；加入 docs.arduino.cc 用户手册条目或更新对应既有条目，确保无重复来源记录。
- [x] **Step 5: 运行本章契约测试并确认通过。**

  Run: `python -B -m unittest discover -s "code/第9篇_Project/第2章_系统架构设计" -p "test_*.py" -v`

  Expected: 本章全部内容、图示、来源、章节入口、反向链接和全书计数测试通过。

### Task 3: 全仓验证与独立审阅

**Files:**
- Verify: Task 1–2 的所有新建/修改文件。

**Interfaces:**
- Consumes: 本章已完成的正文、章节契约、目录与图示/来源登记。
- Produces: 可复现的本章与全仓测试结果、Markdown 链接/图号检查、独立审阅结果及明确的实机验证边界；所有门禁通过后，按用户要求产生本计划范围内的提交并推送当前分支，不创建 PR。

- [x] **Step 1: 运行全仓测试。**

  Run: `python -m pytest -q`

  Expected: 退出码为 0；记录本次实际 passed、subtests 与 skips 数量，不沿用 README 或旧运行结果。
- [x] **Step 2: 检查 diff 与文档结构。** 运行 `git diff --check`；重新核对 front matter、篇内编号、SUMMARY 链接唯一性、所有受影响的相对 Markdown 链接、Fig-61 全局唯一性及 Mermaid 正文/源一致性。若 `mmdc` 可用，则渲染并目视检查 Fig-61；不可用时保留 `.mmd` 源并将 SVG/视觉检查标为未完成，不制造空 SVG。
- [x] **Step 3: 独立审阅内容。** 审阅覆盖双处理器责任、Bridge 语义、时间/重复/恢复、未批准的阈值/硬件及旧值误判。审阅发现一项 Important：分类器原先未检查来源/主机时钟可信度和持久化确认，可能在持久化失败时返回 `NORMAL`。已先添加失败测试，再修复纯函数健康门禁；修复后本章专项测试 9 项通过，全仓 pytest 为 402 项测试、355 个子测试通过。Mermaid 视觉渲染仍未完成，UNO Q/Bridge 未实测。
- [x] **Step 4: 最后核对状态。** 已核对当前分支和变更范围；只纳入本计划范围内的 18 个文件，既有第1章计划继续保持未暂存；未访问板卡或外部 API。
- [ ] **Step 5: 按用户要求提交并推送。** 在全仓测试、文档检查和独立审阅通过后，只暂存本计划范围内的第2章正文、测试、导航/图示/来源登记，以及本章设计规格和实施计划；使用提交说明 `docs(book): add Part 9 architecture chapter`，推送到当前分支 `codex/part9-project-chapter1`，再用远端分支 SHA 和 `git status --short --branch` 核对提交已同步。不得暂存 `docs/superpowers/plans/2026-09-26-part9-chapter1-implementation-plan.md`。

## Review Checklist

- [x] 第2章编号从 1 起算且 front matter 为 `part: 9`、`chapter: 2`。
- [x] 方案 1 仍是参考架构而非未审批准入现场部署；另两方案的使用条件与限制写明。
- [x] Measurement `event_time` 与 Linux `received_at` 分开；事件来源、单位、质量、去重和告警规则版本可追溯。
- [x] 重复、乱序、Bridge 断连、Linux 重启、时钟不可信、持久化失败和规则缺失不会被映射为无条件正常。
- [x] 没有臆定传感器型号、引脚、接线、采样周期、量程、校准、阈值、保留期或队列容量。
- [x] `SYNTHETIC`/`OBSERVED`/`DESIGN_ONLY`/`HOST_TEST`/`TARGET_OBSERVED` 边界明确；UNO Q 实机仍为 `NOT_RUN`。
- [x] 默认关闭远程遥测，不出现自动物理执行器路径。
- [x] Fig-61 唯一、正文源一致、链接可达；SVG/目视检查按实际工具能力报告。
- [x] `SUMMARY.md` 与根 README 的章节数一致，所有本地链接目标存在。
- [x] 本章契约测试及全仓 pytest 输出均为本次新鲜运行结果。
