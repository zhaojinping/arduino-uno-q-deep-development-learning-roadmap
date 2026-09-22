# Python Bridge 结果账本与状态查询 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 编写第四篇第 4 章《结果账本与状态查询：从返回值到可验证证据》，提供一个只依赖 Python 标准库的 SQLite 请求账本、状态查询收敛模型、可运行示例、测试、Mermaid 图示和完整导航登记。

**Architecture:** 使用 `ledger.py` 保存请求的当前状态投影和追加式事件历史，使用 `reconcile_status.py` 对带身份的查询观察进行匹配、过期判断和 UNKNOWN 收敛。正文把本地模型与真实 Router/Bridge、App Lab、MCU、UNO Q 实机证据严格分开；所有状态名和查询协议均标注为本书教学模型。

**Tech Stack:** Python 3.10 语法、Python 标准库 `sqlite3`/`dataclasses`/`unittest`、Markdown、Mermaid、缓存 Mermaid CLI 11.12.0、Chrome 预览。

**Spec:** `docs/superpowers/specs/2026-09-22-python-bridge-chapter4-design.md`

## Global Constraints

- 章节元数据使用 `part: 4`、`chapter: 4`、`status: draft`，章节编号不沿用其他篇。
- 代码只使用 Python 标准库；示例默认可在 Python 3.10 语法下解析，不宣称已在 UNO Q 镜像运行。
- `SENT` 只代表发送证据，不能代表副作用已应用；`UNKNOWN` 不能因 `NOT_FOUND` 自动关闭。
- 账本更新必须以当前状态条件和事件追加为一个事务，非法转移不得静默覆盖。
- 所有正文中的外部事实和新来源先登记到 `resources/references.md`；本章原创状态名、表名和接口不得伪装成 Arduino 官方 API。
- 完成前必须运行两个示例、完整针对性测试、章节检查、`git diff --check` 和 SVG 预览检查。

---

### Task 1: 建立测试契约和代码目录

**Files:**
- Create: `code/第4篇_PythonBridge/第4章_结果账本与状态查询/README.md`
- Create: `code/第4篇_PythonBridge/第4章_结果账本与状态查询/test_ledger.py`
- Create: `code/第4篇_PythonBridge/第4章_结果账本与状态查询/ledger.py`
- Create: `code/第4篇_PythonBridge/第4章_结果账本与状态查询/reconcile_status.py`

**Interfaces:**
- `ledger.py` 将提供 `State`、`RequestSpec`、`Evidence`、`RequestRecord`、`LedgerEvent`、`LedgerConflict` 和 `Ledger`。
- `reconcile_status.py` 将提供 `Observation`、`Decision`、`reconcile(record, observation, now)`。
- 测试只依赖这些公开名称，不依赖 SQLite 私有连接对象。

- [ ] **Step 1: 写出最小失败测试**

在 `test_ledger.py` 中先固定以下行为：创建记录得到 `PENDING`；`PENDING -> SENT -> UNKNOWN -> APPLIED` 可行；错误的期望状态、非法转移、重复请求 ID 和身份不匹配必须抛出或返回明确的安全决策；关闭并重新打开同一个 SQLite 文件后仍能读取当前记录和事件。

测试夹具使用如下稳定请求：

```python
def make_request():
    return RequestSpec(
        request_id="req-001",
        operation_key="output:led:1",
        operation="set_output",
        payload_digest="sha256:demo",
        generation=1,
        created_at=10.0,
        expires_at=30.0,
    )
```

- [ ] **Step 2: 运行测试确认失败**

运行：

```text
python -B "code/第4篇_PythonBridge/第4章_结果账本与状态查询/test_ledger.py"
```

预期：由于 `ledger.py` 和 `reconcile_status.py` 尚未实现，测试失败；此失败只用于确认测试契约已经被执行。

- [ ] **Step 3: 写代码目录说明**

在 `README.md` 说明本目录的两个示例、测试命令、Python 版本下限、SQLite 本地模型边界，并明确不需要网络或 UNO Q 硬件。

