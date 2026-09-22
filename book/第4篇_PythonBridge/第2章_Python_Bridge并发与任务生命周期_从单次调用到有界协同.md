---
title: Python Bridge 并发与任务生命周期：从单次调用到有界协同
part: 4
chapter: 2
status: draft
last_verified: 2026-09-22
updated: 2026-09-22
prerequisites: 第四篇第1章、第三篇第5章和第三篇第6章
tags: Python Bridge, asyncio, 并发, 任务生命周期, 背压
---

# 第2章 Python Bridge 并发与任务生命周期：从单次调用到有界协同

## 学习目标

完成本章后，读者应能够：

- 区分一次 Bridge 调用、一个本地异步任务和一个远端动作；
- 为任务定义可观察的生命周期状态，并明确每次状态迁移的证据；
- 使用有界队列、并发上限和 worker 控制请求压力，避免无限制堆积；
- 区分本地任务取消、远端动作取消、超时和 UNKNOWN；
- 在普通 Python 3 环境中运行两个 asyncio 概念实验，验证背压和对账顺序；
- 为后续连接复用、重连、App Lab 和综合项目建立可交接的任务记录。

第四篇第 1 章回答了“一条消息应该怎样表达”。本章继续回答“多条消息同时存在时，怎样控制它们的生命周期”。章节编号仍然是第四篇自己的编号：这是第四篇第 2 章，不沿用第三篇或第二篇的编号。

## 背景与边界

当 Python App 只处理一条读取请求时，顺序代码看起来足够简单；当多个传感读取、状态查询和控制请求同时进入时，问题会迅速变成任务管理问题：

- 请求是否全部进入内存，还是有明确的队列上限？
- 哪些任务可以并行，哪些任务必须按资源或设备顺序执行？
- 调用方取消的是等待，还是已经发出的远端动作？
- 本地超时以后，远端是否仍可能运行？
- 任务完成的依据是协程返回、Bridge 响应，还是 MCU 后置观察？

本章只建立可验证的应用层模型。示例使用 Python 标准库 `asyncio`，不调用 Router、Bridge/RPC、ADB、SSH、网络、串口或 UNO Q 硬件。概念实验产生的是 `SIMULATED` 证据，不能替代第三篇第 8 章要求的现场预检、实机观察和交接证据。

并发参数也不是硬件能力结论。队列大小、worker 数和超时值只是策略输入；真正的现场预算还需要结合目标镜像、Bridge 实现、MCU 实时任务、网络路径和硬件安全要求测量。

## 1. 调用、任务与远端动作

### 1.1 三个对象不能混为一谈

| 对象 | 生命周期开始点 | 生命周期结束点 | 典型状态来源 |
| --- | --- | --- | --- |
| 调用 | Python App 生成请求信封 | 收到匹配响应或进入 UNKNOWN | `request_id`、契约和响应 |
| 本地任务 | App 把调用交给 event loop 或队列 | 协程返回、取消或异常结束 | `asyncio.Task`、队列和本地日志 |
| 远端动作 | Bridge 或 MCU 接受执行意图 | MCU 返回结果并完成所需观察 | Bridge 响应、MCU 状态和后置观察 |

本地任务完成不代表远端动作完成。例如，Python 任务可以在成功把消息写入一个本地 socket 后结束，但接收端可能尚未执行；反过来，本地等待任务超时，远端动作也可能已经发生。任务模型必须保留这种证据差异。

### 1.2 一个任务至少要携带什么

除了第一章定义的请求信封，一个可管理任务还应有：

| 字段 | 作用 | 设计要求 |
| --- | --- | --- |
| `task_id` | 关联本地排队、worker 和结果 | 与 `request_id` 可一一对应或明确映射 |
| `request_id` | 关联跨处理器请求 | 不能因任务重试而无记录地覆盖 |
| `priority` | 可选的调度优先级 | 不得让低优先级任务永久饥饿 |
| `deadline` | 本地等待或业务有效期限 | 使用明确的时间基准，不用无限等待 |
| `resource_key` | 标识共享资源或目标通道 | 同一资源上的危险动作可串行化 |
| `idempotent` | 标识重复动作是否安全 | 必须有契约依据，不凭调用者感觉填写 |
| `state` | 当前生命周期状态 | 只允许经过定义的状态迁移 |

