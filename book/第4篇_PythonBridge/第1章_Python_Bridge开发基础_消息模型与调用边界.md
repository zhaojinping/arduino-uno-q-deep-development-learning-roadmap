---
title: Python Bridge 开发基础：消息模型与调用边界
part: 4
chapter: 1
status: draft
last_verified: 2026-09-22
updated: 2026-09-22
prerequisites: 第二篇第9章、第三篇第4章和第三篇第8章
tags: Python Bridge, Router, RPC, 消息, 幂等
---

# 第1章 Python Bridge 开发基础：消息模型与调用边界

## 学习目标

完成本章后，读者应能够：

- 解释 Linux 侧 Python App、Router、Bridge/RPC 和 MCU 侧 Arduino Sketch 之间的职责边界；
- 为一次跨处理器调用设计可关联、可脱敏、可审计的请求信封；
- 区分请求、响应、通知、拒绝、超时和 `UNKNOWN`，避免把传输层结果误写成业务结果；
- 根据动作是否幂等决定超时后的下一步，而不是在未知状态下盲目重试；
- 在普通 Python 3 环境中运行两个不触碰设备的概念实验，验证消息分类和重试决策；
- 为后续的 App Lab、Router/Bridge 联调和综合项目准备一份可复用的调用运行手册。

本章是第四篇的第一章。章节编号在新篇章重新从第 1 章开始，不沿用第三篇的编号。第三篇第 8 章已经把 Linux、服务、测试和交接治理收束为运行前提；本章进一步回答“应用代码如何表达一次跨处理器调用”，但不宣称已经完成 UNO Q 实机联调。

## 背景与边界

Arduino UNO Q 将 Linux 侧的应用能力与微控制器（Microcontroller Unit，MCU）侧的实时控制能力放在同一块板卡上。Linux 侧适合承载 Python、文件、网络、数据处理和应用编排；MCU 侧适合承载时序敏感的 GPIO、采样、定时和执行器控制。两侧通过 Bridge/RPC（Remote Procedure Call，远程过程调用）形成逻辑协作。

本章采用以下事实与限制：

1. Arduino App specification 用 App、Python、Arduino Sketch 和 RPC 描述两侧组件的组织方式；正文按照这一职责模型解释消息，而不把概念模型误写成当前镜像的实测实现。
2. Arduino Router 是消息转发与连接基础的一部分；Router 连接成功，只能说明消息通道具有可达性，不能单独证明 MCU 已接受某个业务动作。
3. 本章所有 Python 示例只使用标准库，在本地内存中构造和分类消息；不会调用 ADB、SSH、`systemctl`、Router、网络、串口、GPIO 或真实硬件。
4. 示例中的 `APPLIED`、`REJECTED` 和 `UNKNOWN` 是教学用结果状态。只有在目标设备执行动作并有独立的后置观察时，才可以把运行结论提升为现场证据。

因此，本章先建立“消息契约”，后续章节再讨论 App Lab 入口、并发、连接复用、真实设备观测和综合项目。边界如果没有写清楚，Python 代码很容易从“发出请求”跳跃到“设备已经动作”的错误结论。

## 1. 双侧应用的职责模型

### 1.1 五个角色

一次典型调用至少包含五类角色。这里的“角色”是逻辑职责，不要求每个角色都对应一个独立进程：

| 角色 | 主要职责 | 不应越权承担的职责 | 需要留下的证据 |
| --- | --- | --- | --- |
| Python App | 组织业务意图、校验参数、生成请求、关联响应、记录结果 | 不直接假设 MCU 已执行；不绕过授权和安全状态机 | 请求摘要、关联标识、分类结果 |
| Router | 发现或转发两侧消息，维护通道级可达性 | 不替代业务确认；不把转发成功伪装成动作完成 | 路由状态、传输错误、时间窗口 |
| Bridge/RPC | 把一侧的调用映射到另一侧可调用能力 | 不替代方法级参数校验和后置观察 | 方法名、参数摘要、响应关联 |
| MCU Sketch | 校验安全条件、执行实时动作、返回可解释结果 | 不承担 Linux 文件、网络和长时间业务编排 | 接受/拒绝原因、状态快照、硬件证据 |
| Evidence/Observer | 收集脱敏日志、响应和后置观察，帮助判定结果 | 不修改原始事实，不把推测补成结果 | 时间、请求标识、状态和观察来源 |

