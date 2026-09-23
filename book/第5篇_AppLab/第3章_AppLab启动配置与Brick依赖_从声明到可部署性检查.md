---
title: App Lab 启动配置与 Brick 依赖：从声明到可部署性检查
part: 5
chapter: 3
status: draft
last_verified: 2026-09-23
updated: 2026-09-23
prerequisites: 第五篇第1～2章、第三篇第8章、第四篇第1～4章
tags: App Lab, app.yaml, Brick, 依赖, 部署预检, 端口, 证据
---

# 第3章 App Lab 启动配置与 Brick 依赖：从声明到可部署性检查

## 学习目标

读完本章后，读者应能够：

1. 区分 App 描述文件中的“声明合法”、目标环境中的“依赖满足”和设备侧的“部署成功”。
2. 根据 Arduino App 规范阅读 `app.yaml` 的 `ports`、`bricks`、`model`、`variables` 和 `devices`。
3. 用一个本地声明检查器发现端口、Brick 选项、变量类型和设备引用错误。
4. 用能力快照把 Brick、模型、设备和端口占用情况解析成 `READY`、`MISSING_*`、`CONFLICTING_PORT` 或 `UNKNOWN`。
5. 解释 `data/`、`.cache/` 和敏感变量在导入、导出、共享和运行时之间的边界。
6. 为真实 App Lab/CLI 运行准备一份不会把本地模拟结果冒充为 UNO Q 部署回执的预检记录。

## 背景与边界

