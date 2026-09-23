---
title: App Lab 配置分层与多环境运行参数：从开发机到现场板
part: 5
chapter: 4
status: draft
last_verified: 2026-09-23
updated: 2026-09-23
prerequisites: 第五篇第1～3章、第三篇第8章、第四篇第1～4章
tags: App Lab, 配置分层, 多环境, 运行参数, Secret, run_id, 指纹
---

# 第4章 App Lab 配置分层与多环境运行参数：从开发机到现场板

## 学习目标

读完本章后，读者应能够：

1. 区分 App 固定声明、基础默认值、环境配置、运行参数和 Secret。
2. 设计 `base < environment < runtime` 的确定性覆盖顺序，并锁定目标板等关键身份字段。
3. 识别未知键、类型错误、缺少必填项、未知环境和非法覆盖，而不是把它们静默吞掉。
4. 为一次 `run_id` 生成不包含敏感值的运行配置快照，并用指纹关联后续日志和结果账本。
5. 解释为什么 `data/`、`.cache/`、环境变量和运行参数不能互相替代。
6. 在没有 UNO Q、App Lab 或真实 CLI 的条件下，完成本地配置合并和脱敏验证，同时保留实机验证边界。

## 背景与边界

上一章解决了“声明是否能被解释、依赖是否与能力快照匹配”的问题。本章继续向运行阶段靠近，处理一个很容易被低估的问题：**同一个 App 在开发机、测试板和现场板上，哪些值可以变化，哪些值必须保持身份稳定？**