`task_id` 是本地调度对象的身份；`request_id` 是跨边界消息的身份。记录两者可以区分“本地任务被取消”和“远端请求结果未知”。

## 2. 生命周期状态与迁移规则

### 2.1 建议的状态集合

本章使用以下状态：

| 状态 | 含义 | 允许的下一步 |
| --- | --- | --- |
| `CREATED` | 已创建任务对象，但尚未进入有界队列 | `QUEUED` 或 `REJECTED` |
| `QUEUED` | 已占用队列容量，等待 worker | `RUNNING`、`REJECTED` 或本地取消 |
| `RUNNING` | worker 已取得租约，调用正在进行 | `COMPLETED`、`CANCEL_REQUESTED` 或 `UNKNOWN` |
| `CANCEL_REQUESTED` | 调用方请求取消，等待协作式停止或结果确认 | `COMPLETED`、`REJECTED` 或 `UNKNOWN` |
| `COMPLETED` | 任务结果已经分类，必要的后置观察已完成 | 结束 |
| `REJECTED` | 在执行前或执行中被明确拒绝 | 结束或交给人工重新评审 |
| `UNKNOWN` | 是否执行或最终状态无法判定 | 对账、人工裁决或安全冻结 |

`COMPLETED` 表示生命周期有结论，不等于业务一定成功；业务结果仍应通过第一章的 `APPLIED`、`REJECTED` 或 `UNKNOWN` 说明。为了减少歧义，工程记录可以同时保存 `task_state` 和 `result_state`。

### 2.2 不允许的隐式迁移

以下迁移必须显式记录，不能通过“协程结束”自动推断：

- `QUEUED -> COMPLETED`：必须说明任务是否根本没有执行，以及结果如何分类；
- `RUNNING -> COMPLETED`：必须有匹配响应或明确的本地模拟结果；
- `RUNNING -> REJECTED`：必须说明拒绝发生在本地、Router、Bridge 还是 MCU；
- `RUNNING -> UNKNOWN`：必须保留超时、断链或关联错误的原因；
- `CANCEL_REQUESTED -> COMPLETED`：必须区分“取消已确认”和“动作已完成后才收到结果”；
- `UNKNOWN -> COMPLETED`：必须有对账证据，不能只增加重试次数。

### 2.3 状态记录格式

一条状态事件至少包含：

| 字段 | 示例含义 |
| --- | --- |
| `task_id` | 本地任务标识 |
| `from`、`to` | 状态迁移前后 |
| `at` | 记录时间和时间基准 |
| `reason` | 队列满、超时、取消或响应分类原因 |
| `request_id` | 对应的跨边界请求 |
| `evidence` | 事件、响应、观察或人工决定的来源 |

这类事件不是为了把普通脚本写成复杂框架，而是为了在并发、重连和故障后仍能回答“任务在哪里停止”。如果只有一条最终异常日志，无法判断任务是没入队、已发送、已执行还是结果丢失。

## 3. Fig-25：有界任务生命周期

下面的状态图表达任务状态和停止点。它不表示 Python event loop 的线程数，不表示 Router 的内部状态，也不表示 MCU 的实时状态机。`UNKNOWN` 的两个出口都要求对账或人工决策。

<a id="fig-25-python-bridge-task-lifecycle"></a>

~~~mermaid
stateDiagram-v2
    [*] --> CREATED
    CREATED --> REJECTED: local validation fails
    CREATED --> QUEUED: accepted into bounded queue
    QUEUED --> REJECTED: queue full or policy denies
    QUEUED --> RUNNING: worker leases task
    RUNNING --> COMPLETED: correlated APPLIED plus observation
    RUNNING --> CANCEL_REQUESTED: caller requests cancellation
    CANCEL_REQUESTED --> COMPLETED: cooperative cancellation acknowledged
    CANCEL_REQUESTED --> UNKNOWN: remote result not known
    RUNNING --> UNKNOWN: deadline or transport lost
    UNKNOWN --> COMPLETED: reconciliation confirms APPLIED
    UNKNOWN --> REJECTED: reconciliation confirms not applied
    UNKNOWN --> [*]: human decision or safety freeze
    COMPLETED --> [*]
    REJECTED --> [*]