这五个角色构成的是一条证据链：

~~~text
业务意图
  -> 请求信封
  -> 路由可达
  -> 方法调用
  -> MCU 接受或拒绝
  -> 响应关联
  -> 后置观察
  -> 最终结论
~~~

其中前四步并不自动等于最后一步。例如，Router 日志显示消息已经转发，不表示 MCU 的安全条件满足；Bridge 返回一个响应，也不代表返回内容已经与当前请求关联。每一层都要对自己的边界负责。

### 1.2 传输层、调用层和业务层要分开

建议把结果拆成三个维度，而不是只保存一个布尔值：

- **传输层**：消息是否能够发出、到达或收到字节，例如 `DELIVERED`、`TIMEOUT`；
- **调用层**：方法是否被识别、参数是否被接受，例如 `ACCEPTED`、`REJECTED`；
- **业务层**：目标状态是否已经达到并被观察，例如 `APPLIED`、`UNKNOWN`。

一个请求可能“传输层已发送、调用层未知、业务层未知”。这正是超时后的典型状态。把它压缩成 `False`，会丢失重试风险；把它写成 `True`，又会制造没有证据的成功结论。

## 2. Fig-24：Python Bridge 消息生命周期

下面的时序图只表达消息生命周期和停止点，不表示真实物理连线、线程数量、端口号或当前固件的内部实现。`request_id` 是应用侧生成的关联标识；`Evidence` 代表脱敏记录与后置观察，不是另一个必然存在的系统进程。

<a id="fig-24-python-bridge-message-lifecycle"></a>

~~~mermaid
sequenceDiagram
    participant P as Python App
    participant R as Router
    participant B as Bridge/RPC
    participant M as MCU Sketch
    participant E as Evidence

    P->>P: validate and create request_id
    P->>R: request_id + method + args
    R->>B: route message
    B->>M: invoke
    alt MCU accepts
        M-->>B: APPLIED + result
        B-->>R: correlated response
        R-->>P: APPLIED
        P->>E: record response and observation
    else MCU rejects
        M-->>B: REJECTED + reason
        B-->>R: correlated error
        R-->>P: REJECTED
        P->>E: record rejection
    else timeout or correlation mismatch
        R--x P: timeout or mismatched response
        P->>E: record UNKNOWN and freeze retry
    end
~~~

> 图示占位：图号=Fig-24；位置=本段之后；内容=展示 Python App、Router、Bridge/RPC、MCU Sketch 与证据记录之间的请求、响应、拒绝和 UNKNOWN 生命周期；来源=[资源索引](../../resources/references.md) 中已登记的 Arduino App specification、Arduino Router 与本项目原创 Mermaid 重绘。

读图时要注意三点：

1. `APPLIED` 只有在 MCU 返回可解释结果并且 Python 侧完成响应关联后，才进入记录路径；如果还缺少独立的后置观察，现场结论仍应标注证据不足。
2. `REJECTED` 是可判定的拒绝，通常可以修正参数、权限或前置条件后重新评审；它和通信失败不是同一类结果。
3. 超时或关联标识不匹配进入 `UNKNOWN`。在查询、对账或人工裁决前，Python App 应冻结自动重试。

## 3. 消息模型：从信封到结果

### 3.1 请求信封的最小字段

请求信封不需要一开始就包含所有业务字段，但必须能回答“谁在什么时候请求什么、怎样关联和何时失效”：

