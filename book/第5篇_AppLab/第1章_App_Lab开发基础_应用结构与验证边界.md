---
title: App Lab 开发基础：应用结构、设备入口与验证边界
part: 5
chapter: 1
status: draft
last_verified: 2026-09-23
updated: 2026-09-23
prerequisites: 第三篇第8章、第四篇第1～4章
tags: App Lab, app.yaml, Python, Arduino Sketch, Brick, Bridge, 证据边界
---

# 第1章 App Lab 开发基础：应用结构、设备入口与验证边界

## 学习目标

读完本章后，读者应能够：

1. 解释 Arduino App、Python、Arduino Sketch、Brick、Linux 和 MCU 在一个应用中的职责边界。
2. 根据 `app.yaml`、`python/main.py` 和可选 `sketch/` 判断一个 App 的最小文件结构。
3. 区分 App Lab 的导入/运行入口、启动日志、Python 日志、Sketch 日志和设备行为观察。
4. 说明 `data/` 与 `.cache/` 的用途，避免把持久业务数据和临时运行文件混在发布包中。
5. 在不连接 UNO Q 的条件下，用本章两个 Python 实验验证结构契约和证据判定顺序。
6. 把本地检查结果写成“已验证的代码事实”，而不是提前写成 Router、Bridge 或硬件验收结论。

## 背景与边界

