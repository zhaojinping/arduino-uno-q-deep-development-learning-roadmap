---
title: App Lab 运行证据包与日志关联：从 run_id 到可检索证据
part: 5
chapter: 5
status: draft
last_verified: 2026-09-23
updated: 2026-09-23
prerequisites: 第五篇第1～4章、第三篇第3章、第四篇第4章
tags: App Lab, run_id, 日志, config_fingerprint, 可观测性, 证据包
---

# 第5章 App Lab 运行证据包与日志关联：从 run_id 到可检索证据

## 学习目标

读完本章后，读者应能够：

1. 区分 App Lab Console 中 Start-up、Main (Python) 和 Sketch (Microcontroller) 三类输出。
2. 保留未经改写的原始日志，并建立可追溯的规范化事件索引。
3. 使用 `run_id`、脱敏配置指纹和事件来源关联组件日志，隔离陈旧、缺失或冲突证据。
4. 组织包含运行元数据、日志、事件索引、清单和校验值的最小证据包。
5. 在交付前识别 Secret、个人数据和设备标识，避免误发敏感日志。
6. 用本地模拟脚本演示关联规则，同时说明它没有验证 App Lab、UNO Q 或真实日志采集。

## 背景与边界

前四章依次建立了 App 结构、运行生命周期、启动依赖和多环境配置。现在的问题是：一次运行出现异常时，怎样把“哪次运行、使用什么配置、哪个组件在什么时间输出了什么”整理成一份可复核材料？

