---
title: Python Bridge 连接复用与请求恢复：从断线到可判定结果
part: 4
chapter: 3
status: draft
last_verified: 2026-09-22
updated: 2026-09-22
prerequisites: 第四篇第1～2章、第三篇第5章
tags: Python Bridge, 连接复用, 重连, 请求恢复, 幂等
---

# 第3章 Python Bridge 连接复用与请求恢复：从断线到可判定结果

## 学习目标

读完本章并完成实验后，读者应能够：

- 说明 Arduino UNO Q 上“通道已连接”“方法已注册”和“业务请求已完成”的区别；
- 用一个连接管理者为多个调用提供可复用会话，并为恢复过程设置上限；
- 通过连接代次隔离旧连接事件，防止迟到失败清掉新会话；
- 区分尚未发送和可能已经发送的请求，制定重连后的恢复决策；
- 解释为什么结果查询返回 `NOT_FOUND`，仍不足以允许重复控制动作；
- 运行并修改两个独立的 Python 示例，用测试验证竞争、取消和恢复分支。

本章承接[第四篇第2章：并发与任务生命周期](./第2章_Python_Bridge并发与任务生命周期_从单次调用到有界协同.md)。第二章管理任务怎样排队和结束，本章管理任务依赖的会话怎样恢复，以及恢复后怎样找回原请求的结论。

## 背景与边界

假设 Python App 向微控制器（Microcontroller Unit，MCU）发送了一次“设置输出目标值”请求。MCU 已应用目标值，响应却在返回途中丢失。Python 程序随后连上新的会话，此时有两个独立问题：

1. 新会话现在能否调用目标方法？
2. 原来的动作是否已经执行？

第一个问题可以通过连接与方法探测回答；第二个问题需要原动作的结果记录或可关联的后置观察。若把这两个问题合成一个 `connected=True`，程序就容易在重连后重复执行动作。

本章使用的 `ConnectionOwner`、`generation`、`Delivery`、`NOT_APPLIED_FINAL` 都是本书的应用层教学模型，**不是 Arduino 官方 API 或 Router 内置字段**。示例只使用 Python 标准库和本地替身，证据等级为 `SIMULATED`。接入真实客户端时，需要把库已有的连接、注册和错误处理机制接到应用策略上，并核对所装版本；不能直接用本章替身类代替 Bridge 驱动。

## 1. 从官方通信机制理解重连

### 1.1 方法注册依赖客户端连接