~~~

> 图示占位：图号=Fig-25；位置=本段之后；内容=展示 Python Bridge 任务从创建、入有界队列、worker 执行、取消、完成、拒绝到 UNKNOWN 对账的状态生命周期；来源=[资源索引](../../resources/references.md) 中已登记的 Python asyncio 资料、Arduino App specification 与本项目原创 Mermaid 重绘。

读图时要特别关注：

1. `QUEUE full` 是一个可判定的 `REJECTED`，不是无限扩容的理由；
2. 本地取消请求不保证远端动作已经停止，可能进入 `UNKNOWN`；
3. `UNKNOWN` 只有在对账确认后才可以进入已完成或已拒绝，人工安全冻结是合法终点；
4. 图中 `COMPLETED` 是任务生命周期结论，业务结果仍要单独记录。

## 4. 有界并发、队列与背压

### 4.1 为什么要有界

无界并发会把瞬时流量转化为多个风险：

- 内存中的请求数量持续增长，导致旧任务和新任务互相争抢资源；
- 超时任务仍占用 worker，新的健康查询反而无法执行；
- 同一资源上的控制动作交错，结果难以关联；
- 应用重启时无法知道哪些任务已发出、哪些任务只在本地排队；
- 失败重试把原本的压力再次放大，形成重试风暴。

有界队列不是简单的性能优化，而是一个安全边界。队列达到上限后，系统必须选择拒绝、延迟入口、降级为只读或交给人工，而不是默默接收更多任务。

### 4.2 并发上限与资源串行化

并发上限至少有两个维度：

| 维度 | 控制问题 | 典型策略 |
| --- | --- | --- |
| 全局上限 | App 同时允许多少任务进入执行阶段 | `Semaphore` 或固定 worker 数 |
| 资源上限 | 同一设备、通道或执行器能否并行 | `resource_key` 对应锁或分区队列 |

全局并发为 4，并不代表同一 MCU 功能可以同时执行 4 个动作。读取和控制可能需要不同的资源策略；高风险动作甚至应当与所有其他动作互斥。资源规则必须写进方法契约或运行手册，不应隐藏在一个无法解释的锁中。

### 4.3 背压的四种处理

当生产速度超过消费速度时，可以采用：

1. **阻塞提交**：调用方等待容量释放；适合上游本身可以等待的低风险请求；
2. **立即拒绝**：返回 `REJECTED_QUEUE_FULL`；适合必须快速失败的入口；
3. **丢弃低价值消息**：只对可重建的状态通知使用，不适合控制动作；
4. **降级**：暂停写入，只保留健康查询或最后状态观察。

无论采用哪种策略，都要记录队列容量、拒绝原因和任务标识。仅打印“队列满”而没有 `task_id`，会让后续对账失去入口。

### 4.4 顺序、公平和优先级

并发系统不能只看吞吐，还要说明顺序：

- 同一 `resource_key` 的副作用动作是否保持 FIFO；
- 优先级是否可能让普通健康查询永久饥饿；
- 超时任务从队列移除后，是否会留下一个不能再消费的租约；
- 重试任务是否回到原队列，还是需要经过新的健康门；
- 任务取消时，队列中的占位是否及时释放。

第一版实现可以选择 FIFO 和固定 worker，先确保状态可解释；只有在有明确证据和用例后，才增加优先级、抢占或复杂调度。

## 5. 超时、取消与 UNKNOWN

### 5.1 本地超时的含义

本地 `asyncio.wait_for` 超时，首先说明“调用方没有在期限内得到结果”。它并不自动证明远端没有执行，也不自动撤销已经发出的消息。若远端协议没有取消语义，Python 侧只能：

1. 保存原始 `task_id`、`request_id` 和调用摘要；
2. 把任务标记为 `UNKNOWN`；
3. 查询状态、读取幂等结果或等待明确的迟到响应；
4. 在没有对账结果时停止副作用重试。