UNO Q 官方资料说明，App Lab Console 提供三类标签：Start-up 显示启动序列（包括 MCU 编译与 Linux 部署），Main (Python) 显示 Python 应用输出，Sketch (Microcontroller) 显示 Arduino Sketch 的串口输出。官方资料也提醒，App 成功启动后仍可能有运行时问题，Sketch 编译失败则会中止启动。[Arduino UNO Q datasheet：App Lab Console](https://docs.arduino.cc/resources/datasheets/ABX00162-datasheet.pdf)

官方资料确认的是控制台观察入口和输出类别，并未承诺日志自动带有本书定义的 `run_id`、配置指纹、统一时钟、无限期留存或一键导出。本章的事件字段、关联策略和证据包是**本书的工程建议**。从界面复制或以其他方式采集输出时，应记录采集时间与方式，不把截取文本伪称为平台原生结构化日志。

代码示例只处理人为构造的 JSON Lines，不读取设备或 App Lab，不解析任意格式的 Console 文本，也不自动清洗敏感信息。示例结果均为 `SIMULATED`；本章没有完成 App Lab 或硬件实测。

本章承接[第五篇第2章](./第2章_AppLab运行生命周期_导入启动运行与停止.md)的运行 ID、[第五篇第4章](./第4章_AppLab配置分层与多环境运行参数_从开发机到现场板.md)的脱敏配置指纹；日志时钟边界见[第三篇第3章](../第3篇_Linux/第3章_Linux可观测性与资源管理_日志时间与安全回滚.md)，业务结果收敛见[第四篇第4章](../第4篇_PythonBridge/第4章_Python_Bridge结果账本与状态查询_从返回值到可验证证据.md)。

## 1. 三类控制台输出，不是一条天然连续的日志

| Console 标签 | 官方说明的主要内容 | 排障时能说明什么 | 单独不能说明什么 |
| --- | --- | --- | --- |
| Start-up | 启动序列，包括 MCU 编译与 Linux 部署 | 启动流程推进到哪里；是否出现编译或部署错误 | Python 业务逻辑正确，或设备动作已发生 |
| Main (Python) | Python 应用输出，例如 `print()` | Linux 侧程序实际写出的文本和错误 | MCU 已收到请求或物理输出已完成 |
| Sketch (Microcontroller) | Arduino Sketch 串口输出，例如 `Serial.println()` | MCU 程序实际写出的串口文本 | 日志属于哪个 Linux 请求，除非有可验证的关联字段 |

三类输出可能采用不同格式和时间基准，也可能没有共同的请求标识。直接拼接文本只会得到一个阅读顺序，不一定得到可信的事件顺序。证据整理应区分：

1. **原始材料**：从 Console 或获准的诊断入口取得的原文；记录来源、采集时间和文件边界，不在原件上改写。
2. **规范化事件**：按稳定字段转换的索引；缺字段就标记缺失，不从上下文猜造。
3. **判定摘要**：按规则总结关联、冲突和缺口；每项摘要都能回链到原文。

“应用启动成功”“日志出现”和“请求得到业务结果”是不同的证据命题。跨到 MCU 或 Brick 的动作还需要明确请求/结果关联和独立状态证据。

## 2. 定义可审计的关联字段

推荐使用 JSON Lines：每行一个 UTF-8 JSON 对象。字段边界如下：

| 字段 | 必需性 | 约束与用途 |
| --- | --- | --- |
| `event_id` | 必需 | 单份事件流中唯一；重复时先调查采集重复或 ID 缺陷，不静默去重 |
| `ts_utc` | 必需 | 带时区的 UTC 时间；时钟可信度未知时另记质量，不把采集时间冒充事件时间 |
| `source` | 必需 | 如 `startup`、`main-python`、`sketch`、`brick`；只表示来源 |
| `severity` | 必需 | `DEBUG`、`INFO`、`WARN`、`ERROR` 或 `CRITICAL` |
| `event` | 必需 | 稳定事件名，例如 `app.ready` 或 `camera.init.failed` |
| `run_id` | 尽可能提供 | 与第五篇第2章的运行 ID 一致；缺失时归为未关联，不能按时间邻近补造 |
| `config_fingerprint` | 尽可能提供 | 与第五篇第4章的脱敏快照一致；不一致时隔离为冲突 |
| `raw_ref` | 推荐 | 原日志文件名与行号、偏移等稳定定位方式 |
| `correlation_id` | 按需 | 一次请求或跨组件操作 ID；不能替代运行 ID 或业务结果 ID |

字段样例见[本章 JSONL 文件](../../code/第5篇_AppLab/第5章_AppLab运行证据包与日志关联/sample_events.jsonl)。样例是模拟事件，不表示 App Lab Console 原生输出 JSON。

关联判定按以下顺序执行：

1. 缺少 `run_id`：`UNCORRELATED`，保留原始事件，不纳入本次运行结论。
2. `run_id` 与目标不同：`STALE`，通常是旧运行残留或日志窗口选错。
3. `run_id` 相同但指纹不同：`FINGERPRINT_CONFLICT`，隔离并调查快照绑定或数据混用。
4. `run_id` 和指纹均相同：完整关联。
5. `run_id` 相同但事件没有指纹：可暂按运行 ID 关联，同时计入指纹缺失；不能说配置身份已完整证明。

时间戳用于排序和窗口分析，不能替代身份。如果时钟漂移、时区未知或只记录采集时间，应标记时序精度未知，而非据此宣称因果关系。

## 3. Fig-32：从控制台日志到证据包

图 5-5 展示推荐的证据流。旧运行、缺少 ID 和指纹冲突都会留在包内，但进入隔离分类，不静默丢弃或混入有效事件。

<a id="fig-32-uno-q-app-lab-evidence-package"></a>

> 图示占位：图号=Fig-32；位置=本段之后；内容=展示三类 Console 原始日志与脱敏运行快照如何经规范化、run_id/指纹关联，保留陈旧、缺失和冲突分支后形成证据包；来源=依据已登记的 UNO Q 官方资料原创绘制。

~~~mermaid
flowchart LR
    subgraph CONSOLE["App Lab Console：官方输出类别"]
        START["Start-up<br/>启动序列"]
        PY["Main (Python)<br/>应用输出"]
        MCU["Sketch (Microcontroller)<br/>串口输出"]
    end
    START --> RAW["原始日志<br/>来源与采集时间"]
    PY --> RAW
    MCU --> RAW
    RAW --> NORMAL["规范化事件<br/>event_id · ts_utc · source"]
    SNAP["run.json + 脱敏配置快照<br/>run_id · config_fingerprint"] --> MATCH{"关联判定"}
    NORMAL --> MATCH
    MATCH -->|"run_id 缺失"| ORPHAN["UNCORRELATED<br/>未关联"]
    MATCH -->|"run_id 不同"| STALE["STALE<br/>陈旧运行"]
    MATCH -->|"run_id 相同"| FP{"配置指纹"}
    FP -->|"一致"| MATCHED["完整关联"]
    FP -->|"事件未提供"| PARTIAL["按 run_id 关联<br/>指纹缺失"]
    FP -->|"不一致"| CONFLICT["FINGERPRINT_CONFLICT<br/>隔离调查"]
    ORPHAN --> BUNDLE["证据包<br/>清单 · 摘要 · 文件校验值"]
    STALE --> BUNDLE
    MATCHED --> BUNDLE
    PARTIAL --> BUNDLE
    CONFLICT --> BUNDLE
    BUNDLE --> REVIEW["脱敏复核<br/>按需交付"]
~~~

这是原创工作流图，不是 App Lab 内部数据流或官方导出流程。独立源文件为[uno-q-app-lab-evidence-package.mmd](../../diagrams/uno-q-app-lab-evidence-package.mmd)。

## 4. 组织一份最小证据包

每次运行使用独立目录，以 `run_id` 命名，避免多次运行混写：

~~~text
evidence/
└── run-043/
    ├── run.json                 # 环境、软件版本、目标别名、时间与 run_id
    ├── config.redacted.json     # 第4章公开配置快照；不含 Secret
    ├── events.jsonl             # 规范化事件；保留 raw_ref
    ├── logs/
    │   ├── startup.log         # Start-up 原始输出
    │   ├── main-python.log     # Main (Python) 原始输出
    │   └── sketch.log          # Sketch 原始输出
    ├── manifest.json            # 文件清单、大小、SHA-256 与关联摘要
    └── handoff.md               # 复现条件、缺口、结论与下一步
~~~

未启用或无法采集的组件，应在清单中标注 `not_applicable`、`unavailable` 或原因；不要创建空文件冒充采集成功。清单至少记录：

- `run_id`、环境名、目标设备的非敏感别名、App 代码版本或提交号；
- 实际观察到的 App Lab、App CLI、目标系统镜像版本；不可观察时写 `UNKNOWN`；
- 脱敏配置指纹、运行起止时间、时间来源及已知时钟偏差；
- 文件相对路径、字节数、SHA-256、来源和脱敏状态；
- 关联、陈旧、未关联、指纹缺失、指纹冲突计数，以及判定摘要；
- 未采集流、人工转换步骤、已知缺口和复现环境。

哈希只说明这份**已审阅证据副本**在交付后是否发生字节变化；不能证明来源真实、设备可信、时间准确或内容完整。先脱敏和复核，再计算交付文件的哈希。不要把带凭据的原始材料、密钥、令牌、个人信息或无需交付的 `data/`、`.cache/` 整体打包。原日志意外含 Secret 时，先隔离受限保存，再制作明确标注为派生件的脱敏副本；不要把未经审阅的原件推入 Git。

## 5. 实验：按运行 ID 关联规范化事件

离线示例读取脱敏运行元数据和 JSONL 事件，分类本次事件、陈旧运行、未关联事件及指纹冲突。它只处理已规范化输入，不把任意 Console 文本自动转换成可靠事件。

代码说明
- 用途：演示基于 `run_id` 与配置指纹的关联和保守判定。
- 运行环境：Python 3.10 或更高版本；Windows、Linux 或 macOS。
- 文件位置：`code/第5篇_AppLab/第5章_AppLab运行证据包与日志关联/correlate_events.py`。
- 依赖：Python 标准库；输入为同目录的 `sample_run.json`、`sample_events.jsonl`。
- 操作步骤：从仓库根目录运行下面命令；仅读取固定模拟样例，不连接设备、不写文件。
- 预期输出：3 条按运行 ID 关联、1 条陈旧、1 条未关联、1 条指纹冲突；结论为 `RUNTIME_ERROR`。
- 故障排查：检查每行是否为 JSON 对象、UTC 时间是否含时区、事件 ID 是否重复、指纹是否为 64 位小写十六进制；不要按时间邻近补齐运行 ID。
- 验证方式：逐项对照模拟输出并确认四类事件进入不同计数；这不构成 App Lab 或 UNO Q 实测。

~~~text
python -B "code/第5篇_AppLab/第5章_AppLab运行证据包与日志关联/correlate_events.py" --metadata "code/第5篇_AppLab/第5章_AppLab运行证据包与日志关联/sample_run.json" --events "code/第5篇_AppLab/第5章_AppLab运行证据包与日志关联/sample_events.jsonl"
~~~

示例输出（`SIMULATED`；本次未在 UNO Q 上运行）：

~~~text
SIMULATED run_id=run-043 total=6 correlated=3 stale=1 uncorrelated=1 fingerprint_conflict=1
SIMULATED verdict=RUNTIME_ERROR errors=1 warnings=0 sources=main-python,startup
SIMULATED fingerprint_missing=0
~~~

`RUNNING_NO_ERROR_OBSERVED` 只表示样例中存在 `app.ready` 且没有发现已关联错误，不等于功能正确、设备安全或验收通过。`RUNTIME_ERROR` 也只是事件摘要，仍须回到 `raw_ref` 指向的原文和组件状态。脚本拒绝重复事件 ID 和格式错误的时间/指纹，避免静默丢弃数据制造“干净”结论。

## 6. 从采集到交付的操作顺序

1. 启动前创建唯一 `run_id`，先生成第五篇第4章的脱敏配置快照。
2. 记录目标别名、代码版本、App Lab/CLI/系统镜像版本、启动时间和时钟来源；未知值标注 `UNKNOWN`。
3. 在 App Lab Console 中分别记录 Start-up、Main (Python)、Sketch (Microcontroller) 输出，保留原始文本与来源边界；不要假定标签具有相同的导出、留存期限或时间戳。
4. 对事件逐条规范化。关联字段必须来自明确日志、可追溯的请求传播或明确人工记录；不得仅凭时间相近补造 `run_id`。
5. 分别统计已关联、陈旧、未关联、指纹缺失和冲突事件；为错误保留上下文窗口，而非只摘录报错单行。
6. 检查 Secret、个人信息、网络地址、序列号和业务敏感数据，制作最小化脱敏副本并记录复核状态。
7. 为交付副本生成清单与 SHA-256；把已观察事实、模型判定和未验证事项分别写入 `handoff.md`。
8. 交付后不原地改写证据包。补充或脱敏时生成新版本并记录关系；受限原件不上传公开仓库。

若应用和 Sketch 无法共享同一个 `run_id`，可以用受控操作记录分别记录启动窗口和请求 ID，但必须标记为“人工关联”，不能升级成强因果证明。长期方案是在应用协议与组件日志中显式传播运行/请求 ID，并以 MCU 回执或业务状态再次闭环。

## 7. 采集检查单与验证矩阵

### 7.1 采集检查单

- [ ] 每次运行有唯一 `run_id`，且在启动前生成。
- [ ] 配置指纹来自脱敏快照；Secret 不进入普通日志、事件文件或仓库。
- [ ] 三类 Console 输出分别保存并标明来源、采集时间与边界。
- [ ] 原始文本保持不变；规范化事件能回指原文。
- [ ] 陈旧、未关联、指纹缺失和冲突各自计数，没有被静默丢弃。
- [ ] 事件时间采用明确时区；时钟质量未知时如实记录。
- [ ] 哈希只覆盖经审阅的交付副本，不被解释为真实性证明。
- [ ] 摘要列明尚未完成的 Router/Bridge、MCU、Brick、实机和业务结果验证。

### 7.2 本章验证矩阵

| 验证项 | 本章状态 | 能说明什么 | 不能说明什么 |
| --- | --- | --- | --- |
| JSONL 关联示例 | 固定模拟输入已写入；本次未执行脚本 | 样例设计覆盖同一运行、陈旧、缺失 ID 与指纹冲突分类 | 任意格式日志都能自动解析 |
| 原始日志采集 | 未执行 UNO Q/App Lab 实测 | — | Console 实际导出、留存时长、时间戳质量 |
| Fig-32 Mermaid | 源文件与正文已建立；SVG 尚未生成 | 关系可由 Mermaid 源文件追溯 | App Lab 内部实现或产品 UI |
| 实机运行/故障注入 | 未执行 | — | Router/Bridge、MCU、Brick、设备行为或验收结果 |

### 7.3 练习

1. 为样例增加一条缺少 `config_fingerprint`、但 `run_id` 相同的错误事件，说明它为何仍按运行 ID 关联，同时计入指纹缺失。
2. 设计跨 Python 与 Sketch 的请求，列出 `correlation_id`、MCU 回执、Python 结果和第四篇结果账本之间的证据关系。
3. 为含访问令牌的模拟日志制定隔离、脱敏、复核与重新计算哈希流程；不要将真实凭据写入练习文件。
4. 假设系统时钟快 90 秒，分别说明时间排序、运行 ID 关联和请求因果判断还能支持哪些结论。

## 8. 常见问题

### Q1：官方 Console 已分成三个标签，为什么还要保存来源？

复制或跨工具分析后，标签边界可能丢失。将来源写进文件名和事件字段，才能让脱离界面的证据包仍然可读。

### Q2：时间戳相近，能否把没有 `run_id` 的 MCU 日志归给当前运行？

不能自动归属。时间接近只能形成候选线索；没有可复核传播字段或明确人工记录时，应保留为 `UNCORRELATED`。

### Q3：配置指纹一致是否证明现场使用了正确的 Secret？

不能。指纹只覆盖脱敏配置快照，Secret 被刻意排除。凭据有效性和权限需另行验证，且不能泄露秘密。

### Q4：为什么不把所有日志直接拼成一个文件？

可以生成派生时间线，但必须保留原始分片、来源、时间转换规则和每条事件的 `raw_ref`。拼接文件是索引视图，不能替代原件。

### Q5：`RUNTIME_ERROR` 是最终故障结论吗？

不是。它表示规范化事件中存在按运行 ID 关联的错误；根因仍要结合错误上下文、组件状态、配置快照和复现步骤判定，不自动代表 MCU 或硬件失败。

## 9. 本章小结与下一步

本章把 App Lab 三类控制台输出、第五篇第2章的 `run_id` 和第五篇第4章的配置指纹连成一条可审计证据链：原始材料只读保留，规范化事件显式关联，冲突与缺口单独计数，脱敏后再计算交付文件校验值。

本地示例只展示 JSONL 关联规则，不读取 Console、导出实际日志或证明设备运行。下一章将进一步处理 App 的健康观察、运行状态和故障处置：哪些信号可以自动采集，哪些必须由操作者确认，哪些结果仍是 `UNKNOWN`。

## 延伸阅读

- [第五篇第2章：App Lab 运行生命周期](./第2章_AppLab运行生命周期_导入启动运行与停止.md)
- [第五篇第3章：App Lab 启动配置与 Brick 依赖](./第3章_AppLab启动配置与Brick依赖_从声明到可部署性检查.md)
- [第五篇第4章：App Lab 配置分层与多环境运行参数](./第4章_AppLab配置分层与多环境运行参数_从开发机到现场板.md)
- [第三篇第3章：Linux 可观测性与资源管理](../第3篇_Linux/第3章_Linux可观测性与资源管理_日志时间与安全回滚.md)
- [第四篇第4章：Python Bridge 结果账本与状态查询](../第4篇_PythonBridge/第4章_Python_Bridge结果账本与状态查询_从返回值到可验证证据.md)
- [Arduino UNO Q datasheet：App Lab Console](https://docs.arduino.cc/resources/datasheets/ABX00162-datasheet.pdf)
- [参考资料索引](../../resources/references.md)