Arduino App 规范把 `app.yaml` 定义为 App 的描述文件，并规定 App 根目录、Python 入口、可选 Sketch、Brick、端口以及 `data/`、`.cache/` 等边界。[Arduino App specification](https://github.com/arduino/arduino-app-cli/blob/main/docs/app-specification.md) 这些字段描述的是项目和运行组件，不等于一套完整的多环境配置管理系统。因此，本章提出的“配置分层、锁定键和运行快照”是本书的工程治理模型，不能写成 App Lab 当前版本必然提供的内置覆盖机制。

本章只验证本地数据结构和合并策略。它不会：

- 修改 `app.yaml` 或真实 App Lab 项目；
- 读取操作系统环境变量、Secret 管理器、UNO Q 文件系统或目标 Linux 镜像；
- 调用 App CLI、启动 Python/Sketch/Brick、创建容器或连接 Router/Bridge；
- 把脱敏快照指纹当作 Secret 正确性的证明；
- 把本地合并结果当作开发机、测试板或现场板已经部署成功。

本章与[第五篇第3章](./第3章_AppLab启动配置与Brick依赖_从声明到可部署性检查.md)的关系是：第 3 章判断“声明和能力快照是否匹配”，本章判断“匹配之后，运行所使用的配置是否可追溯”。与[第五篇第2章](./第2章_AppLab运行生命周期_导入启动运行与停止.md)的关系是：第 2 章用 `run_id` 区分运行会话，本章为该会话补上 `environment`、配置来源和脱敏指纹。

## 1. 配置不是一个文件

### 1.1 五种来源，五种责任

把所有值塞进一个 YAML、JSON 或 Python 文件，会让“项目声明”和“现场变量”互相污染。更稳妥的做法是先按责任拆开：

| 来源 | 典型内容 | 是否进入仓库 | 是否允许被覆盖 |
| --- | --- | --- | --- |
| App 声明 | `name`、`ports`、`bricks`、入口结构 | 通常是 | 只通过代码审查或版本变更 |
| 基础层 | 日志格式、默认超时、功能开关默认值 | 可以 | 可由环境层覆盖 |
| 环境层 | 测试板地址、测试端口、环境模式 | 视敏感性决定 | 可由运行层有限覆盖 |
| 运行层 | 本次实验的安全开关、采样次数、Dry-run | 通常不持久化 | 只允许安全字段 |
| Secret 来源 | API 密钥、数据库密码、私有令牌 | 不应进入仓库 | 由运行时注入或专门系统提供 |

这里的“基础层、环境层、运行层”是推荐的输入分层，不是对 Arduino App Lab UI 的功能承诺。实际工程可以把它们映射为不同配置文件、命令行参数、受控环境变量或部署系统字段，但映射完成后必须保留来源。

### 1.2 配置值和目标身份不是同一类东西

`LOG_LEVEL=debug` 在测试环境中被覆盖通常是合理的；`TARGET_BOARD=test-q` 被运行参数改成 `现场-q` 则可能意味着把测试配置误发到现场设备。配置治理不能只关心“最后得到什么值”，还要关心“谁在什么层覆盖了什么值”。

因此，本章把目标板、App 身份和协议版本视为**锁定键**。普通运行层可以调整日志级别或采样次数，但不能改变已批准的目标身份。若确实需要换板，应创建新的环境配置或新的发布对象，而不是在一次运行命令中偷偷覆盖。

## 2. 三层配置与覆盖顺序

### 2.1 确定性优先级

本章采用单向覆盖顺序：

```text
base < environment < runtime
```

越靠右的层优先级越高，但优先级不等于无限权限。合并器同时执行三类规则：

1. 键必须在 schema 中声明；
2. 值必须符合该键的类型；
3. 锁定键不能被后层用不同值覆盖。

如果没有这些规则，配置系统会把拼写错误变成“新增配置”，把数字字符串和整数混在一起，把现场板身份藏在一条临时命令中，最后只能从运行日志里猜原因。

### 2.2 Schema 是边界，不是默认值仓库

schema 只描述“允许哪些键、每个键的类型是什么”。它不应该偷偷填充缺失值，也不应该从环境名称推断目标板。默认值可以在 `base` 层明确写出，必填项则在合并结束后检查。

示意 schema：

```text
APP_MODE: str       required
LOG_LEVEL: str      default=info
TARGET_BOARD: str   locked
PORT: int            environment-specific
```

当 `APP_MODE` 缺失时，结果是 `MISSING_REQUIRED`；当出现 `LOG_LEVLE` 时，结果是 `UNKNOWN_KEY`；当 `PORT` 传入 `"8080"` 而 schema 要求整数时，结果是 `TYPE_MISMATCH`。这三种问题需要不同的修复路径，不能都显示为“配置无效”。

### 2.3 覆盖记录比最终字典更重要

最终字典适合给程序使用，但排障需要来源信息：

| 最终键 | 最终值 | 最终来源 | 是否发生覆盖 |
| --- | --- | --- | --- |
| `APP_MODE` | `staging` | `environment` | 是 |
| `LOG_LEVEL` | `trace` | `runtime` | 是 |
| `TARGET_BOARD` | `test-q` | `base` | 否 |

本章的 `ConfigResolution` 同时保留 `values`、`sources` 和 `overridden_keys`。它没有写入时间戳，因为时间属于运行证据而不是纯合并函数；调用方可以在生成 `run_config_snapshot` 时绑定 `run_id` 和采集时间。

## 3. 运行参数与身份锁定

### 3.1 允许覆盖和禁止覆盖

可以把键分为两组：

| 类型 | 示例 | 运行层策略 |
| --- | --- | --- |
| 安全运行参数 | `LOG_LEVEL`、`DRY_RUN`、`SAMPLE_LIMIT` | 允许覆盖，但仍需类型校验 |
| 身份/边界参数 | `APP_ID`、`TARGET_BOARD`、协议版本、数据目录 | 锁定或要求新环境配置 |

锁定不是为了让系统僵化，而是为了把高风险变化提升到可审查的位置。运行层如果需要修改 `TARGET_BOARD`，应先生成新的环境层快照并重新走第 3 章的能力预检。

### 3.2 多环境不等于复制三份项目

开发机、测试板和现场板可以共享同一份 App 代码与声明，但它们不应共享未经区分的运行状态。推荐至少记录：

- `environment`：`development`、`staging` 或 `production`；
- `TARGET_BOARD`：目标设备的稳定身份；
- `config_fingerprint`：脱敏配置快照的指纹；
- `run_id`：本次运行会话标识；
- `source_versions`：代码、App/CLI 和 Brick 能力快照版本。

如果现场问题只能通过“把测试板的配置复制过来”解决，说明环境边界尚未被建模。配置分层的目标不是减少文件数量，而是减少不可解释的差异。

## 4. Fig-31：从分层配置到运行快照

<a id="fig-31-uno-q-app-lab-config-layering"></a>

图 5-4 将配置输入、合并策略和运行生命周期连接起来。注意两条边界：Secret 只在运行时注入，快照只保存脱敏值；`.cache/` 是易失运行数据，不应偷偷成为配置源。

~~~mermaid
flowchart LR
    MANIFEST["项目声明<br/>app.yaml · 代码入口"] --> BASE["基础层<br/>稳定默认值"]
    BASE --> ENV["环境层 / environment<br/>development · staging · production"]
    ENV --> RUNTIME["运行层 / runtime<br/>本次安全参数"]
    RUNTIME --> MERGE["类型校验与合并<br/>来源 · 覆盖 · 锁定键"]
    MERGE --> SNAPSHOT["run_config_snapshot<br/>run_id · 环境 · 脱敏值 · 指纹"]
    SNAPSHOT --> LIFE["第2章生命周期<br/>导入 · 准备 · 启动"]
    SNAPSHOT --> EVIDENCE["证据与结果账本<br/>可复核配置身份"]
    SECRET["Secret 提供方<br/>不进入仓库与日志"] -.运行时注入.-> MERGE
    LOCK["目标身份锁定<br/>TARGET_BOARD · APP_ID"] -.禁止覆盖.-> MERGE
    DATA["data/<br/>持久化状态"] -.环境隔离.-> ENV
    CACHE[".cache/<br/>易失运行数据"] -.不作为配置源.-> RUNTIME

    classDef source fill:#e8f1ff,stroke:#2563eb,color:#0f172a
    classDef control fill:#dcfce7,stroke:#16a34a,color:#0f172a
    classDef evidence fill:#fef3c7,stroke:#d97706,color:#0f172a
    classDef risk fill:#fee2e2,stroke:#dc2626,color:#0f172a
    class MANIFEST,BASE,ENV,RUNTIME source
    class MERGE,SNAPSHOT,LIFE control
    class EVIDENCE,DATA,CACHE evidence
    class SECRET,LOCK risk
~~~

这是一张原创概念图，不是 App Lab UI、Arduino Router 协议或 UNO Q 部署拓扑。它表达的是本书的证据顺序：先合并并校验，再创建快照，最后把快照身份交给运行生命周期和结果账本。

## 5. 实验一：合并配置层并保留来源

- 用途：验证基础层、环境层和运行层的覆盖顺序，并阻止未知键、类型错误和锁定键覆盖。
- 运行环境：Python 3.10 或更高版本；Windows、Linux 或 macOS；标准库即可。
- 文件位置：`code/第5篇_AppLab/第4章_AppLab配置分层与多环境运行参数/config_layers.py`。
- 依赖：无第三方包；输入是人工构造的 schema 和配置映射。
- 操作步骤：在仓库根目录运行 `python -B "code/第5篇_AppLab/第4章_AppLab配置分层与多环境运行参数/config_layers.py"`。
- 预期输出：观察有效合并、覆盖键、未知键和锁定键错误四类结果。
- 故障排查：若 `TARGET_BOARD` 被改写，确认它是否加入 `locked_keys`；若 `LOG_LEVEL` 没有覆盖，检查层顺序是否仍为 base、environment、runtime。
- 验证方式：运行 `test_config_layers.py`，确认 5 项测试通过，并核对 `sources` 是否指向最终生效的层。

~~~python
"""Resolve layered application configuration without contacting a device."""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass


class ConfigError(ValueError):
    """Raised for invalid configuration inputs that cannot be resolved."""


@dataclass(frozen=True)
class ConfigIssue:
    """One deterministic configuration problem."""

    code: str
    path: str
    message: str


@dataclass(frozen=True)
class ConfigResolution:
    """Immutable result of applying layers from left to right."""

    environment: str
    values: tuple[tuple[str, object], ...]
    sources: tuple[tuple[str, str], ...]
    overridden_keys: tuple[str, ...]
    issues: tuple[ConfigIssue, ...]

    @property
    def valid(self) -> bool:
        return not self.issues

    def as_dict(self) -> dict[str, object]:
        """Return a copy suitable for passing to the next local stage."""
        return dict(self.values)


def _issue(issues: list[ConfigIssue], code: str, path: str, message: str) -> None:
    issues.append(ConfigIssue(code, path, message))


def _matches(value: object, expected: type | tuple[type, ...]) -> bool:
    if isinstance(expected, tuple):
        return any(type(value) is candidate for candidate in expected)
    return type(value) is expected


def merge_layers(
    environment: str,
    layers: tuple[tuple[str, Mapping[str, object]], ...],
    *,
    schema: Mapping[str, type | tuple[type, ...]],
    required: tuple[str, ...] = (),
    allowed_environments: tuple[str, ...] = (),
    locked_keys: tuple[str, ...] = (),
) -> ConfigResolution:
    """Merge ``layers`` in order, retaining provenance and validation issues.

    The intended precedence is ``base < environment < runtime``. A later layer
    may override a known key unless that key is locked. This is a local policy
    model; it is not an assertion about App Lab's built-in configuration API.
    """
    issues: list[ConfigIssue] = []
    if not isinstance(environment, str) or not environment.strip():
        _issue(issues, "ENVIRONMENT_INVALID", "environment", "environment must not be empty")
        normalized_environment = ""
    else:
        normalized_environment = environment

    if allowed_environments and normalized_environment not in allowed_environments:
        _issue(
            issues,
            "UNKNOWN_ENVIRONMENT",
            "environment",
            "environment is not in the allowed set",
        )

    values: dict[str, object] = {}
    sources: dict[str, str] = {}
    overridden: list[str] = []
    locked = set(locked_keys)

    for layer_name, layer in layers:
        if not isinstance(layer_name, str) or not layer_name.strip():
            _issue(issues, "LAYER_NAME_INVALID", "layers", "layer name must be non-empty")
            continue
        if not isinstance(layer, Mapping):
            _issue(
                issues,
                "LAYER_NOT_MAPPING",
                layer_name,
                "configuration layer must be a mapping",
            )
            continue
        for key, value in layer.items():
            path = f"{layer_name}.{key}"
            if key not in schema:
                _issue(issues, "UNKNOWN_KEY", path, "key is not declared in the schema")
                continue
            if not _matches(value, schema[key]):
                _issue(issues, "TYPE_MISMATCH", path, "value does not match the schema type")
                continue
            if key in values and values[key] != value:
                if key in locked:
                    _issue(
                        issues,
                        "LOCKED_OVERRIDE",
                        path,
                        "a later layer cannot override this locked key",
                    )
                    continue
                if key not in overridden:
                    overridden.append(key)
            values[key] = value
            sources[key] = layer_name

    for key in required:
        if key not in values:
            _issue(issues, "MISSING_REQUIRED", key, "required key is missing after merge")

    return ConfigResolution(
        normalized_environment,
        tuple(sorted(values.items())),
        tuple(sorted(sources.items())),
        tuple(overridden),
        tuple(issues),
    )


def _format_values(values: Mapping[str, object]) -> str:
    return ",".join(f"{key}={values[key]}" for key in sorted(values))


def _demonstrate() -> None:
    schema = {"APP_MODE": str, "LOG_LEVEL": str, "TARGET_BOARD": str}
    resolved = merge_layers(
        "staging",
        (
            ("base", {"APP_MODE": "production", "LOG_LEVEL": "info", "TARGET_BOARD": "test-q"}),
            ("environment", {"APP_MODE": "staging", "LOG_LEVEL": "debug"}),
        ),
        schema=schema,
        required=("APP_MODE", "TARGET_BOARD"),
        allowed_environments=("development", "staging", "production"),
    )
    print(
        f"SIMULATED env={resolved.environment} valid={str(resolved.valid).lower()} "
        f"values={_format_values(resolved.as_dict())}"
    )
    print(f"SIMULATED overrides={','.join(resolved.overridden_keys)}")

    invalid = merge_layers("staging", (("environment", {"EXTRA": "value"}),), schema=schema)
    issue = invalid.issues[0]
    print(f"SIMULATED invalid={issue.code}:{issue.path}")

    locked = merge_layers(
        "staging",
        (("base", {"TARGET_BOARD": "test-q"}), ("runtime", {"TARGET_BOARD": "现场-q"})),
        schema=schema,
        locked_keys=("TARGET_BOARD",),
    )
    issue = locked.issues[0]
    print(f"SIMULATED locked={issue.code}:{issue.path}")


if __name__ == "__main__":
    _demonstrate()
~~~

~~~text
SIMULATED env=staging valid=true values=APP_MODE=staging,LOG_LEVEL=debug,TARGET_BOARD=test-q
SIMULATED overrides=APP_MODE,LOG_LEVEL
SIMULATED invalid=UNKNOWN_KEY:environment.EXTRA
SIMULATED locked=LOCKED_OVERRIDE:runtime.TARGET_BOARD
~~~

`ConfigResolution` 是本地策略结果。真实工程还需要把层文件的版本、提交哈希、采集时间和读取入口写入更大的证据包；本实验不读取这些外部元数据。

## 6. 实验二：生成脱敏运行配置快照

- 用途：为一个 `run_id` 固定本次运行的环境、脱敏配置值和确定性指纹。
- 运行环境：Python 3.10 或更高版本；标准库；不需要网络、App Lab 或 UNO Q。
- 文件位置：`code/第5篇_AppLab/第4章_AppLab配置分层与多环境运行参数/run_config_snapshot.py`。
- 依赖：无第三方包；只接受 JSON 标量值，不接受嵌套对象或数组。
- 操作步骤：在仓库根目录运行 `python -B "code/第5篇_AppLab/第4章_AppLab配置分层与多环境运行参数/run_config_snapshot.py"`。
- 预期输出：输出快照身份、脱敏键、脱敏 JSON 和指纹前 12 位；原始密码不会出现在输出中。
- 故障排查：若出现 `secret key is missing`，先确认 Secret 键已经由受控输入提供；若指纹不稳定，检查是否把未排序的字典直接序列化。
- 验证方式：运行 `test_run_config_snapshot.py`，确认 5 项测试通过，并检查相同输入顺序变化不会改变指纹。

~~~python
"""Build a deterministic, redacted snapshot for one App run."""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
import hashlib
import json


class SnapshotError(ValueError):
    """Raised when a run configuration cannot be safely snapshotted."""


JSON_SCALARS = (str, int, float, bool, type(None))


@dataclass(frozen=True)
class ConfigSnapshot:
    """Immutable public view of one run's redacted configuration."""

    run_id: str
    environment: str
    _redacted_values: tuple[tuple[str, object], ...]
    redacted_keys: tuple[str, ...]
    fingerprint: str

    @property
    def redacted_values(self) -> dict[str, object]:
        return dict(self._redacted_values)

    def to_dict(self) -> dict[str, object]:
        return {
            "environment": self.environment,
            "run_id": self.run_id,
            "values": self.redacted_values,
        }

    def to_json(self) -> str:
        return json.dumps(
            self.to_dict(), ensure_ascii=False, sort_keys=True, separators=(",", ":")
        )


def _canonical_json(environment: str, run_id: str, values: Mapping[str, object]) -> str:
    payload = {"environment": environment, "run_id": run_id, "values": dict(values)}
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def build_snapshot(
    run_id: str,
    environment: str,
    values: Mapping[str, object],
    secret_keys: tuple[str, ...] = (),
) -> ConfigSnapshot:
    """Return a stable snapshot whose public payload never contains secret values."""
    if not isinstance(run_id, str) or not run_id.strip():
        raise SnapshotError("run_id must not be empty")
    if not isinstance(environment, str) or not environment.strip():
        raise SnapshotError("environment must not be empty")
    if not isinstance(values, Mapping):
        raise SnapshotError("values must be a mapping")

    for key, value in values.items():
        if not isinstance(key, str) or not key.strip():
            raise SnapshotError("configuration keys must be non-empty strings")
        if not any(type(value) is scalar for scalar in JSON_SCALARS):
            raise SnapshotError(f"{key} must be a JSON scalar")

    normalized_secret_keys = tuple(sorted(secret_keys))
    for key in normalized_secret_keys:
        if key not in values:
            raise SnapshotError(f"secret key is missing: {key}")

    redacted = dict(values)
    for key in normalized_secret_keys:
        redacted[key] = "<redacted>"
    ordered = tuple(sorted(redacted.items()))
    canonical = _canonical_json(environment, run_id, dict(ordered))
    fingerprint = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return ConfigSnapshot(run_id, environment, ordered, normalized_secret_keys, fingerprint)


def _demonstrate() -> None:
    snapshot = build_snapshot(
        "run-042",
        "staging",
        {"APP_MODE": "staging", "DB_PASSWORD": "do-not-print", "LOG_LEVEL": "debug"},
        secret_keys=("DB_PASSWORD",),
    )
    print(
        f"SIMULATED snapshot={snapshot.run_id} env={snapshot.environment} "
        f"redacted={','.join(snapshot.redacted_keys)}"
    )
    print(f"SIMULATED payload={snapshot.to_json()}")
    print(f"SIMULATED fingerprint={snapshot.fingerprint[:12]}")


if __name__ == "__main__":
    _demonstrate()
~~~

~~~text
SIMULATED snapshot=run-042 env=staging redacted=DB_PASSWORD
SIMULATED payload={"environment":"staging","run_id":"run-042","values":{"APP_MODE":"staging","DB_PASSWORD":"<redacted>","LOG_LEVEL":"debug"}}
SIMULATED fingerprint=44da1cca1074
~~~

指纹针对脱敏后的规范化 JSON 计算，因此它能证明“这份公开快照的内容没有变化”，但不能证明 Secret 的实际值正确，也不能由指纹反推出 Secret。Secret 的可用性仍要在目标环境以最小权限和独立证据验证。

## 7. Secret、`data/` 与 `.cache/` 的边界

### 7.1 Secret 只在受控边界出现

上一章已经说明，Brick 是否把某个变量定义为 Secret，取决于 Brick 自身的定义；`app.yaml` 中仍以普通变量形式表达，导出时由系统依据 Secret 标记进行脱敏。[Arduino App specification](https://github.com/arduino/arduino-app-cli/blob/main/docs/app-specification.md) 本章进一步规定本地快照只能存放 `<redacted>`，不能把真实值放到测试输出、章节代码块、Git 提交或运行日志。

这并不意味着快照可以替代 Secret 管理。快照故意丢失了 Secret 的实际值，适合做配置身份和来源审计，不适合做凭据健康检查。凭据健康检查应该记录“目标环境已提供/未提供”和验证时间，不应记录凭据本身。

### 7.2 `data/` 是状态，不是配置层

官方规范把 `data/` 作为持久化应用数据目录，分享前应按策略备份或清理；`.cache/` 是易失运行数据，App 停止后可以清理。[Arduino App specification](https://github.com/arduino/arduino-app-cli/blob/main/docs/app-specification.md) 因此：

- 不从 `data/` 反向推断当前环境名称；
- 不把 `.cache/` 中生成的虚拟环境、临时文件或 Compose 文件当作配置来源；
- 若 `data/` 需要按环境隔离，应在环境设计中明确目录或实例边界，而不是依赖目录内容猜测；
- 快照只记录配置值和来源，不复制持久化数据或缓存内容。

### 7.3 目标环境参考也要留版本边界

App CLI 文档可帮助理解用户目录、运行时目录和环境变量的参考关系，但文档默认值不能直接替代目标镜像和当前版本的实测。[Arduino App CLI user documentation](https://github.com/arduino/arduino-app-cli/blob/main/docs/user-documentation.md) 在部署记录中应同时写入 App/CLI 版本、目标镜像标识、运行用户和入口方式。

## 8. 与 `run_id` 和生命周期的衔接

### 8.1 快照必须先于启动证据

推荐顺序如下：

1. 读取 App 声明和配置层；
2. 校验 schema、环境和锁定键；
3. 生成脱敏 `run_config_snapshot`；
4. 创建 `run_id`；
5. 把 `run_id`、环境名和配置指纹写入导入/准备证据；
6. 再进入[第五篇第2章的生命周期](./第2章_AppLab运行生命周期_导入启动运行与停止.md)。

如果启动以后才生成快照，启动失败时可能没有配置身份；如果每条日志都重新读取环境变量，单次运行中可能出现配置漂移。快照的作用是为一次运行建立“当时使用的公开配置视图”。

### 8.2 与结果账本的连接

在[第四篇第4章的结果账本](../第4篇_PythonBridge/第4章_Python_Bridge结果账本与状态查询_从返回值到可验证证据.md)中，结果对象需要有请求身份、状态和证据来源。本章可以为结果对象增加两个非敏感字段：

```text
environment: staging
config_fingerprint: 44da1cca1074...
```

这样排障时可以回答“同一个请求是否使用了同一份公开配置”，而不需要把密码或令牌复制到结果账本。若指纹不同，应先解释配置差异，再解释业务结果差异。

## 9. 多环境检查单与验证矩阵

### 9.1 运行前检查单

1. App 声明仍由版本控制和代码审查管理，未被运行层临时改写。
2. `base`、`environment`、`runtime` 层的顺序明确且固定。
3. schema 已声明键、类型和必填项；未知键不会静默加入。
4. `TARGET_BOARD`、`APP_ID` 和协议版本等身份字段已锁定。
5. 覆盖键、最终来源和环境名被记录。
6. Secret 不进入仓库、演示输出、快照 JSON 或普通日志。
7. `data/` 与 `.cache/` 没有被误当作配置源。
8. 脱敏快照在生命周期启动证据之前生成，并与 `run_id` 关联。
9. 目标环境实际版本、权限、空间、Brick、模型、设备和端口仍需独立预检。

### 9.2 本章验证矩阵

| 验证项 | 本地状态 | 证明什么 | 不证明什么 |
| --- | --- | --- | --- |
| `test_config_layers.py` | 5 项通过 | 覆盖顺序、来源和锁定规则稳定 | App Lab 内置配置能力 |
| `test_run_config_snapshot.py` | 5 项通过 | 脱敏、排序和指纹稳定 | Secret 实际可用 |
| 两个演示脚本 | 输出固定 | 示例可复现且不打印 Secret | 目标板环境一致 |
| Fig-31 Mermaid/SVG | 源码与产物一致 | 配置边界图示可解析、可读 | App Lab UI 或部署拓扑 |
| 真实多环境运行 | 尚未执行 | — | 开发机、测试板、现场板的实际部署 |

### 9.3 练习

1. 增加 `SAMPLE_LIMIT: int` 和 `DRY_RUN: bool`，验证字符串形式的 `"10"` 不会被静默转换为整数。
2. 设计一个只允许 `runtime` 覆盖、但不允许 `environment` 覆盖的字段，并说明为什么需要单独的策略层。
3. 将快照指纹写入第四篇结果账本的本地模拟记录，证明同一请求的结果查询不会泄露 Secret。
4. 为三套环境设计不同的 `data/` 隔离策略，列出切换环境时必须重新执行的证据。

## 10. 常见问题

### Q1：为什么不直接把所有环境写进一个 `app.yaml`？

`app.yaml` 描述 App 的固定结构和依赖声明，多环境变量属于运行治理。把二者混在一起会让一次临时测试修改看起来像项目结构变更，也会提高误发布风险。

### Q2：后层覆盖前层是不是一定危险？

不是。覆盖是多环境配置的正常机制，危险在于没有 schema、来源和锁定策略。本章允许普通键按明确顺序覆盖，同时禁止关键身份键被运行层改变。

### Q3：为什么相同 Secret 改变后指纹不变？

本章指纹计算的是脱敏快照。这样能避免通过指纹暴露 Secret 的变化，但也意味着指纹不能证明 Secret 值本身；Secret 健康检查必须另行完成。

### Q4：`run_id` 已经能区分运行，为什么还要配置指纹？

`run_id` 区分的是会话，配置指纹区分的是该会话使用的公开配置视图。两个运行可以有不同 `run_id` 却使用相同配置，也可以使用相同环境名但配置不同。

### Q5：本章的配置分层是 App Lab 的官方功能吗？

不是。本章明确把它作为项目治理和验证模型。真实工程应根据 App Lab、App CLI、目标镜像和组织的 Secret 设施选择具体落地方式，并记录版本和实测证据。

## 11. 本章小结与下一步

本章建立了从 `base` 到 `environment` 再到 `runtime` 的确定性配置合并，并通过 schema、来源记录和锁定键减少多环境漂移。`config_layers.py` 只输出经过类型校验的本地结果；`run_config_snapshot.py` 把一次运行的环境和非敏感配置固定为可复核的 JSON 与指纹。

最重要的边界是：配置快照是运行身份的辅助证据，不是目标设备部署回执，也不是 Secret 健康检查。只有把配置来源、生命周期、能力预检、结果账本和现场观察串起来，开发机到现场板的差异才不会变成不可解释的“同样代码却不同结果”。

下一章将继续处理 App Lab 项目的可观测性：如何把配置指纹、`run_id`、组件日志和错误来源组织成一份可检索的运行证据包。

## 延伸阅读

- [第五篇第1章：App Lab 开发基础](./第1章_App_Lab开发基础_应用结构与验证边界.md)
- [第五篇第2章：App Lab 运行生命周期](./第2章_AppLab运行生命周期_导入启动运行与停止.md)
- [第五篇第3章：App Lab 启动配置与 Brick 依赖](./第3章_AppLab启动配置与Brick依赖_从声明到可部署性检查.md)
- [Arduino App specification](https://github.com/arduino/arduino-app-cli/blob/main/docs/app-specification.md)
- [Arduino App CLI user documentation](https://github.com/arduino/arduino-app-cli/blob/main/docs/user-documentation.md)
- [Arduino App Lab examples](https://docs.arduino.cc/software/app-lab/tutorials/examples/)
- [Arduino UNO Q datasheet](https://docs.arduino.cc/resources/datasheets/ABX00162-datasheet.pdf)