### 5.2 取消的三个层次

| 层次 | 取消对象 | 可以确认什么 |
| --- | --- | --- |
| 排队取消 | 尚未被 worker 取得的本地任务 | 任务没有进入执行阶段，前提是队列记录可核验 |
| 协程取消 | Python 本地 `asyncio.Task` | 本地等待被取消；不自动证明远端动作停止 |
| 远端取消 | Bridge/MCU 明确支持的取消操作 | 只有收到取消确认并完成观察，才可提高结论强度 |

协作式取消意味着被取消的代码有机会释放本地资源、关闭等待和记录状态；它不是强行终止一个可能已经影响硬件的动作。控制类调用需要把取消能力写入协议，而不是仅依赖 Python 任务的 `cancel()`。

### 5.3 UNKNOWN 的冻结规则

出现以下任一情况，默认冻结自动副作用动作：

- 本地期限到达但请求可能已经发出；
- 任务被取消时已经进入 `RUNNING`；
- 收到与当前 `request_id` 不匹配的迟到响应；
- Bridge 重连后无法确认前一请求是否应用；
- 本地结果与 MCU 后置观察相互矛盾。

冻结并不意味着系统停止所有功能。可以允许只读状态查询、证据收集和人工审批，但必须把它们与原动作分开记录。

## 6. 概念实验一：有界队列与 worker

这个实验在内存中创建容量为 2 的队列。前三个任务先在 worker 启动前提交，因此第三个任务会得到明确的队列满拒绝；随后一个 worker 依次处理前两个任务。实验验证背压和生命周期记录，不执行任何 Bridge 调用。

**代码说明**

- 用途：验证有界队列、立即拒绝、worker 取得任务和完成事件。
- 运行环境：Python 3.10 或更高版本；Windows、Linux 或 macOS 均可。
- 文件位置：可保存为 `code/第4篇_PythonBridge/ch02_bounded_dispatcher.py`；本章只在正文中提供示例。
- 依赖：仅 Python 标准库 `asyncio` 和 `dataclasses`，无需安装第三方包。
- 操作步骤：将代码保存到临时目录后执行 `python ch02_bounded_dispatcher.py`；不要把真实设备动作放入 `Job`。
- 预期输出：前两个任务入队，第三个任务得到 `REJECTED_QUEUE_FULL`，前两个任务依次产生 `RUNNING` 和 `COMPLETED`。
- 故障排查：若第三个任务没有被拒绝，检查任务是否在 worker 启动前提交以及队列容量是否确实为 2；若程序不退出，检查 `queue.task_done()` 和 `queue.join()` 是否成对出现。
- 验证方式：核对每个接受的任务都有一次运行和一次完成事件，并确认队列满时没有隐式扩容。

~~~python
from __future__ import annotations

import asyncio
from dataclasses import dataclass


@dataclass(frozen=True)
class Job:
    task_id: str
    duration: float


class BoundedDispatcher:
    def __init__(self, maxsize: int) -> None:
        self.queue: asyncio.Queue[Job] = asyncio.Queue(maxsize=maxsize)
        self.events: list[tuple[str, str]] = []

    def submit(self, job: Job) -> bool:
        try:
            self.queue.put_nowait(job)
        except asyncio.QueueFull:
            self.events.append((job.task_id, "REJECTED_QUEUE_FULL"))
            return False
        self.events.append((job.task_id, "QUEUED"))
        return True

    async def worker(self) -> None:
        while True:
            job = await self.queue.get()
            self.events.append((job.task_id, "RUNNING"))
            try:
                await asyncio.sleep(job.duration)
                self.events.append((job.task_id, "COMPLETED"))
            finally:
                self.queue.task_done()


async def main() -> None:
    dispatcher = BoundedDispatcher(maxsize=2)
    for job in (
        Job("task-001", 0.01),
        Job("task-002", 0.01),
        Job("task-003", 0.01),
    ):
        dispatcher.submit(job)

    worker = asyncio.create_task(dispatcher.worker())
    await dispatcher.queue.join()
    worker.cancel()
    try:
        await worker
    except asyncio.CancelledError:
        pass

    for task_id, state in dispatcher.events:
        print(f"{task_id}: {state}")


