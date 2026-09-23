---
title: App Lab 运行生命周期：导入、启动、运行与停止
part: 5
chapter: 2
status: draft
last_verified: 2026-09-23
updated: 2026-09-23
prerequisites: 第五篇第1章、第三篇第8章、第四篇第1～4章
tags: App Lab, 生命周期, run_id, 日志, 停止, 重启, 证据
---

# 第2章 App Lab 运行生命周期：导入、启动、运行与停止

## 学习目标

读完本章后，读者应能够：

1. 解释 App Lab 的 Run 操作为什么不是一个简单的布尔值，而是一条有阶段、有来源、有会话编号的运行链。
2. 把一次 App 运行拆成导入、准备、启动、运行、停止或失败等可复核阶段。
3. 使用 `run_id` 把当前运行的日志与上一次运行的陈旧日志分开，避免“旧错误污染新结果”。
4. 区分“启动阶段完成”“Python 已启动”“Sketch 有输出”“用户请求停止”和“设备动作已完成”。
5. 在不打开 App Lab、不连接 UNO Q 的条件下，用两个标准库 Python 实验验证状态迁移和会话证据分类。
6. 为真实设备运行准备最小证据记录，知道哪些结论仍必须通过 App Lab、Router/Bridge、MCU 或现场观察确认。

## 背景与边界