| 字段 | 类型 | 作用 | 安全与验证要求 |
| --- | --- | --- | --- |
| `request_id` | 字符串 | 关联请求、响应和证据 | 非空、在有效窗口内唯一；不要放入密码或个人信息 |
| `method` | 字符串 | 指定可调用能力 | 只能来自允许的方法集合；不要把任意代码表达式当方法 |
| `args` | 对象 | 业务参数 | 按方法 schema 校验大小、类型、范围和单位 |
| `deadline_ms` | 正整数 | 请求的有效期限 | 必须大于零；不能用无限等待替代超时策略 |
| `contract` | 字符串 | 标识消息契约版本 | 契约变化时显式升级或拒绝，不静默兼容 |
| `mode` | 字符串 | 区分 `call`、`notify` 等调用语义 | 默认采用最保守的等待确认语义 |
| `idempotency_key` | 字符串或空 | 帮助接收端去重 | 对可能重复执行的动作必须有明确生成和保存策略 |

`request_id` 负责“这条消息属于哪一次请求”；`idempotency_key` 负责“重复到达时是否仍被视为同一个动作”。两者可以相同，也可以不同，但不能因为有了 `request_id` 就假设接收端天然幂等。

### 3.2 响应不是单纯的返回值

响应至少要有以下信息：

| 字段 | 说明 |
| --- | --- |
| `request_id` | 必须与当前等待的请求匹配；不匹配时不得直接消费 |
| `state` | 建议使用 `APPLIED`、`REJECTED` 或 `UNKNOWN` |
| `result` | 成功时的脱敏结果或状态摘要，不能用日志推测代替 |
| `reason` | 拒绝、未知或失败的机器可读原因 |
| `observed_at` | 接收端或观察端的时间信息，需注明时间基准 |
| `contract` | 响应使用的契约版本 |

当响应缺少 `request_id`、状态值未知、契约版本不兼容或结果字段无法解释时，默认分类为 `UNKNOWN`，而不是“尽量猜测”。严格分类会增加少量人工处理，但能阻止错误状态向上游扩散。

### 3.3 请求、通知和错误的区别

| 消息类型 | 是否等待响应 | 适合场景 | 主要风险 |
| --- | --- | --- | --- |
| `call` | 是 | 需要明确结果的读取或受控动作 | 超时后的副作用和重复执行 |
| `notify` | 否或不保证 | 低风险状态提示、日志或无副作用事件 | 发送成功不能证明接收，更不能证明动作完成 |
| `response` | 对应一个 `call` | 返回状态、结果和原因 | 关联错误导致误消费 |
| `error` | 对应请求或协议错误 | 参数拒绝、契约不兼容、方法不存在 | 把错误详情直接写入日志造成泄密 |

控制输出、继电器、运动和其他有副作用的方法，不应默认使用“无需响应”的通知语义。通知可以用于意图提示，但必须另有状态查询或观察路径，否则无法判定最终状态。

## 4. 调用边界：call、notify 与 provide

### 4.1 三种语义

为了让调用方和提供方对等待、失败和副作用有共同预期，本书使用以下三个词：

| 语义 | 调用方行为 | 提供方行为 | 章节中的默认规则 |
| --- | --- | --- | --- |
| `call` | 发送请求并等待匹配响应 | 校验、执行或拒绝，并返回结果 | 适合需要结果的动作和读取 |
| `notify` | 发送后继续运行，不把发送成功当完成 | 尽力接收，是否处理不保证 | 仅用于低风险、无副作用事件 |
| `provide` | 不主动发起，调用已公开能力 | 暴露方法、schema、状态和错误 | 必须有白名单、参数边界和版本契约 |

`provide` 不是“给 Python 任意执行 MCU 代码”的入口。它应当只暴露经过设计的能力，例如“读取温度”“设置一个经过范围限制的占空比”或“查询执行状态”。提供方仍然拥有最后的安全拒绝权。

### 4.2 方法边界的四道门

一个 Bridge 方法在进入 MCU 前，至少要过四道门：

1. **方法门**：方法名存在并且当前角色有权调用；
2. **参数门**：字段、类型、单位、范围、数据量和版本正确；
3. **时序门**：当前状态允许动作，不能在故障、急停或初始化未完成时执行；
4. **结果门**：调用返回后，Python 侧能将响应与请求关联，并能说明是否还需要后置观察。