Arduino App specification 将 Arduino App 定义为一个自包含的应用目录：根目录有 `app.yaml`，`python/main.py` 是 Linux 侧 Python 入口；如果应用包含 MCU 侧 Sketch，则 `sketch/` 中应同时存在 `sketch.ino` 和 `sketch.yaml`。同一份规范还把 App 描述为 Python、Sketch、Bricks 和容器等组件的组合，并说明 Sketch 与 Python 通过基于 RPC 的消息协作。[Arduino App specification](https://github.com/arduino/arduino-app-cli/blob/main/docs/app-specification.md)

这条规范适合用来建立**文件和角色的共同语言**，但不能替代目标板上的运行证据。本章的本地实验不会：

- 打开 Arduino App Lab 或 `arduino-app-cli`；
- 连接 USB、网络模式、mDNS、ADB、SSH 或真实 UNO Q；
- 编译、上传或执行任何 Arduino Sketch；
- 启动 Router、Bridge、Brick 容器或 Linux 服务；
- 证明某个传感器、执行器、LED 或摄像头已经发生物理变化。

因此，本章的“通过”只表示目录契约和证据分类函数通过本地测试。真正的 App Lab 运行还需要在目标环境中记录版本、入口、启动日志、Python 日志、Sketch 日志以及设备侧观察，形成可复核的证据包。

## 1. App Lab 不是单一脚本编辑器

### 1.1 一个 App 是协作边界

在 UNO Q 的双处理器模型中，Linux 侧适合运行 Python、高层数据处理、网络服务和 Brick；MCU 侧适合运行 Arduino Sketch、实时采样和执行器控制。Arduino 的 UNO Q 产品资料把 App Lab 描述为连接 Python 应用、Arduino Sketch 和 AI 模型的统一开发体验；这是一种开发入口，不是把两个处理器变成了同一个执行上下文。[UNO Q 产品页](https://docs.arduino.cc/hardware/uno-q)

可以用下面的责任表先固定语言：

| 对象 | 主要责任 | 不应直接承担的责任 |
| --- | --- | --- |
| App Lab / App CLI | 组织 App、导入/运行入口、日志观察和应用管理 | 替代业务逻辑或证明物理动作已完成 |
| `app.yaml` | 声明 App 名称、描述、端口和 Brick 依赖 | 保存未经治理的秘密或记录硬件验收 |
| Python | Linux 侧流程、数据处理、界面/服务和请求编排 | 直接假定 MCU 已执行某个动作 |
| Arduino Sketch | MCU 侧引脚、传感器、执行器和实时状态机 | 依赖 Linux 文件系统或网络可用性 |
| Brick | 为 App 增加预打包能力，例如数据库、视觉或服务 | 自动替应用定义业务验收条件 |
| Bridge / RPC | 在 Linux 与 MCU 之间传递请求和结果 | 把传输成功自动等同于业务成功 |
| 设备观察 | 读取实际输出、状态或现场结果 | 被启动日志替代 |

第四篇已经建立了请求身份、`UNKNOWN`、结果账本和证据收敛模型。本篇把这个模型落到 App 的目录和入口上：先确认“这个项目是什么”，再确认“它是否启动”，最后才讨论“设备做了什么”。

### 1.2 App、Sketch 和 Brick 可以独立变化

一个只有 Python 的 App 可以没有 `sketch/`；一个需要 MCU 的 App 才把 Sketch 加入根目录。Brick 是可选扩展，并不因为它出现在 `app.yaml` 中就自动证明容器已拉取、服务已启动或接口可用。

这会影响排障顺序：

1. `app.yaml` 不存在，先处理项目结构，不讨论 Bridge。
2. `python/main.py` 不存在，先处理 Linux 入口，不讨论 Python 业务结果。
3. `sketch/` 只存在半套文件，先处理 Sketch 项目完整性，不把启动失败归因于网络。
4. 启动日志成功但 Python 日志报错，问题在 Linux 应用路径，不代表 MCU 失败。
5. Python 和 Sketch 日志都存在，仍需设备侧观察，不能只凭日志说输出已发生。

## 2. App 根目录与运行角色

### 2.1 推荐的目录形状

下面是一个同时包含 Python 和 Sketch 的教学项目。目录名、版本和运行时文件应根据目标 App Lab 版本再核对；这里的树形图只表达职责和必选关系：

~~~text
demo-app/
├── app.yaml                  # 必需：App 描述符
├── README.md                 # 可选：给用户看的说明
├── python/
│   ├── main.py               # 必需：Python 入口
│   └── requirements.txt      # 可选：Python 依赖
├── sketch/
│   ├── sketch.ino            # 可选组：MCU Sketch 源文件
│   └── sketch.yaml           # 可选组：Sketch 依赖声明
├── data/                     # 保留目录：持久应用数据
└── .cache/                   # 保留目录：易失运行数据
~~~

规范中的关键不是“文件越多越完整”，而是入口和生命周期清楚：`app.yaml` 让运行时识别 App；`python/main.py` 提供 Linux 侧入口；`sketch/` 若存在，就必须能被当作一个完整的 Sketch 项目处理。根目录的 `README.md` 还可以为 App Lab 提供说明；当 `description` 缺失时，规范允许从 README 的第一个非标题段落推导描述。

### 2.2 目录存在不等于功能成立

`data/` 与 `.cache/` 的语义不同：前者用于用户可访问、可备份或可清理的应用状态；后者用于虚拟环境、Docker Compose 支持文件等易失运行内容。分享 App 前应清理个人数据，删除 `.cache/` 前则要确认 App 没有运行。

这两个目录都不应成为“运行成功”的证据。一个空的 `data/` 目录只能说明项目允许保存状态；一个生成的 `.cache/` 目录只能说明某个运行步骤产生了缓存。它们不能证明 Python 已经启动，更不能证明 MCU 已执行动作。

### 2.3 描述符和依赖的最小治理

`app.yaml` 是 YAML 文件，不是任意扩展名的配置文件；规范要求文件名严格为 `app.yaml`，并允许声明 `name`、`icon`、`description`、`ports` 和 `bricks`。Brick 的配置可以包含模型、变量和设备映射，但变量是否为秘密由 Brick 定义决定；导出时被标记为秘密的变量会被自动清除，不能因此放松本地日志、示例和版本库中的秘密治理。

本书的建议是：

- 用稳定的、人类可读的 `name` 和短 `description` 解释应用意图。
- 只暴露确实需要的端口，并在文档中说明监听进程和停止方式。
- 把 Brick ID、模型和设备映射作为可审查的依赖清单，不把“列入清单”写成“已经可用”。
- 不在示例中放置真实密码、API Key、设备地址、序列号或现场数据。
- 把持久数据、临时缓存和可再生成产物分开，导出前检查 `data/` 是否含有个人或现场信息。

## 3. `app.yaml`：声明应用意图，不是设备验收

一个最小的 Python-only 描述符可以是：

~~~yaml
name: App Lab Contract Demo
icon: 🧭
description: Validate an App structure before connecting a board
ports:
  - 8080
bricks: []
~~~

这个片段只说明运行时应如何识别应用和端口，不说明：

1. 主机是否安装了对应版本的 App Lab。
2. Python 依赖是否能在目标 Linux 镜像中安装。
3. 端口是否已经被防火墙、其他服务或网络模式阻断。
4. Brick 是否下载成功、模型是否加载成功或设备映射是否满足。
5. Python 发出的 Bridge 请求是否被 MCU 接受并执行。

因此，描述符检查应该放在最前面，但不能成为唯一的验证门。建议把验证拆成五层：

| 层级 | 问题 | 最小证据 |
| --- | --- | --- |
| 结构 | App 是否具备必需入口 | 文件清单、`app.yaml` 解析结果 |
| 启动 | 运行时是否完成启动阶段 | Start-up 日志、退出原因 |
| 进程 | Python/Sketch 是否有各自输出 | Main（Python）和 Sketch 日志 |
| 通信 | 请求是否被正确关联和返回 | request ID、Bridge/RPC 观察 |
| 设备 | 目标状态是否真实改变 | 读回、波形、传感器或现场观察 |

前两层可以在没有硬件时部分验证；后三层必须严格区分本地替身、软件日志和设备证据。

## 4. Fig-28：项目结构与设备入口

<a id="fig-28-uno-q-app-lab-app-structure-boundary"></a>

~~~mermaid
flowchart LR
    subgraph APP[Arduino App 根目录]
        MANIFEST[app.yaml\n必需：应用描述]
        PYTHON[python/\nmain.py 必需]
        SKETCH[sketch/\n可选：sketch.ino + sketch.yaml]
        README[README.md\n可选：说明入口]
        DATA[data/\n持久应用数据]
        CACHE[.cache/\n易失运行数据]
    end

    LAB[App Lab / App CLI\n导入 · 运行 · 观察]
    LINUX[Linux / Python / Bricks\nMPU 侧运行时]
    MCU[Arduino Sketch\nMCU 侧实时边界]
    BRIDGE[Bridge / RPC\n逻辑通信边界]
    EVIDENCE[证据分层\n启动 · Python · Sketch · 设备观察]

    LAB --> MANIFEST
    LAB --> PYTHON
    LAB --> SKETCH
    LAB --> README
    MANIFEST --> LINUX
    PYTHON --> LINUX
    SKETCH --> MCU
    LINUX <--> BRIDGE
    BRIDGE <--> MCU
    LAB --> EVIDENCE
    LINUX --> EVIDENCE
    MCU --> EVIDENCE

    classDef required fill:#e8f1ff,stroke:#2563eb,color:#0f172a
    classDef optional fill:#fef3c7,stroke:#d97706,color:#0f172a
    classDef boundary fill:#dcfce7,stroke:#16a34a,color:#0f172a
    class MANIFEST,PYTHON required
    class SKETCH,README,DATA,CACHE optional
    class LAB,LINUX,MCU,BRIDGE,EVIDENCE boundary
~~~

图 5-1（Fig-28）把目录、运行角色和证据边界放在同一张图中。图源为[Mermaid 文件](../../diagrams/uno-q-app-lab-app-structure-boundary.mmd)，导出图示为[Fig-28 SVG](../../images/第5篇_AppLab/ch01-fig28-uno-q-app-lab-app-structure-boundary.svg)，登记记录见[第五篇图示资源](../../images/第5篇_AppLab/README.md#fig-28-uno-q-app-lab-app-structure-boundary)。它是本书根据官方 App 规范绘制的教学图，不是 Arduino 官方协议图或 UNO Q 内部连线图。

图中 `Bridge / RPC` 使用逻辑边界表示：它提示两侧存在消息协作，但没有承诺某个方法名、接口版本、调用时序或“恰好一次”语义。`证据分层` 也不是一个 App 目录，它提醒读者把启动、进程、通信和设备观察分开保存。

## 5. 从导入到运行：先验证入口再验证行为

### 5.1 两种入口，三类问题

UNO Q User Manual 说明 App Lab 可以在 PC-hosted 模式下使用，也可以在单板机模式下运行；网络模式依赖本地网络发现，能通过浏览器、SSH 或 IP 访问设备，也不自动保证设备会出现在 App Lab 的 Network Mode 列表中。[UNO Q User Manual](https://github.com/arduino/docs-content/blob/main/content/hardware/02.uno/boards/uno-q/tutorials/01.user-manual/content.md)

因此，遇到“看不到板子”时，至少要把问题拆成：

- **入口问题**：App Lab 本身、USB/网络发现、权限或登录是否成立。
- **项目问题**：App 目录、描述符、Python 入口或 Sketch 文件是否完整。
- **运行问题**：启动阶段、Python 进程、Sketch 编译或 Bridge 调用是否报错。

不要因为能 SSH 就直接推断 App Lab 入口已经可用；也不要因为 App Lab 能打开项目，就推断设备端已经运行。

### 5.2 日志至少分成三条线

官方 UNO Q 文档把运行观察分为启动序列、Python 输出和 Sketch 输出。实践中可以用下面的记录表，不把三种日志拼成一行“运行成功”：

| 日志线 | 应回答的问题 | 失败时的动作 |
| --- | --- | --- |
| Start-up | 应用是否完成导入、编译和启动准备 | 保留启动阶段的原始错误，停止解释业务结果 |
| Main（Python） | Linux 入口是否启动、依赖是否可用 | 记录异常和版本，先修复 Python 侧 |
| Sketch（MCU） | MCU Sketch 是否编译并进入运行路径 | 区分编译错误、串口输出和真实引脚观察 |

一个 App 可能启动成功后仍在 Python 运行时失败；一个 Sketch 可能有串口输出但没有产生目标波形；一个 Bridge 调用可能返回成功但设备状态仍需读回。证据必须随着层级增加而增加，而不是被最早的“Run 完成”覆盖。

### 5.3 不把当前 UI 操作写成永久协议

App Lab 的菜单、启动项位置和日志界面可能随版本变化。本章只固定可复核的对象：项目文件、入口、日志类别、证据字段和停止条件。具体按钮位置应以当前 App Lab 和 UNO Q User Manual 为准；书稿不把某个版本的 UI 截图当作长期接口。

## 6. 实验一：验证 App 文件结构

这个实验把 App specification 中的结构要求转换为一个不依赖 YAML 第三方库的本地契约函数。它接收一个已经被调用方解析出的 manifest 映射和文件路径集合，检查必需入口、可选 Sketch 成对文件、端口范围和 Brick 配置类型。

**代码说明**

- 用途：在导入 App Lab 或连接 UNO Q 前，先验证项目目录是否满足最小结构契约。
- 运行环境：Python 3.10 或更高版本；Windows、Linux 或 macOS 均可。
- 文件位置：`code/第5篇_AppLab/第1章_App_Lab开发基础/app_contract.py`。
- 依赖：仅 Python 标准库 `dataclasses` 和 `typing`；不安装 YAML 解析器，不访问网络或设备。
- 操作步骤：在仓库根目录执行下方代码；测试使用内存中的字典和路径集合，不会修改 App 文件。
- 预期输出：一个同时包含 Python 与 Sketch 的有效结构、保留目录说明，以及缺少 `python/main.py` 的失败结果。
- 故障排查：若提示 `missing sketch/sketch.yaml`，说明 `sketch/` 只复制了一半；若端口被拒绝，检查是否为 1～65535 的整数；不要通过删除校验来绕过结构问题。
- 验证方式：运行本章 `test_app_contract.py`，确认 Python-only、带 Sketch、缺入口、半套 Sketch、非法端口/Brick 和保留目录场景均有明确结果。

~~~python
"""Offline checks for the structural contract of an Arduino App."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


class AppContractError(ValueError):
    """Raised when an App manifest and its files cannot form a safe project."""


@dataclass(frozen=True)
class LayoutResult:
    mode: str
    required: tuple[str, ...]
    optional: tuple[str, ...]


def validate_layout(
    manifest: Mapping[str, object], files: set[str],
) -> LayoutResult:
    """Validate App Lab's file-level contract without opening a board or YAML parser."""
    if not isinstance(manifest, Mapping):
        raise AppContractError("manifest must be a mapping")
    if "app.yaml" not in files:
        raise AppContractError("missing app.yaml")
    if "python/main.py" not in files:
        raise AppContractError("missing python/main.py")

    ports = manifest.get("ports")
    if ports is not None and (
        not isinstance(ports, list)
        or any(isinstance(port, bool) or not isinstance(port, int) or not 1 <= port <= 65535 for port in ports)
    ):
        raise AppContractError("ports must be a list of TCP port integers")

    bricks = manifest.get("bricks")
    if bricks is not None and (
        not isinstance(bricks, list)
        or any(not isinstance(brick, (str, Mapping)) for brick in bricks)
    ):
        raise AppContractError("bricks must be a list of IDs or configurations")

    sketch_files = {"sketch/sketch.ino", "sketch/sketch.yaml"}
    has_sketch_folder = any(path == "sketch" or path.startswith("sketch/") for path in files)
    if not has_sketch_folder:
        return LayoutResult("PYTHON_ONLY", ("app.yaml", "python/main.py"), ())
    missing = sorted(sketch_files - files)
    if missing:
        raise AppContractError(f"missing {missing[0]}")
    return LayoutResult(
        "PYTHON_AND_SKETCH",
        ("app.yaml", "python/main.py"),
        ("sketch/sketch.ino", "sketch/sketch.yaml"),
    )


def _demonstrate() -> None:
    valid = validate_layout(
        {"name": "Contract Demo", "ports": [8080], "bricks": ["arduino:web_ui"]},
        {"app.yaml", "python/main.py", "sketch/sketch.ino", "sketch/sketch.yaml"},
    )
    print(f"SIMULATED valid={valid.mode} app_yaml=present python_main=present")
    print("SIMULATED sketch=optional-present sketch_ino=present sketch_yaml=present")
    print("SIMULATED reserved=data:persistent,.cache:volatile")
    try:
        validate_layout({"name": "Contract Demo"}, {"app.yaml"})
    except AppContractError as error:
        print(f"SIMULATED invalid={error}")


if __name__ == "__main__":
    _demonstrate()
~~~

预期输出：

~~~text
SIMULATED valid=PYTHON_AND_SKETCH app_yaml=present python_main=present
SIMULATED sketch=optional-present sketch_ino=present sketch_yaml=present
SIMULATED reserved=data:persistent,.cache:volatile
SIMULATED invalid=missing python/main.py
~~~

这里的 `PYTHON_AND_SKETCH` 只表示文件集合满足本地结构判断；它不表示 `python/main.py` 已被目标 Linux 解释器执行，也不表示 `sketch.ino` 已经被编译或刷写。

## 7. 实验二：按日志证据判定启动状态

第二个实验把“启动成功”拆成启动阶段、Python 输出和可选 Sketch 输出。函数只分类调用方提供的日志，不读取文件、不启动进程、不连接设备。它的设计目标是让缺失证据保持缺失，而不是把缺失项填成成功。

**代码说明**

- 用途：练习按组件区分启动失败、Python 运行时错误、Sketch 日志缺失和需要设备观察的状态。
- 运行环境：Python 3.10 或更高版本；普通本地终端即可。
- 文件位置：`code/第5篇_AppLab/第1章_App_Lab开发基础/launch_evidence.py`。
- 依赖：仅 Python 标准库 `dataclasses`；输入是内存中的不可变日志证据。
- 操作步骤：在仓库根目录执行下方代码，再运行 `test_launch_evidence.py`；不要把真实密码、完整网络地址或现场数据放入示例日志。
- 预期输出：编译失败停止在启动层；Python-only 只要求 Python 日志；含 Sketch 的 App 即使两侧日志存在，也仍标记为需要设备侧断言。
- 故障排查：若 Sketch 日志为空，不要改成 `READY`；若启动阶段不是 `READY`，先处理导入/编译/权限问题；若出现 `ERROR`，保留原始日志并按对应侧排查。
- 验证方式：运行本章 `test_launch_evidence.py`，逐项检查启动失败、Python-only、Sketch 日志完整、Sketch 日志缺失和两侧运行时错误。

~~~python
"""Classify App Lab launch logs without claiming hardware success."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LaunchEvidence:
    startup: str
    python_lines: tuple[str, ...]
    sketch_present: bool
    sketch_lines: tuple[str, ...]


@dataclass(frozen=True)
class LaunchDecision:
    action: str
    reason: str


def assess_launch(evidence: LaunchEvidence) -> LaunchDecision:
    """Classify only the local launch evidence supplied by the caller."""
    if evidence.startup != "READY":
        return LaunchDecision("BLOCKED_STARTUP", "startup did not reach READY")
    if any(line.startswith("ERROR") for line in evidence.python_lines):
        return LaunchDecision("PYTHON_RUNTIME_ERROR", "Python log contains an ERROR line")
    if not evidence.python_lines:
        return LaunchDecision("MISSING_PYTHON_LOG", "Python log is empty")
    if not evidence.sketch_present:
        return LaunchDecision("PYTHON_LOG_READY", "Python log is present; no sketch is part of this App")
    if any(line.startswith("ERROR") for line in evidence.sketch_lines):
        return LaunchDecision("SKETCH_RUNTIME_ERROR", "Sketch log contains an ERROR line")
    if not evidence.sketch_lines:
        return LaunchDecision("MISSING_SKETCH_LOG", "Sketch is present but its log is empty")
    return LaunchDecision(
        "SKETCH_LOG_READY_NEEDS_DEVICE_ASSERTION",
        "startup, Python and Sketch logs are present; device behavior remains unproved",
    )


def _demonstrate() -> None:
    cases = (
        ("compile_error", LaunchEvidence("COMPILE_FAILED", (), True, ())),
        ("python_only", LaunchEvidence("READY", ("INFO app started",), False, ())),
        (
            "app_with_sketch",
            LaunchEvidence("READY", ("INFO app started",), True, ("INFO sketch started",)),
        ),
        ("missing_sketch", LaunchEvidence("READY", ("INFO app started",), True, ())),
    )
    for label, evidence in cases:
        print(f"SIMULATED {label}={assess_launch(evidence).action}")


if __name__ == "__main__":
    _demonstrate()
~~~

预期输出：

~~~text
SIMULATED compile_error=BLOCKED_STARTUP
SIMULATED python_only=PYTHON_LOG_READY
SIMULATED app_with_sketch=SKETCH_LOG_READY_NEEDS_DEVICE_ASSERTION
SIMULATED missing_sketch=MISSING_SKETCH_LOG
~~~

`SKETCH_LOG_READY_NEEDS_DEVICE_ASSERTION` 是本实验故意使用的长名称：它把“日志证据存在”和“设备行为已被观察”明确分开。即使真实 App Lab 控制台显示 Python 与 Sketch 都有输出，也仍需根据动作类型设计读回、波形、传感器、LED 或现场安全观察。

## 8. 设备入口、网络模式与权限边界

### 8.1 PC-hosted、SBC 和 Network Mode

UNO Q User Manual 描述了 PC-hosted 与 Single-Board Computer 两种使用方式，也说明 Network Mode 使用局域网发现来连接设备。网络发现受 mDNS、访客网络、企业网络、VPN 和防火墙规则影响；“设备能被 SSH 访问”与“设备出现在 App Lab 列表中”是不同断言。

建议首次接入时保存如下记录：

~~~text
host_mode: PC-hosted | SBC | Network Mode
app_lab_version: <实际版本>
board_identity: <脱敏后的设备标识>
discovery: visible | not-visible | not-tested
authentication: passed | failed | not-tested
project_import: passed | failed | not-tested
~~~

不要把密码、完整 IP、序列号或访问令牌提交到本书仓库。记录应足够让后续人员知道验证到哪一层，但不足以让不相关人员直接访问设备。

### 8.2 连接成功与运行成功不是一个门

连接门只回答“开发入口是否可用”；运行门回答“项目是否完成启动”；业务门回答“目标动作是否有可归因证据”。三个门可以独立失败：

```text
连接失败       -> 无法进行后续 App Lab 验证
连接成功/导入失败 -> 项目结构或权限问题
导入成功/启动失败 -> App、Sketch 或运行时问题
启动成功/动作未知 -> 需要 Bridge 对账或设备侧观察
```

这也是为什么本章实验不模拟“连接成功”：本地函数只验证结构和日志决策，避免给读者一个虚假的设备在线感。

## 9. Brick、数据目录与秘密

Brick 可以让 App 获得数据库、视觉、Web 服务或其他预打包能力。它们把部署复杂度降低，却没有消除依赖、版本、资源和秘密问题。建议为每个 Brick 维护一行依赖记录：

| 字段 | 示例 | 证据要求 |
| --- | --- | --- |
| Brick ID | `arduino:web_ui` | `app.yaml` 中声明，记录核验日期 |
| 版本/模型 | `<版本或模型 ID>` | 记录目标环境实际解析值 |
| 资源 | 端口、设备、内存、存储 | 目标板检查，不由声明文件替代 |
| 变量 | 非敏感配置名 | 值不写入本仓库或普通日志 |
| 健康检查 | 进程、端口、API、设备观察 | 记录具体命令和输出摘要 |

`data/` 需要纳入备份和清理策略；`.cache/` 需要纳入重建和删除策略。导出前应检查两者是否含有个人数据、模型、令牌、日志或大体积临时文件。即使 App specification 说明某些 Brick secret 在导出时会被自动清除，也不能把导出动作当成秘密扫描的替代品。

## 10. 验证矩阵、练习与交接

### 10.1 本章验证矩阵

| 编号 | 验证项 | 本地可验证内容 | 当前未覆盖内容 |
| --- | --- | --- | --- |
| APP-01 | 最小目录 | `app.yaml`、`python/main.py` 存在 | App Lab 真实导入 |
| APP-02 | Sketch 成对文件 | `sketch.ino` 与 `sketch.yaml` 同时存在 | Arduino CLI/编译器构建 |
| APP-03 | 描述符字段 | 端口和 Brick 的基本类型/范围 | 目标运行时的完整 YAML 语义 |
| APP-04 | 启动证据 | 启动、Python、Sketch 日志的分类顺序 | App Lab 控制台真实输出 |
| APP-05 | 设备边界 | 含 Sketch 的日志结果仍要求设备断言 | UNO Q、MCU、Bridge 实机 |
| APP-06 | 图示追溯 | Mermaid 与本章源文件一致 | 图示是否符合某个具体 UI 版本 |
| APP-07 | 数据治理 | `data/`、`.cache/` 的责任区分 | 目标板实际备份、清理和权限 |

### 10.2 练习

1. 从一个 Python-only App 增加空的 `sketch/` 目录，预测 `validate_layout()` 的结果。为什么“目录存在”不等于 Sketch 完整？
2. 把 `python/main.py` 改成 `python/app.py`，说明为什么应用可以有很多 Python 文件，但仍需要保留规范要求的入口。
3. 让 `LaunchEvidence` 的 `startup` 为 `READY`、Python 有输出、Sketch 为空。为什么结果不是成功？
4. 为一个 `arduino:dbstorage` Brick 设计变量清单，分别标出可公开的变量名、不可提交的变量值和需要设备检查的资源。
5. 对一次真实运行建立三条日志记录，再补一条设备观察。指出哪一条证据能证明“请求被接收”，哪一条才能支持“目标状态已改变”。

### 10.3 跨篇交接

- 第三篇第 8 章提供预检、健康门、证据包、`UNKNOWN` 和交接模型；本章把其中的应用入口细化为 App 目录和日志层。
- 第四篇第 1～4 章提供消息模型、并发边界、连接恢复和结果账本；本章不重新定义请求状态，而是说明这些状态从哪个 App 入口产生。
- 第五篇后续章节将继续讨论 App 生命周期、运行日志、启动配置和部署验证；当前章节只建立结构和证据语言。
- 第九篇项目篇必须把 App 结构、运行环境、设备观察和验收条件一起纳入项目交付清单。

## 11. 常见问题

### 11.1 为什么 `app.yaml` 存在了还要检查 `python/main.py`？

描述符只告诉运行时“有一个 App”；`python/main.py` 才是规范要求的 Linux 侧 Python 入口。二者缺一不可。结构检查先拒绝缺入口项目，可以把后续错误留给真正的运行时问题。

### 11.2 没有 `sketch/` 的 App 是不完整的吗？

不是。App specification 将 Sketch 目录定义为可选；Python-only App 可以不包含 MCU 代码。只有当项目声明或实际需求包含 Sketch 时，才必须同时提供 `sketch.ino` 和 `sketch.yaml`。

### 11.3 Python 日志没有错误，能否说明 LED 已经亮了？

不能。Python 日志最多说明 Linux 侧代码走到了某个输出点。还需要确认请求被正确关联、Bridge/MCU 侧收到并处理，并通过读回、波形或现场观察证明目标行为。

### 11.4 App Lab 看不到板子，是项目结构错误吗？

不一定。可能是 USB、网络发现、mDNS、防火墙、权限、登录或 App Lab 版本问题。先记录入口层证据，再检查项目文件，避免把连接故障直接归因于 Python 或 Sketch。

### 11.5 为什么不在示例中直接写完整 `app.yaml` 和真实 Brick 密码？

因为可复制的结构与现场秘密是两类资产。示例可以展示字段形状和占位值，但真实值必须在受控环境注入，并在导出、日志、提交和交接前分别检查。

### 11.6 `data/` 和 `.cache/` 都是目录，为什么处理方式不同？

`data/` 面向需要保留、备份或清理的应用状态；`.cache/` 面向可以重建的易失运行内容。把二者混合会导致分享时泄露数据，或清理缓存时误删业务状态。

## 12. 本章小结与下一步

App Lab 的第一个工程问题不是“按钮在哪里”，而是“这个 App 由哪些组件组成、入口在哪里、每个结果由什么证据支撑”。`app.yaml`、`python/main.py` 和可选 `sketch/` 固定了项目结构；`data/` 与 `.cache/` 固定了数据生命周期；启动、Python、Sketch 和设备观察固定了证据分层。

本章的两个实验只证明本地契约函数和判定函数的行为。它们没有连接设备，也没有替代 Arduino App Lab 的实际运行。下一章将沿着本章的目录和日志边界，进入 App 的生命周期、运行日志、停止与重启策略；读者应先能够解释为什么“项目可导入”“Python 有输出”和“设备已完成动作”必须写成三个不同结论。

## 延伸阅读

- [Arduino App specification](https://github.com/arduino/arduino-app-cli/blob/main/docs/app-specification.md)：App 根目录、`app.yaml`、Python、Sketch、README、`data/`、`.cache/` 和 Brick 字段。
- [Arduino UNO Q User Manual](https://github.com/arduino/docs-content/blob/main/content/hardware/02.uno/boards/uno-q/tutorials/01.user-manual/content.md)：PC-hosted、SBC、Network Mode、Hello World 和运行入口边界。
- [Arduino UNO Q 产品页](https://docs.arduino.cc/hardware/uno-q)：双处理器、App Lab、Arduino IDE 和 Bridge 的产品层说明。
- [Arduino App Lab 示例](https://docs.arduino.cc/software/app-lab/getting-started/examples)：官方示例入口和应用类型索引；示例本身不替代本章的证据边界。
- [Arduino App CLI 用户文档](https://github.com/arduino/arduino-app-cli/blob/main/docs/user-documentation.md)：App 目录、运行时目录和环境变量参考；具体目标镜像仍需现场核验。
- [本章配套代码](../../code/第5篇_AppLab/第1章_App_Lab开发基础/README.md)
- [第五篇图示登记](../../images/第5篇_AppLab/README.md)
- [全书目录](../../SUMMARY.md)
