---
title: Python Bridge 结果账本与状态查询：从返回值到可验证证据
part: 4
chapter: 4
status: draft
last_verified: 2026-09-22
updated: 2026-09-22
prerequisites: 第四篇第1～3章、第三篇第8章
tags: Python Bridge, 结果账本, 状态查询, UNKNOWN, SQLite, 证据
---

# 第4章 Python Bridge 结果账本与状态查询：从返回值到可验证证据

## 学习目标

读完本章并完成实验后，读者应能够：

- 区分 Arduino UNO Q 请求的传输返回值、发送证据、本地持久账本与设备侧结果。
- 用稳定请求身份关联当前投影和追加式事件，说明关闭并重新打开数据库后保留了什么。
- 解释七种请求状态，拒绝把 `NOT_FOUND` 当作最终未执行的证明。
- 使用纯函数判定查询观察，再由调用方把允许的状态转移写入账本。
- 复现两个本地实验和 22 项测试，准确记录模型验证与实机验收的边界。

本章承接[第四篇第3章：连接复用与请求恢复](./第3章_Python_Bridge连接复用与请求恢复_从断线到可判定结果.md)。第三章用连接代次隔离旧事件，并提出“先判定、再恢复”；本章把待判定请求和证据保存下来，使应用重新启动后仍有可追溯的查询依据。

## 背景与边界

假设 Python 已发送一次“设置输出目标值”请求，微控制器（Microcontroller Unit，MCU）执行了动作，但响应丢失。应用随后退出并重新启动。如果它只记得最后一次异常，就可能把原动作当成未发送，再执行一遍。结果账本要保存的是“哪一个请求、可能走到了哪里、依据是什么”，而不是把异常换成一个成功布尔值。

本章的状态名、表名 `requests` 与 `request_events`、请求信封 `RequestSpec`、观察类型 `Observation.kind`、决策动作 `Decision.action`，全部是本书的教学模型，**不是 Arduino 官方 API 字段或内置查询协议**。`Ledger`、`reconcile()` 也都是本仓库的原创接口。

本地模型只验证状态语义、事务行为和证据分类。它不证明 Router/Bridge 可用性、App Lab 行为、MCU 执行、设备侧状态查询支持、掉电时文件系统持久性、并发性能或 UNO Q 硬件运行。两个实验均标记为 `SIMULATED`，不访问网络和开发板。

## 1. 返回值为什么不是最终证据

### 1.1 四层信息回答不同问题

| 信息层 | 能回答的问题 | 不能据此推出的结论 |
| --- | --- | --- |
| 传输返回值 | 本次调用收到什么值或异常？ | 正常返回不必然等于物理动作完成；超时不证明未执行 |
| 发送证据 | 请求是否交给了某个明确的发送边界？ | `SENT` 不等于 `APPLIED`，也不等于 MCU 已接收 |
| 持久请求账本 | 应用记住哪些身份、状态和证据，重开后能否读取？ | 本地记录存在不等于远端事实真实或已经硬件验收 |
| 设备侧状态或结果记录 | 提供方能否证明该历史请求的结果？ | 当前值相同或查无记录，不必然能归因到原请求 |

收到返回值后，还要解释其契约：它表示接受、排队、应用，还是一次读取？只有满足约定验收条件、与原身份匹配且来源可信的结果，才可能成为终态证据。账本保存结论及其依据，不会提升原始证据的可信等级。

### 1.2 三个容易误判的时刻

第一，发送接口返回以后，接收方可能还没执行，因此只能保存发送证据。第二，等待响应超时以后，接收方可能已经执行，因此进入 `UNKNOWN`；它既不是成功，也不是失败。第三，重启后查询得到 `NOT_FOUND`，可能是缓存失效、查询了错误实例、结果尚未同步，或者旧请求仍在途中，不能据此证明没有执行。

`NOT_APPLIED_FINAL` 要求更强：负责该动作的提供方能权威确认最终未应用，并且旧尝试已经被阻止继续执行。仅给观察加上一个 `authoritative=True` 标签不能创造这种事实，实际接入时必须由受信适配层依据协议和来源验证后设置它。

## 2. 请求身份、当前投影与事件历史

### 2.1 请求身份在创建后保持稳定

`RequestSpec` 是请求信封；本章实际代码包含以下七个字段：

| 字段 | 用途与边界 |
| --- | --- |
| `request_id` | 本条请求的持久身份；数据库主键，重复创建会冲突 |
| `operation_key` | 业务动作的幂等键，跨查询与恢复保持不变；本地表没有为它建立唯一约束 |
| `operation` | 操作名，例如教学标签 `set_output`；不是对官方同名方法的声明 |
| `payload_digest` | 规范化参数摘要，区分同键不同参数；示例的 `sha256:demo` 是标签，不是真实摘要 |
| `generation` | 发起请求时的连接代次，用于追溯旧会话；不等于 MCU 启动次数 |
| `created_at` | 请求创建时间，与记录和观察时间分开保留 |
| `expires_at` | 业务期限；真实持久记录应使用约定的协调世界时（UTC）时间基准 |

第三章的 `request_id` 用于标识调用尝试；本章把该请求记录持久化，重启后查询同一记录不能另换 ID。若未来按第三章的恢复契约创建新尝试，应创建新记录并关联原业务键，不能覆盖原记录。

