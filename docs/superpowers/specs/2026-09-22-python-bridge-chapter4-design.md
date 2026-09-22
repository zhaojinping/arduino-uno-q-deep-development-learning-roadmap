# 第四篇第4章：结果账本与状态查询设计说明

> 状态：设计已获确认，进入计划与实现
>
> 日期：2026-09-22

## 1. 目标与承接

本章承接第四篇第3章的连接代次、幂等键和“先判定、再恢复”原则，回答一个更具体的问题：当 Python Bridge 已经发起请求、返回值丢失或对端重启后，应用如何保存请求事实、查询结果并形成可审计的最终判断。

本章交付一个只依赖 Python 标准库 `sqlite3` 的本地教学模型。它不实现真实 Router、Bridge、App Lab 或 MCU 通信，而是把请求身份、状态转移、观察证据和查询闭环做成可以运行、测试和复盘的最小账本。

## 2. 范围与非目标

### 2.1 本章范围

- 用唯一请求 ID、业务键、操作名、参数摘要和连接代次建立请求身份。
- 将当前状态与不可变的状态转移事件分开保存，支持重启后恢复查询。
- 明确 `PENDING`、`SENT`、`UNKNOWN`、`APPLIED`、`REJECTED`、`EXPIRED` 和 `NOT_APPLIED_FINAL` 的语义及合法转移。
- 用匹配的查询结果关闭 `UNKNOWN`，但不把 `NOT_FOUND` 自动解释为“没有执行”。
- 把过期判断、身份匹配和证据来源写入恢复决策，避免无证据重放副作用动作。
- 为正文、代码、Mermaid 图和检查脚本建立可维护的交叉引用。

### 2.2 非目标

- 不声明 Arduino 官方 API 存在本章自定义的账本表、状态名或查询协议。
- 不连接真实 UNO Q、Router、Bridge、App Lab、STM32 或网络服务。
- 不把本地 SQLite 的通过结果当作并发性能、掉电持久性、文件系统可靠性或硬件验收证据。
- 不在本章引入第三方 ORM、网络客户端或后台服务；需要这些能力时在后续现场联调章节另行设计。

## 3. 设计选择

### 3.1 采用 SQLite 而不是仅内存字典

内存字典适合解释状态机，但无法演示应用重启后的查询。SQLite 随 Python 标准库提供，能够在单文件中保存当前请求记录和追加式事件，足以表达“状态是当前投影，事件是证据历史”这一教学重点，同时不增加包管理负担。

### 3.2 当前投影与事件历史分离

`requests` 表保存每个请求的最新状态、身份摘要、期限和最后证据；`request_events` 表只追加状态变更、来源、摘要和时间。每次合法转移必须原子地更新当前投影并追加事件；状态冲突或身份不匹配不得静默覆盖。

### 3.3 查询结果必须经过身份匹配

查询观察只有在 `request_id`、业务键、操作名和参数摘要均匹配时，才允许关闭 `UNKNOWN`。只凭“当前值相同”、`NOT_FOUND` 或一条没有身份字段的成功响应，不足以证明某个历史副作用请求已经应用。

## 4. 数据模型与状态机

### 4.1 请求身份

每条请求至少包含：

| 字段 | 作用 | 是否可改变 |
| --- | --- | --- |
| `request_id` | 一次业务请求的持久身份 | 创建后不可改变 |
| `operation_key` | 跨重试保持不变的幂等业务键 | 创建后不可改变 |
| `operation` | 操作名，例如 `set_output` | 创建后不可改变 |
| `payload_digest` | 规范化参数摘要，防止同键不同参数 | 创建后不可改变 |
| `generation` | 发起时连接代次，辅助隔离旧响应 | 仅由新请求记录携带 |
| `expires_at` | 业务期限，使用可持久化的 UTC 时间 | 创建后不可改变 |

### 4.2 状态转移

账本允许以下教学模型转移：

```text
PENDING -> SENT -> APPLIED
                  ├-> REJECTED
                  ├-> UNKNOWN -> APPLIED
                  │           ├-> REJECTED
                  │           └-> NOT_APPLIED_FINAL
                  └-> EXPIRED
PENDING -> EXPIRED
```

`APPLIED`、`REJECTED`、`EXPIRED` 和 `NOT_APPLIED_FINAL` 是终态。`UNKNOWN` 不是成功，也不是失败；它表示请求可能已经越过副作用边界，但当前证据不足。恢复流程可以在相同业务键下重新查询，但不得因为 `NOT_FOUND` 就直接转为 `NOT_APPLIED_FINAL`。

### 4.3 状态转移约束

- 新记录只能从 `PENDING` 开始。
- `SENT` 只表示发送证据已经写入账本，不表示对端已经应用。
- `UNKNOWN` 必须附带“响应丢失、连接中断或查询证据不足”等原因。
- 只有身份完整且来源受信的查询结果才能把 `UNKNOWN` 转为终态。
- 过期会阻止新的发送或重放；迟到的权威观察仍可将 `UNKNOWN` 收敛到 `APPLIED`、`REJECTED` 或 `NOT_APPLIED_FINAL`，但必须保留事件时间和观察来源。
- 任何非法转移都应返回可测试的冲突，而不是覆盖当前状态。

## 5. 代码接口

代码目录为 `code/第4篇_PythonBridge/第4章_结果账本与状态查询/`，由四个职责清晰的文件组成：

- `ledger.py`：SQLite schema、请求身份、状态转移、事件追加和重启后读取。
- `reconcile_status.py`：查询观察的身份匹配、期限判断和 `UNKNOWN` 收敛决策。
- `test_ledger.py`：状态机、事件顺序、重启、身份冲突、过期与查询收敛测试。
- `check_chapter.py`：元数据、代码示例、Mermaid、SVG、内部链接和来源登记检查。

约定的最小接口如下：

```python
Ledger(path: str | Path)
Ledger.create(request: RequestSpec) -> RequestRecord
Ledger.transition(request_id: str, expected: State, target: State, evidence: Evidence) -> RequestRecord
Ledger.get(request_id: str) -> RequestRecord | None
Ledger.events(request_id: str) -> tuple[LedgerEvent, ...]
reconcile(record: RequestRecord, observation: Observation, now: float) -> Decision
```

示例默认使用 `:memory:`，另提供临时文件重启实验。实际生产系统还需要文件权限、备份、并发写策略、时钟治理和掉电测试，这些不在本章验收范围内。

## 6. 验证与交付门槛

本章完成的最低证据包括：

1. `ledger.py` 和 `reconcile_status.py` 在 Python 3.10 语法下可解析，并能在当前 Python 解释器运行。
2. 测试覆盖合法/非法状态转移、事件追加顺序、重启读取、身份不匹配、`NOT_FOUND`、可信 `NOT_APPLIED_FINAL` 和迟到权威成功。
3. Mermaid 源图与正文内嵌版本一致，SVG 经过实际渲染和预览检查。
4. 正文中的代码说明、内部链接、图示登记和参考资料索引通过章节检查脚本。
5. 验证结果明确区分“本地模型通过”和“Router/Bridge、App Lab、MCU、UNO Q 实机尚未验证”。

## 7. 后续交接

本章完成后，第四篇将拥有消息模型、并发任务、连接恢复和结果账本四个连续层次。下一步可在第五篇 App Lab 中把本地账本接口映射到真实应用入口，但必须先重新核对官方接口、目标镜像和设备端查询能力，不能直接把本章模拟协议当作 UNO Q 现成接口。
