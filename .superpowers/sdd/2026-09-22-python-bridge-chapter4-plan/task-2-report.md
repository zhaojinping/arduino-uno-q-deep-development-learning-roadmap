# Task 2 执行报告：SQLite 请求账本和状态转移

## 范围

仅实现 `code/第4篇_PythonBridge/第4章_结果账本与状态查询/ledger.py` 及其台账契约测试；未修改 `reconcile_status.py`、章节正文、导航或任何 Router、Bridge、网络及硬件调用。

## 实现内容

- 使用 Python 标准库 `sqlite3` 创建 `requests` 当前投影表和 `request_events` 追加式历史表。
- 启用 SQLite 外键，使用参数化 SQL、请求 ID 唯一约束，以及每个请求递增的事件序列。
- `create()` 以 `PENDING` 创建请求并写入 `None -> PENDING` 初始事件。
- `transition()` 在同一 `BEGIN IMMEDIATE` 事务中读取当前状态、校验 expected/目标状态和 `SENT` 的 `send` 证据、更新投影并追加事件；异常回滚。
- 实现 `get()`、`events()`、安全关闭、上下文管理和重启后持久化读取。
- 保留公开类型和状态词汇；`reconcile_status.py` 仍为 Task 3 的 `NotImplementedError` 骨架。
- 添加身份与初始事件、未知 ID 空结果、无效 `SENT` 证据不改变投影/历史的真实 SQLite 契约测试。
- 保留可直接执行的无网络、无硬件演示。

## TDD 证据

父任务的完整基线共有 12 项测试：10 项 SQLite 台账测试和 2 项 Task 3 调和测试。实现前的台账骨架会以 `NotImplementedError` 阻塞台账行为；两项调和测试保留给 Task 3，不计入本任务的台账实现范围。

## 验证

| 命令 | 结果 |
| --- | --- |
| `python -B "code/第4篇_PythonBridge/第4章_结果账本与状态查询/test_ledger.py"` | 13 项 SQLite 台账测试通过；2 项 `reconcile()` 测试按任务边界保留为 `NotImplementedError`。 |
| `python -B "code/第4篇_PythonBridge/第4章_结果账本与状态查询/ledger.py"` | 退出码 0，输出精确为 3 行 `SIMULATED` 状态/事件计数。 |
| `git diff --check` | 退出码 0，无空白错误。 |

演示输出：

```text
SIMULATED current=UNKNOWN events=3
SIMULATED restart_state=UNKNOWN events=3
SIMULATED applied=APPLIED events=4
```

## 提交

- `6227514911e464ea8906a49b03db240c34469069` — `feat: implement Python Bridge result ledger`

## 已知边界

完整测试脚本的两个调和测试仍失败，原因是 `reconcile_status.py` 的 Task 3 骨架有意抛出 `NotImplementedError`；本任务未削弱、删除或实现这些测试。

## 审查修复补充

### 补充的测试覆盖

- 在隔离的临时 SQLite 文件上创建 `request_events` 插入触发器，使有效的 `PENDING -> SENT` 转移在追加事件时以 `RAISE(ABORT, ...)` 失败。测试使用公开 `Ledger` API 比较失败前后的 `RequestRecord`（含 `state` 和 `updated_at`）与完整事件元组，证明事务回滚同时保留投影和历史。
- 使用参数化子测试覆盖全部 10 条允许转移：`PENDING -> SENT/EXPIRED`、`SENT -> UNKNOWN/APPLIED/REJECTED/EXPIRED`、`UNKNOWN -> APPLIED/REJECTED/EXPIRED/NOT_APPLIED_FINAL`。
- 显式验证 `APPLIED`、`REJECTED`、`EXPIRED` 和 `NOT_APPLIED_FINAL` 均拒绝后续转移。
- 保留两项 Task 3 调和骨架测试，未修改 `reconcile_status.py`。

### 修正与复核

- 父任务完整基线为 12 项测试：10 项 SQLite 台账测试和 2 项 Task 3 调和测试。
- 本轮后完整测试脚本共 15 项：13 项 SQLite 台账测试通过，2 项 Task 3 调和测试按既定边界以 `NotImplementedError` 报错。
- 触发器测试首次在 Windows 临时目录清理时发现独立 SQLite 连接未关闭；已在测试中显式关闭该连接，未修改账本生产事务代码。

## 复审报告更正

- 将先前误写为“10 项测试”的父任务基线更正为完整 12 项，并明确拆分为 10 项 SQLite 台账测试与 2 项 Task 3 调和测试。
- `git diff --check`：退出码 0，无空白错误。