if __name__ == "__main__":
    asyncio.run(main())
~~~

示例输出：

~~~text
task-001: QUEUED
task-002: QUEUED
task-003: REJECTED_QUEUE_FULL
task-001: RUNNING
task-001: COMPLETED
task-002: RUNNING
task-002: COMPLETED
~~~

实验结果只说明本地队列按容量拒绝了第三个任务。它没有说明 Bridge 是否可达、MCU 是否空闲或控制动作是否安全。真实系统还要把 `resource_key`、请求契约、权限和后置观察加入任务记录。

## 7. 概念实验二：超时、对账与协作式取消

这个实验演示两个容易混淆的情况：

1. 使用 `asyncio.shield` 保护一个仍可能继续运行的本地替身；外层等待超时后先记录 `UNKNOWN`，再等待替身结果完成对账；
2. 取消一个本地任务，观察本地任务进入取消状态，但不把它解释成远端动作已经取消。

**代码说明**

- 用途：验证本地等待超时、对账和协作式任务取消之间的区别。
- 运行环境：Python 3.10 或更高版本；普通本地终端即可。
- 文件位置：可保存为 `code/第4篇_PythonBridge/ch02_timeout_reconcile.py`；本章只在正文中提供示例。
- 依赖：仅 Python 标准库 `asyncio`，无网络、设备和第三方依赖。
- 操作步骤：保存后执行 `python ch02_timeout_reconcile.py`；示例中的远端替身只返回内存字典。
- 预期输出：第一次等待先得到 `UNKNOWN`，对账后得到 `APPLIED`；第二个本地任务被明确标记为 `CANCELLED_LOCAL`。
- 故障排查：如果没有出现超时，保持远端替身延迟大于 `wait_for` 期限；如果取消任务没有结束，检查是否在 `await task` 处捕获了 `asyncio.CancelledError`。
- 验证方式：确认超时和对账是两个事件，确认本地取消没有被写成远端硬件取消。

~~~python
from __future__ import annotations

import asyncio


async def simulated_remote(
    task_id: str,
    delay: float,
    result_state: str,
) -> dict[str, str]:
    await asyncio.sleep(delay)
    return {"task_id": task_id, "state": result_state}


async def timeout_then_reconcile() -> None:
    remote_task = asyncio.create_task(
        simulated_remote("task-004", delay=0.02, result_state="APPLIED")
    )
    try:
        await asyncio.wait_for(asyncio.shield(remote_task), timeout=0.005)
    except asyncio.TimeoutError:
        print("local decision: UNKNOWN")

    result = await remote_task
    print(f"reconciliation: {result['task_id']} -> {result['state']}")


async def cancel_local_task() -> None:
    local_task = asyncio.create_task(
        simulated_remote("task-005", delay=0.05, result_state="APPLIED")
    )
    await asyncio.sleep(0)
    local_task.cancel()
    try:
        await local_task
    except asyncio.CancelledError:
        print("local task: CANCELLED_LOCAL")


async def main() -> None:
    await timeout_then_reconcile()
    await cancel_local_task()


if __name__ == "__main__":
    asyncio.run(main())
~~~

示例输出：

~~~text
local decision: UNKNOWN
reconciliation: task-004 -> APPLIED
local task: CANCELLED_LOCAL
~~~

这里的 `simulated_remote` 仍然只是本地协程。`shield` 的教学意义是：外层等待超时不必然取消底层等待；在真实 Bridge 中，底层请求可能已经离开 Python 进程，更不能把 Python `Task.cancel()` 当成 MCU 的取消协议。只有远端明确支持取消，并返回可关联的取消结果，才可以进一步提高结论强度。

## 8. 并发调用运行手册

### 8.1 进入队列前

1. 校验方法、参数、权限、契约版本和 `resource_key`。
2. 为任务生成 `task_id`，并将它与 `request_id` 建立明确映射。
3. 判断动作是否幂等、是否允许排队、是否允许取消。
4. 检查队列容量和全局并发预算；容量不足时返回明确的 `REJECTED_QUEUE_FULL`。
5. 写入脱敏的 `CREATED` 或 `REJECTED` 事件，不记录完整敏感参数。