- [ ] **Step 4: 提交测试契约**

运行 `git diff --check`，确认新增文件没有空白错误后提交：

```text
git add "code/第4篇_PythonBridge/第4章_结果账本与状态查询"
git commit -m "test: define Python Bridge result ledger contract"
```

### Task 2: 实现 SQLite 请求账本和状态转移

**Files:**
- Modify: `code/第4篇_PythonBridge/第4章_结果账本与状态查询/ledger.py`
- Test: `code/第4篇_PythonBridge/第4章_结果账本与状态查询/test_ledger.py`

**Interfaces:**
- `State` 是继承 `str, Enum` 的七状态枚举：`PENDING`、`SENT`、`UNKNOWN`、`APPLIED`、`REJECTED`、`EXPIRED`、`NOT_APPLIED_FINAL`。
- `RequestSpec` 保存 `request_id`、`operation_key`、`operation`、`payload_digest`、`generation`、`created_at`、`expires_at`。
- `Evidence` 保存 `kind`、`source`、`observed_at`、`detail`。
- `Ledger.create()` 返回 `RequestRecord`，并写入初始 `None -> PENDING` 事件。
- `Ledger.transition()` 接收 `request_id`、`expected`、`target` 和 `Evidence`，成功时原子更新请求投影并追加事件，冲突时抛出 `LedgerConflict`。
- `Ledger.get()` 和 `Ledger.events()` 返回不可变数据类对象；`Ledger` 支持 `close()`、`__enter__` 和 `__exit__`。

- [ ] **Step 1: 建立 schema 和数据类**

创建 `requests` 表保存身份、状态和最后证据，创建 `request_events` 表保存递增事件序号、前后状态、证据字段和时间；启用外键和显式提交。所有 SQL 参数使用参数绑定，不拼接用户输入。

- [ ] **Step 2: 实现创建、读取和事件映射**

实现 schema 初始化、`RequestSpec`/`RequestRecord`/`LedgerEvent` 的行映射、重复 ID 检查、`create()`、`get()` 和 `events()`。创建事件的 `previous_state` 为 `None`，`next_state` 为 `PENDING`。

- [ ] **Step 3: 实现安全状态转移**

用显式允许表限制合法转移；`transition()` 在事务中先按 `request_id` 和 `expected` 检查当前状态，再更新投影、插入事件并提交。终态不得继续转移，预期状态不匹配必须回滚。

- [ ] **Step 4: 运行账本测试并补齐回归用例**

运行：

```text
python -B "code/第4篇_PythonBridge/第4章_结果账本与状态查询/test_ledger.py"
```

预期：账本持久化、事件顺序、非法转移、重复 ID、状态竞争和重启读取相关测试全部通过；若失败，先修正数据模型或事务边界，再进入查询策略实现。

### Task 3: 实现状态查询与 UNKNOWN 收敛策略

**Files:**
- Modify: `code/第4篇_PythonBridge/第4章_结果账本与状态查询/reconcile_status.py`
- Modify: `code/第4篇_PythonBridge/第4章_结果账本与状态查询/test_ledger.py`

**Interfaces:**
- `Observation` 保存 `request_id`、`operation_key`、`operation`、`payload_digest`、`kind`、`source`、`observed_at`、`authoritative` 和 `detail`。
- `Decision` 保存 `action`、`target` 和 `reason`；`target` 为 `State | None`。
- `reconcile()` 只返回判定，不直接写 SQLite；调用方根据 `Decision.target` 调用 `Ledger.transition()`，保持查询策略与存储层解耦。

- [ ] **Step 1: 写查询判定测试**

覆盖：完整匹配的权威 `APPLIED` 关闭为 `APPLIED`；权威 `REJECTED` 关闭为 `REJECTED`；权威 `NOT_APPLIED_FINAL` 关闭为 `NOT_APPLIED_FINAL`；`NOT_FOUND` 保持 `KEEP_UNKNOWN`；任一身份字段不匹配保持未知；已过期且无权威终态时返回 `STOP_EXPIRED`；过期但有权威 `NOT_APPLIED_FINAL` 时返回 `CLOSE_NOT_APPLIED`。