Arduino 官方 App Lab 示例文档把运行示例描述为：选择示例、点击 Run、等待启动完成，然后与 App 交互。[Arduino App Lab examples](https://docs.arduino.cc/software/app-lab/tutorials/examples/) 这个用户动作很短，但后台可能同时涉及 Linux 组件、MCU Sketch、Brick 和日志流。UNO Q 数据表进一步说明，Run 操作会构建 Linux 组件、刷写 MCU Sketch、部署选定的 Brick，并在板上启动相关组件；运行状态可以从 App 的控制台观察。[UNO Q datasheet](https://docs.arduino.cc/resources/datasheets/ABX00162-datasheet.pdf)

这意味着“我点击了 Run”只是一个请求，“界面没有报错”只是一个观察，“设备已经完成动作”则是更高等级的结论。若把它们都压缩成 `running = true`，后续排障、重启和验收会失去时间顺序与证据来源。

本章建立一个**教学用的本地生命周期模型**。它不会：

- 打开 Arduino App Lab 或 `arduino-app-cli`；
- 连接 USB、Network Mode、mDNS、ADB、SSH 或真实 UNO Q；
- 编译、刷写或执行任何 Python、Brick、Arduino Sketch；
- 启动 Router、Bridge、容器或目标板上的服务；
- 把本地状态机、模拟日志或 SVG 图示写成 App Lab、MCU 或设备动作的验收结论。

本章的“通过”只表示本地状态迁移和会话证据函数满足测试契约。真实运行还需要记录目标设备、App Lab/CLI 版本、入口方式、启动日志、Python/Sketch/Brick 日志、停止原因和设备侧观察。Arduino App specification 对 App 目录和组件职责的定义，仍是本章承接[第五篇第1章](./第1章_App_Lab开发基础_应用结构与验证边界.md)的结构基线；本章新增的是运行时间的顺序和证据窗口，而不是新的官方 API。[Arduino App specification](https://github.com/arduino/arduino-app-cli/blob/main/docs/app-specification.md)

## 1. Run 不是一个布尔值

### 1.1 一个按钮背后有多条执行线

UNO Q 的 App 由 Linux 侧和 MCU 侧协同组成。官方 App 规范把 Python、Brick 和容器放在 Linux OS 一侧，把 Arduino Sketch 放在集成 MCU 一侧，并通过基于 RPC 的消息协作。[Arduino App specification](https://github.com/arduino/arduino-app-cli/blob/main/docs/app-specification.md) 因此，一次 Run 至少可能触发这些执行线：

| 执行线 | 它可能做什么 | 需要什么证据 | 不能直接推出什么 |
| --- | --- | --- | --- |
| App 入口 | 接收项目、解析描述符、显示运行状态 | 入口和控制台记录 | Python 业务已经正确 |
| Linux/Python | 创建环境、安装依赖、启动 `main.py` | Python 进程日志和版本 | MCU 已收到请求 |
| Brick | 准备服务、模型、数据库或设备资源 | Brick 启动/健康日志 | Brick API 已完成业务动作 |
| MCU/Sketch | 编译、刷写并执行低层逻辑 | Sketch 日志、读回或波形 | Linux 请求一定已经到达 |
| Bridge/RPC | 传递请求和响应 | request ID、方向、返回状态 | 目标物理状态已经改变 |
| 设备观察 | 读取实际电平、传感器或执行器结果 | 读回、仪器或现场观察 | 其他日志可以被省略 |

这些执行线可能先后发生，也可能并行发生。运行模型必须保留顺序和来源，而不能只保留最后一个颜色或图标。

### 1.2 “运行中”也必须限定范围

本章把 `RUNNING` 定义为一个有限结论：在指定 `run_id` 下，启动通道报告 `READY`，Python 通道报告 `STARTED`，且没有更晚的当前运行错误或停止标记。它只说明**本地证据窗口满足启动条件**，不说明：

1. Sketch 一定存在或已经开始执行；
2. Brick 一定健康或已经加载模型；
3. Bridge/RPC 一定完成某个业务请求；
4. GPIO、电机、LED、摄像头或传感器已经产生目标物理结果。

如果项目要求 Sketch 也必须启动，应把 `sketch` 加入必需通道，并要求当前 `run_id` 的 Sketch `STARTED` 事件。证据不足时保留 `UNKNOWN_INCOMPLETE`，而不是为了让界面变绿而补写成功。

## 2. 生命周期状态机

### 2.1 阶段和迁移

本章的状态机只描述**一次运行对象的本地投影**。它不是 App Lab 内部实现，也不是对官方 UI 或未来版本行为的承诺。

| 阶段 | 含义 | 允许的下一阶段 | 常见证据 |
| --- | --- | --- | --- |
| `IMPORTED` | 项目已经被识别为一次候选运行 | `PREPARING`、`FAILED` | 项目路径、版本、导入结果 |
| `PREPARING` | 正在解析依赖、生成运行内容或准备资源 | `STARTING`、`FAILED` | 准备日志、依赖解析结果 |
| `STARTING` | Linux、MCU 或 Brick 正在进入运行入口 | `RUNNING`、`FAILED` | 启动日志、组件启动事件 |
| `RUNNING` | 当前证据窗口满足最低启动条件 | `STOPPING`、`FAILED` | 当前 `run_id` 的启动与 Python 事件 |
| `STOPPING` | 已收到停止意图，正在清理运行对象 | `STOPPED`、`FAILED` | 停止请求、清理结果 |
| `STOPPED` | 本次运行已结束且停止过程有记录 | 无 | 停止确认、退出码或结束事件 |
| `FAILED` | 本次运行在某一阶段遇到明确错误 | 无 | 错误来源、消息、时间和退出信息 |

`UNKNOWN` 不作为可以随意跳转的阶段。它表示证据不够、日志属于其他 `run_id`、连接中断或停止/失败的最终状态没有收敛。把 `UNKNOWN` 设计成“需要查询或人工复核”的结论，能避免把未知自动改写成重试或成功。

### 2.2 为什么结束状态不能直接回到运行中

当一次运行已经进入 `STOPPED` 或 `FAILED`，应创建新的 `run_id`，而不是复用旧对象直接跳回 `PREPARING`。这样做有三个好处：

- 旧运行的错误不会被新运行的成功覆盖；
- 日志和请求可以按会话边界归档；
- 重启行为可以明确记录为“新的一次运行”，而不是修改历史。

这和[第四篇第3章的连接恢复模型](../第4篇_PythonBridge/第3章_Python_Bridge连接复用与请求恢复_从断线到可判定结果.md)以及[第四篇第4章的结果账本](../第4篇_PythonBridge/第4章_Python_Bridge结果账本与状态查询_从返回值到可验证证据.md)一致：身份先稳定，状态再收敛，不能靠覆盖旧记录制造确定性。

## 3. Fig-29：一次 App 运行的证据窗口

<a id="fig-29-uno-q-app-lab-run-lifecycle"></a>

~~~mermaid
flowchart LR
    IMPORT[导入\napp.yaml + 入口] --> PREP[准备\n依赖 · 资源 · 运行内容]
    PREP --> START[启动\nLinux · MCU · Brick]
    START --> RUN[运行\nPython · Sketch · Brick]
    RUN --> STOPPING[停止请求\n记录意图]
    STOPPING --> STOPPED[已停止\n结束证据]
    PREP --> FAILED[失败\n保留来源与原因]
    START --> FAILED
    RUN --> FAILED
    RUN --> UNKNOWN[未知\n证据缺口或断线]
    OLD[旧 run_id 日志] -.过滤.-> WINDOW[证据窗口\nrun_id + channel + event]
    NEW[当前 run_id] --> WINDOW
    WINDOW --> RUN
    WINDOW --> FAILED
    WINDOW --> STOPPED

    classDef phase fill:#e8f1ff,stroke:#2563eb,color:#0f172a
    classDef terminal fill:#fee2e2,stroke:#dc2626,color:#0f172a
    classDef evidence fill:#dcfce7,stroke:#16a34a,color:#0f172a
    class IMPORT,PREP,START,RUN,STOPPING phase
    class STOPPED,FAILED,UNKNOWN terminal
    class OLD,NEW,WINDOW evidence
~~~

图 5-2（Fig-29）把“用户请求”和“可判定证据”分开：上方主链表达一次运行的阶段迁移，左下方的旧/新 `run_id` 进入同一个证据窗口，窗口再输出运行、失败或停止判断。图源为[Mermaid 文件](../../diagrams/uno-q-app-lab-run-lifecycle.mmd)，导出图示为[Fig-29 SVG](../../images/第5篇_AppLab/ch02-fig29-uno-q-app-lab-run-lifecycle.svg)，登记记录见[第五篇图示资源](../../images/第5篇_AppLab/README.md#fig-29-uno-q-app-lab-run-lifecycle)。

这张图是本书原创的教学模型。它没有复制 App Lab 截图，也没有声称 `PREPARING`、`STARTING` 或 `UNKNOWN` 是 Arduino 内置字段；实际目标环境的日志字段、退出码和界面状态必须在现场核验。

## 4. 从导入到运行：四个阶段，五类结果

### 4.1 导入阶段只解决“项目是谁”

导入阶段要固定的不是“按钮颜色”，而是运行身份：项目目录、App 名称、版本提交、目标设备和一次新的 `run_id`。App CLI 用户文档给出了用户 App 目录和运行时目录的参考形状，但目标镜像的实际路径、权限和版本仍要现场确认。[Arduino App CLI user documentation](https://github.com/arduino/arduino-app-cli/blob/main/docs/user-documentation.md)

最小记录可以包含：

| 字段 | 作用 | 示例 |
| --- | --- | --- |
| `run_id` | 标识一次运行尝试 | `20260923T101500Z-001` |
| `app_revision` | 绑定代码和配置版本 | `git:00c4054` |
| `target` | 区分 PC-hosted、SBC 或 Network 目标 | `network:<device-alias>` |
| `requested_at` | 记录用户意图时间 | ISO 8601 时间 |
| `operator` | 记录操作主体或自动化身份 | 脱敏后的标识 |

示例中的设备别名、提交号和用户标识只是格式示意；不要把真实密码、API Key、完整局域网地址或设备序列号写进公开示例。

### 4.2 准备阶段不能跳过依赖和资源记录

准备阶段可能涉及 Python 依赖、Sketch 依赖、Brick、模型、端口和设备资源。官方 App 规范允许在 `app.yaml` 中声明端口、Brick、模型、变量和设备映射，但声明本身只表示依赖意图；它不自动证明资源已经可用。[Arduino App specification](https://github.com/arduino/arduino-app-cli/blob/main/docs/app-specification.md)

因此，准备阶段至少要有以下结果之一：

- `PREPARED`：已生成可供启动的运行内容，并保留版本/依赖摘要；
- `FAILED`：依赖、权限、端口或资源准备失败，保留原始来源；
- `UNKNOWN`：准备过程被中断或日志不足，不能自动继续下一个阶段。

### 4.3 启动阶段是组件进入运行入口，不是业务完成

UNO Q 数据表把 Run 流程描述为一组组合动作：构建 Linux 组件、刷写 MCU Sketch、部署 Brick 和启动组件。不同 App 是否包含这些组件、是否需要编译或部署，取决于项目结构和声明。启动阶段应把每条执行线的结果分别保留，避免一条“Run finished”日志掩盖某个侧边失败。

### 4.4 运行、停止、失败和未知必须分别记录

| 结果 | 最小含义 | 允许的下一步 |
| --- | --- | --- |
| `RUNNING` | 当前会话的最低启动证据已满足 | 接收请求、观察日志或发起停止 |
| `STOPPED` | 当前会话有明确停止标记 | 创建新 `run_id` 后重新运行 |
| `FAILED` | 当前会话有明确错误来源 | 修复并创建新 `run_id`，禁止覆盖历史 |
| `UNKNOWN_NO_CURRENT_LINES` | 没有当前会话的日志 | 先查询/补证据，不自动重试 |
| `UNKNOWN_INCOMPLETE` | 有当前日志，但必需通道或事件缺失 | 补齐日志或人工复核 |

`UNKNOWN` 的存在不是悲观设计，而是为了把“系统没有告诉我们”与“系统告诉我们失败了”分开。第四篇已经讨论过 `UNKNOWN` 不应自动变成重放授权；本章把相同边界应用到 App 运行会话。

## 5. 实验一：用不可变状态机管理一次运行

第一个实验把阶段迁移写成一个小而明确的纯函数模型。它不解析 YAML，不调用 App Lab，不访问文件系统，也不模拟设备。`RunLifecycle` 是不可变数据类，每次 `advance()` 都返回新对象，因此调用方可以保留每一步的历史快照。

**代码说明**

- 用途：验证一次 App 运行的合法阶段顺序，以及终态不能在原对象上重新启动。
- 运行环境：Python 3.10 或更高版本；Windows、Linux 或 macOS 均可。
- 文件位置：`code/第5篇_AppLab/第2章_AppLab运行生命周期/lifecycle.py`。
- 依赖：仅 Python 标准库 `dataclasses`；不访问 App Lab、Router/Bridge、网络或开发板。
- 操作步骤：在仓库根目录运行示例，再运行 `test_lifecycle.py`；先观察 `RUNNING`，再观察合法停止和非法迁移。
- 预期输出：一次会话从 `IMPORTED` 走到 `RUNNING`，非法跳转被拒绝，停止后历史保持完整。
- 故障排查：若测试允许 `IMPORTED -> STOPPED`，说明迁移表过宽；若终态能直接进入 `PREPARING`，说明没有按 `run_id` 建立新会话。
- 验证方式：测试空 `run_id`、合法序列、非法序列、不可变性和终态重启五种行为；本实验不证明真实 App Lab 的内部状态名。

~~~python
"""Model an App Lab run lifecycle without starting an App or a device."""
from __future__ import annotations

from dataclasses import dataclass


class LifecycleError(ValueError):
    """Raised when a local lifecycle transition is not allowed."""


ALLOWED_TRANSITIONS: dict[str, frozenset[str]] = {
    "IMPORTED": frozenset({"PREPARING", "FAILED"}),
    "PREPARING": frozenset({"STARTING", "FAILED"}),
    "STARTING": frozenset({"RUNNING", "FAILED"}),
    "RUNNING": frozenset({"STOPPING", "FAILED"}),
    "STOPPING": frozenset({"STOPPED", "FAILED"}),
    "STOPPED": frozenset(),
    "FAILED": frozenset(),
}


@dataclass(frozen=True)
class RunLifecycle:
    """Immutable local projection of one App run."""

    run_id: str
    phase: str
    history: tuple[str, ...]


def new_session(run_id: str) -> RunLifecycle:
    """Create a new run at the imported phase."""
    if not run_id.strip():
        raise LifecycleError("run_id must not be empty")
    return RunLifecycle(run_id=run_id, phase="IMPORTED", history=("IMPORTED",))


def advance(session: RunLifecycle, target: str) -> RunLifecycle:
    """Return a new session after one allowed phase transition."""
    if target not in ALLOWED_TRANSITIONS:
        raise LifecycleError(f"unknown target phase: {target}")
    if target not in ALLOWED_TRANSITIONS[session.phase]:
        raise LifecycleError(f"{session.phase} cannot advance to {target}")
    return RunLifecycle(
        run_id=session.run_id,
        phase=target,
        history=session.history + (target,),
    )


def _demonstrate() -> None:
    running = new_session("run-001")
    for phase in ("PREPARING", "STARTING", "RUNNING"):
        running = advance(running, phase)
    print(
        f"SIMULATED session={running.run_id} phase={running.phase} "
        f"history={'>'.join(running.history)}"
    )

    try:
        advance(new_session("run-002"), "STOPPED")
    except LifecycleError as error:
        print(f"SIMULATED rejected={error}")

    stopped = running
    for phase in ("STOPPING", "STOPPED"):
        stopped = advance(stopped, phase)
    print(
        f"SIMULATED terminal={stopped.phase} "
        f"history={'>'.join(stopped.history)}"
    )


if __name__ == "__main__":
    _demonstrate()
~~~

预期输出：

~~~text
SIMULATED session=run-001 phase=RUNNING history=IMPORTED>PREPARING>STARTING>RUNNING
SIMULATED rejected=IMPORTED cannot advance to STOPPED
SIMULATED terminal=STOPPED history=IMPORTED>PREPARING>STARTING>RUNNING>STOPPING>STOPPED
~~~

输出中的 `SIMULATED` 是故意保留的边界标记。它证明的是状态迁移函数和历史记录行为，不是 App Lab 控制台的原始输出。

## 6. 实验二：按 `run_id` 过滤陈旧日志

状态机只能告诉我们“允许怎样走”，不能告诉我们某条日志属于哪一次运行。第二个实验把日志先按 `run_id` 筛选，再按通道和事件分类。当前运行有 `startup=READY` 与 `python=STARTED` 时，才给出最低限度的 `RUNNING`；旧运行的 `ERROR` 会被忽略，但当前运行的 `ERROR` 会得到 `FAILED`。明确的 `STOPPED` 标记优先作为结束证据。

**代码说明**

- 用途：验证当前运行的日志窗口不会被上一次运行的错误污染，并保留缺失证据的 `UNKNOWN` 结果。
- 运行环境：Python 3.10 或更高版本；普通本地终端即可。
- 文件位置：`code/第5篇_AppLab/第2章_AppLab运行生命周期/session_evidence.py`。
- 依赖：仅 Python 标准库 `dataclasses`；输入是内存中的不可变日志元组。
- 操作步骤：运行示例，再运行 `test_session_evidence.py`；将 `run-old` 和 `run-new` 对照阅读。
- 预期输出：陈旧错误不影响当前运行；没有当前日志时保持未知；当前错误得到失败；停止标记得到停止。
- 故障排查：若旧 `run_id` 的错误导致新运行失败，说明筛选发生得太晚；若缺少 Sketch 通道仍得到完整结论，说明调用方没有声明必需通道。
- 验证方式：测试陈旧错误、无当前日志、当前错误、停止标记和必需 Sketch 通道缺失五种行为；本实验不判断设备物理状态。

~~~python
"""Classify run-scoped App Lab evidence without claiming hardware success."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EvidenceLine:
    """One normalized log observation associated with a run identifier."""

    run_id: str
    channel: str
    event: str
    message: str


@dataclass(frozen=True)
class EvidenceDecision:
    """Local decision made from the selected run's evidence only."""

    action: str
    reason: str
    channels: tuple[str, ...] = ()
    missing: tuple[str, ...] = ()


def assess_session(
    run_id: str,
    lines: tuple[EvidenceLine, ...],
    required_channels: tuple[str, ...] = ("startup", "python"),
) -> EvidenceDecision:
    """Classify one run while ignoring lines belonging to older runs."""
    current = tuple(line for line in lines if line.run_id == run_id)
    if not current:
        return EvidenceDecision(
            "UNKNOWN_NO_CURRENT_LINES",
            "no evidence belongs to the requested run",
        )

    channels = tuple(sorted({line.channel for line in current}))
    if any(line.event == "STOPPED" for line in current):
        return EvidenceDecision("STOPPED", "current run contains STOPPED", channels)
    for line in current:
        if line.event == "ERROR":
            return EvidenceDecision(
                "FAILED",
                f"{line.channel} emitted ERROR",
                channels,
            )

    missing = tuple(sorted(set(required_channels) - set(channels)))
    if missing:
        return EvidenceDecision(
            "UNKNOWN_INCOMPLETE",
            "required evidence channel is missing",
            channels,
            missing,
        )

    startup_ready = any(
        line.channel == "startup" and line.event == "READY" for line in current
    )
    python_started = any(
        line.channel == "python" and line.event == "STARTED" for line in current
    )
    if not startup_ready or not python_started:
        return EvidenceDecision(
            "UNKNOWN_INCOMPLETE",
            "required startup or Python event is missing",
            channels,
        )

    if "sketch" in required_channels and not any(
        line.channel == "sketch" and line.event == "STARTED" for line in current
    ):
        return EvidenceDecision(
            "UNKNOWN_INCOMPLETE",
            "required Sketch STARTED event is missing",
            channels,
            ("sketch",),
        )
    return EvidenceDecision("RUNNING", "current run has required start evidence", channels)


def _demonstrate() -> None:
    stale_case = assess_session(
        "run-new",
        (
            EvidenceLine("run-old", "python", "ERROR", "old failure"),
            EvidenceLine("run-new", "startup", "READY", "startup ready"),
            EvidenceLine("run-new", "python", "STARTED", "main started"),
        ),
    )
    print(
        f"SIMULATED stale_error={stale_case.action} "
        f"channels={','.join(stale_case.channels)}"
    )

    no_current = assess_session(
        "run-new",
        (EvidenceLine("run-old", "startup", "READY", "old run"),),
    )
    print(f"SIMULATED no_current={no_current.action}")

    failed = assess_session(
        "run-new",
        (
            EvidenceLine("run-new", "startup", "READY", "startup ready"),
            EvidenceLine("run-new", "python", "ERROR", "traceback"),
        ),
    )
    print(f"SIMULATED runtime_error={failed.action}")

    stopped = assess_session(
        "run-new",
        (
            EvidenceLine("run-new", "startup", "READY", "startup ready"),
            EvidenceLine("run-new", "python", "STARTED", "main started"),
            EvidenceLine("run-new", "lifecycle", "STOPPED", "user requested stop"),
        ),
    )
    print(f"SIMULATED stopped={stopped.action}")


if __name__ == "__main__":
    _demonstrate()
~~~

预期输出：

~~~text
SIMULATED stale_error=RUNNING channels=python,startup
SIMULATED no_current=UNKNOWN_NO_CURRENT_LINES
SIMULATED runtime_error=FAILED
SIMULATED stopped=STOPPED
~~~

这里的 `RUNNING` 仍然只是“当前会话具有最低启动证据”。若需要证明 Sketch 或 Brick 已经就绪，应在调用 `assess_session()` 时把对应通道加入 `required_channels`，并为该通道定义清晰的 `STARTED` 事件。若需要证明请求已经由 MCU 执行，则还必须接入第四篇的请求身份与结果账本，以及真实设备侧的可观察结果。

## 7. 停止、失败与重新运行

### 7.1 停止是一个有意图的操作

用户点击 Stop、关闭 App 或发送停止命令时，首先记录的是**停止意图**，而不是已经完成的停止。一个安全的本地模型可以按如下顺序写证据：

1. 记录 `stop_requested`，包含当前 `run_id`、操作者和时间。
2. 进入 `STOPPING`，停止接受本次运行的新业务请求。
3. 等待 Python、Brick、Sketch 或其他组件报告清理结果。
4. 只有当结束条件满足时才写 `STOPPED`；超时或连接中断则保留 `UNKNOWN` 或 `FAILED`。
5. 下一次运行使用新的 `run_id`，不能修改上一次运行的历史。

停止请求本身不能撤销已经发往远端的动作，也不能把一个已发出的 Bridge 请求自动变成“未执行”。这与[第四篇第3章的已发送/可能已发送边界](../第4篇_PythonBridge/第3章_Python_Bridge连接复用与请求恢复_从断线到可判定结果.md)相同：停止运行和确认业务动作是两个不同问题。

### 7.2 失败要保留来源，不只保留红色状态

失败记录至少要有：

- 当前 `run_id`；
- 失败阶段：导入、准备、启动、运行或停止；
- 来源通道：App 入口、Python、Brick、Sketch、Bridge 或设备观察；
- 原始消息的脱敏摘要；
- 代码/配置版本和时间；
- 是否已经产生可能无法撤销的外部动作。

例如，Python `ERROR` 不能直接写成“MCU 失败”；Sketch 编译失败也不能直接写成“网络不可用”。错误来源决定下一步检查对象，错误摘要则让后续交接能够复核当时的判断。

### 7.3 重启不是覆盖旧运行

重启流程至少产生两个对象：旧会话的结束记录和新会话的导入记录。建议使用如下关联字段：

| 字段 | 旧会话 | 新会话 |
| --- | --- | --- |
| `run_id` | `run-001` | `run-002` |
| `supersedes` | 空 | `run-001` |
| `reason` | `FAILED` 或 `STOPPED` | `operator_retry` 或修复说明 |
| `revision` | 旧版本 | 新版本或同版本复核 |
| `evidence` | 结束证据 | 新的导入/准备证据 |

这种记录可以回答“第二次为什么重新运行”，而不是只留下一个最终绿色状态。

## 8. 证据矩阵与现场记录

### 8.1 从阶段到结论的最小矩阵

| 结论 | 最低证据 | 仍然不能推出 |
| --- | --- | --- |
| 项目已导入 | App 身份、版本、`run_id` | 依赖已安装、设备在线 |
| 项目已准备 | 依赖/资源准备结果 | 所有组件已经运行 |
| App 已启动 | 当前启动通道 `READY` | Python 业务正确 |
| Python 已运行 | 当前 Python `STARTED` | Sketch 已运行、动作已执行 |
| Sketch 已运行 | 当前 Sketch `STARTED` | 引脚产生目标波形 |
| App 已停止 | 当前会话停止请求和结束记录 | 远端已经撤销所有动作 |
| 动作已完成 | request ID、返回状态、设备读回/观察 | 其他相似会话的日志可以替代 |

### 8.2 推荐的现场记录顺序

真实设备运行时，可按下面顺序建立证据包：

1. 记录 App Lab/CLI、UNO Q 软件镜像和目标设备信息；
2. 记录 App 仓库提交、`app.yaml` 摘要和新 `run_id`；
3. 保存导入、准备、启动、运行和停止的原始日志，并标出来源通道；
4. 对每个 Bridge/RPC 请求保留 request ID、发送时间、返回状态和查询结果；
5. 对需要物理动作的结论补充读回、波形、传感器值、视频或现场观察；
6. 将失败、未知和停止原因与下一次运行的 `supersedes` 关系写入交接记录。

任何日志中出现的密码、令牌、完整局域网地址、设备序列号和个人数据，都应在提交或共享前脱敏。App CLI 文档中的默认目录和环境变量是参考资料，不应未经核对就写进目标设备的生产操作手册。[Arduino App CLI user documentation](https://github.com/arduino/arduino-app-cli/blob/main/docs/user-documentation.md)

## 9. 验证矩阵、练习与交接

### 9.1 本章验证矩阵

| 编号 | 验证项 | 本地可验证内容 | 当前未覆盖内容 |
| --- | --- | --- | --- |
| APP-LC-01 | 阶段迁移 | 合法迁移按顺序发生 | App Lab 内部真实状态名 |
| APP-LC-02 | 非法迁移 | `IMPORTED -> STOPPED` 被拒绝 | 真实 UI 对非法操作的提示 |
| APP-LC-03 | 终态隔离 | `STOPPED`/`FAILED` 不能原地重启 | 目标板进程清理是否完整 |
| APP-LC-04 | 会话过滤 | 旧 `run_id` 的错误不污染新运行 | App Lab 实际日志字段是否含会话 ID |
| APP-LC-05 | 当前失败 | 当前会话 `ERROR` 判为 `FAILED` | 真实组件的退出码和重试语义 |
| APP-LC-06 | 未知保留 | 缺少当前日志或通道时保持 `UNKNOWN` | 现场查询能否补齐最终状态 |
| APP-LC-07 | 图示追溯 | Mermaid、SVG、正文锚点和登记一致 | 图示是否匹配某个具体 UI 版本 |

### 9.2 练习

1. 把 `STARTING -> RUNNING` 改成直接允许 `STARTING -> STOPPED`，说明为什么这会丢失停止过程证据。
2. 为一次 Python-only App 设计 `required_channels`；再为包含 Sketch 的 App 增加 `sketch`，比较两种 `UNKNOWN_INCOMPLETE` 的含义。
3. 构造 `run-old` 有错误、`run-new` 有启动成功的日志，解释为什么不能只按时间排序而不按 `run_id` 过滤。
4. 设计一次“启动成功但动作未知”的证据包，标出哪些字段需要第四篇结果账本，哪些字段需要设备观察。
5. 设计一次停止超时：停止意图已经记录，但没有结束事件。应该保留 `STOPPING`、`FAILED` 还是 `UNKNOWN`？给出你的判定依据。

### 9.3 跨篇交接

- 第五篇第1章负责 App 文件结构、入口和初始证据语言；本章负责一次运行的阶段和会话边界。
- 第三篇第8章负责预检、健康门、Dry-run、证据包和回滚；真实部署时应把本章的 `run_id` 接入其运行手册。
- 第四篇第1～4章负责消息模型、并发、连接恢复和结果账本；本章不重新定义 Bridge 请求状态，只说明请求发生在哪个 App 会话中。
- 后续第五篇章节将继续进入运行配置、Brick/服务依赖和部署验证；它们必须沿用“新会话、新证据、未知不自动成功”的原则。
- 第九篇项目篇应把 App 生命周期记录、设备验收和失败交接纳入项目交付清单，而不是只截图一次绿色界面。

## 10. 常见问题

### 10.1 App Lab 显示 Run 完成，为什么本章仍不写成设备成功？

因为 Run 完成最多说明某个工具链阶段返回了结果。Python、Sketch、Bridge 和设备观察分别回答不同问题；如果目标结论涉及物理动作，还需要更高等级的读回、波形、传感器或现场证据。

### 10.2 `RUNNING` 和“业务动作已完成”有什么区别？

`RUNNING` 是当前会话达到最低启动条件的本地判断；“业务动作已完成”需要请求身份、返回状态和目标状态观察。前者是进程/日志层结论，后者是通信和设备层结论。

### 10.3 为什么停止后不能复用同一个 `run_id`？

复用会让旧错误、旧日志和新运行混在一起，导致无法回答“哪一次运行产生了这个结果”。新 `run_id` 让重启成为一条可追溯的新记录，旧会话仍然保持不可变历史。

### 10.4 没有当前会话日志时，能否使用上一会话的最后状态？

不能直接使用。上一会话的状态可以作为诊断背景，但不能替代当前运行的证据。当前没有日志时应返回 `UNKNOWN_NO_CURRENT_LINES`，再通过受控查询或人工复核补证据。

### 10.5 Sketch 日志存在，是否说明 MCU 已经产生了波形？

不说明。日志可以证明代码走过某个输出点，但波形、引脚电平、传感器读回或执行器反馈需要独立的设备观察。日志和物理结果必须在证据包中分别记录。

### 10.6 本地状态机是不是 Arduino 官方 API？

不是。本章的 `RunLifecycle`、`EvidenceLine`、`EvidenceDecision` 和状态名称都是本书的教学模型，用于训练证据思维和测试边界。它们不应被当作 App Lab、Router、Bridge 或 Arduino CLI 的内置字段。

## 11. 本章小结与下一步

App Lab 的 Run 是一条生命周期，而不是一个瞬时的成功按钮。通过 `run_id`、阶段历史、来源通道和结束原因，可以把导入、准备、启动、运行、停止、失败和未知分开保存。这样，陈旧日志不会污染新运行，终态不会被原地覆盖，未知也不会被自动解释成成功。

本章的两个实验只验证本地状态机与证据分类函数；它们没有打开 App Lab、启动 Router/Bridge、编译或刷写 Sketch，也没有连接 UNO Q。下一章将沿着“运行对象已经清楚”的前提，进一步讨论 App 的启动配置、Brick 依赖和可部署性检查。

## 延伸阅读

- [Arduino App specification](https://github.com/arduino/arduino-app-cli/blob/main/docs/app-specification.md)：App 组件、目录和 Brick 字段的官方规范。
- [Arduino App CLI user documentation](https://github.com/arduino/arduino-app-cli/blob/main/docs/user-documentation.md)：App 目录、运行时目录和环境变量参考；目标镜像仍需现场核验。
- [Arduino App Lab examples](https://docs.arduino.cc/software/app-lab/tutorials/examples/)：官方示例的访问、运行和复制流程。
- [Arduino UNO Q datasheet](https://docs.arduino.cc/resources/datasheets/ABX00162-datasheet.pdf)：Run 流程、Linux/MCU/Brick/Bridge 的产品级说明。
- [Arduino UNO Q 产品页](https://docs.arduino.cc/hardware/uno-q)：双处理器、App Lab 和 Bridge 的产品层说明。
- [第五篇第1章：App Lab 开发基础](./第1章_App_Lab开发基础_应用结构与验证边界.md)
- [本章配套代码](../../code/第5篇_AppLab/第2章_AppLab运行生命周期/README.md)
- [第五篇图示登记](../../images/第5篇_AppLab/README.md)
- [全书目录](../../SUMMARY.md)