前两道门可以在 Python 侧提前做，第三道门必须在 MCU 侧再次做，第四道门由调用方和证据系统共同完成。客户端校验不能替代接收端校验，因为请求可能来自旧版本、错误配置或不受信任的调用者。

## 5. 超时、幂等与 UNKNOWN

### 5.1 超时不等于没有执行

至少要区分以下情况：

| 观察 | 更准确的解释 | 默认下一步 |
| --- | --- | --- |
| 未发出请求 | 本地校验或前置健康门拒绝 | 修正输入或停止 |
| 发出前超时 | 请求没有进入调用边界 | 可以重新生成请求，但要保留拒绝证据 |
| 已发送但未收到响应 | 接收、执行或返回路径未知 | 查询、对账或人工裁决 |
| 收到 `REJECTED` | 接收端明确拒绝 | 停止当前动作，修正原因 |
| 收到 `APPLIED` 但缺少观察 | 方法报告成功，外部状态还未独立确认 | 补后置观察，不扩大结论 |
| 响应 `request_id` 不匹配 | 可能是迟到消息、复用错误或协议异常 | 丢弃为当前响应，记录 `UNKNOWN` |

最危险的自动化代码是：

~~~text
try:
    call()
except Timeout:
    call()  # 未确认状态就重复动作
~~~

正确的路径应是：

~~~text
timeout
  -> 保存原 request_id 和摘要
  -> 查询状态或读取幂等结果
  -> 能确认 APPLIED/REJECTED 才结束
  -> 仍无法确认则 UNKNOWN，暂停自动动作
~~~

### 5.2 幂等决定是否允许重试

幂等不是“调用看起来简单”，而是重复请求不会产生额外不期望副作用，或者接收端能够利用幂等键把重复请求折叠为同一次动作。读取通常更容易设计为幂等；设置目标值可以通过明确的资源版本或幂等键做到幂等；“向前移动 100 步”“翻转一次继电器”则不能因为网络重试就自动视为幂等。

本章采用如下决策：

| 当前状态 | 动作幂等 | 尝试次数未达上限 | 决策 |
| --- | --- | --- | --- |
| `APPLIED` | 任意 | 任意 | 停止并记录成功 |
| `REJECTED` | 任意 | 任意 | 停止并记录拒绝 |
| `UNKNOWN` | 否 | 任意 | `ESCALATE_UNKNOWN`，等待人工或明确对账 |
| `UNKNOWN` | 是 | 是 | `RECONCILE_BEFORE_RETRY`，先对账再决定 |
| `UNKNOWN` | 是 | 否 | `ESCALATE_UNKNOWN` |

“先对账再重试”不是永远重试。对账可能发现动作已经生效，也可能发现动作没有发生，还可能仍然无法判定。只有第三种结果仍保持 `UNKNOWN`，不能凭借重试次数把未知变成失败。

## 6. 概念实验一：构造信封并分类响应

这个实验验证三件事：请求字段是否在构造时被约束；响应是否按 `request_id` 关联；写入日志前是否能够脱敏。脚本不建立任何网络连接，所有响应都是本地构造的替身。

**代码说明**

- 用途：在本地验证请求信封、响应分类和参数脱敏规则。
- 运行环境：Python 3.10 或更高版本；Windows、Linux 或 macOS 均可。
- 文件位置：可保存为 `code/第4篇_PythonBridge/ch01_message_contract.py`；本章只在正文中提供示例。
- 依赖：仅 Python 标准库 `json` 和 `typing`，无需安装第三方包。
- 操作步骤：将代码保存到临时目录后执行 `python ch01_message_contract.py`；不要填写真实密钥、设备地址、序列号或业务数据。
- 预期输出：打印一条脱敏请求、一个 `APPLIED`、一个 `REJECTED` 和一个因关联标识不匹配产生的 `UNKNOWN`；最后展示非法信封被拒绝。
- 故障排查：若提示 Python 版本过低，使用 Python 3.10+；若输出含真实参数，说明脱敏函数未在记录前调用，应立即停止并删除该测试记录。
- 验证方式：检查所有响应分类都与其 `request_id` 和 `state` 一致，并确认异常输入没有进入发送路径。