Arduino App specification 将 Linux 侧 Python 与 MCU 侧 Sketch 作为同一个 App 的不同组成部分，并通过远程过程调用（Remote Procedure Call，RPC）交换消息。[Arduino App specification](https://github.com/arduino/arduino-app-cli/blob/main/docs/app-specification.md)

Arduino Router 的官方说明给出了三个与本章直接相关的行为：

- 提供方注册方法后，Router 才能将相应调用转发给它；
- 客户端断开时，该客户端已注册的方法会被移除；
- Router 可以改写传输消息编号，以避免不同客户端之间的编号冲突。

这些是读取官方说明得到的事实，核验日期为 `2026-09-22`；目标板的软件版本仍要单独记录。[Arduino Router README](https://github.com/arduino/arduino-router#readme)

由此可以推导出本章的应用设计：连接建立后，还需要确认必要方法与契约可用；业务层的 `operation_key` 不能直接依赖 Router 某一跳的消息编号。这里的“推导”是本书设计建议，并不是官方自动恢复保证。

### 1.2 先确定谁拥有连接

一个完整 App 至少有三层需要分工：

| 层次 | 拥有的对象 | 重连时负责什么 |
| --- | --- | --- |
| 客户端库或适配器 | 具体通道、编解码、收发循环 | 按当前版本要求关闭失效通道、连接、注册与探测 |
| 应用连接管理者 | 一次恢复过程和已就绪会话 | 合并并发恢复请求、控制退避与预算、发布新代次 |
| 请求管理者 | 等待中的业务意图和结果记录 | 区分未发送/可能已发送，关联结果并安排查询 |

如果客户端库已负责自动重连，应用层应观察其状态并设置业务准入条件。不要再让每个 worker 各自创建一条恢复循环，否则多个循环会竞争连接、方法名和时间预算。

本章并不假定当前 Bridge 客户端允许任意多线程、多连接或并发读写同一通道。是否支持这些行为，应由目标版本文档和联调结果决定。

## 2. 连接复用：复用什么，谁能关闭

### 2.1 一次就绪会话供多个任务使用

连接复用的基本原则是：获取一个仍然有效的会话时，返回已有对象；只有不存在就绪会话时，才进入建立和探测流程。

一个应用中的多个协程可以同时要求 `ready()`。如果没有统一管理，它们可能各自发起连接。第一个实验使用 `asyncio.Lock`，让同一时刻只有一个协程执行恢复，其余协程在锁释放后读取已经建立的会话。该锁只适用于同一事件循环中的协程，不是跨线程或跨进程锁。[Python 3.10 同步原语](https://docs.python.org/3.10/library/asyncio-sync.html#lock)

连接复用也不等于业务动作可以无限并发。第二章的队列容量、worker 数量和资源串行化仍然适用。复用会话解决连接的所有权；队列和资源键解决任务的数量与顺序。

### 2.2 使用者报告故障，管理者使会话失效

设某个任务使用了代次 `7` 的会话，并发生连接错误。它应当报告“代次 7 失效”。管理者只有在当前会话仍是代次 `7` 时才清除缓存。

如果另一个任务已经建立代次 `8`，随后才收到代次 `7` 的失败回调，这个旧事件不能把代次 `8` 清掉。否则系统会出现“刚重连就又断开”的假象。

实际通道关闭应集中在拥有者处完成。请求调用方释放的是自己的等待对象或租约；它不应随意关闭其他任务还在使用的共享通道。

### 2.3 失效窗口仍需由请求层处理

`ready()` 返回后，连接可能立刻断开，因此拿到会话不构成永久可用承诺。发送失败时，请求层仍需判断是否已进入发送边界；只靠连接缓存无法判断硬件动作是否发生。

## 3. 连接代次与业务身份

### 3.1 三种标识各有用途

| 标识 | 生命周期 | 本章用途 |
| --- | --- | --- |
| `generation` | 本进程的一次成功连接与探测 | 拒绝旧连接事件覆盖新会话 |
| `request_id` | 一次应用调用尝试 | 在本地待响应表中关联结果 |
| `operation_key` | 一项业务动作，可跨重连 | 查询同一动作的历史结果或去重记录 |

应用可以用 `(generation, request_id)` 索引活跃等待者，并由适配器映射到实际传输消息编号。这里的 `request_id` 是第一章的应用关联标识，不能未经核对就当作 Router 两端相同的底层编号。

进程重启后，仅有一个从 1 重新计数的 `generation` 不够。持久记录还要带进程运行标识或其他不会混淆的命名空间；对方重启标识也应单独记录。**连接代次不等于 MCU 启动次数。**

### 3.2 旧响应可以成为历史证据

旧连接上的响应不能直接完成新请求，但它可能解释原来的动作。因此恢复过程需要两条入口：

- **实时响应入口**：匹配活跃的连接代次、调用标识和目标；
- **历史对账入口**：匹配目标、业务键、参数摘要和权威结果记录。

不要因为旧代次响应无法匹配当前等待者，就把历史动作的所有证据永久丢弃。可以将其转入隔离记录，经过身份、契约和来源校验后参与对账。

### 3.3 参数摘要防止同键不同动作

若同一个 `operation_key` 第一次表示“设为 25”，第二次却表示“设为 80”，不能把它们视为同一动作。结果记录需要同时匹配目标、业务键和参数摘要。

实际摘要应来自契约规定的规范化参数，包括单位和版本；摘要本身不提供身份认证。第二个实验使用 `demo-payload-A` 作为假摘要标签，便于观察匹配逻辑，不把它称为真实哈希。

## 4. Fig-26：连接恢复状态图

本图只表达连接管理者。图中的 `READY` 意味着通道和必要方法通过探测，不表示旧请求已经恢复完成。

<a id="fig-26-python-bridge-connection-recovery"></a>

~~~mermaid
stateDiagram-v2
    [*] --> ACTIVE
    state "Connection owner" as ACTIVE {
        [*] --> DISCONNECTED
        DISCONNECTED --> CONNECTING: begin recovery
        CONNECTING --> PROBING: channel opened
        CONNECTING --> BACKOFF: transient error
        CONNECTING --> PAUSED: recovery cancelled
        PROBING --> READY: method verified
        PROBING --> BACKOFF: not ready yet
        PROBING --> PAUSED: incompatible or cancelled
        READY --> DISCONNECTED: link lost
        BACKOFF --> CONNECTING: delay elapsed
        BACKOFF --> PAUSED: exhausted or cancelled
        PAUSED --> CONNECTING: explicit restart
    }
    ACTIVE --> STOPPED: application shutdown
    STOPPED --> [*]
~~~

图 4-3（Fig-26）：连接管理者的建立、探测、就绪、退避、暂停与关闭路径。图源为[Mermaid 文件](../../diagrams/uno-q-python-bridge-connection-recovery.mmd)，可查看[导出 SVG](../../images/第4篇_PythonBridge/ch03-fig26-uno-q-python-bridge-connection-recovery.svg)。依据[已登记的官方资料](../../resources/references.md)原创设计；`2026-09-22` 使用 Mermaid CLI `11.12.0` 渲染，并检查了预览中的文字、连线与边界。

连接丢失时，进入 `DISCONNECTED` 的同时保留未决请求；可能已发送的请求保持 `UNKNOWN`。重连到 `READY` 后，恢复模块先处理这些请求的查询需求，再按资源范围恢复新的业务动作。

图中的 `PAUSED` 表示恢复预算耗尽、契约不兼容或本轮恢复被取消。新的恢复周期由上层在原因处理后明确发起，不能由下一个排队 worker 无条件重新开始。`ACTIVE` 包含连接管理者的各内部状态；整个应用关闭时统一进入 `STOPPED`。

## 5. 重连退避与时间预算

### 5.1 指数退避加抖动

第 `k` 次连接失败后，可以先计算等待上限：

`ceiling(k) = min(cap, base × 2^(k−1))`

再从 `[0, ceiling(k)]` 中抽取本次等待时间。这种完整区间抖动可以分散多个实例同时重连的时刻。它是本书示例采用的策略，Python `random.uniform` 只是产生区间随机数的工具。[Python 3.10 random](https://docs.python.org/3.10/library/random.html#random.uniform)

第一个实验使用 `base=0.01` 秒、`cap=0.04` 秒，最多尝试 3 次。这些是为了快速观察行为的教学参数。示例使用固定随机种子以方便复现；部署时不能让所有实例共享同一个固定种子序列。

### 5.2 连接预算和动作期限分别计算

| 预算 | 包含什么 | 到期之后 |
| --- | --- | --- |
| 一次建立/探测超时 | 打开通道及确认必要能力 | 释放本次尝试的资源，判断错误是否可重试 |
| 一轮恢复预算 | 多次尝试、退避和清理 | 暂停恢复，报告最后失败原因 |
| 业务动作期限 | 排队、等连接、发送和等待结果 | 禁止过期动作重新发送，继续保留对账入口 |
| 停止预算 | 收尾、释放资源和保存未决记录 | 记录未完成清理，不报告虚假的远端取消 |

本地经过时间宜使用单调时钟，避免系统时间校正使期限倒退。`time.monotonic()` 的绝对起点未定义，只适合在兼容时间基准下计算差值；不能把原进程的任意计数值直接发给 MCU，或跨设备重启恢复期限。[Python 3.10 time](https://docs.python.org/3.10/library/time.html#time.monotonic)

### 5.3 哪些错误可以重试

连接暂时不可达、方法尚未完成注册，可以在有限预算内再探测。明确的身份错误、权限拒绝和不兼容契约需要修正配置或版本；继续退避通常不能解决它们。

`asyncio.wait_for` 超时会尝试取消被等待的协程，并等待取消完成，所以实际等待可能超过所设时长。不要把它当成无法超越的硬实时界限。取消必须继续向调用者传播，并由适配器清理部分建立的资源。[Python 3.10 超时语义](https://docs.python.org/3.10/library/asyncio-task.html#timeouts)

## 6. 请求恢复：先判定，再决定是否发送

### 6.1 发送证据比异常名称更重要

本章将发送证据分为两类：

- `NOT_SENT`：能够证明请求尚未交给发送边界，例如仍在本地队列，或连接探测失败时尚未调用发送接口；
- `MAYBE_SENT`：已交给发送接口，或进程在可能发送的窗口中中断，无法排除接收端已经执行。

向发送接口提交前，应先记录“即将发送”的意图；发生不确定窗口时，恢复为 `MAYBE_SENT`。这会保守地保留少量未知请求，但能够避免把实际上已发生的动作当作首次执行。

恢复账本和物理动作之间通常没有一个共同事务。仅在 Python 侧记日志，不能宣称获得跨处理器“恰好一次执行”。

### 6.2 恢复决策表

以下均是本书的应用策略，不是官方协议返回码：

| 发送证据与查询结果 | 下一步 | 保留的约束 |
| --- | --- | --- |
| `NOT_SENT`，连接未就绪 | `WAIT_READY` | 继续检查原期限 |
| `NOT_SENT`，连接就绪且未过期 | `SEND_FIRST_ATTEMPT` | 再走方法授权和资源调度 |
| `NOT_SENT`，已过期 | `STOP_EXPIRED` | 不因重连自动延长期限 |
| `MAYBE_SENT`，尚无结果 | `QUERY_ONLY` | 仅查询，不重复业务动作 |
| 查询确认 `IN_PROGRESS` | `WAIT_AND_QUERY` | 查询也要有间隔与预算 |
| 查询返回 `NOT_FOUND` | `KEEP_UNKNOWN` | 记录可能过期、丢失，或原请求仍在途 |
| 可信结果为 `APPLIED` / `REJECTED` | `STOP_APPLIED` / `STOP_REJECTED` | 记录来源及后置观察 |
| 已过期，但可信证据确认最终未应用 | `STOP_NOT_APPLIED` | 关闭原请求，不再重发 |
| 目标、键或参数摘要不一致 | `KEEP_UNKNOWN` | 隔离错误记录 |
| 已证明最终未应用，且重放契约有效 | `RESUBMIT_SAME_KEY` | 沿用业务键，创建新的调用尝试记录 |

`WAIT_READY`、`QUERY_ONLY` 等是恢复动作建议，不会把原请求的结果状态从 `UNKNOWN` 改成成功。

### 6.3 “最终未应用”比“当前查不到”严格得多

实验中的 `NOT_APPLIED_FINAL` 必须满足一个额外前提：提供方已阻止旧尝试继续执行，并能权威地说明该动作最终没有应用。只查一次状态、读不到键、缓存过期或者方法重新注册，都不满足这个前提。

本书没有声称 Arduino Router 提供这种查询。需要由应用协议及接收端状态机实现并验证。如果提供方无法给出这一证据，实验中的该分支就不应接入真实动作。

即使最终未应用，也要重新检查原期限、当前资源状态和重放契约。重复“设置目标值”在数学意义上可能幂等，但延迟到新场景后执行仍可能已经不合适。

### 6.4 接收端重启与账本保存

如果结果账本只在 MCU 内存中，重启后得到 `NOT_FOUND`，只能说明当前查不到记录。恢复前要确认去重记录是否跨重启保存、保存多久，以及版本升级是否改变键的含义。

持久记录至少包含目标别名、业务键、参数摘要、契约版本、发送证据、最近结果、时间基准和对方启动标识。第一版实验用内存数据类展示决策，不实现持久化、身份校验或真实的接收端去重。

## 7. 实验一：共享会话与有界重连

代码已经保存为[connection_owner.py](../../code/第4篇_PythonBridge/第3章_连接复用与请求恢复/connection_owner.py)，可直接运行。

**代码说明**

- 用途：让 6 个并发调用者共享一轮连接恢复，演示重试上限、会话复用和旧代次失效事件隔离。
- 运行环境：Python 3.10+；一个进程和一个事件循环。
- 文件位置：`code/第4篇_PythonBridge/第3章_连接复用与请求恢复/connection_owner.py`。
- 依赖：标准库 `asyncio`、`dataclasses` 和 `random`。
- 操作步骤：在仓库根目录执行 `python -B "code/第4篇_PythonBridge/第3章_连接复用与请求恢复/connection_owner.py"`。
- 预期输出：第一次恢复尝试 3 次，6 个调用者拿到同一会话；重连后代次为 2，旧代次无法清除新会话。
- 故障排查：导入失败先核对 Python 版本；出现 `recovery paused` 表示该实例已暂停恢复，可能是预算耗尽、恢复被取消、连接失败或契约不兼容，应结合异常和尝试次数检查具体原因；停止本地脚本即可结束模拟。
- 验证方式：执行随附测试，确认并发等待者不会各自重启一轮恢复，且取消会释放锁。

~~~python
"""Local simulation of a shared connection owner; no network or hardware."""
from __future__ import annotations

import asyncio
from dataclasses import dataclass
from random import Random


@dataclass(frozen=True)
class Session:
    generation: int
    contract: str = "demo-v1"


class FakeConnector:
    def __init__(self, failures: int = 2, contract: str = "demo-v1") -> None:
        self.failures = failures
        self.contract = contract
        self.attempts = 0

    async def open_and_probe(self, generation: int) -> Session:
        self.attempts += 1
        await asyncio.sleep(0)
        if self.attempts <= self.failures:
            raise ConnectionError("simulated unavailable endpoint")
        return Session(generation, self.contract)


class ConnectionOwner:
    def __init__(self, connector: FakeConnector, max_attempts: int = 3) -> None:
        if type(max_attempts) is not int or not 1 <= max_attempts <= 10:
            raise ValueError("max_attempts must be an integer from 1 to 10")
        self.connector = connector
        self.max_attempts = max_attempts
        self._lock = asyncio.Lock()
        self._session: Session | None = None
        self._generation = 0
        self._paused = False
        self._attempts = 0
        self._random = Random(7)  # Fixed seed only for reproducible teaching.
        self.delays: list[float] = []

    async def ready(self) -> Session:
        async with self._lock:
            if self._paused:
                raise ConnectionError("recovery paused")
            if self._session is not None:
                return self._session
            try:
                while self._attempts < self.max_attempts:
                    self._attempts += 1
                    try:
                        candidate = await asyncio.wait_for(
                            self.connector.open_and_probe(self._generation + 1),
                            timeout=0.5,
                        )
                    except (ConnectionError, asyncio.TimeoutError):
                        if self._attempts == self.max_attempts:
                            raise
                        ceiling = min(0.04, 0.01 * (2 ** (self._attempts - 1)))
                        delay = self._random.uniform(0.0, ceiling)
                        self.delays.append(delay)
                        await asyncio.sleep(delay)
                        continue
                    if candidate.contract != "demo-v1":
                        raise ValueError("contract mismatch")
                    self._generation = candidate.generation
                    self._session = candidate
                    return candidate
            except asyncio.CancelledError:
                self._paused = True
                raise
            except Exception:
                self._paused = True
                raise
        raise RuntimeError("unreachable")

    def invalidate(self, observed_generation: int) -> bool:
        # Called on the same event loop; a stale failure cannot clear a new session.
        if self._session is None:
            return False
        if self._session.generation != observed_generation:
            return False
        self._session = None
        self._attempts = 0
        return True


async def main() -> None:
    connector = FakeConnector(failures=2)
    owner = ConnectionOwner(connector)
    sessions = await asyncio.gather(*(owner.ready() for _ in range(6)))
    assert all(session is sessions[0] for session in sessions)
    assert connector.attempts == 3
    print(f"SIMULATED shared=6 attempts={connector.attempts} generation=1")
    owner.invalidate(sessions[0].generation)
    current = await owner.ready()
    stale_cleared = owner.invalidate(sessions[0].generation)
    assert current.generation == 2 and not stale_cleared
    print(f"SIMULATED generation={current.generation} stale_cleared={stale_cleared}")


if __name__ == "__main__":
    asyncio.run(main())
~~~

示例输出：

~~~text
SIMULATED shared=6 attempts=3 generation=1
SIMULATED generation=2 stale_cleared=False
~~~

`open_and_probe()` 在本例中把建立和探测合成一步。真实适配器需要在失败或取消时关闭部分建立的连接；不能只删除 Python 对象引用。这里没有实际通道，所以 `invalidate()` 只清除缓存。

另外，`ready()` 持锁等待时，后来者会排队。实际调用方仍需用自己的业务期限限制“等待获得会话”的时间。示例的三次上限限制一轮建立尝试，不覆盖任意数量的排队调用者。

恢复预算保存在管理者上。发起恢复的协程被取消时，该轮恢复进入暂停，取消异常仍向上传播，其他等待者会得到明确失败；它们不会各自获得新的三次预算。只在锁外排队的等待者取消，则不会取消当前恢复。明确启动新管理者实例代表一轮新的恢复，运行标识也必须相应更新。

## 8. 实验二：丢失响应后的恢复决策

代码保存为[recovery_policy.py](../../code/第4篇_PythonBridge/第3章_连接复用与请求恢复/recovery_policy.py)。它只返回下一步决策，因此读者可以先检查策略，再把允许的动作交给真实执行器。

**代码说明**

- 用途：演示响应丢失、账本查无记录、迟到确认、参数冲突和动作过期时的不同恢复结果。
- 运行环境：Python 3.10+；不依赖事件循环。
- 文件位置：`code/第4篇_PythonBridge/第3章_连接复用与请求恢复/recovery_policy.py`。
- 依赖：标准库 `dataclasses`、`enum` 和 `math`。
- 操作步骤：在仓库根目录执行 `python -B "code/第4篇_PythonBridge/第3章_连接复用与请求恢复/recovery_policy.py"`；示例目标、键和摘要都是虚构标签。
- 预期输出：未知请求只查询，`NOT_FOUND` 保持未知；可信的迟到成功结束请求；最终未应用且满足重放契约才返回同键重提建议。
- 故障排查：`KEEP_UNKNOWN` 需要检查证据和匹配字段；不能通过修改状态字符串强行放行；本地脚本没有远端副作用。
- 验证方式：运行测试中的过期、错目标、错键、错摘要和非有限时间用例，确认它们不会产生自动重放许可。

~~~python
"""Pure recovery decisions for validated application records; no I/O."""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from math import isfinite


class Delivery(Enum):
    NOT_SENT = "NOT_SENT"
    MAYBE_SENT = "MAYBE_SENT"


@dataclass(frozen=True)
class Request:
    target: str
    operation_key: str
    payload_digest: str
    delivery: Delivery
    expires_at: float
    replay_safe: bool = False


@dataclass(frozen=True)
class ResultRecord:
    target: str
    operation_key: str
    payload_digest: str
    state: str


def decide_recovery(
    request: Request,
    record: ResultRecord | None,
    *,
    ready: bool,
    now: float,
) -> str:
    if not isfinite(now) or not isfinite(request.expires_at):
        raise ValueError("finite monotonic times required")
    if not isinstance(request.delivery, Delivery):
        raise ValueError("unsupported delivery evidence")
    if record is not None:
        expected = (request.target, request.operation_key, request.payload_digest)
        actual = (record.target, record.operation_key, record.payload_digest)
        if actual != expected:
            return "KEEP_UNKNOWN"
        if record.state == "APPLIED":
            return "STOP_APPLIED"
        if record.state == "REJECTED":
            return "STOP_REJECTED"
        if record.state not in {"NOT_FOUND", "IN_PROGRESS", "NOT_APPLIED_FINAL"}:
            return "KEEP_UNKNOWN"
    if now >= request.expires_at:
        if record is not None and record.state == "NOT_APPLIED_FINAL":
            return "STOP_NOT_APPLIED"
        return (
            "STOP_EXPIRED"
            if request.delivery is Delivery.NOT_SENT
            else "KEEP_UNKNOWN"
        )
    if not ready:
        return "WAIT_READY"
    if request.delivery is Delivery.NOT_SENT:
        # An unexpected remote record contradicts the local NOT_SENT evidence.
        return "SEND_FIRST_ATTEMPT" if record is None else "KEEP_UNKNOWN"
    if record is None:
        return "QUERY_ONLY"
    if record.state == "IN_PROGRESS":
        return "WAIT_AND_QUERY"
    if record.state == "NOT_APPLIED_FINAL" and request.replay_safe:
        return "RESUBMIT_SAME_KEY"
    if record.state == "NOT_APPLIED_FINAL":
        return "MANUAL_REVIEW"
    return "KEEP_UNKNOWN"


def main() -> None:
    request = Request(
        "sim-device", "op-007", "demo-payload-A", Delivery.MAYBE_SENT, 20.0
    )
    record = ResultRecord("sim-device", "op-007", "demo-payload-A", "NOT_FOUND")
    cases = [
        ("lost_response", request, None, 10.0),
        ("missing_record", request, record, 10.0),
        ("late_confirmation", request, replace(record, state="APPLIED"), 30.0),
        (
            "fenced_and_safe",
            replace(request, replay_safe=True),
            replace(record, state="NOT_APPLIED_FINAL"),
            10.0,
        ),
        ("wrong_payload", request, replace(record, payload_digest="other"), 10.0),
        ("expired_not_applied", request, replace(record, state="NOT_APPLIED_FINAL"), 30.0),
        (
            "expired_unsent",
            replace(request, delivery=Delivery.NOT_SENT),
            None,
            30.0,
        ),
    ]
    for label, req, result, now in cases:
        decision = decide_recovery(req, result, ready=True, now=now)
        print(f"SIMULATED {label}: {decision}")


if __name__ == "__main__":
    main()
~~~

示例输出：

~~~text
SIMULATED lost_response: QUERY_ONLY
SIMULATED missing_record: KEEP_UNKNOWN
SIMULATED late_confirmation: STOP_APPLIED
SIMULATED fenced_and_safe: RESUBMIT_SAME_KEY
SIMULATED wrong_payload: KEEP_UNKNOWN
SIMULATED expired_not_applied: STOP_NOT_APPLIED
SIMULATED expired_unsent: STOP_EXPIRED
~~~

有三个容易忽略的细节：

1. `late_confirmation` 在期限之后仍可关闭原请求，因为它只记录已经发生的结果，不产生新的动作。
2. `RESUBMIT_SAME_KEY` 是策略建议；真正发送前还要重新取得会话、检查权限、当前资源状态和期限。
3. `ResultRecord` 假定输入已经经过来源和结构校验，`replay_safe` 假定来自已确认的应用契约。这个纯函数不解析不可信网络输入，也不提供认证或硬件后置观察。

`expired_not_applied` 说明期限约束的是后续发送，不会抹去已有的可信结论。已证实最终未应用时，应关闭原请求；继续保留 `UNKNOWN` 会让相冲突的资源无故停留在冻结状态。

## 9. 接入实际 App 的顺序

把模拟换成实际客户端时，按下列顺序逐步接入：

1. **记录版本与职责。** 固定 App、Python 包、Router 与 Sketch 版本，确认客户端库已负责哪些连接行为。
2. **接入只读探测。** 用应用定义的无副作用方法确认目标和契约。若本端也是提供方，按库的生命周期恢复自身注册；调用方不能替代对方注册其能力。
3. **观察一次复用。** 连续发起两次只读请求，确认使用同一就绪会话，分别保留应用关联标识。
4. **引入受控断线。** 在允许的测试环境模拟链路失败，记录通道状态、连接代次和所有在途请求；副作用请求保留为未知。
5. **恢复方法与查询。** 新会话通过探测后，优先查询历史业务键；缓存必须带来源和新鲜度。
6. **恢复新任务。** 依据资源范围解除暂停。一个资源上仍有未知动作，不要求所有无关只读任务都停下，但相冲突的动作必须等待判定。
7. **演练停止。** 停止接收新动作，收集未决记录，取消本地等待，关闭自有通道；不把本地清理完成写成 MCU 动作已撤销。

方法名、客户端类名和实际调用方式应按安装版本的官方文档填入适配层。本章的 `open_and_probe()` 只是教学接口，没有推荐可直接调用的官方同名方法。

## 10. 验证结果与复现实验

随附测试为[test_recovery.py](../../code/第4篇_PythonBridge/第3章_连接复用与请求恢复/test_recovery.py)。在仓库根目录执行 `python -B "code/第4篇_PythonBridge/第3章_连接复用与请求恢复/test_recovery.py"`。

| 检查对象 | 关注的错误 | 判定方法 |
| --- | --- | --- |
| 共享恢复 | 每个等待者各发起一轮连接 | 并发请求最终共享同一会话，建立计数符合预算 |
| 旧代次故障 | 新会话被迟到失败清除 | 新代次对象保持不变 |
| 重试耗尽 | 排队任务接力无限重试 | 所有等待者结束，建立计数不再增长 |
| 取消与超时 | 锁泄漏、后台继续建立 | 取消传播、锁可再次取得；超时按预算暂停 |
| 查询关联 | 错目标或错参数被接受 | 匹配失败返回 `KEEP_UNKNOWN` |
| 业务期限 | 重连后过期动作被重放 | 禁止新发送，仍能记录可信迟到结果 |
| 图文一致性 | 正文图和源文件漂移 | Mermaid 与代码块对照实际文件 |
| 板端验证 | 本机结果被当作硬件证据 | 单独保留未执行的实机项目 |

本次本地验证日期为 `2026-09-22`，实际解释器为 Python `3.14.6`：两个示例运行成功，17 项针对性测试全部通过；Fig-26 已完成 SVG 渲染与预览检查。源代码使用 Python 3.10 语法检查，但尚未在 Python 3.10 解释器和目标板镜像中执行。

文档的重复校验入口为[check_chapter.py](../../code/第4篇_PythonBridge/第3章_连接复用与请求恢复/check_chapter.py)，检查代码与正文一致、内部路径和锚点、图源、SVG 及来源登记。命令与审阅记录见[实施记录](../../docs/superpowers/plans/2026-09-22-python-bridge-chapter3-plan.md)。当前章节保持 `draft`；板端的真实连接复用、注册恢复、结果账本和接收端去重仍需后续联调。

### 练习

1. 将 `FakeConnector(failures=2)` 改为 `failures=100`，推断为什么排队的 6 个调用者不会产生 18 次建立尝试。
2. 让代次 1 的错误事件在代次 2 建立后到达，说明为什么必须带上 `observed_generation`。
3. 把 `NOT_FOUND` 改成“最终未应用”，列出接收端还必须证明的条件。
4. 给业务键相同的记录换一个参数摘要，解释为什么“动作名相同”不能恢复这个请求。

参考答案的关键点分别是：恢复耗尽状态共享；只允许当前代次使会话失效；阻止旧尝试继续执行并形成权威结论；业务身份需要同时匹配目标、键和参数。

## 11. 常见问题

### 11.1 连上 Router 后，为什么方法仍不可用？

连接可达与提供方注册是两个条件。提供方可能尚在启动、刚断开或契约已经变更。区分临时注册延迟和不兼容配置，再决定是否退避。

### 11.2 为什么不直接使用 Router 的消息编号作为永久业务键？

消息编号服务于传输关联，Router 还可能进行编号映射。持久业务身份需要由应用明确设计，跨连接保存。

### 11.3 一次只读查询返回当前值，能证明某个历史请求执行过吗？

通常不能。当前状态相同可能由其他请求造成；瞬时读取也不能排除原请求仍在途。要看该观察是否能关联到原业务键、版本和目标，以及是否满足动作的验收条件。

### 11.4 应用重启后，还能继续使用原单调时钟期限吗？

需要先核对时间基准。持久任务应记录适合恢复的业务时间约束，并在启动时重新验证有效性；不能直接比较来自不同机器或不兼容启动周期的任意计数值。

### 11.5 所有未知状态都必须人工处理吗？

不必。如果应用提供可信的结果查询，且身份、版本和结果都能判定，可以自动结束请求。需要人工处理的是当前协议无法消除的歧义，或超出既定恢复策略的情况。

## 12. 本章小结与下一步

复用连接需要明确所有权；恢复连接需要有限预算；恢复请求需要与原动作关联的证据。连接代次解决旧事件污染，业务键与参数摘要解决历史动作的身份问题，这两组信息共同构成恢复过程的基础。

下一章将进一步讨论结果账本、状态查询与一致性，把本章的 `QUERY_ONLY` 和 `KEEP_UNKNOWN` 接入可检查的查询契约。阅读入口以[全书目录](../../SUMMARY.md)为准。

## 延伸阅读

- [第四篇第1章：消息模型与调用边界](./第1章_Python_Bridge开发基础_消息模型与调用边界.md)
- [第四篇第2章：并发与任务生命周期](./第2章_Python_Bridge并发与任务生命周期_从单次调用到有界协同.md)
- [第三篇第5章：队列、重连与状态缓存](../第3篇_Linux/第5章_Linux现场自动化与Python_Bridge_队列重连与状态缓存.md)
- [第三篇第8章：综合运行手册](../第3篇_Linux/第8章_Linux与Python_Bridge综合运行手册_从预检到交接.md)
- [本章代码与运行说明](../../code/第4篇_PythonBridge/第3章_连接复用与请求恢复/README.md)
- [Fig-26 图示登记](../../images/第4篇_PythonBridge/README.md#fig-26-python-bridge-connection-recovery)
- [参考资料索引](../../resources/references.md)：官方资料核验日期、用途和版权边界。