本章查询匹配的四元组是 `request_id`、`operation_key`、`operation`、`payload_digest`；`generation` 保留在请求中，但 `Observation` 没有这个字段。因此历史查询可以跨连接代次收敛，实时响应仍应按[第三章的连接代次规则](./第3章_Python_Bridge连接复用与请求恢复_从断线到可判定结果.md#3-连接代次与业务身份)隔离。真实多设备系统还需在适配层校验目标、启动标识和契约版本，本地四元组不提供这些能力。

默认记账时间来自 `time.time()`；实验显式传入 `10.0`、`30.0` 等同一模拟时间轴上的值，不能把这些值复制成现场期限。持久期限需要统一时间基准和时钟校正策略，不能沿用不兼容的单调时钟起点。相关时间边界见[Python 3.10 time](https://docs.python.org/3.10/library/time.html)及第三章。

### 2.2 当前投影回答“现在”，事件历史回答“如何走到现在”

`requests` 保存最新状态、完整请求身份、`updated_at` 和最近一次转移的证据字段。它是便于查询的当前投影。`request_events` 保存按请求递增的 `sequence`、前后状态、证据及 `recorded_at`，通过复合主键 `(request_id, sequence)` 标识事件。

创建请求同时追加 `None → PENDING` 事件。每次合法转移追加一条新事件，不覆盖旧事件；因此实验到达 `UNKNOWN` 时有 3 条事件，收敛到 `APPLIED` 后有 4 条。这里的“追加式”是 `Ledger` 公共接口的行为约束，不是防篡改存储或数据库管理员无法删除的保证。

`get()` 返回 `RequestRecord(request, state, updated_at)`，不直接返回表里的最后证据字段。要查看来源及原因，读取 `events()` 返回的 `LedgerEvent` 元组，其中的 `Evidence` 包含 `kind`、`source`、`observed_at`、`detail`。观察发生时间和本地记账时间应分别保存，迟到证据尤其需要这一区分。

记录、事件、观察和决策使用 `@dataclass(frozen=True)`，防止一般代码直接赋值修改字段；它模拟不可变对象，不负责验证字段类型或提供数据库防篡改能力。[Python 3.10 dataclasses](https://docs.python.org/3.10/library/dataclasses.html)

### 2.3 查不到记录与记录状态未知不是一回事

本地 `get("missing")` 返回 `None`，`events("missing")` 返回空元组；这是本地账本不存在该 ID。远端观察的 `NOT_FOUND` 则是查询结果类型。二者都不能反推物理世界一定没有发生动作。

重启时应打开原数据库、读取原请求和历史，再安排查询。当前接口没有自动扫描未决请求、后台恢复或自动发送功能；管理层需要保存待查 ID，或另行实现未决记录枚举。

## 3. 状态机与安全收敛

### 3.1 七种状态及批准设计中的主路径

| 状态 | 语义 | 是否终态 |
| --- | --- | --- |
| `PENDING` | 已建立本地请求记录，尚未登记发送证据 | 否 |
| `SENT` | 已登记发送边界证据；尚不能证明应用结果 | 否 |
| `UNKNOWN` | 可能发生了副作用，当前证据不足 | 否 |
| `APPLIED` | 按应用契约确认请求已经应用 | 是 |
| `REJECTED` | 获得与请求匹配的最终拒绝结论 | 是 |
| `EXPIRED` | 请求在业务管理层以过期关闭；不证明最终未应用 | 是 |
| `NOT_APPLIED_FINAL` | 权威确认最终未应用，旧尝试不能再执行 | 是 |

批准设计给出的主路径如下：

~~~text
PENDING -> SENT -> APPLIED
                  ├-> REJECTED
                  ├-> UNKNOWN -> APPLIED
                  │           ├-> REJECTED
                  │           └-> NOT_APPLIED_FINAL
                  └-> EXPIRED
PENDING -> EXPIRED
~~~

终态没有出边，不能重新改成 `PENDING`。底层实现还允许 `UNKNOWN → EXPIRED`，这是比上述主路径更宽的存储能力；**本章的查询策略不会选择这条边**。它返回 `STOP_EXPIRED` 时的 `target` 为 `None`，保留 `UNKNOWN`，以便迟到权威证据继续收敛。若调用方直接把记录写成终态 `EXPIRED`，之后便不能再用 `transition()` 改成 `APPLIED`。

`SENT → EXPIRED` 也只是业务关闭，不代表“从未执行”。如果发送结果仍不确定、还需等待历史证据，应进入并保留 `UNKNOWN`。不能把终态 `EXPIRED` 与“过期后停止发送，但结果仍未知”混为一谈。

### 3.2 查询边界先校验身份，再接受终态证据

`reconcile(record, observation, now)` 是无输入输出副作用的纯判定函数：它不发送查询、不写 SQLite、不重放动作。实际顺序如下：

| 检查顺序 | 条件 | 返回动作与目标 |
| --- | --- | --- |
| 1 | `now` 不是有限的整数或浮点数，或是布尔值 | 抛出 `ValueError` |
| 2 | 记录不是 `UNKNOWN` | `KEEP_UNKNOWN`，`target=None`；原状态不变 |
| 3 | 任一身份字段不是非空字符串，或四元组不匹配 | `KEEP_UNKNOWN`，`target=None` |
| 4 | 观察类型为 `NOT_FOUND`，无论是否标记权威 | `KEEP_UNKNOWN`，`target=None` |
| 5 | 身份匹配，`authoritative is True`，类型为三个受支持终态之一 | `CLOSE_APPLIED`、`CLOSE_REJECTED` 或 `CLOSE_NOT_APPLIED`，目标为相应终态 |
| 6 | 其余观察且 `now >= expires_at` | `STOP_EXPIRED`，`target=None` |
| 7 | 其余观察且未到期限 | `KEEP_UNKNOWN`，`target=None` |

`CLOSE_NOT_APPLIED` 对应 `State.NOT_APPLIED_FINAL`，不是新增的第八种状态。`KEEP_UNKNOWN` 是动作名称；即使传入已终结记录，该返回值也不会把它改成未知。

身份不匹配和 `NOT_FOUND` 的分支早于过期判断，所以过期的此类观察仍返回 `KEEP_UNKNOWN`，而不是 `STOP_EXPIRED`。调用方必须独立执行“过期禁止发送或重放”的准入规则；不能把未收到 `STOP_EXPIRED` 当作可发送许可。

### 3.3 过期约束未来动作，不抹去已经发生的事实

期限为 `30.0`、当前时间为 `31.0` 时，匹配且权威的 `APPLIED` 仍返回 `CLOSE_APPLIED`；匹配且权威的 `NOT_APPLIED_FINAL` 仍返回 `CLOSE_NOT_APPLIED`。这两种决策记录的是既有结果，不启动新动作。

相比[第三章的恢复策略](./第3章_Python_Bridge连接复用与请求恢复_从断线到可判定结果.md#6-请求恢复先判定再决定是否发送)，本章只做结果收敛，不返回 `RESUBMIT_SAME_KEY`。即使最终未应用，也不能从本章决策中推导出自动重放授权。

调用方应在完成来源校验后，把观察映射成 `Evidence`，保留来源、观察时间和摘要；只有 `Decision.target` 非空时，才以 `expected=State.UNKNOWN` 调用 `transition()`。如果期间记录已改变，`LedgerConflict` 会阻止覆盖；应重新读取并复核，而不是跳过预期状态检查。对于 `target=None`，当前示例不追加事件；若需审计每次无结论查询，应由集成层另存观察日志，不能声称现有 `request_events` 已收集全部查询。

## 4. Fig-27：结果账本与状态查询闭环

<a id="fig-27-python-bridge-result-ledger"></a>

~~~mermaid
stateDiagram-v2
    direction TB
    [*] --> PENDING
    PENDING --> SENT: send evidence recorded
    PENDING --> EXPIRED: deadline closes unsent request
    SENT --> APPLIED: matched final evidence
    SENT --> REJECTED: matched final rejection
    SENT --> UNKNOWN: response lost or uncertain
    SENT --> EXPIRED: explicit expiry closure
    UNKNOWN --> QUERY: query original identity
    state QUERY <<choice>>
    QUERY --> UNKNOWN: NOT_FOUND or identity mismatch
    QUERY --> UNKNOWN: insufficient proof / KEEP_UNKNOWN
    QUERY --> UNKNOWN: expired without final proof / STOP_EXPIRED
    QUERY --> APPLIED: authoritative APPLIED
    QUERY --> REJECTED: authoritative REJECTED
    QUERY --> NOT_APPLIED_FINAL: authoritative final non-application
    note right of UNKNOWN
        Expiry blocks send and replay.
        STOP_EXPIRED leaves UNKNOWN open.
        Late authoritative proof can still close it.
    end note
    note left of QUERY
        Decision boundary, not a ledger state.
        Match identity before accepting final proof.
        Caller commits the chosen transition.
    end note
    APPLIED --> [*]
    REJECTED --> [*]
    EXPIRED --> [*]
    NOT_APPLIED_FINAL --> [*]
~~~

图 4-4（Fig-27）：请求状态、查询观察判定与结果收敛。图源为[Mermaid 文件](../../diagrams/uno-q-python-bridge-result-ledger.mmd)，[导出 SVG（预留入口）](../../images/第4篇_PythonBridge/ch04-fig27-uno-q-python-bridge-result-ledger.svg) 将由后续 Task 5 渲染并预览，本任务没有生成或验证 SVG。此图依据[已登记的官方资料](../../resources/references.md)原创设计，不是 Arduino 官方协议图；只链接外部资料，不复制其图表。

图中的 `QUERY` 是临时判定边界，不是数据库中的第八种状态；它将实验二的判定与调用方负责的写入组合展示。`NOT_FOUND` 返回 `UNKNOWN`；期限到达阻止重放，但保留迟到权威证据入口。图展示批准设计和查询策略的主路径；底层额外允许的 `UNKNOWN → EXPIRED` 及其不可逆关闭含义见第 3.1 节。

## 5. SQLite 实现：把事实保存下来

### 5.1 一个事务同时改变投影和事件

`Ledger.create()` 在同一事务里插入请求和初始事件；`transition()` 在 `with connection:` 内执行 `BEGIN IMMEDIATE`，读取当前状态、校验 `expected` 和允许转移表，然后更新投影并追加下一序号事件。参数使用占位符绑定。

Python 的连接上下文管理器在正常退出时提交已打开事务，异常时回滚；它本身既不会隐式开启事务，也不会关闭连接。因此源码显式开始事务，并由 `close()` 或 `Ledger` 自身的上下文管理器关闭连接。[Python 3.10 sqlite3](https://docs.python.org/3.10/library/sqlite3.html)

这保证本地事务内两项写入共同成功或回滚。测试通过故意让第二条事件插入失败，验证已执行的投影更新也被回滚；它没有模拟真实掉电。

### 5.2 存储约束不等于证据验证

`transition()` 拒绝不存在的请求、错误的预期状态、未知状态值和非法转移；进入 `SENT` 还要求 `Evidence.kind == "send"`。但它不会验证证据来源，也不检查当前时间是否超过期限。除发送证据外，它没有强制每次转移都提供证据，更不会替调用方判断 `APPLIED` 是否真实。

因此集成层必须为 `UNKNOWN` 保存响应丢失、断线或证据不足的原因，并只把验证后的最终观察交给账本。实验一直接写入模拟权威证据用于展示存储过程；实验二演示独立的判定步骤，两者尚未组成真实通信执行器。

### 5.3 重开文件保留记录，但不跨越硬件证据边界

`Ledger(database)` 必须显式提供路径。`Ledger(":memory:")` 可用于不需要持久化的场景；实验一实际使用临时文件，在同一个进程中关闭并重新打开连接，模拟应用恢复时重新读取账本。它不是杀进程重启或断电恢复测试，临时目录在实验结束时自动清理。

本地数据库提交与 MCU 执行动作之间没有共同事务。尤其在“请求已发送、发送证据尚未落账”时进程退出，数据库可能仍显示 `PENDING`，不能据此认定没有发送。真实发送器须按第三章的原则先持久化发送意图，并保守处理这个不确定窗口；本示例没有实现该发送器。

数据库文件权限、备份、时钟治理、多进程写入策略、崩溃恢复和设备侧去重都需要单独设计与实测。本地 SQLite 不是硬件验收证据。

## 6. 实验一：账本持久化与事件历史

代码保存为[ledger.py](../../code/第4篇_PythonBridge/第4章_结果账本与状态查询/ledger.py)。下面完整收录当前源文件，保留其原始代码；维护时必须同步源文件与正文。

**代码说明**

- 用途：创建请求，保存发送与响应丢失证据，重开临时数据库并追加模拟成功证据。
- 运行环境：Python 3.10+，本地单进程；不需要开发板。
- 文件位置：`code/第4篇_PythonBridge/第4章_结果账本与状态查询/ledger.py`。
- 依赖：标准库 `sqlite3`、`tempfile`、`time`、`dataclasses`、`enum`、`pathlib`，无第三方包。
- 操作步骤：在仓库根目录执行 `python -B "code/第4篇_PythonBridge/第4章_结果账本与状态查询/ledger.py"`；仅创建临时数据库，退出时自动清理，不写开发板或现有业务账本。
- 预期输出：下方三行 `SIMULATED`，依次为未知状态 3 条事件、重开后仍为未知且 3 条事件、应用成功后 4 条事件。
- 故障排查：导入失败先核对解释器和标准库；`unable to open database file` 时检查临时目录权限；Windows 删除临时目录失败时检查是否仍有连接或其他进程打开文件。遇到锁或 I/O 异常先停止实验并检查原因，不删除业务数据库来规避错误。
- 验证方式：逐行比较输出，并执行本章 `test_ledger.py` 检查重开、事件顺序、非法转移和事务回滚。

~~~python
"""SQLite-backed local result ledger for Python Bridge requests."""
from __future__ import annotations

import sqlite3
import tempfile
import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class State(str, Enum):
    PENDING = "PENDING"
    SENT = "SENT"
    UNKNOWN = "UNKNOWN"
    APPLIED = "APPLIED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"
    NOT_APPLIED_FINAL = "NOT_APPLIED_FINAL"


@dataclass(frozen=True)
class RequestSpec:
    request_id: str
    operation_key: str
    operation: str
    payload_digest: str
    generation: int
    created_at: float
    expires_at: float


@dataclass(frozen=True)
class Evidence:
    kind: str
    source: str
    observed_at: float | None = None
    detail: str = ""


@dataclass(frozen=True)
class RequestRecord:
    request: RequestSpec
    state: State
    updated_at: float


@dataclass(frozen=True)
class LedgerEvent:
    request_id: str
    from_state: State | None
    to_state: State
    evidence: Evidence | None
    recorded_at: float


class LedgerConflict(Exception):
    """Raised when a ledger operation cannot be applied safely."""


_ALLOWED_TRANSITIONS = {
    State.PENDING: {State.SENT, State.EXPIRED},
    State.SENT: {State.UNKNOWN, State.APPLIED, State.REJECTED, State.EXPIRED},
    State.UNKNOWN: {
        State.APPLIED,
        State.REJECTED,
        State.EXPIRED,
        State.NOT_APPLIED_FINAL,
    },
}


class Ledger:
    """Append-only event ledger with a SQLite current-state projection."""

    def __init__(self, database: str | Path) -> None:
        self.database = Path(database)
        self._connection: sqlite3.Connection | None = sqlite3.connect(str(self.database))
        self._connection.execute("PRAGMA foreign_keys = ON")
        self._initialize_schema()

    def create(self, request: RequestSpec, *, now: float | None = None) -> RequestRecord:
        recorded_at = time.time() if now is None else now
        connection = self._require_connection()
        try:
            with connection:
                connection.execute("BEGIN IMMEDIATE")
                connection.execute(
                    """
                    INSERT INTO requests (
                        request_id, operation_key, operation, payload_digest, generation,
                        created_at, expires_at, state, updated_at,
                        evidence_kind, evidence_source, evidence_observed_at, evidence_detail
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, NULL, NULL, NULL, NULL)
                    """,
                    (
                        request.request_id,
                        request.operation_key,
                        request.operation,
                        request.payload_digest,
                        request.generation,
                        request.created_at,
                        request.expires_at,
                        State.PENDING.value,
                        recorded_at,
                    ),
                )
                connection.execute(
                    """
                    INSERT INTO request_events (
                        request_id, sequence, from_state, to_state,
                        evidence_kind, evidence_source, evidence_observed_at, evidence_detail,
                        recorded_at
                    ) VALUES (?, 1, NULL, ?, NULL, NULL, NULL, NULL, ?)
                    """,
                    (request.request_id, State.PENDING.value, recorded_at),
                )
        except sqlite3.IntegrityError as error:
            raise LedgerConflict("request ID already exists") from error
        return RequestRecord(request, State.PENDING, recorded_at)

    def transition(
        self,
        request_id: str,
        *,
        expected: State,
        target: State,
        evidence: Evidence | None = None,
        now: float | None = None,
    ) -> RequestRecord:
        recorded_at = time.time() if now is None else now
        connection = self._require_connection()
        try:
            expected_state = State(expected)
            target_state = State(target)
        except ValueError as error:
            raise LedgerConflict("unknown state") from error

        with connection:
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute(
                "SELECT * FROM requests WHERE request_id = ?", (request_id,)
            ).fetchone()
            if row is None:
                raise LedgerConflict("request does not exist")

            current_state = State(row["state"])
            if current_state != expected_state:
                raise LedgerConflict("request is not in the expected state")
            if target_state not in _ALLOWED_TRANSITIONS.get(current_state, set()):
                raise LedgerConflict("state transition is not allowed")
            if target_state == State.SENT and (evidence is None or evidence.kind != "send"):
                raise LedgerConflict("SENT requires send evidence")

            sequence = connection.execute(
                "SELECT COALESCE(MAX(sequence), 0) + 1 FROM request_events WHERE request_id = ?",
                (request_id,),
            ).fetchone()[0]
            evidence_values = self._evidence_values(evidence)
            connection.execute(
                """
                UPDATE requests
                SET state = ?, updated_at = ?, evidence_kind = ?, evidence_source = ?,
                    evidence_observed_at = ?, evidence_detail = ?
                WHERE request_id = ?
                """,
                (target_state.value, recorded_at, *evidence_values, request_id),
            )
            connection.execute(
                """
                INSERT INTO request_events (
                    request_id, sequence, from_state, to_state,
                    evidence_kind, evidence_source, evidence_observed_at, evidence_detail,
                    recorded_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    request_id,
                    sequence,
                    current_state.value,
                    target_state.value,
                    *evidence_values,
                    recorded_at,
                ),
            )
        return RequestRecord(self._request_from_row(row), target_state, recorded_at)

    def get(self, request_id: str) -> RequestRecord | None:
        row = self._require_connection().execute(
            "SELECT * FROM requests WHERE request_id = ?", (request_id,)
        ).fetchone()
        if row is None:
            return None
        return RequestRecord(self._request_from_row(row), State(row["state"]), row["updated_at"])

    def events(self, request_id: str) -> tuple[LedgerEvent, ...]:
        rows = self._require_connection().execute(
            "SELECT * FROM request_events WHERE request_id = ? ORDER BY sequence", (request_id,)
        ).fetchall()
        return tuple(self._event_from_row(row) for row in rows)

    def close(self) -> None:
        if self._connection is not None:
            self._connection.close()
            self._connection = None

    def __enter__(self) -> Ledger:
        return self

    def __exit__(self, exc_type: object, exc_value: object, traceback: object) -> None:
        self.close()

    def _initialize_schema(self) -> None:
        connection = self._require_connection()
        connection.row_factory = sqlite3.Row
        with connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS requests (
                    request_id TEXT PRIMARY KEY,
                    operation_key TEXT NOT NULL,
                    operation TEXT NOT NULL,
                    payload_digest TEXT NOT NULL,
                    generation INTEGER NOT NULL,
                    created_at REAL NOT NULL,
                    expires_at REAL NOT NULL,
                    state TEXT NOT NULL,
                    updated_at REAL NOT NULL,
                    evidence_kind TEXT,
                    evidence_source TEXT,
                    evidence_observed_at REAL,
                    evidence_detail TEXT
                );
                CREATE TABLE IF NOT EXISTS request_events (
                    request_id TEXT NOT NULL,
                    sequence INTEGER NOT NULL,
                    from_state TEXT,
                    to_state TEXT NOT NULL,
                    evidence_kind TEXT,
                    evidence_source TEXT,
                    evidence_observed_at REAL,
                    evidence_detail TEXT,
                    recorded_at REAL NOT NULL,
                    PRIMARY KEY (request_id, sequence),
                    FOREIGN KEY (request_id) REFERENCES requests(request_id)
                );
                """
            )

    def _require_connection(self) -> sqlite3.Connection:
        if self._connection is None:
            raise RuntimeError("ledger is closed")
        return self._connection

    @staticmethod
    def _evidence_values(evidence: Evidence | None) -> tuple[str | None, str | None, float | None, str | None]:
        if evidence is None:
            return (None, None, None, None)
        return (evidence.kind, evidence.source, evidence.observed_at, evidence.detail)

    @staticmethod
    def _request_from_row(row: sqlite3.Row) -> RequestSpec:
        return RequestSpec(
            row["request_id"],
            row["operation_key"],
            row["operation"],
            row["payload_digest"],
            row["generation"],
            row["created_at"],
            row["expires_at"],
        )

    @classmethod
    def _event_from_row(cls, row: sqlite3.Row) -> LedgerEvent:
        evidence = None
        if row["evidence_kind"] is not None:
            evidence = Evidence(
                row["evidence_kind"],
                row["evidence_source"],
                row["evidence_observed_at"],
                row["evidence_detail"],
            )
        from_state = State(row["from_state"]) if row["from_state"] is not None else None
        return LedgerEvent(
            row["request_id"],
            from_state,
            State(row["to_state"]),
            evidence,
            row["recorded_at"],
        )


def _demonstrate() -> None:
    request = RequestSpec("simulated-001", "output:led:1", "set_output", "sha256:demo", 1, 10.0, 30.0)
    with tempfile.TemporaryDirectory() as directory:
        database = Path(directory) / "ledger.sqlite3"
        ledger = Ledger(database)
        ledger.create(request, now=10.0)
        ledger.transition(
            request.request_id,
            expected=State.PENDING,
            target=State.SENT,
            evidence=Evidence("send", "simulator", 11.0),
            now=11.0,
        )
        ledger.transition(
            request.request_id,
            expected=State.SENT,
            target=State.UNKNOWN,
            evidence=Evidence("lost-response", "simulator", 12.0),
            now=12.0,
        )
        print(f"SIMULATED current={ledger.get(request.request_id).state.value} events={len(ledger.events(request.request_id))}")
        ledger.close()

        reopened = Ledger(database)
        print(f"SIMULATED restart_state={reopened.get(request.request_id).state.value} events={len(reopened.events(request.request_id))}")
        reopened.transition(
            request.request_id,
            expected=State.UNKNOWN,
            target=State.APPLIED,
            evidence=Evidence("authoritative-query", "simulator", 13.0),
            now=13.0,
        )
        print(f"SIMULATED applied={reopened.get(request.request_id).state.value} events={len(reopened.events(request.request_id))}")
        reopened.close()


if __name__ == "__main__":
    _demonstrate()
~~~

预期输出（本次本地运行已逐行核对；不是板端输出）：

~~~text
SIMULATED current=UNKNOWN events=3
SIMULATED restart_state=UNKNOWN events=3
SIMULATED applied=APPLIED events=4
~~~

初始创建已经是一条事件，因此 `PENDING → SENT → UNKNOWN` 对应 3 条事件，而不是 2 条。重开数据库只读取，不追加事件。随后 `UNKNOWN → APPLIED` 才增加第 4 条；`Evidence("authoritative-query", "simulator", 13.0)` 仍然只是模拟输入。

## 7. 实验二：状态查询与 UNKNOWN 收敛

代码保存为[reconcile_status.py](../../code/第4篇_PythonBridge/第4章_结果账本与状态查询/reconcile_status.py)。该文件导入同目录 `ledger.py` 的类型，但运行演示不会建立数据库连接，也不会写入实验一的账本。

**代码说明**

- 用途：比较查无记录、权威成功、过期后的权威最终未应用和身份不匹配四种观察。
- 运行环境：Python 3.10+；与 `ledger.py` 位于同一目录，无事件循环或网络要求。
- 文件位置：`code/第4篇_PythonBridge/第4章_结果账本与状态查询/reconcile_status.py`。
- 依赖：标准库 `dataclasses`、`math`，以及本章本地模块 `ledger`；该模块的依赖也都是标准库。
- 操作步骤：在仓库根目录执行 `python -B "code/第4篇_PythonBridge/第4章_结果账本与状态查询/reconcile_status.py"`；观察四项决策，不把 `CLOSE_*` 输出当作数据库已提交。
- 预期输出：下方四行 `SIMULATED`；`NOT_FOUND` 和错身份保持未知，另外两种权威观察给出关闭建议。
- 故障排查：`No module named ledger` 时恢复两个文件的同目录关系并运行仓库中的原文件；`now must be finite` 时检查传入值；收到 `KEEP_UNKNOWN` 应复核身份和来源，不能强改 `authoritative` 绕过证据校验。停止脚本即可结束，无远端动作需要撤销。
- 验证方式：逐行比较输出，并运行同一测试文件检查全部四个身份字段、终态类型、过期和迟到结果。

~~~python
"""Public type skeleton for safe result reconciliation."""
from __future__ import annotations

from dataclasses import dataclass
import math
from ledger import RequestRecord, RequestSpec, State


@dataclass(frozen=True)
class Observation:
    request_id: str
    operation_key: str
    operation: str
    payload_digest: str
    kind: str
    source: str
    observed_at: float
    authoritative: bool
    detail: str = ""


@dataclass(frozen=True)
class Decision:
    action: str
    target: State | None
    reason: str


def reconcile(record: RequestRecord, observation: Observation, now: float) -> Decision:
    """Choose a safe next action without changing the ledger."""
    if isinstance(now, bool) or not isinstance(now, (int, float)) or not math.isfinite(now):
        raise ValueError("now must be finite")

    if record.state != State.UNKNOWN:
        return Decision("KEEP_UNKNOWN", None, "record is not UNKNOWN")

    request = record.request
    record_identity = (
        request.request_id,
        request.operation_key,
        request.operation,
        request.payload_digest,
    )
    observation_identity = (
        observation.request_id,
        observation.operation_key,
        observation.operation,
        observation.payload_digest,
    )
    if not _matching_identity(record_identity, observation_identity):
        return Decision("KEEP_UNKNOWN", None, "observation identity does not match")

    if observation.kind == "NOT_FOUND":
        return Decision("KEEP_UNKNOWN", None, "not found is not final proof")

    final_decisions = {
        "APPLIED": ("CLOSE_APPLIED", State.APPLIED),
        "REJECTED": ("CLOSE_REJECTED", State.REJECTED),
        "NOT_APPLIED_FINAL": ("CLOSE_NOT_APPLIED", State.NOT_APPLIED_FINAL),
    }
    if observation.authoritative is True and observation.kind in final_decisions:
        action, target = final_decisions[observation.kind]
        return Decision(action, target, "authoritative final observation")

    if now >= request.expires_at:
        return Decision("STOP_EXPIRED", None, "request has expired without final proof")
    return Decision("KEEP_UNKNOWN", None, "observation is not authoritative final proof")


def _matching_identity(
    record_identity: tuple[str, str, str, str],
    observation_identity: tuple[str, str, str, str],
) -> bool:
    """Reject malformed identities rather than converting or comparing them loosely."""
    values = record_identity + observation_identity
    if any(not isinstance(value, str) or not value for value in values):
        return False
    return record_identity == observation_identity


def _demonstrate() -> None:
    request = RequestSpec(
        "simulated-001", "output:led:1", "set_output", "sha256:demo", 1, 10.0, 30.0
    )
    record = RequestRecord(request, State.UNKNOWN, 12.0)
    identity = (
        request.request_id,
        request.operation_key,
        request.operation,
        request.payload_digest,
    )
    observations = (
        ("not_found", Observation(*identity, "NOT_FOUND", "simulator", 20.0, True), 20.0),
        ("applied", Observation(*identity, "APPLIED", "simulator", 20.0, True), 20.0),
        (
            "expired_not_applied",
            Observation(*identity, "NOT_APPLIED_FINAL", "simulator", 31.0, True),
            31.0,
        ),
        (
            "mismatch",
            Observation("other", request.operation_key, request.operation, request.payload_digest,
                        "APPLIED", "simulator", 20.0, True),
            20.0,
        ),
    )
    for label, observation, now in observations:
        print(f"SIMULATED {label}: {reconcile(record, observation, now).action}")


if __name__ == "__main__":
    _demonstrate()
~~~

预期输出（本次本地运行已逐行核对；不是设备查询结果）：

~~~text
SIMULATED not_found: KEEP_UNKNOWN
SIMULATED applied: CLOSE_APPLIED
SIMULATED expired_not_applied: CLOSE_NOT_APPLIED
SIMULATED mismatch: KEEP_UNKNOWN
~~~

这四个场景使用同一个不可变 `RequestRecord` 分别判定，不是连续四次状态转移。`expired_not_applied` 在模拟时间 `31.0` 收到最终未应用证据，超过 `expires_at=30.0` 仍能关闭；`mismatch` 即使标记权威成功，也不能关闭另一个 ID 的请求。

`source`、`observed_at` 和 `detail` 保留在观察对象中，但纯函数没有验证来源身份、时间新鲜度或观测签名。`expires_at` 也依赖输入层提供有效值。它只严格校验 `now`、身份字段和受支持的判定条件，不能承担不可信网络数据的完整验证。

## 8. 接入真实 App 的顺序

以下是集成建议，不是已经完成的 UNO Q 操作。官方 [Arduino App specification](https://github.com/arduino/arduino-app-cli/blob/main/docs/app-specification.md) 用于核对 App 组成和两侧协作；[Arduino Router README](https://github.com/arduino/arduino-router#readme) 用于核对方法注册与连接生命周期。两者都不替本书定义设备结果查询方法。

1. **固定目标与契约。** 记录软件版本、设备身份、业务键范围、参数规范化方式、结果保留期和设备重启后的查询语义；确认设备确实支持历史请求查询。
2. **先保存请求身份。** 在发送前创建持久记录，核验原期限和资源准入条件；另外设计发送意图与崩溃窗口处理。若账本写入失败，暂停该请求发送。
3. **记录发送边界与原因。** 按适配器真实语义保存发送证据。响应丢失或无法排除已发送时，保留未知状态及原因，不自动创建重复动作。
4. **恢复连接，再查询历史身份。** 按第三章连接代次与恢复策略确认通道及必要方法，再进行有预算、无业务副作用的状态查询；方法注册成功本身不等于原动作完成。
5. **验证观察并调用纯策略。** 校验目标、来源、版本、完整身份和时间，把受信结果转换为 `Observation`。无法证明权威最终未应用时，不生成该观察。
6. **原子写入后展示终态。** `Decision.target` 非空时保存证据并尝试条件转移；写入失败或冲突时不向业务界面报告已持久确认。保留 `UNKNOWN` 的资源继续遵守冲突动作限制。
7. **演练异常与交接。** 分别测试应用重启、设备重启、迟到响应、查无记录、重复 ID 和原期限到达，按[第三篇第8章综合运行手册](../第3篇_Linux/第8章_Linux与Python_Bridge综合运行手册_从预检到交接.md)保存版本、证据与未决事项。

## 9. 验证结果、练习与交接

### 9.1 本地验证结果

本次核验日期为 `2026-09-22`，运行解释器为 Python `3.14.6`。两个源文件演示输出与上文一致；[test_ledger.py](../../code/第4篇_PythonBridge/第4章_结果账本与状态查询/test_ledger.py) 的 22 项测试通过。复现命令为 `python -B "code/第4篇_PythonBridge/第4章_结果账本与状态查询/test_ledger.py"`。

| 测试组 | 覆盖的行为 | 证据限制 |
| --- | --- | --- |
| 请求与状态 | 初始状态及事件、七状态词汇、重复 ID、缺失记录、全部允许转移、终态无出边、错误预期状态与非法转移 | 测试公共接口约束，不提供远端认证 |
| 事务与历史 | 发送证据门槛、事件插入失败回滚、主路径事件顺序、关闭并重开文件读取 | 没有进程崩溃、掉电或并发压力实测 |
| 查询匹配 | 三种权威终态、`NOT_FOUND`、非权威或未知类型、四个身份字段不匹配、畸形身份 | 观察由本地夹具构造，不是 Router 回执 |
| 期限与迟到证据 | 非有限 `now`、过期无终态、过期最终未应用、迟到成功 | 不验证设备时钟、现场期限或网络传输 |

源码按 Python 3.10+ 编写，实际执行环境是以上列出的版本；不能把本机运行写成已经在 Python 3.10 解释器或目标板镜像中执行。章节仍为 `draft`。

### 9.2 练习与判定要点

1. 在实验一的副本中先读取全部事件，再解释为什么初始事件的 `from_state` 为 `None`。要点：创建是历史的起点，不是从一个假定的既有状态转入。
2. 把实验二 `not_found` 场景的 `now` 改成 `31.0`，预测输出。要点：仍是 `KEEP_UNKNOWN`，调用方仍必须禁止过期重放。
3. 让成功观察只改变 `payload_digest`，分析为什么当前输出值相同也不应关闭请求。要点：状态相同无法证明历史动作身份，四元组必须完整匹配。
4. 比较直接写入 `EXPIRED` 和接收 `STOP_EXPIRED` 的后果。要点：前者是不可再转移的终态；后者没有写入目标，保留迟到证据入口。
5. 说明运行实验二后为什么实验一的事件数不会自动增加。要点：纯决策没有存储副作用，演示也没有打开实验一的临时数据库。

### 9.3 交接给下一任务的内容

Task 5 负责章节检查器、Fig-27 SVG 的实际渲染和预览，以及导航和图示登记。本任务提供正文、同步的 Mermaid 源码与官方来源登记，没有声称章节检查器或 SVG 检查已通过。

配套代码 README 当前仍使用早期预留正文路径，需在后续导航同步时改为本章的完整文件名；本章直接链接实际 Python 文件供复现。后续应继续检查代码块逐字同步、内部链接、来源登记和图文一致性，并把实际渲染工具版本、日期与视觉检查结果写入图示记录。

## 10. 常见问题

### 10.1 SQLite 提交成功是否就等于可靠落盘？

本地事务成功和重开读取有具体价值，但本实验没有验证存储介质、操作系统缓存或掉电恢复。它也不证明物理动作发生。可靠性和硬件验收必须分别测试。

### 10.2 为什么 `NOT_FOUND` 不能转为 `NOT_APPLIED_FINAL`？

“现在查不到”无法排除旧请求仍在途中、记录丢失或结果已过保留期。“最终未应用”还必须由权威提供方证明旧尝试不可能再执行。

### 10.3 过期后为什么还能接收成功？

期限限制新的发送和重放；迟到的权威成功只补充历史事实。保留为 `UNKNOWN` 的请求可以因此收敛，已写成终态 `EXPIRED` 的记录则不再允许修改。

### 10.4 当前设备值相同，为什么不能证明历史请求执行过？

同一值可能来自另一请求、默认值或人工操作。历史请求需要完整身份和可归因证据；只读当前值不自动具有这种归因能力。

### 10.5 `frozen=True` 和追加式事件是否意味着账本不可篡改？

不是。`frozen=True` 限制一般对象字段赋值，追加式接口避免本程序覆盖历史；它们不提供签名、访问控制、数据库外部修改防护或独立审计。

### 10.6 `reconcile()` 返回关闭建议后是否已经完成记账？

没有。调用方还要保存证据并执行条件转移，确认事务成功。它也不能因为 `target=None` 就启动重放；本章没有任何允许发送的决策动作。

## 11. 本章小结与下一步

请求身份把发送、查询和历史结果关联起来；当前投影便于读取，追加式事件保留形成结论的过程。两者必须在同一事务里更新，才能避免“状态变了却没有证据历史”的本地不一致。

连接恢复之后，仍需依据原请求身份查询。未知结果不能靠超时或查无记录变成确定结论；过期停止新动作，迟到权威证据则仍可关闭未决请求。下一步进入真实 App 的集成时，应先验证查询协议和接收端能力，再把本地接口映射到现场证据。阅读顺序以[全书目录](../../SUMMARY.md)为准，导航将在后续任务同步。

## 延伸阅读

- [第四篇第1章：消息模型与调用边界](./第1章_Python_Bridge开发基础_消息模型与调用边界.md)
- [第四篇第2章：并发与任务生命周期](./第2章_Python_Bridge并发与任务生命周期_从单次调用到有界协同.md)
- [第四篇第3章：连接复用与请求恢复](./第3章_Python_Bridge连接复用与请求恢复_从断线到可判定结果.md)
- [第三篇第8章：综合运行手册](../第3篇_Linux/第8章_Linux与Python_Bridge综合运行手册_从预检到交接.md)
- [Python 3.10 sqlite3 官方文档](https://docs.python.org/3.10/library/sqlite3.html)：数据库接口、事务和连接上下文行为。
- [Python 3.10 dataclasses 官方文档](https://docs.python.org/3.10/library/dataclasses.html)：冻结数据类与其边界。
- [本章测试契约](../../code/第4篇_PythonBridge/第4章_结果账本与状态查询/test_ledger.py)
- [参考资料索引](../../resources/references.md)：来源、核验日期与版权边界。