~~~python
from __future__ import annotations

import json
from typing import Any


def build_request(
    request_id: str,
    method: str,
    args: dict[str, Any],
    deadline_ms: int,
) -> dict[str, Any]:
    if not request_id or not method or deadline_ms <= 0:
        raise ValueError("invalid request envelope")
    if not isinstance(args, dict):
        raise TypeError("args must be an object")
    return {
        "request_id": request_id,
        "method": method,
        "args": args,
        "deadline_ms": deadline_ms,
        "contract": "bridge-v1",
        "mode": "call",
    }


def classify_response(
    response: dict[str, Any],
    expected_request_id: str,
) -> dict[str, Any]:
    if response.get("request_id") != expected_request_id:
        return {"state": "UNKNOWN", "reason": "request_id_mismatch"}
    if response.get("state") in {"APPLIED", "REJECTED", "UNKNOWN"}:
        return {
            "state": response["state"],
            "reason": response.get("reason", ""),
        }
    return {"state": "UNKNOWN", "reason": "unsupported_response_state"}


def redact_request(request: dict[str, Any]) -> dict[str, Any]:
    safe = dict(request)
    safe["args"] = "[REDACTED]"
    return safe


def main() -> None:
    request = build_request(
        request_id="demo-001",
        method="read_temperature",
        args={"channel": 0},
        deadline_ms=500,
    )
    print(
        "脱敏请求:",
        json.dumps(redact_request(request), ensure_ascii=False, sort_keys=True),
    )

    responses = [
        {"request_id": "demo-001", "state": "APPLIED", "result": {"c": 23.5}},
        {
            "request_id": "demo-001",
            "state": "REJECTED",
            "reason": "channel_not_ready",
        },
        {"request_id": "late-999", "state": "APPLIED", "result": {"c": 23.5}},
    ]
    for response in responses:
        print("响应分类:", classify_response(response, request["request_id"]))

    try:
        build_request("", "read_temperature", {}, 500)
    except ValueError as exc:
        print("非法信封:", exc)


if __name__ == "__main__":
    main()
~~~

示例输出：

~~~text
脱敏请求: {"args": "[REDACTED]", "contract": "bridge-v1", "deadline_ms": 500, "method": "read_temperature", "mode": "call", "request_id": "demo-001"}
响应分类: {'state': 'APPLIED', 'reason': ''}
响应分类: {'state': 'REJECTED', 'reason': 'channel_not_ready'}
响应分类: {'state': 'UNKNOWN', 'reason': 'request_id_mismatch'}
非法信封: invalid request envelope
~~~

这段代码没有验证温度是否真实存在，也没有验证设备是否真的执行了动作。它只证明本地分类规则能够把“正确关联”“明确拒绝”和“迟到或错配响应”区分开。

## 7. 概念实验二：根据状态决定重试或升级

第二个实验把超时后的决策显式化。它不执行重试，只输出下一步建议；这样可以在接入真实 Bridge 前先审查策略，避免把网络异常变成重复硬件动作。

**代码说明**

- 用途：验证 `APPLIED`、`REJECTED`、`UNKNOWN` 在不同幂等性和尝试次数下的决策。
- 运行环境：Python 3.10 或更高版本；普通本地终端即可。
- 文件位置：可保存为 `code/第4篇_PythonBridge/ch01_retry_policy.py`；本章只在正文中提供示例。
- 依赖：仅 Python 标准库，无网络、设备和第三方依赖。
- 操作步骤：保存后执行 `python ch01_retry_policy.py`；只使用示例中的虚拟请求标识和状态。
- 预期输出：已应用和已拒绝分别停止；幂等未知状态先对账；非幂等未知状态和达到上限的未知状态升级处理。
- 故障排查：如果未知状态直接输出重试，检查 `decide_retry` 的状态分支；如果状态拼写变化，必须先进入 `ESCALATE_UNSUPPORTED`，不要静默兼容。
- 验证方式：逐项对照本章的重试决策表，确认每个 `UNKNOWN` 都没有被直接改写为成功或失败。