- [ ] **Step 2: 实现身份匹配和终止判定**

先比较 `request_id`、`operation_key`、`operation` 和 `payload_digest`，任一不匹配即不允许关闭。再按 `authoritative`、观察类型和 `now >= expires_at` 判断 `CLOSE_APPLIED`、`CLOSE_REJECTED`、`CLOSE_NOT_APPLIED`、`KEEP_UNKNOWN` 或 `STOP_EXPIRED`。

核心判定保持纯函数形态：

```python
def reconcile(record, observation, now):
    if not same_identity(record, observation):
        return Decision("KEEP_UNKNOWN", None, "identity mismatch")
    if observation.authoritative and observation.kind == "APPLIED":
        return Decision("CLOSE_APPLIED", State.APPLIED, "authoritative query")
    if observation.kind == "NOT_FOUND":
        return Decision("KEEP_UNKNOWN", None, "not found is not final proof")
    if now >= record.expires_at:
        if observation.authoritative and observation.kind == "NOT_APPLIED_FINAL":
            return Decision("CLOSE_NOT_APPLIED", State.NOT_APPLIED_FINAL, "final evidence")
        return Decision("STOP_EXPIRED", None, "business deadline passed")
    return Decision("KEEP_UNKNOWN", None, "insufficient evidence")
```

- [ ] **Step 3: 运行测试确认查询闭环**

运行同一 `test_ledger.py`，预期账本测试和查询测试全部通过；输出中不得出现“NOT_FOUND 即未执行”或“UNKNOWN 自动重放”的路径。

- [ ] **Step 4: 增加独立演示输出**

让 `reconcile_status.py` 在直接运行时输出以下稳定行，正文将按原样引用：

```text
SIMULATED not_found: KEEP_UNKNOWN
SIMULATED applied: CLOSE_APPLIED
SIMULATED expired_not_applied: CLOSE_NOT_APPLIED
SIMULATED mismatch: KEEP_UNKNOWN
```

### Task 4: 编写第四篇第 4 章和 Fig-27

**Files:**
- Create: `book/第4篇_PythonBridge/第4章_Python_Bridge结果账本与状态查询_从返回值到可验证证据.md`
- Create: `diagrams/uno-q-python-bridge-result-ledger.mmd`
- Modify: `resources/references.md`

**Interfaces:**
- 正文 frontmatter 使用 `part: 4`、`chapter: 4`、`status: draft`、`last_verified: 2026-09-22`、`updated: 2026-09-22`。
- 正文必须包含与 `uno-q-python-bridge-result-ledger.mmd` 完全一致的 Mermaid 代码块，并登记唯一锚点 `fig-27-python-bridge-result-ledger`。
- 新增官方来源至少包括 Python 3.10 `sqlite3` 文档；Arduino Router/App specification 继续引用已登记来源，不重复伪造 API 事实。

- [ ] **Step 1: 写背景、边界和状态语义**

解释“返回值、发送证据、业务账本、设备状态”四层差异，明确 `SENT`、`UNKNOWN`、`NOT_FOUND`、`NOT_APPLIED_FINAL` 的边界，并链接第四篇第 3 章。

- [ ] **Step 2: 写 Fig-27 状态图**

使用 Mermaid `stateDiagram-v2` 表达 `PENDING -> SENT -> UNKNOWN` 以及 `APPLIED`、`REJECTED`、`EXPIRED`、`NOT_APPLIED_FINAL` 终态；在图下注明这是本书教学模型，不是 Arduino 官方协议图。

- [ ] **Step 3: 写两个实验章节**

实验一运行 `ledger.py`，展示创建、发送、未知、关闭、文件重启和事件历史；实验二运行 `reconcile_status.py`，展示四种查询观察判定。每个实验写齐用途、环境、文件位置、依赖、操作步骤、预期输出、故障排查和验证方式。