### 8.2 worker 执行时

1. worker 取得任务时写入 `QUEUED -> RUNNING` 事件和时间。
2. 同一资源的危险动作使用串行化策略，不通过增加 worker 数绕过互斥要求。
3. 每次等待都有有限期限；不要让一个失去响应的任务无限占用 worker。
4. 响应先做 `request_id`、契约和状态校验，再更新任务结果。
5. 对超时、断链和错配响应统一进入 `UNKNOWN`，冻结自动副作用重试。

### 8.3 结束或交接时

1. `APPLIED` 结果仍要完成约定的后置观察，才能写入更强的业务结论。
2. `REJECTED` 保留原因、来源层次和修正建议，不重复提交相同非法请求。
3. `UNKNOWN` 保留最后观察、原始标识和人工决策入口。
4. 队列关闭时先停止接收新任务，再等待可安全收尾的任务，最后取消空闲 worker。
5. 应用重启或 Bridge 重连后，先恢复状态查询和证据收集，再恢复副作用动作。

## 9. 故障矩阵

| 现象 | 可能层次 | 不应直接得出的结论 | 推荐动作 |
| --- | --- | --- | --- |
| 队列持续满 | 流量或消费能力 | 只要增加队列容量就能解决 | 记录生产/消费速率，拒绝或降级，评估 worker 与资源边界 |
| worker 被单个任务长期占用 | 远端调用或本地等待 | 继续增加 worker 一定安全 | 设定 deadline，隔离资源，超时进入 UNKNOWN |
| 任务被本地取消 | Python 调度层 | MCU 动作已停止 | 查询远端状态；没有取消确认时保持 UNKNOWN |
| 超时后收到迟到响应 | 关联和生命周期 | 迟到响应就是当前新请求结果 | 按原 request_id 对账，拒绝跨任务消费 |
| 并发动作互相覆盖 | 资源建模 | Bridge 随机丢消息 | 检查 resource_key、串行化规则和状态机 |
| 重连后重复提交 | 恢复和幂等 | 重试次数不足 | 先恢复查询和幂等结果，再决定是否允许重试 |
| 低优先级健康查询长期没有机会 | 调度公平性 | 只提高健康查询优先级 | 评估优先级反转、保留配额和限时调度 |

## 10. 本章验证矩阵

| 编号 | 验证项 | 本地可验证内容 | 当前未覆盖内容 |
| --- | --- | --- | --- |
| TASK-01 | 状态定义 | 状态集合和迁移路径可读 | 目标 Bridge 的实际状态事件 |
| TASK-02 | 有界队列 | 队列满时明确拒绝第三个任务 | 现场入口流量和内存预算 |
| TASK-03 | worker 生命周期 | 入队、运行、完成事件成对出现 | 多 worker 竞争和资源锁 |
| TASK-04 | 超时对账 | 外层超时先 UNKNOWN，再读取对账结果 | 远端迟到响应和状态缓存 |
| TASK-05 | 本地取消 | Task.cancel() 只产生本地取消证据 | MCU 取消协议 |
| TASK-06 | 图示追溯 | 正文 Mermaid 与 Fig-25 源文件一致 | SVG 渲染和视觉审阅 |
| TASK-07 | 导航 | SUMMARY、篇入口和图示登记可达 | GitHub 页面实际渲染 |
| TASK-08 | 实机闭环 | 未执行，保持范围声明 | Router、Bridge、App Lab、MCU 和 UNO Q 实机 |

本章状态保持为 `draft`。两个 Python 示例验证的是本地 asyncio 规则，不是并发性能基线；不能据此确定 UNO Q 的吞吐、实时性、队列容量或安全动作延迟。

## 11. 与前后章节的交接