~~~python
from __future__ import annotations

import json


def decide_retry(
    state: str,
    idempotent: bool,
    attempts: int,
    max_attempts: int,
) -> str:
    if state == "APPLIED":
        return "STOP_APPLIED"
    if state == "REJECTED":
        return "STOP_REJECTED"
    if state == "UNKNOWN":
        if not idempotent:
            return "ESCALATE_UNKNOWN"
        if attempts < max_attempts:
            return "RECONCILE_BEFORE_RETRY"
        return "ESCALATE_UNKNOWN"
    return "ESCALATE_UNSUPPORTED"


def summarize_unknown(
    request_id: str,
    reason: str,
    last_observation: str,
) -> dict[str, str]:
    return {
        "request_id": request_id,
        "state": "UNKNOWN",
        "reason": reason,
        "last_observation": last_observation,
        "next_action": "reconcile_or_human_decision",
    }


def main() -> None:
    cases = [
        ("APPLIED", True, 1, 3),
        ("REJECTED", False, 1, 3),
        ("UNKNOWN", True, 1, 3),
        ("UNKNOWN", False, 1, 3),
        ("UNKNOWN", True, 3, 3),
    ]
    for state, idempotent, attempts, max_attempts in cases:
        decision = decide_retry(state, idempotent, attempts, max_attempts)
        print(
            "决策:",
            json.dumps(
                {
                    "state": state,
                    "idempotent": idempotent,
                    "attempts": attempts,
                    "decision": decision,
                },
                ensure_ascii=False,
                sort_keys=True,
            ),
        )

    print(
        "未知摘要:",
        json.dumps(
            summarize_unknown("demo-002", "response_timeout", "no correlated response"),
            ensure_ascii=False,
            sort_keys=True,
        ),
    )


if __name__ == "__main__":
    main()
~~~

示例输出：

~~~text
决策: {"attempts": 1, "decision": "STOP_APPLIED", "idempotent": true, "state": "APPLIED"}
决策: {"attempts": 1, "decision": "STOP_REJECTED", "idempotent": false, "state": "REJECTED"}
决策: {"attempts": 1, "decision": "RECONCILE_BEFORE_RETRY", "idempotent": true, "state": "UNKNOWN"}
决策: {"attempts": 1, "decision": "ESCALATE_UNKNOWN", "idempotent": false, "state": "UNKNOWN"}
决策: {"attempts": 3, "decision": "ESCALATE_UNKNOWN", "idempotent": true, "state": "UNKNOWN"}
未知摘要: {"last_observation": "no correlated response", "next_action": "reconcile_or_human_decision", "reason": "response_timeout", "request_id": "demo-002", "state": "UNKNOWN"}
~~~

真实系统还需要把“对账”具体化，例如查询目标状态、读取接收端的幂等结果缓存、检查 MCU 状态机版本或由人工确认现场输出。概念实验只验证决策顺序，不提供这些设备级证据。

## 8. 一次 Bridge 调用的运行手册

将上面的规则合并到实际开发时，可以按以下顺序组织一次调用：

### 8.1 调用前

1. 明确目标方法、输入单位、允许范围和是否存在副作用。
2. 检查本地配置、契约版本和权限；缺少必要条件时在发送前返回 `REJECTED`。
3. 生成唯一 `request_id`，为可重复动作生成可保存的 `idempotency_key`。
4. 记录脱敏请求摘要，不把完整参数、凭据和设备隐私写入普通日志。
5. 设置有限 `deadline_ms`，并给调用方一个明确的停止点。

### 8.2 调用中

1. 只把方法白名单中的调用交给 Bridge/RPC。
2. 对返回消息先做契约、`request_id` 和状态校验，再读取业务结果。
3. 传输成功只作为中间证据；不得直接把它映射为 `APPLIED`。
4. 收到 `REJECTED` 时记录机器可读原因和版本，不用异常堆栈掩盖业务拒绝。
5. 超时、断链、格式错误或关联标识不匹配时，把当前动作冻结为 `UNKNOWN`。