- [ ] **Step 4: 写接入顺序、验证门槛、FAQ 和小结**

说明真实 App 接入时先持久化请求身份，再记录发送证据，再查询收敛，最后才允许业务层显示最终结果；FAQ 覆盖 SQLite 是否等于可靠落盘、为什么 `NOT_FOUND` 不足够、过期后为什么还能接收迟到权威结果、为什么当前值相同仍不能证明历史请求。

### Task 5: 渲染图示并同步仓库导航

**Files:**
- Create: `images/第4篇_PythonBridge/ch04-fig27-uno-q-python-bridge-result-ledger.svg`
- Create: `code/第4篇_PythonBridge/第4章_结果账本与状态查询/check_chapter.py`
- Modify: `SUMMARY.md`
- Modify: `README.md`
- Modify: `book/第4篇_PythonBridge/README.md`
- Modify: `code/README.md`
- Modify: `images/第4篇_PythonBridge/README.md`
- Modify: `resources/references.md`

**Interfaces:**
- `check_chapter.py` 检查 frontmatter、两个示例输出、Python 3.10 AST、Mermaid 一致性、SVG XML、图示锚点、内部链接和外部来源登记。
- Fig-27 登记包含源图、SVG、正文锚点、渲染日期、Mermaid CLI 版本和预览结果。

- [ ] **Step 1: 渲染 SVG**

使用缓存 Mermaid CLI 11.12.0 和已验证 Chrome 路径生成 SVG，不修改全局依赖；用 `view_image` 或等效预览检查文字、箭头、终态边界和白色背景。

- [ ] **Step 2: 编写章节检查器**

复用第四篇第 3 章检查器的检查风格，但把示例输出、文件路径、图号、元数据和内部链接替换为第 4 章实际内容；脚本失败时使用非零退出码。

- [ ] **Step 3: 同步所有入口**

在 `SUMMARY.md` 和第四篇 README 添加第 4 章；在根 README 的进度、文件清单和验证记录补充本章；在代码、图片和参考资料 README 中登记对应入口和来源。

- [ ] **Step 4: 运行章节检查**

运行：

```text
python -B "code/第4篇_PythonBridge/第4章_结果账本与状态查询/check_chapter.py"
```

预期：元数据、两个示例、Python 3.10 语法、Mermaid、SVG、内部链接和来源登记全部通过。

### Task 6: 总体验证、审查与提交

**Files:**
- Modify: `docs/superpowers/plans/2026-09-22-python-bridge-chapter4-plan.md`

- [ ] **Step 1: 运行两个示例和完整测试**

```text
python -B "code/第4篇_PythonBridge/第4章_结果账本与状态查询/ledger.py"
python -B "code/第4篇_PythonBridge/第4章_结果账本与状态查询/reconcile_status.py"
python -B "code/第4篇_PythonBridge/第4章_结果账本与状态查询/test_ledger.py"
python -B "code/第4篇_PythonBridge/第4章_结果账本与状态查询/check_chapter.py"
git diff --check
```

逐条记录实际输出、测试数量和未完成的 Python 3.10/UNO Q 实机验证，不用“应该通过”替代结果。

- [ ] **Step 2: 进行只读代码审查**

重点复核事务原子性、状态转移白名单、事件历史顺序、身份匹配、过期请求、`NOT_FOUND` 和权威迟到结果；审查意见若要求修改，先补测试再改实现。

- [ ] **Step 3: 更新计划验证记录**

把实际解释器版本、测试数量、章节检查结果、SVG 渲染版本、预览状态和未执行的板端验证写入本计划，勾选已经完成的任务。

- [ ] **Step 4: 提交章节实现**

```text
git add --all
git diff --cached --check
git commit -m "docs: add Python Bridge result ledger chapter"
```

- [ ] **Step 5: 验证提交状态**

运行 `git status --short --branch`、`git log -2 --oneline --decorate` 和 `git diff --check`；只有在输出确认工作树和提交内容符合计划后，才报告本章本地完成。推送动作单独等待用户明确要求。