- 前置章节：[第四篇第1章：消息模型与调用边界](./第1章_Python_Bridge开发基础_消息模型与调用边界.md)，提供 `request_id`、结果状态、幂等和 UNKNOWN 规则。
- 运行治理：[第三篇第5章：现场自动化与 Python Bridge](../第3篇_Linux/第5章_Linux现场自动化与Python_Bridge_队列重连与状态缓存.md)，提供队列、背压、重连和缓存 freshness 的运行背景。
- 测试治理：[第三篇第6章：现场测试与性能治理](../第3篇_Linux/第6章_Linux与Python_Bridge现场测试与性能治理_从基准压测到故障注入.md)，用于区分概念实验和现场性能预算。
- 综合运行：[第三篇第8章：综合运行手册](../第3篇_Linux/第8章_Linux与Python_Bridge综合运行手册_从预检到交接.md)，用于处理 UNKNOWN、证据包、健康门和交接。
- 后续章节：[第四篇第3章：连接复用与请求恢复](./第3章_Python_Bridge连接复用与请求恢复_从断线到可判定结果.md)继续讨论连接所有权、退避和未决请求；本章的任务状态是连接管理的输入。

## 12. 常见问题

### Q1：队列满时为什么不自动等待？

是否等待取决于入口性质。对低风险读取，等待可能合理；对控制动作或已经接近 deadline 的请求，立即拒绝更容易保持边界。无论选择什么，都要让调用方看到明确结果。

### Q2：增加 worker 数是不是可以提高所有场景的性能？

不是。同一资源可能要求串行，Bridge、MCU 或网络也可能成为瓶颈。增加 worker 还会增加并发副作用、关联复杂度和取消成本。

### Q3：本地任务取消后，为什么还要查询远端？

因为取消动作发生在本地调度层，而请求可能已经发送。没有远端取消确认或状态查询，不能排除动作已经执行。

### Q4：UNKNOWN 会不会导致系统永远停住？

如果没有对账和人工流程，确实可能。正确做法不是把 UNKNOWN 改成失败，而是提供只读查询、幂等结果、人工裁决和安全冻结的恢复路径。

### Q5：为什么实验使用很短的 sleep？

实验只需要展示状态顺序，不需要模拟现场延迟。短时间让示例更容易复现；真实时间预算必须在目标系统上单独测量。

### Q6：asyncio 任务可以代表 MCU 任务吗？

不能。它只能帮助理解 Linux/Python 侧的本地调度。MCU 的实时任务、硬件中断、状态机和安全输出仍属于另一层证据。

### Q7：任务完成是否就可以从内存删除？

要先确认结果、观察和交接记录已经落盘或交给可靠的证据系统。对 UNKNOWN 和未决任务，不应只保留一个异常字符串后删除上下文。

## 13. 本章小结

本章把第一章的单次消息扩展为可管理的任务生命周期：

1. 调用、本地任务和远端动作是三个不同对象，完成点和证据来源不能混淆。
2. `CREATED`、`QUEUED`、`RUNNING`、`CANCEL_REQUESTED`、`COMPLETED`、`REJECTED` 和 `UNKNOWN` 让停止点可见。
3. 有界队列和并发上限是安全边界；队列满时应拒绝、阻塞或降级，不能静默无限扩容。
4. 本地超时或取消不自动代表远端停止；没有对账时必须保持 `UNKNOWN`。
5. asyncio 概念实验只能验证本地调度逻辑，不能生成 UNO Q、Bridge、MCU 或现场性能证据。

下一阶段的连接复用和重连设计，必须以本章的 `task_id`、`request_id`、资源键和 UNKNOWN 交接为输入，不能只围绕“如何把连接保持住”展开。

## 延伸阅读

- [第四篇第1章：消息模型与调用边界](./第1章_Python_Bridge开发基础_消息模型与调用边界.md)
- [第三篇第5章：队列、重连与状态缓存](../第3篇_Linux/第5章_Linux现场自动化与Python_Bridge_队列重连与状态缓存.md)
- [第三篇第6章：测试与性能治理](../第3篇_Linux/第6章_Linux与Python_Bridge现场测试与性能治理_从基准压测到故障注入.md)
- [资源索引](../../resources/references.md)
- [Fig-25 图示登记](../../images/第4篇_PythonBridge/README.md)