### 8.3 调用后

1. 对 `APPLIED` 执行必要的后置观察，例如读取目标状态、检查事件记录或确认安全输出。
2. 对 `UNKNOWN` 先查询和对账，保留原始 `request_id`、时间窗口和最后观察。
3. 只有确认动作尚未发生且方法具有幂等保障时，才进入下一次尝试。
4. 将请求、响应、观察、决策和人工裁决分开记录，便于复盘。
5. 把未决项交给下一篇或项目交接，不以“脚本退出码为零”结束证据链。

## 9. 故障矩阵

| 现象 | 可能层次 | 不应直接得出的结论 | 推荐动作 |
| --- | --- | --- | --- |
| Python 进程无法导入客户端库 | 本地环境 | Bridge 或 MCU 故障 | 记录环境版本，先修复本地依赖或使用标准库概念实验 |
| Router 不可达 | 传输层 | MCU 没有执行 | 保存连接错误，停止跨处理器调用，检查入口和权限 |
| 方法不存在 | 契约/版本 | 设备离线 | 比对方法白名单和版本，输出 `REJECTED` |
| 参数被拒绝 | 调用层 | 网络不稳定 | 保存参数校验原因，不自动重试同一非法输入 |
| 请求超时 | 传输或执行路径 | 动作一定失败 | 分类为 `UNKNOWN`，先查询或对账 |
| 收到旧 `request_id` | 关联/并发 | 旧响应就是当前结果 | 丢弃为当前响应，记录迟到消息和时间窗口 |
| 返回 `APPLIED` 但状态未改变 | 业务/观察层 | 硬件已经正常 | 检查后置观察、版本和状态机，必要时升级为 `UNKNOWN` |
| 设备重启后出现重复动作 | 幂等/恢复 | 只需增加重试次数 | 回顾幂等键、持久化状态和恢复顺序，暂停自动写入 |

故障矩阵的目标不是让每个问题都自动恢复，而是让“停止在哪里、保留什么证据、谁来决定下一步”变得清楚。

## 10. 本章验证矩阵

| 编号 | 验证项 | 本地可验证内容 | 当前未覆盖内容 |
| --- | --- | --- | --- |
| BRG-01 | 请求字段校验 | 空标识、空方法、非正期限和非对象参数被拒绝 | 真实 Bridge schema |
| BRG-02 | 响应关联 | 正确、拒绝和错配响应分别分类 | Router 实时返回 |
| BRG-03 | 脱敏 | 日志摘要不展开 `args` | 现场日志采集策略 |
| BRG-04 | 状态决策 | `APPLIED`、`REJECTED`、`UNKNOWN` 分支稳定 | 设备状态查询 |
| BRG-05 | 幂等策略 | 幂等未知状态先对账，非幂等未知状态升级 | 接收端幂等缓存 |
| BRG-06 | 图示追溯 | 正文 Mermaid 与 `diagrams/` 源文件一致 | SVG 渲染和视觉审阅 |
| BRG-07 | 文档导航 | `SUMMARY.md`、篇入口和图示索引可达 | GitHub 页面实际渲染 |
| BRG-08 | 硬件闭环 | 未执行，保持边界声明 | UNO Q 实机、MCU、Bridge 联调 |

本章完成后的状态仍为 `draft`。本地 Python 概念实验通过，只能证明消息和策略代码的逻辑；它不授予现场写入授权，也不替代第三篇第 8 章要求的实机观察、证据包和交接条件。

## 11. 与前后篇章的交接