Arduino App 规范把一个 App 定义为一个自包含的根目录，根目录中必须有 `app.yaml` 和 `python/main.py`；`sketch/` 是可选的，但一旦存在就需要同时包含 `sketch.ino` 和 `sketch.yaml`。[Arduino App specification](https://github.com/arduino/arduino-app-cli/blob/main/docs/app-specification.md) 这给出了**文件和声明层**的入口，却没有替我们证明目标板上已经安装了某个 Brick、模型或外设。

同一规范还把职责分到两侧：Sketch 在集成 MCU 上运行，Python、Brick 和容器在 Linux 上运行，Sketch 与 Python 通过基于 RPC 的消息协作。`app.yaml` 可以声明暴露端口和所需 Brick；Brick 配置还可以包含模型、变量和设备引用。[Arduino App specification](https://github.com/arduino/arduino-app-cli/blob/main/docs/app-specification.md) 因此，“启动配置正确”至少要经过三层判断：文件结构成立、声明形状正确、目标环境能够满足声明。

本章只建立一个**本地、可重复的部署预检模型**。它不会：

- 解析真实 App Lab 界面或调用 `arduino-app-cli`；
- 查询 UNO Q 上实际安装的 Brick、模型、容器、端口或设备节点；
- 编译、刷写或启动 Python、Sketch、Router、Bridge 或 Brick；
- 把 `READY` 写成“已经部署”，也不把变量占位符写成真实密钥；
- 替代目标板上的版本、权限、空间、网络、日志和物理设备核验。

本章与[第五篇第1章](./第1章_App_Lab开发基础_应用结构与验证边界.md)的关系是：第 1 章回答“项目应该长什么样”，本章回答“声明能否进入运行前置检查”。与[第五篇第2章](./第2章_AppLab运行生命周期_导入启动运行与停止.md)的关系是：第 2 章从运行请求开始建立 `run_id` 和状态顺序，本章在运行请求之前增加配置与依赖门槛。

## 1. 从“声明存在”到“可以部署”

### 1.1 四种容易混淆的结论

一个 App 工程经常同时出现四个不同问题：

| 结论 | 它回答的问题 | 最小证据 | 不能推出的结论 |
| --- | --- | --- | --- |
| `VALID` | 描述文件的字段和类型是否合理？ | 本地契约报告 | Brick 已安装、端口空闲 |
| `READY` | 给定能力快照是否满足声明？ | 快照版本、时间和匹配结果 | App Lab 已经导入或运行 |
| `PREFLIGHT_PASS` | 目标环境的运行前置条件是否满足？ | 目标板预检记录 | 业务动作已经完成 |
| `DEPLOYED` | 部署动作是否有目标侧回执？ | CLI/App Lab 回执、日志和对象标识 | 传感器、电机或外部系统已达到目标状态 |

本章的两个程序最多产生前两类结果。`VALID` 只处理输入形状；`READY` 只对调用者提供的能力快照负责。若能力快照是空映射，含义是“已观察到没有匹配项”；若快照是 `None`，含义是“没有拿到清单”，结果必须是 `UNKNOWN`。

### 1.2 声明、解析与执行是三条不同的线

可以把启动前的工作拆成下面三条线：

1. **声明线**：读取项目文件，检查 `app.yaml` 的字段类型、端口范围和 Brick 配置形状。
2. **解析线**：将声明中的 Brick、模型、设备和端口与某个有时间戳的本地能力快照比对。
3. **执行线**：由 App Lab 或 CLI 真正导入、准备、启动并产生目标设备回执。

前两条线可以在没有 UNO Q 的情况下测试，第三条线不可以。把三条线合并成一个 `deploy()` 函数，会让测试报告看起来很完整，却无法回答“结果到底来自哪里”。

## 2. `app.yaml` 的三层检查

### 2.1 从官方字段到本地规则

官方规范将 `ports` 定义为应用暴露的整数端口列表，将 `bricks` 定义为所需 Brick ID 的列表；Brick 条目可以附加 `model`、`variables` 和 `devices`。变量和变量值都必须是字符串，设备引用是字符串列表。[Arduino App specification](https://github.com/arduino/arduino-app-cli/blob/main/docs/app-specification.md)

教学示例可以写成：

~~~yaml
name: Smart Garden
description: AI-powered irrigation and monitoring system
ports:
  - 5000
bricks:
  - arduino:dbstorage:
      variables:
        DB_PASSWORD: "${DB_PASSWORD}"
  - arduino:objectdetection:
      model: yolo-v8
      devices:
        - remote_camera_0
~~~

这里的 `${DB_PASSWORD}` 是本书为本地示例约定的**占位值**，不是 App 规范要求的特殊语法。规范说明，敏感变量的识别来自 Brick 自身的定义；在 `app.yaml` 中仍按普通变量写入，导出时由系统依据 Brick 的 Secret 标记进行脱敏。[Arduino App specification](https://github.com/arduino/arduino-app-cli/blob/main/docs/app-specification.md)

### 2.2 第一层：字段形状

第一层不需要目标板，只检查：

- `ports` 是列表，每个元素是 `1～65535` 的整数，且不重复；
- `bricks` 是列表，每个元素是 Brick ID 字符串，或只包含一个 Brick ID 的配置映射；
- `model` 是非空字符串；
- `variables` 是映射，键和值都是字符串；
- `devices` 是非空字符串列表；
- 可选字段没有被误写成未知的本地配置选项。

这层发现的是“配置无法稳定解释”的问题。例如把 `MODE: 1` 写成整数，把 `devices: camera_0` 写成字符串，或者在同一个 Brick 条目中放入两个 ID，均应在进入运行阶段前停止。

### 2.3 第二层：声明语义

字段类型正确不等于声明语义正确。`arduino:objectdetection` 和 `arduino:dbstorage` 都可能是字符串，但它们的职责、模型和设备要求不同；端口是合法整数也不代表目标板上没有其他服务占用它。

因此，本书把第二层的结果限定为“规范化后的需求集合”：

```text
BrickRequirement(
    brick_id="arduino:objectdetection",
    model="yolo-v8",
    devices=("remote_camera_0",),
)
```

它仍然不是目标板事实。它只是把 YAML 语义转换为后续解析器能够处理的稳定数据结构。

### 2.4 第三层：目标环境预检

第三层才需要访问目标环境，至少要回答：

1. 目标 App CLI/App Lab 版本是否与项目预期一致？
2. 需要的 Brick 是否存在，模型是否可加载？
3. `devices` 中的引用是否与目标环境的设备类别和连接状态匹配？
4. `ports` 是否空闲，运行用户是否有必要权限？
5. `data/`、`.cache/`、空间、网络和凭据边界是否符合发布策略？

当前章节不执行这些访问，只定义它们在证据链中的位置。实际运行时可参考 [Arduino App CLI user documentation](https://github.com/arduino/arduino-app-cli/blob/main/docs/user-documentation.md)，但文档中的默认目录和环境变量不能直接替代当前 UNO Q 镜像、权限和版本的现场确认。

## 3. Brick 依赖的最小模型

### 3.1 “Brick 存在”不够

一个 Brick 依赖可以抽象为四元组：

| 项目 | 示例 | 检查问题 |
| --- | --- | --- |
| Brick ID | `arduino:objectdetection` | 目标环境是否提供同一个 ID？ |
| 模型 | `yolo-v8` | Brick 能力快照是否包含这个模型？ |
| 设备 | `remote_camera_0` | 设备引用是否在能力快照中？ |
| 端口 | `5000` | 目标环境是否已被其他服务占用？ |

其中，模型和设备都是可选声明。没有声明模型，不应由本地检查器擅自挑选一个模型；没有声明设备，也不应由检查器假定“默认摄像头”一定存在。这种保守规则能把未知留给目标环境，而不是把猜测写进部署证据。

### 3.2 能力快照和时间边界

能力快照是调用者提供的观察结果，例如：

```text
snapshot_id: board-a-2026-09-23T09:30+08:00
brick: arduino:objectdetection
models: yolo-v8
devices: remote_camera_0
occupied_ports: 8080
```

解析结果只对这份快照的时间有效。若之后安装了模型、拔出了摄像头或启动了新的服务，旧的 `READY` 不应自动延长有效期。实际系统应把快照 ID、采集时间、采集入口和版本写入证据包；本章示例用函数参数表达这一边界。

### 3.3 判定状态的优先级

本章使用如下状态：

| 状态 | 含义 | 后续动作 |
| --- | --- | --- |
| `READY` | 所有声明的 Brick、模型、设备和端口都与快照匹配 | 进入目标环境预检 |
| `MISSING_BRICK` | Brick ID 不在能力快照中 | 核对安装来源、版本和目标板 |
| `MISSING_MODEL` | Brick 存在，但请求模型不在快照中 | 核对模型包或 Brick 配置 |
| `MISSING_DEVICE` | Brick 存在，但设备引用不满足 | 核对设备类别、连接和映射 |
| `CONFLICTING_PORT` | 声明端口已被占用 | 释放端口或修改配置 |
| `UNKNOWN` | 能力清单或端口清单不可用 | 查询、补证据或人工复核 |

如果同时存在多个缺口，返回结果要保留完整 `missing` 和 `conflicts` 列表；状态名称用于路由，列表用于修复。优先报告 Brick 缺失，再报告模型、设备和端口冲突，能让最基础的依赖问题先被处理。

## 4. Fig-30：声明、能力解析与部署边界

<a id="fig-30-uno-q-app-lab-deployability-boundary"></a>

下面的图把本章的证据边界画成一条有分支的流水线：声明契约失败时回到修复；声明通过后才进入能力快照解析；`READY` 仍然要经过目标环境预检，才有资格尝试部署。`data/`、`.cache/` 和敏感变量则在共享包边界上单独处理。

~~~mermaid
flowchart LR
    APP["App 根目录<br/>app.yaml · python/main.py"] --> CONTRACT["声明契约检查<br/>字段 · 端口 · Brick 选项"]
    CONTRACT -->|通过| RESOLVE["能力快照解析<br/>Brick · model · devices"]
    CONTRACT -->|失败| REPAIR["修复声明<br/>重新检查"]
    RESOLVE --> READY["READY<br/>声明与快照匹配"]
    RESOLVE --> MISSING["MISSING_*<br/>Brick · 模型 · 设备缺口"]
    RESOLVE --> CONFLICT["CONFLICTING_PORT<br/>端口已被占用"]
    RESOLVE --> UNKNOWN["UNKNOWN<br/>能力或端口清单不可用"]
    READY --> PREFLIGHT["目标环境预检<br/>版本 · 权限 · 资源 · 入口"]
    PREFLIGHT --> TRY["可尝试部署<br/>不是部署回执"]
    PREFLIGHT --> BLOCK["阻断或人工复核<br/>保留证据"]
    SECRET["variables<br/>Secret 由 Brick 定义"] -.导出时脱敏边界.-> BUNDLE["Import/Export<br/>共享包"]
    DATA["data/<br/>持久化数据"] -.分享前清理.-> BUNDLE
    CACHE[".cache/<br/>易失运行数据"] -.停止后可清理.-> BUNDLE

    classDef declaration fill:#e8f1ff,stroke:#2563eb,color:#0f172a
    classDef decision fill:#dcfce7,stroke:#16a34a,color:#0f172a
    classDef blocked fill:#fee2e2,stroke:#dc2626,color:#0f172a
    classDef boundary fill:#fef3c7,stroke:#d97706,color:#0f172a
    class APP,CONTRACT,REPAIR declaration
    class RESOLVE,READY,PREFLIGHT,TRY decision
    class MISSING,CONFLICT,UNKNOWN,BLOCK blocked
    class SECRET,DATA,CACHE,BUNDLE boundary
~~~

图示是本书原创的概念图，不是 Arduino 官方 UI 截图、部署协议或设备连线图。图示中的 `READY` 只表示“声明和输入快照相容”；它没有进入真实 App Lab，也没有产生 App CLI 的部署回执。

## 5. 实验一：检查 App Descriptor 的声明契约

- 用途：在不接触目标设备的情况下，检查端口、Brick 条目、变量值和设备引用的形状。
- 运行环境：Python 3.10 或更高版本；Windows、Linux 或 macOS；标准库即可。
- 文件位置：`code/第5篇_AppLab/第3章_AppLab启动配置与Brick依赖/deployment_contract.py`。
- 依赖：无第三方包；输入是已经解析成 Python 映射的 `app.yaml` 示例。
- 操作步骤：在仓库根目录运行 `python -B "code/第5篇_AppLab/第3章_AppLab启动配置与Brick依赖/deployment_contract.py"`。
- 预期输出：先得到一个合法清单，再得到端口类型和变量值类型错误；输出中的 `SIMULATED` 表示本地模拟。
- 故障排查：若出现 `ModuleNotFoundError`，确认从仓库根目录运行；若输出改变，先检查代码文件与正文代码块是否同步。
- 验证方式：运行对应的 `test_deployment_contract.py`，确认 5 项契约测试全部通过；再人工核对 `ContractReport` 中的 `ports`、`brick_ids` 和 `issues`。

~~~python
"""Validate the declarative part of an Arduino App manifest offline."""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass


@dataclass(frozen=True)
class ContractIssue:
    """One deterministic issue found in an App descriptor."""

    code: str
    path: str
    message: str


@dataclass(frozen=True)
class ContractReport:
    """Normalized result of validating a manifest-shaped mapping."""

    valid: bool
    issues: tuple[ContractIssue, ...]
    ports: tuple[int, ...]
    brick_ids: tuple[str, ...]


def _issue(issues: list[ContractIssue], code: str, path: str, message: str) -> None:
    issues.append(ContractIssue(code, path, message))


def _validate_ports(value: object, issues: list[ContractIssue]) -> tuple[int, ...]:
    if value is None:
        return ()
    if not isinstance(value, list):
        _issue(issues, "PORTS_NOT_LIST", "ports", "ports must be a list")
        return ()

    ports: list[int] = []
    seen: set[int] = set()
    for index, port in enumerate(value):
        path = f"ports[{index}]"
        if isinstance(port, bool) or not isinstance(port, int) or not 1 <= port <= 65535:
            _issue(
                issues,
                "PORT_INVALID",
                path,
                "port must be an integer between 1 and 65535",
            )
            continue
        if port in seen:
            _issue(issues, "PORT_DUPLICATE", path, "port must not be repeated")
            continue
        seen.add(port)
        ports.append(port)
    return tuple(ports)


def _validate_brick(
    value: object,
    index: int,
    issues: list[ContractIssue],
) -> str | None:
    path = f"bricks[{index}]"
    if isinstance(value, str):
        if value.strip():
            return value
        _issue(issues, "BRICK_ID_INVALID", path, "Brick id must not be empty")
        return None

    if not isinstance(value, Mapping):
        _issue(
            issues,
            "BRICK_ENTRY_INVALID",
            path,
            "Brick entry must be an id string or a one-key mapping",
        )
        return None
    if len(value) != 1:
        _issue(
            issues,
            "BRICK_ENTRY_SHAPE",
            path,
            "configured Brick entry must contain exactly one id",
        )
        return None

    brick_id, options = next(iter(value.items()))
    if not isinstance(brick_id, str) or not brick_id.strip():
        _issue(issues, "BRICK_ID_INVALID", path, "Brick id must be a non-empty string")
        return None
    if not isinstance(options, Mapping):
        _issue(
            issues,
            "BRICK_CONFIG_INVALID",
            f"{path}.{brick_id}",
            "Brick options must be a mapping",
        )
        return brick_id

    allowed = {"model", "variables", "devices"}
    for option in options:
        if option not in allowed:
            _issue(
                issues,
                "BRICK_OPTION_UNKNOWN",
                f"{path}.{brick_id}.{option}",
                "unsupported local Brick option",
            )

    model = options.get("model")
    if model is not None and (not isinstance(model, str) or not model.strip()):
        _issue(
            issues,
            "MODEL_INVALID",
            f"{path}.{brick_id}.model",
            "model must be a non-empty string",
        )

    variables = options.get("variables")
    if variables is not None:
        if not isinstance(variables, Mapping):
            _issue(
                issues,
                "VARIABLES_NOT_MAPPING",
                f"{path}.{brick_id}.variables",
                "variables must be a mapping",
            )
        else:
            for key, variable in variables.items():
                variable_path = f"{path}.{brick_id}.variables.{key}"
                if not isinstance(key, str) or not key.strip():
                    _issue(
                        issues,
                        "VARIABLE_KEY_INVALID",
                        variable_path,
                        "variable keys must be non-empty strings",
                    )
                if not isinstance(variable, str):
                    _issue(
                        issues,
                        "VARIABLE_VALUE_INVALID",
                        variable_path,
                        "variable values must be strings",
                    )

    devices = options.get("devices")
    if devices is not None:
        if not isinstance(devices, list):
            _issue(
                issues,
                "DEVICES_NOT_LIST",
                f"{path}.{brick_id}.devices",
                "devices must be a list",
            )
        else:
            for device_index, device in enumerate(devices):
                if not isinstance(device, str) or not device.strip():
                    _issue(
                        issues,
                        "DEVICE_INVALID",
                        f"{path}.{brick_id}.devices[{device_index}]",
                        "device references must be non-empty strings",
                    )
    return brick_id


def _validate_bricks(value: object, issues: list[ContractIssue]) -> tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, list):
        _issue(issues, "BRICKS_NOT_LIST", "bricks", "bricks must be a list")
        return ()

    brick_ids: list[str] = []
    for index, brick in enumerate(value):
        brick_id = _validate_brick(brick, index, issues)
        if brick_id is not None:
            brick_ids.append(brick_id)
    return tuple(brick_ids)


def validate_manifest(manifest: Mapping[str, object]) -> ContractReport:
    """Validate ``app.yaml`` fields represented as a Python mapping.

    This function intentionally validates types and local shape only. It does not
    resolve a Brick, inspect a target board, or infer whether a variable is a
    secret; secret classification belongs to the Brick definition and runtime.
    """
    issues: list[ContractIssue] = []
    if not isinstance(manifest, Mapping):
        _issue(issues, "MANIFEST_NOT_MAPPING", "", "manifest must be a mapping")
        return ContractReport(False, tuple(issues), (), ())

    if "name" in manifest and not isinstance(manifest["name"], str):
        _issue(issues, "NAME_INVALID", "name", "name must be a string when present")

    ports = _validate_ports(manifest.get("ports"), issues)
    brick_ids = _validate_bricks(manifest.get("bricks"), issues)
    return ContractReport(not issues, tuple(issues), ports, brick_ids)


def _demonstrate() -> None:
    valid = validate_manifest(
        {
            "name": "Smart Garden",
            "ports": [5000],
            "bricks": [
                {"arduino:dbstorage": {"variables": {"DB_PASSWORD": "${DB_PASSWORD}"}}},
                {"arduino:objectdetection": {"model": "yolo-v8", "devices": ["remote_camera_0"]}},
            ],
        }
    )
    print(
        f"SIMULATED manifest={'VALID' if valid.valid else 'INVALID'} "
        f"ports={','.join(str(port) for port in valid.ports)} "
        f"bricks={','.join(valid.brick_ids)}"
    )

    invalid = validate_manifest({"ports": [0]})
    issue = invalid.issues[0]
    print(f"SIMULATED invalid={issue.code}:{issue.path}")

    typed = validate_manifest(
        {"bricks": [{"arduino:camera": {"variables": {"MODE": 1}}}]}
    )
    issue = typed.issues[0]
    print(f"SIMULATED invalid_type={issue.code}:{issue.path}")


if __name__ == "__main__":
    _demonstrate()
~~~

~~~text
SIMULATED manifest=VALID ports=5000 bricks=arduino:dbstorage,arduino:objectdetection
SIMULATED invalid=PORT_INVALID:ports[0]
SIMULATED invalid_type=VARIABLE_VALUE_INVALID:bricks[0].arduino:camera.variables.MODE
~~~

运行结果的三行分别表示：完整示例通过、端口值超出范围、变量值不是字符串。它们只说明检查器的分支被执行，不说明这些 Brick 在任何目标设备上可用。

## 6. 实验二：解析 Brick 能力快照与端口占用

- 用途：把规范化的 Brick 需求与调用者提供的能力快照相匹配，明确缺少 Brick、模型、设备、端口或清单的情况。
- 运行环境：Python 3.10 或更高版本；标准库；不需要 UNO Q、网络或 App Lab。
- 文件位置：`code/第5篇_AppLab/第3章_AppLab启动配置与Brick依赖/dependency_resolution.py`。
- 依赖：无第三方包；`BrickCapability` 和端口占用表都是模拟输入。
- 操作步骤：在仓库根目录运行 `python -B "code/第5篇_AppLab/第3章_AppLab启动配置与Brick依赖/dependency_resolution.py"`。
- 预期输出：依次观察 `READY`、`MISSING_MODEL`、`CONFLICTING_PORT` 和 `UNKNOWN`。
- 故障排查：`UNKNOWN` 不是测试失败，而是调用者传入了 `None`，表示没有取得相应清单；空字典则表示清单已取得但没有匹配能力。
- 验证方式：运行对应的 `test_dependency_resolution.py`，确认 6 项测试通过，并核对 `missing`、`conflicts` 与 `reason` 是否保留修复所需信息。

~~~python
"""Resolve App Brick and port requirements against a supplied local snapshot."""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass


@dataclass(frozen=True)
class BrickRequirement:
    """One normalized requirement declared by an App."""

    brick_id: str
    model: str | None = None
    devices: tuple[str, ...] = ()


@dataclass(frozen=True)
class BrickCapability:
    """A local, externally supplied capability snapshot for one Brick."""

    brick_id: str
    models: tuple[str, ...] = ()
    devices: tuple[str, ...] = ()


@dataclass(frozen=True)
class DeployabilityDecision:
    """Offline deployability result; it is not a device deployment receipt."""

    action: str
    reason: str
    missing: tuple[str, ...] = ()
    conflicts: tuple[int, ...] = ()


def _unknown(capabilities: object, occupied_ports: object) -> DeployabilityDecision:
    missing_sources: list[str] = []
    if capabilities is None:
        missing_sources.append("Brick inventory is unavailable")
    if occupied_ports is None:
        missing_sources.append("port inventory is unavailable")
    return DeployabilityDecision("UNKNOWN", "; ".join(missing_sources))


def resolve_deployability(
    requirements: tuple[BrickRequirement, ...],
    capabilities: Mapping[str, BrickCapability] | None,
    requested_ports: tuple[int, ...],
    occupied_ports: Mapping[int, str] | None,
) -> DeployabilityDecision:
    """Compare declared requirements with a caller-provided local snapshot.

    ``None`` deliberately means that the relevant inventory is unknown. An empty
    mapping means the inventory was observed and contains no matching item.
    """
    if capabilities is None or occupied_ports is None:
        return _unknown(capabilities, occupied_ports)

    missing_bricks: list[str] = []
    missing_models: list[str] = []
    missing_devices: list[str] = []
    for requirement in requirements:
        capability = capabilities.get(requirement.brick_id)
        if capability is None:
            missing_bricks.append(requirement.brick_id)
            continue
        if requirement.model and requirement.model not in capability.models:
            missing_models.append(f"{requirement.brick_id}:model:{requirement.model}")
        for device in requirement.devices:
            if device not in capability.devices:
                missing_devices.append(f"{requirement.brick_id}:device:{device}")

    conflicts = tuple(sorted({port for port in requested_ports if port in occupied_ports}))
    missing = tuple(missing_bricks + missing_models + missing_devices)
    if missing_bricks:
        action = "MISSING_BRICK"
        reason = "one or more declared Bricks are absent from the snapshot"
    elif missing_models:
        action = "MISSING_MODEL"
        reason = "one or more requested models are absent from the Brick snapshot"
    elif missing_devices:
        action = "MISSING_DEVICE"
        reason = "one or more requested devices are absent from the Brick snapshot"
    elif conflicts:
        action = "CONFLICTING_PORT"
        reason = "one or more requested ports are occupied"
    elif missing or conflicts:
        action = "NOT_READY"
        reason = "the supplied snapshot does not satisfy all requirements"
    else:
        action = "READY"
        reason = "all declared Bricks, models, devices and ports are available"
    return DeployabilityDecision(action, reason, missing, conflicts)


def _demonstrate() -> None:
    requirements = (
        BrickRequirement("arduino:objectdetection", "yolo-v8", ("remote_camera_0",)),
    )
    capabilities = {
        "arduino:objectdetection": BrickCapability(
            "arduino:objectdetection", ("yolo-v8",), ("remote_camera_0",)
        )
    }
    ready = resolve_deployability(requirements, capabilities, (5000,), {})
    print(f"SIMULATED deploy={ready.action} missing=none conflicts=none")

    missing_model = resolve_deployability(
        requirements,
        {
            "arduino:objectdetection": BrickCapability(
                "arduino:objectdetection", ("yolo-v7",), ("remote_camera_0",)
            )
        },
        (),
        {},
    )
    print(
        f"SIMULATED deploy={missing_model.action} "
        f"missing={','.join(missing_model.missing)}"
    )

    conflict = resolve_deployability(requirements, capabilities, (5000,), {5000: "web"})
    print(f"SIMULATED deploy={conflict.action} conflicts={','.join(map(str, conflict.conflicts))}")

    unknown = resolve_deployability(requirements, None, (5000,), None)
    print(f"SIMULATED deploy={unknown.action} reason={unknown.reason}")


if __name__ == "__main__":
    _demonstrate()
~~~

~~~text
SIMULATED deploy=READY missing=none conflicts=none
SIMULATED deploy=MISSING_MODEL missing=arduino:objectdetection:model:yolo-v8
SIMULATED deploy=CONFLICTING_PORT conflicts=5000
SIMULATED deploy=UNKNOWN reason=Brick inventory is unavailable; port inventory is unavailable
~~~

这里的 `BrickCapability` 不是从 UNO Q 自动读取的对象，而是测试用的能力快照。真实适配层应该负责采集目标侧信息并给它加上版本、时间、入口和权限证据；解析器只负责确定性比较。

## 7. `data/`、`.cache/` 和敏感变量的发布边界

### 7.1 持久化与易失数据不能混装

官方规范将 `data/` 作为 App 的持久化数据目录，内容可以被用户备份或删除；分享 App 前应清空它，避免个人数据泄露。`.cache/` 用于运行所需的易失数据，例如 Python 虚拟环境或 Docker Compose 支持文件，在 App 未运行时可以安全删除。[Arduino App specification](https://github.com/arduino/arduino-app-cli/blob/main/docs/app-specification.md)

因此，一个发布前预检至少要问三遍：

| 目录/字段 | 允许存在什么 | 分享前动作 | 证据边界 |
| --- | --- | --- | --- |
| `data/` | 用户状态、数据库或持久化结果 | 备份后清理或按策略保留 | 不能把样例数据当成现场数据 |
| `.cache/` | 虚拟环境、缓存和易失运行文件 | App 停止后清理 | 不能把缓存存在当成 Brick 可用 |
| `variables` | Brick 配置参数 | 不写入真实密钥到仓库 | 是否为 Secret 由 Brick 定义决定 |

### 7.2 Secret 不是“看起来像密码”

本地检查器没有把包含 `PASSWORD`、`TOKEN` 或 `KEY` 的字符串自动判成 Secret。这是有意为之：是否敏感由 Brick 定义决定，字符串外观不能替代规范和运行时元数据。仓库示例使用 `${DB_PASSWORD}` 这样的占位符，是为了避免把真实凭据带入代码、日志或测试；它不是自动脱敏机制。

分享或导出时，应同时检查：

1. `data/` 中没有个人数据、现场数据或令牌；
2. `.cache/` 没有不应分发的本地运行产物；
3. `variables` 没有真实密钥；
4. 对于被 Brick 定义为 Secret 的变量，确认导出流程确实产生了脱敏结果；
5. 记录导出入口、时间、App/CLI 版本和包校验值。

这五项属于发布卫生，不由本章两个 Python 函数自动完成。函数只负责在进入目标环境前减少明显的声明错误。

## 8. 可部署性检查单

可以把本章的方法压缩成一份运行前检查单：

1. **项目入口**：根目录名称和位置满足 App 规范；`app.yaml`、`python/main.py` 存在；若有 `sketch/`，两个 Sketch 文件齐全。
2. **声明形状**：端口是唯一的合法整数；Brick 条目是可解释的 ID 或单键配置映射；变量和设备引用类型正确。
3. **需求规范化**：将每个 Brick 的 ID、模型和设备引用转换成不可变需求对象。
4. **快照采集**：记录能力快照的来源、时间、版本和权限；拿不到清单时保留 `UNKNOWN`。
5. **能力解析**：先确认 Brick，再确认模型和设备，最后检查端口冲突；保留完整缺口列表。
6. **数据卫生**：清理或备份 `data/`；停止 App 后再处理 `.cache/`；不把真实凭据放入仓库和演示输出。
7. **目标预检**：补充 App Lab/CLI 版本、Linux 权限、空间、网络、Router/Bridge、MCU 和物理设备的现场证据。
8. **执行与验收**：只有获得目标侧导入/启动/部署回执，才可以创建新的 `run_id` 并进入[第 2 章的生命周期](./第2章_AppLab运行生命周期_导入启动运行与停止.md)。

其中第 1～6 项可以做成 CI 或本地脚本；第 7～8 项必须由真实入口和设备证据补齐。自动化检查应当阻止明显错误，但不能为了输出绿色结果而替现场完成缺失的观察。

## 9. 验证矩阵、练习与交接

### 9.1 本章验证矩阵

| 验证项 | 本地状态 | 证明什么 | 不证明什么 |
| --- | --- | --- | --- |
| `test_deployment_contract.py` | 5 项通过 | 声明契约分支稳定 | YAML 解析器或目标 App Lab 行为 |
| `test_dependency_resolution.py` | 6 项通过 | 快照比较和 `UNKNOWN` 语义稳定 | Brick 已安装、模型可加载 |
| 两个演示脚本 | 输出固定 | 示例路径可复现 | UNO Q 实机运行 |
| Fig-30 Mermaid/SVG | 源码与产物一致 | 图示可解析、可读 | 部署协议或硬件连接 |
| 目标预检 | 尚未执行 | — | Linux、MCU、Router/Bridge、App Lab 或实机验收 |

### 9.2 练习

1. 把一个 Brick 的 `devices` 从 `remote_camera_0` 改成两个设备，设计一条测试证明缺口列表会保留两个设备，而不是只返回第一个。
2. 让能力快照缺少端口信息但包含 Brick 信息，扩展解析器区分 `UNKNOWN` 的来源。
3. 为 `data/` 和 `.cache/` 写一个发布前扫描器，要求它只输出文件名、大小和分类，不打印文件内容。
4. 将 `ContractReport` 与[第四篇第4章的结果账本](../第4篇_PythonBridge/第4章_Python_Bridge结果账本与状态查询_从返回值到可验证证据.md)对接，设计一个不会把预检结果误写成设备执行结果的状态映射。

### 9.3 交接记录

本章完成后，下一位实现者应接收以下信息：

- 本地声明检查器和能力解析器均为标准库示例；
- 测试只使用人工构造的映射、能力快照和端口表；
- `READY` 的有效期受快照时间限制；
- `UNKNOWN` 需要查询或人工复核，不能自动改写为失败、重试或成功；
- 真实 App Lab/CLI、Linux、MCU、Brick、Router/Bridge 和 UNO Q 证据仍待补齐。

## 10. 常见问题

### Q1：`VALID` 了，为什么还不能直接 Run？

`VALID` 只说明声明可以被本地模型解释。目标板上可能缺少 Brick、模型、设备或空闲端口，所以还要取得能力快照并通过预检。

### Q2：能力快照是空字典时，为什么不是 `UNKNOWN`？

空字典表示“已经取得清单，但没有匹配项”，属于可修复的缺失；`None` 表示“没有取得清单”，无法区分不存在和未查询，因此必须是 `UNKNOWN`。

### Q3：没有写 `model`，检查器为什么不自动选择默认模型？

默认模型可能来自 Brick 版本、目标镜像或用户配置。自动选择会把猜测变成部署证据；本章只检查已声明的约束。

### Q4：变量值是字符串，是否就安全？

不是。字符串类型只满足声明契约。是否为 Secret、是否应脱敏、是否能访问外部服务，仍由 Brick 定义、导出流程和目标环境权限决定。

### Q5：为什么图中 `READY` 后面还要有预检？

因为能力快照只能说明某一时刻的匹配关系。版本、权限、磁盘、网络、入口和实际设备状态仍需要在目标环境中核验。

## 11. 本章小结与下一步

本章把 App Lab 启动前的问题分为三层：声明契约、能力快照解析和目标环境预检。`deployment_contract.py` 负责发现字段和类型错误；`dependency_resolution.py` 负责将已规范化的 Brick 需求与外部提供的能力快照比较；两者都不启动 App，也不伪造设备侧回执。

最重要的工程习惯是保留证据来源：声明来自项目文件，能力来自带时间边界的快照，部署来自目标侧回执，物理效果来自设备观察。只有把这四类来源分开，后续的运行生命周期、日志、故障恢复和发布回滚才有可追溯的起点。

下一章将从“已经通过启动前预检”的项目继续，讨论 App Lab 中的配置复用、运行参数和多环境差异，重点处理开发机、测试板和现场板之间的配置分层。

## 延伸阅读

- [第五篇第1章：App Lab 开发基础](./第1章_App_Lab开发基础_应用结构与验证边界.md)
- [第五篇第2章：App Lab 运行生命周期](./第2章_AppLab运行生命周期_导入启动运行与停止.md)
- [Arduino App specification](https://github.com/arduino/arduino-app-cli/blob/main/docs/app-specification.md)
- [Arduino App CLI user documentation](https://github.com/arduino/arduino-app-cli/blob/main/docs/user-documentation.md)
- [Arduino App Lab examples](https://docs.arduino.cc/software/app-lab/tutorials/examples/)
- [Arduino UNO Q datasheet](https://docs.arduino.cc/resources/datasheets/ABX00162-datasheet.pdf)