- 前置阅读：[第二篇第9章：传感、控制与 MCU/Linux 协同闭环](../第2篇_STM32/第9章_综合实验_传感控制与MCU_Linux协同闭环.md)，用于理解 MCU 状态机、传感数据和控制输出的边界。
- 运行前提：[第三篇第4章：Linux 远程运维与 Python Bridge](../第3篇_Linux/第4章_Linux远程运维与Python_Bridge_从安全命令到可验证请求.md)，用于理解入口、白名单、请求信封、幂等和 `UNKNOWN`。
- 综合交接：[第三篇第8章：Linux 与 Python Bridge 综合运行手册](../第3篇_Linux/第8章_Linux与Python_Bridge综合运行手册_从预检到交接.md)，用于把调用结果放入预检、健康门、证据包和回滚语境。
- 下一阶段：[第五篇：App Lab](../第5篇_AppLab/README.md)，将承接 App 入口、运行界面和应用组织；本章的消息边界不能替代 App Lab 的实际验证。
- 综合项目：[第九篇：Project](../第9篇_Project/README.md)，将承接真实需求、验收条件、风险和复盘；项目中必须保留 `UNKNOWN` 的人工决策记录。

## 12. 常见问题

### Q1：为什么有了 `request_id` 还要 `idempotency_key`？

`request_id` 解决的是响应关联；`idempotency_key` 解决的是重复请求的动作语义。网络重试可能产生新的 `request_id`，但接收端仍需知道它们是否代表同一个业务动作。

### Q2：收到 `APPLIED` 是否可以马上对用户说“硬件已动作”？

不一定。必须确认 `APPLIED` 的定义是方法执行完成，还是仅仅进入队列；如果契约没有包含目标状态或后置观察，用户提示应保持较弱措辞，并继续完成观察。

### Q3：为什么不把超时直接归类为 `REJECTED`？

拒绝表示接收端明确没有接受；超时只表示当前调用者没有在期限内获得足够证据。两者的恢复动作不同，混淆会造成重复执行或错误告警。

### Q4：通知消息是不是更快？

通知通常减少等待，但它也减少确认。速度不是选择通知的充分理由；只有在丢失或重复不会造成不可接受后果，并且另有状态观察时，才适合使用通知。

### Q5：客户端已经校验参数，为什么 MCU 还要再校验？

客户端和 MCU 版本可能不同，请求也可能来自旧程序、错误配置或不受信任来源。MCU 是最终安全边界，不能把客户端校验当成唯一防线。

### Q6：重试次数设为三次是不是通用最佳实践？

不是。本章的三次只用于概念实验，真实值应由动作副作用、超时预算、对账能力和现场安全要求决定。对非幂等动作，即使只重试一次也可能不可接受。

### Q7：图里为什么单独画 Evidence？

因为“收到响应”和“证明目标状态”是不同证据。把记录和观察单独表示，可以提醒读者不要用一条传输日志替代业务验收。

## 13. 本章小结

本章建立了第四篇的第一个稳定抽象：

1. Python App 负责意图、校验、关联和记录；Router 负责通道；Bridge/RPC 负责能力映射；MCU Sketch 负责最终实时与安全边界。
2. 请求必须有有限期限、方法白名单、契约版本和可关联标识；响应必须先校验关联，再解释状态。
3. `call`、`notify` 和 `provide` 具有不同的确认语义；发送成功、路由成功和业务应用成功不能混为一谈。
4. 超时和关联错配默认进入 `UNKNOWN`；是否幂等决定下一步能否对账后重试。
5. 本地概念实验验证了代码规则，但没有产生 UNO Q、Router、Bridge 或 MCU 的实机证据。

下一章[《Python Bridge 并发与任务生命周期：从单次调用到有界协同》](./第2章_Python_Bridge并发与任务生命周期_从单次调用到有界协同.md)将在这个模型上继续讨论并发、任务生命周期、连接复用和取消；在此之前，读者应先能解释每一次调用的请求标识、状态来源、停止点和证据缺口。

## 延伸阅读

- [资源索引](../../resources/references.md)：本章使用的 Arduino UNO Q User Manual、Arduino App specification、Arduino Router 和 Python 标准库资料均已登记。
- [第三篇第8章：综合运行手册](../第3篇_Linux/第8章_Linux与Python_Bridge综合运行手册_从预检到交接.md)：了解从预检到跨篇交接的证据边界。
- [第五篇入口](../第5篇_AppLab/README.md)：后续应用入口的预留位置。
- [图示登记](../../images/第4篇_PythonBridge/README.md)：查看 Fig-24 的源文件、占位状态和许可边界。
