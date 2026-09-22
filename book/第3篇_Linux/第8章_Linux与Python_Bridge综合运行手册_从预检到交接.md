---
title: Linux 与 Python Bridge 综合运行手册：从预检到篇末交接
part: 3
chapter: 8
status: draft
last_verified: 2026-09-22
updated: 2026-09-22
prerequisites: 第三篇第1～7章
tags: Linux, Python Bridge, 运行手册, 证据, 交接
---

# 第8章 Linux 与 Python Bridge 综合运行手册：从预检到篇末交接

## 学习目标

完成本章后，读者应能够：

- 把一次 Linux、Python Bridge、服务和 MCU 协同运行定义为有边界的运行批次，而不是一组零散命令；
- 区分观察、模拟、受控动作、已应用、拒绝、未知和回滚等结果状态；
- 在进入任何受控动作前，完成范围、身份、版本、时间、网络、服务和回滚点的只读盘点；
- 使用健康门判断“可以继续”“必须停止”“需要回滚”或“只能交给人工裁决”；
- 生成不包含凭据、序列号和个人数据的证据包，并将其交接给后续篇章；
- 明确本机静态检查、概念实验、UNO Q 现场观察和 MCU 闭环验证之间的证据差异。

本章把第三篇已经建立的 Linux、Python Bridge、测试和服务治理知识合并成一条运行路线。它不替代第四篇的 Bridge 编程教程，也不替代第五篇的 App Lab 运行教程；它回答的是一个更窄但更重要的问题：当多个层次同时参与一次运行时，怎样知道自己正在改变什么、结果是否可判定，以及什么时候必须停止。

## 背景与边界

Arduino UNO Q 是一个由 Linux 侧高性能处理能力与 MCU 侧实时硬件控制共同组成的平台。Linux 侧可以承载 Python、应用服务、网络和数据处理；MCU 侧负责确定性更强的 GPIO、定时、采样和执行器控制；两侧通过 Bridge/RPC 形成逻辑协作。Arduino App specification 将 App 拆分为 Linux 侧的 Python、Brick 或容器，以及 MCU 侧的 Arduino Sketch，并用 RPC 消息连接两者。本章沿用这个职责边界，但不把“能够建立连接”直接写成“业务动作已经生效”。

第三篇前面的章节已经分别讨论了：

- [第三篇第 4 章：远程运维与 Python Bridge](./第4章_Linux远程运维与Python_Bridge_从安全命令到可验证请求.md)中的入口、白名单、请求信封、幂等和 UNKNOWN；
- [第三篇第 5 章：现场自动化与 Python Bridge](./第5章_Linux现场自动化与Python_Bridge_队列重连与状态缓存.md)中的队列、背压、重连和缓存 freshness；
- [第三篇第 6 章：现场测试与性能治理](./第6章_Linux与Python_Bridge现场测试与性能治理_从基准压测到故障注入.md)中的基线、分位数、故障注入和测试放行门；
- [第三篇第 7 章：现场部署与服务化治理](./第7章_Linux与Python_Bridge现场部署与服务化治理_从systemd配置分层到安全回滚.md)中的部署对象、systemd、配置/凭据分层、健康门和回滚。

因此，本章不再重新解释 systemd.service 的每一个字段，不重新设计性能指标，也不把一个概念脚本包装成现场工具。本章给出的代码只能在普通 Python 3 环境中生成脱敏的本地记录；它不调用 ADB、SSH、systemctl、Bridge、网络或硬件。

这里的“完结”有一个明确含义：第三篇的正文路线从基础、观察、远程入口、自动化、测试、部署走到综合运行和跨篇交接，形成第 1～8 章初稿。它不表示当前工作站已经连接 Arduino UNO Q，也不表示已经执行过真实的服务安装、配置替换、Bridge 重启、远程写入、MCU 联调或现场性能测试。

## 1. 综合运行的对象、状态和证据等级

### 1.1 一次运行批次至少要有七个对象

“运行一次 App”在教学演示里通常只有一个按钮；在工程现场，它至少包含以下对象：

| 对象 | 要回答的问题 | 典型证据 |
| --- | --- | --- |
| 范围 | 哪一台设备、哪个 App、哪个版本、哪个时间窗口在范围内？ | 运行批次、目标标识、版本和时间窗口 |
| 目标 | 请求将作用于 Linux 服务、Python 进程、Bridge 入口还是 MCU 功能？ | 目标类型、逻辑名称和授权范围 |
| 动作 | 本次是观察、模拟、配置变化、服务动作还是业务写入？ | 动作名称、参数摘要和变更前快照 |
| 观察 | 哪些指标用来判断结果？ | 服务状态、日志字段、队列/缓存状态、Bridge 响应 |
| 健康门 | 满足哪些条件才可以进入下一阶段？ | 可判定的门槛、检查时间和检查人 |
| 回滚点 | 如果结果不确定或健康门失败，怎样恢复到已知状态？ | 旧版本、配置快照、停止点和回滚验证 |
| 交接包 | 其他人接手时，需要看到哪些证据和未决项？ | 脱敏清单、状态摘要、日志引用和未决项 |

如果其中一个对象没有明确边界，运行批次就还没有准备好。例如，只写“升级服务”而没有写目标 unit、应用版本、配置 revision 和回滚点，无法在失败后判断究竟改变了哪一层。

### 1.2 结果状态必须能区分

本书统一使用以下结果状态。状态是证据结论，不是日志级别，也不是 HTTP 状态码：

| 状态 | 含义 | 允许的下一步 |
| --- | --- | --- |
| OBSERVED | 只读观察到某个事实，例如服务状态或日志字段 | 可以形成基线，不代表执行过动作 |
| SIMULATED | 在本地替身或概念脚本中演示了规则 | 只能验证代码逻辑，不能代替设备证据 |
| APPLIED | 受控动作已执行，并且有独立的后置观察证明目标状态达到要求 | 可以进入下一阶段，但仍需保留证据 |
| REJECTED | 动作在执行前被范围、权限、版本或健康门阻止 | 停止当前批次，修正前置条件后重新评审 |
| UNKNOWN | 动作是否生效无法判定，或结果与观察相互矛盾 | 不自动重试；先查询、对账或交给人工裁决 |
| ROLLED_BACK | 已恢复到明确的旧状态，并且恢复结果经过独立验证 | 关闭批次或保留未决项，不得仅凭回滚命令宣称恢复 |

最危险的误判是把 UNKNOWN 当作 FAILED。失败至少说明某个动作明确没有达到预期；未知说明系统可能已经改变，重试可能产生重复动作、越过幂等边界或进一步改变硬件状态。对于控制类请求，未知状态必须先进入对账流程。

### 1.3 证据等级决定措辞强度

综合运行的结论应与证据等级匹配：

| 等级 | 证据来源 | 可以怎样写 | 不能怎样写 |
| --- | --- | --- | --- |
| L0 | 文档阅读和来源登记 | “官方文档说明……” | “本设备已经……” |
| L1 | Markdown、链接、front matter、Mermaid 和代码静态检查 | “仓库结构和静态检查显示……” | “已经在 UNO Q 上运行……” |
| L2 | 本地 Python 概念实验或替身 | “概念实验返回……” | “Bridge 已返回……” |
| L3 | UNO Q Linux 侧只读观察 | “目标设备在该时间点观察到……” | “MCU 输出已经正确……” |
| L4 | 受控 Bridge 请求和 MCU 侧独立观察 | “请求已应用并由独立观察确认……” | 省略时间、版本或回滚信息 |
| L5 | 可重复的硬件、性能、故障注入和部署闭环 | “在指定版本和条件下复现……” | 脱离条件推广为永久保证 |

本章当前能够交付的是 L0～L2 的正文和仓库证据框架。L3～L5 必须在拥有目标设备、明确授权和可控实验窗口时单独执行。

## 2. Fig-23：Linux、Python Bridge、服务治理与跨篇交接闭环

<a id="fig-23-linux-python-bridge-operational-handoff"></a>

~~~mermaid
flowchart LR
    A["范围确认"] --> B["只读盘点"]
    B --> C["Dry-run"]
    C --> D{"健康门"}
    D -->|APPLIED| E["受控运行"]
    D -->|REJECTED| X["停止并保留证据"]
    E -->|APPLIED| F["证据归档"]
    E -->|UNKNOWN| G["人工裁决"]
    G -->|ROLLED_BACK| H["回滚验证"]
    H --> F
    F --> I["交接包"]
    I -.-> J["第四篇 Python Bridge"]
    I -.-> K["第五篇 App Lab"]
    I -.-> L["第九篇 Project"]
~~~

> 图示占位：图号=Fig-23；位置=本段之后；内容=Linux、Python Bridge、服务治理、健康门、证据归档与跨篇交接的综合运行闭环；来源=见 ../../diagrams/uno-q-linux-operational-handoff.mmd。

图中的实线表示本章建议的运行顺序，虚线表示交接目标，不表示处理器之间存在一条物理连线。APPLIED 只能在动作和后置观察都满足要求时使用；REJECTED 表示尚未进入受控动作；UNKNOWN 进入人工裁决；只有回滚动作和回滚后的独立验证都完成，才可把结果标记为 ROLLED_BACK。如果无法完成回滚验证，应保留 UNKNOWN 或 DEGRADED 的未决状态，而不是为了关闭工单而改写结论。

## 3. 预检与只读盘点

### 3.1 先锁定范围，再接触动作

预检不是“把所有命令都执行一遍”，而是确认本次运行允许观察和允许改变的范围。建议在运行批次中固定以下字段：

| 字段 | 示例 | 安全要求 |
| --- | --- | --- |
| run_id | run-2026-09-22-sample-001 | 不含密码、访问令牌或完整个人信息 |
| target | sample-uno-q-lab | 实际现场使用设备登记号；正文示例使用脱敏值 |
| app_revision | app-git-a1b2c3d | 使用不可变 revision，不使用 latest 或 main |
| config_revision | cfg-sample-07 | 只记录标识，不记录秘密值 |
| bridge_contract | bridge-v1 | 记录协议或契约版本 |
| window | 2026-09-22T09:00/09:30+08:00 | 明确时区和开始/结束时间 |
| operator | operator-redacted | 使用组织内批准的脱敏或工号映射 |

如果目标、版本或变更窗口无法确认，预检结果应为 REJECTED。不要用“先试一下”绕过身份确认，因为试验本身可能就是一次不可逆的服务、配置或硬件动作。

### 3.2 只读盘点的最小集合

只读盘点至少覆盖以下七类信息：

1. **设备身份**：设备名、登记号、镜像或系统版本、当前用户和时区。
2. **软件身份**：App revision、Python 依赖摘要、Bridge 契约版本、配置 revision 和 unit revision。
3. **入口可见性**：USB/ADB、SSH、Network Mode 或 App Lab 的可见性。入口可用只代表路径可达，不代表应用或 MCU 结果正确。
4. **网络状态**：接口、活动连接、地址和时间；密码、私钥和完整网络凭据不进入证据包。
5. **服务状态**：unit 是否存在、是否 enabled、是否 active、最近启动时间和最近错误；active 不能替代业务健康。
6. **Bridge 状态**：Router/Bridge 进程或入口是否可观察、请求队列是否有未决项、最近一次结果是否可对账。
7. **回滚条件**：旧版本路径、配置快照、停止新控制的方式、回滚验证动作和人工联系人。

Linux 侧的查询工具应按目标镜像实际存在情况选择。nmcli、systemctl、journalctl、adb 或 App Lab 入口的通用语义来自各自官方文档，但具体命令是否可用、权限是否足够、输出字段是否一致，仍需在目标设备上现场确认。不能因为主机上有某个命令，就推断 UNO Q 当前镜像已经具备同样的工具和 unit。

### 3.3 预检输出应是可审查的清单

预检结束时，不要只留下终端滚屏。建议输出一张短清单：

| 检查项 | 状态 | 证据引用 | 停止条件 |
| --- | --- | --- | --- |
| 范围和版本 | OBSERVED / REJECTED | manifest 摘要 | 目标或 revision 缺失 |
| 网络和时间 | OBSERVED | 脱敏快照 | 时间不可比或入口不明 |
| service | OBSERVED | unit 状态和日志窗口 | unit 不存在或反复重启 |
| Bridge | OBSERVED | Router/Bridge 观测 | 请求未决且无法对账 |
| 回滚点 | OBSERVED / REJECTED | 快照清单 | 没有已知旧状态 |
| 安全边界 | OBSERVED | 权限和秘密检查 | 证据将暴露凭据 |

只读盘点不能改变配置、重启服务、清空日志或触发硬件动作。如果一个“健康检查”本身会发送业务请求，它就不再是纯只读检查，必须移到受控阶段并标明风险。

## 4. Dry-run 与受控运行

### 4.1 Dry-run 不是空转，而是验证计划

Dry-run 的产物不是“命令执行成功”，而是回答以下问题：

- 计划会触碰哪些对象；
- 每个对象的旧状态是什么；
- 预期改变哪一个变量；
- 改变后用什么独立观察判断结果；
- 如果观察不到结果，回滚点在哪里；
- 哪些步骤需要人工确认。

一个合格的 Dry-run 可以生成待执行动作列表，但不应写入目标服务、配置、凭据、队列或 MCU。对于会改变系统的命令，Dry-run 是否真的无副作用取决于具体工具，不能只看命令名称中是否出现 --dry-run。

### 4.2 一次只改变一个变量

如果一次同时替换 App、配置、凭据、unit 和 Bridge 协议，就算最后恢复成功，也无法解释哪一个变量造成了问题。受控运行应尽量按以下顺序拆分：

1. 只验证候选构建产物和 revision；
2. 只验证配置 schema、权限和引用；
3. 只验证 unit 文件语法和执行环境；
4. 只激活一个候选版本；
5. 观察 service、Bridge、队列、缓存和 MCU 结果；
6. 通过健康门后再进入下一个变量；
7. 一旦出现 UNKNOWN，冻结后续变化。

这个顺序与第 7 章的“配置变化和应用变化分开回滚”一致，也与第 6 章的“故障注入一次只改变一个假设”一致。

### 4.3 运行阶段的状态转换

| 阶段 | 允许动作 | 必须记录 | 失败处理 |
| --- | --- | --- | --- |
| 预检 | 只读观察 | 范围、版本、入口、回滚点 | REJECTED，不进入下一阶段 |
| Dry-run | 本地解析和模拟 | 计划、预计对象和停止条件 | 修改计划，不触碰设备 |
| 暂存 | 准备候选文件或本地副本 | 文件摘要、权限和 revision | 删除暂存副本或保留审查证据 |
| 激活 | 一次一个受控变化 | 动作开始/结束时间和操作者 | 停止新控制，进入健康门 |
| 健康门 | 独立只读检查和必要对账 | 检查项、窗口和原始引用 | 通过、拒绝、未知或回滚 |
| 收尾 | 关闭变更窗口 | 最终状态、未决项和交接人 | 未决项不能被静默关闭 |

服务管理器报告进程已经启动，只能说明生命周期层有一个结果；应用能够接受请求、Bridge 请求真正到达 MCU、MCU 的安全状态机接受动作、输出达到要求，分别属于更高层的健康结论。综合运行必须把这些层分开记录。

## 5. 健康门、故障分级与 UNKNOWN

### 5.1 健康门至少包含六类判断

健康门不是一个布尔值，而是一组有明确证据来源的条件：

| 健康门 | 通过条件 | 不通过时的动作 |
| --- | --- | --- |
| 身份门 | 目标、App revision、配置 revision 和窗口一致 | 停止，不允许激活 |
| 服务门 | 服务状态稳定，日志没有与本变更相关的启动错误 | 保持观察或回滚 |
| 业务门 | 业务入口返回符合契约的结果 | 不以进程存活代替成功 |
| Bridge 门 | 请求关联、响应状态和 MCU 侧可观察状态可对账 | UNKNOWN 时冻结重试 |
| 资源门 | 队列、内存、CPU、I/O、缓存 freshness 在预算内 | 降级、停止或回滚 |
| 证据门 | 时间、版本、日志引用和结果状态齐全 | 不得关闭运行批次 |

健康门的检查顺序应该从低风险、低成本到高风险、强证据：先检查身份和版本，再检查进程和日志，再检查业务读路径，最后才允许受控写路径或硬件闭环。这样可以减少在前置条件不满足时触发高风险动作。

### 5.2 四级故障处理

建议将异常分为四级：

- **可观察偏差**：服务仍然稳定，某个指标接近预算但未越界。保持观察，不能直接扩大范围。
- **可恢复失败**：某个动作明确被拒绝或失败，旧状态仍然清晰。停止新控制，按预案恢复。
- **结果未知**：超时、连接中断、日志缺失或响应与状态不一致。冻结批次，先对账，不自动重试。
- **安全边界事件**：身份错配、凭据暴露、权限异常、MCU 安全状态机拒绝或输出未进入安全态。立即停止并保留证据，必要时由人工接管。

这四类故障不应被压缩成一个 FAILED 字段。对于现场交接，下一位工程师最需要知道的往往不是“失败”，而是“失败发生在动作前、动作中、动作后还是无法判定”。

### 5.3 UNKNOWN 的处理协议

当结果未知时，按照以下顺序处理：

1. **冻结**：不再发送同一业务动作，不扩大并发，不清理可能有价值的日志。
2. **标识**：记录请求关联 ID、目标、动作摘要、发送时间、超时位置和最后可观察状态。
3. **对账**：执行只读查询，确认服务、队列、缓存、Bridge 和 MCU 侧是否存在对应状态。
4. **判断幂等性**：只有在协议明确说明请求可安全重复，且对账证明旧请求没有生效时，才可以单独评审重试。
5. **回滚或人工裁决**：如果无法证明安全重试，恢复到旧状态或交给有权限的人员裁决。
6. **关闭证据**：最终状态只能是已应用、明确拒绝、已回滚或仍未决，不把未决写成成功。

## 6. 证据包和现场交接

### 6.1 证据包的最小字段

建议把证据包拆成四类，而不是把完整终端日志和所有配置直接打包：

| 类别 | 字段 | 脱敏规则 |
| --- | --- | --- |
| 身份 | run_id、目标别名、App/config/unit revision | 不放真实序列号和密钥 |
| 时间 | 开始、结束、时区、时间源说明 | 保留可比的时间窗口 |
| 动作 | 动作名称、模式、参数摘要、前后状态 | 参数中秘密字段改为 [REDACTED] |
| 结果 | 状态、健康门、回滚结论、未决项 | 保留 UNKNOWN，不改写 |
| 引用 | 日志窗口、文件摘要、请求 ID | 引用位置，不复制敏感原文 |
| 责任 | 操作者、审批或交接人、下一步 | 使用组织批准的标识 |

可以把证据包理解为“让另一位工程师在不接触秘密的情况下复核结论”的最小集合。原始日志和秘密材料应在受控存储中按组织策略保存，Markdown 仓库只记录引用、摘要和边界。

### 6.2 证据包中的版本关系

至少同时记录以下版本关系：

- App 或容器的不可变 revision；
- 配置 schema 和配置 revision；
- systemd unit revision；
- Bridge 契约版本；
- MCU Sketch 或固件构建标识；
- 运行手册或测试规格的版本。

如果 App revision 已更新、配置 revision 没有更新，不能自动推断配置仍兼容；如果服务 active 但 Bridge 契约不匹配，不能把服务门通过写成综合健康。版本关系本身就是健康门的一部分。

### 6.3 交接不是一句“请继续”

交接包至少要有三段：

1. **已确认**：只写有证据支持的事实，例如“静态检查通过”“观察到 service active”“概念实验返回 SIMULATED”。
2. **未决项**：写出缺失证据、未知结果、未完成回滚验证和需要谁裁决。
3. **下一步**：给出低风险的只读动作、明确的停止条件和交接目标，不直接把危险动作当作默认下一步。

交接时应把“尚未执行”写成一等信息。没有实机并不等于失败，但必须让读者知道此时只能做文档、代码和本地替身层面的结论。

## 7. 第一个 Python 实验：运行批次与证据清单

### 7.1 实验目标

本实验用 Python 标准库创建一个脱敏的运行记录，演示如何将多个事件附加到同一个 run_id，再生成只包含摘要的证据清单。它不会读文件、访问网络、调用 Linux 命令、连接 Bridge 或修改设备。

### 7.2 代码说明

- 用途：演示运行批次、事件状态和脱敏证据清单的最小数据结构。
- 运行环境：Python 3.10 或更高版本的标准库；Windows、Linux 或 macOS 均可。
- 文件位置：概念脚本；建议保存为 run-evidence-manifest.py。
- 依赖：仅使用 copy 和 json；不需要 UNO Q、Arduino App Lab、systemd、网络或第三方包。
- 操作步骤：将代码保存为脚本后直接运行；先观察 OBSERVED 和 SIMULATED 事件，再尝试把状态改成未定义值，确认校验会阻止它。
- 预期输出：输出一行 JSON 证据清单，包含脱敏目标、版本和事件状态；这是 SIMULATED 示例输出，不是目标设备运行结果。
- 故障排查：检查 Python 版本、JSON 括号、状态名称和 run_id 是否为空；不要把真实密码、令牌或设备序列号填入示例字段。
- 验证方式：分别删除 run_id、传入不在允许集合中的状态、改变事件顺序，确认脚本在本地拒绝不完整记录且不执行外部动作。

~~~python
from __future__ import annotations

import json
from copy import deepcopy


ALLOWED_STATES = {
    "OBSERVED",
    "SIMULATED",
    "APPLIED",
    "REJECTED",
    "UNKNOWN",
    "ROLLED_BACK",
}


def new_run_record(
    run_id: str,
    target: str,
    version: str,
    mode: str,
) -> dict[str, object]:
    if not run_id or not target or not version:
        raise ValueError("run_id, target and version are required")
    if mode not in {"observe", "dry_run", "controlled"}:
        raise ValueError("unsupported mode")
    return {
        "run_id": run_id,
        "target": target,
        "version": version,
        "mode": mode,
        "events": [],
    }


def append_event(
    record: dict[str, object],
    event: str,
    state: str,
    evidence: str,
) -> dict[str, object]:
    if state not in ALLOWED_STATES:
        raise ValueError("unsupported state")
    updated = deepcopy(record)
    events = list(updated["events"])
    events.append(
        {
            "event": event,
            "state": state,
            "evidence": evidence,
        }
    )
    updated["events"] = events
    return updated


def render_evidence_manifest(record: dict[str, object]) -> str:
    events = record["events"]
    return json.dumps(
        {
            "run_id": record["run_id"],
            "target": record["target"],
            "version": record["version"],
            "mode": record["mode"],
            "events": events,
        },
        ensure_ascii=False,
        sort_keys=True,
    )


def main() -> None:
    record = new_run_record(
        run_id="run-2026-09-22-sample-001",
        target="sample-target",
        version="app-git-a1b2c3d",
        mode="dry_run",
    )
    record = append_event(
        record,
        event="scope-check",
        state="OBSERVED",
        evidence="local-example:scope",
    )
    record = append_event(
        record,
        event="health-gate",
        state="SIMULATED",
        evidence="local-example:gate",
    )
    print(render_evidence_manifest(record))


if __name__ == "__main__":
    main()
~~~

示例输出：

~~~text
{"events": [{"event": "scope-check", "evidence": "local-example:scope", "state": "OBSERVED"}, {"event": "health-gate", "evidence": "local-example:gate", "state": "SIMULATED"}], "mode": "dry_run", "run_id": "run-2026-09-22-sample-001", "target": "sample-target", "version": "app-git-a1b2c3d"}
~~~

这个脚本使用 deepcopy 返回新记录，避免调用者在函数内部被隐式改变。真实系统还需要限制事件大小、校验时间格式、过滤秘密字段和保存不可抵赖的原始证据；这些工作不应由这个教学示例假装完成。

## 8. 第二个 Python 实验：交接门与未决项清单

### 8.1 实验目标

本实验把观察结果转换为交接状态。它特意覆盖四种情况：

- 所有必需项已应用，结果为 APPLIED；
- 缺少必需项，结果为 REJECTED；
- 存在未知项，结果为 UNKNOWN；
- 旧状态已经恢复，结果为 ROLLED_BACK。

实验只处理内存字典，不调用服务管理器、Bridge、网络或 MCU。

### 8.2 代码说明

- 用途：演示健康门如何在交接前阻止缺项、保留未知和识别已验证回滚。
- 运行环境：Python 3.10 或更高版本的标准库。
- 文件位置：概念脚本；建议保存为 handoff-gate.py。
- 依赖：无第三方依赖；输入是本地构造的观察结果。
- 操作步骤：依次运行 applied、rejected、unknown 和 rolled_back 四组固定数据，比较交接状态和未决项。
- 预期输出：四组结果分别为 APPLIED、REJECTED、UNKNOWN、ROLLED_BACK；这是 SIMULATED 示例输出，不是现场放行结论。
- 故障排查：检查必需键名称、状态拼写和回滚证据字段；UNKNOWN 不应被 summarize_open_items 删除。
- 验证方式：逐一移除 identity、version、service_health，或把 Bridge 观察改成 UNKNOWN，确认结果不会错误地变成 APPLIED。

~~~python
from __future__ import annotations

from typing import Any


def evaluate_handoff_gate(
    observations: dict[str, dict[str, Any]],
    required_keys: list[str],
) -> dict[str, Any]:
    missing = [key for key in required_keys if key not in observations]
    if missing:
        return {"state": "REJECTED", "missing": missing}

    if any(
        item.get("state") == "UNKNOWN"
        for item in observations.values()
    ):
        return {"state": "UNKNOWN", "missing": []}

    if any(
        item.get("state") == "ROLLED_BACK"
        for item in observations.values()
    ):
        return {"state": "ROLLED_BACK", "missing": []}

    if any(
        item.get("state") == "REJECTED"
        for item in observations.values()
    ):
        return {"state": "REJECTED", "missing": []}

    return {"state": "APPLIED", "missing": []}


def summarize_open_items(
    observations: dict[str, dict[str, Any]],
) -> list[str]:
    return [
        key
        for key, item in observations.items()
        if item.get("state") not in {"APPLIED", "ROLLED_BACK"}
    ]


def main() -> None:
    required = ["identity", "version", "service_health"]
    cases = {
        "applied": {
            "identity": {"state": "APPLIED"},
            "version": {"state": "APPLIED"},
            "service_health": {"state": "APPLIED"},
        },
        "rejected": {
            "identity": {"state": "APPLIED"},
            "version": {"state": "REJECTED"},
        },
        "unknown": {
            "identity": {"state": "APPLIED"},
            "version": {"state": "APPLIED"},
            "service_health": {"state": "UNKNOWN"},
        },
        "rolled_back": {
            "identity": {"state": "APPLIED"},
            "version": {"state": "ROLLED_BACK"},
            "service_health": {"state": "ROLLED_BACK"},
        },
    }

    for name, observations in cases.items():
        print(
            name,
            evaluate_handoff_gate(observations, required),
            summarize_open_items(observations),
        )


if __name__ == "__main__":
    main()
~~~

示例输出：

~~~text
applied {'state': 'APPLIED', 'missing': []} []
rejected {'state': 'REJECTED', 'missing': ['service_health']} ['version']
unknown {'state': 'UNKNOWN', 'missing': []} ['service_health']
rolled_back {'state': 'ROLLED_BACK', 'missing': []} []
~~~

这个实验有一个故意保守的顺序：缺少必需项先得到 REJECTED，未知状态优先于普通拒绝，回滚状态只有在没有未知项时才被识别。实际项目需要把规则写进契约并配套测试，不能仅凭示例函数决定真实设备的安全动作。

## 9. 综合运行手册

以下步骤适合用作一次受控运行的模板。每一步都要有负责人、停止条件和证据引用。

### 9.1 预检：确认范围和旧状态

- 创建 run_id，记录目标别名、App/config/unit/Bridge revision 和时间窗口；
- 确认执行者具有本次动作所需权限，且证据包不会收集秘密；
- 只读检查入口、服务、日志、资源、队列、缓存和回滚点；
- 发现目标不明、版本缺失、旧状态不可恢复或时间不可比时，标记 REJECTED 并停止。

### 9.2 暂存：让新旧版本可区分

- 把候选文件、配置和 unit 放在可识别的暂存位置；
- 计算或登记构建产物摘要、配置 revision 和 unit revision；
- 将配置 schema、文件权限、目录所有权和凭据引用分开检查；
- 不把秘密内容写入命令行、Git、日志、Markdown 或截图。

“新旧版本并存”不是为了长期保留所有副本，而是为了在健康门失败时仍然有已知回滚点。暂存清单不完整时，不应进入激活。

### 9.3 Dry-run：验证动作计划

- 列出将要创建、替换、启用、停止或重启的对象；
- 说明每个动作的预期输出和后置观察；
- 说明动作失败、超时或结果未知时的停止点；
- 用本地替身验证 manifest 和健康门规则；
- 由执行者和复核者确认计划，而不是用“命令没有报错”代替评审。

### 9.4 激活：一次改变一个变量

- 先进入变更窗口，停止无关的并发控制；
- 每次只改变 App、配置、unit 或协议中的一个变量；
- 记录动作开始和结束时间、命令类别、返回状态和请求关联；
- 立即进入只读健康观察，不要在健康未确认时继续下一次变更；
- 如果动作结果超时或连接中断，标记 UNKNOWN 并冻结。

### 9.5 健康门：观察服务、业务和 Bridge

健康观察至少包括三层：

1. **生命周期层**：进程、unit、退出码、重启次数和启动日志；
2. **业务层**：应用入口、队列、缓存 freshness、请求关联和错误率；
3. **硬件协同层**：Bridge/RPC 结果、MCU 侧状态机和必要的安全输出观察。

只有三层证据在同一个时间窗口、同一个 revision 和同一个目标范围内相互一致，才可以把综合运行标记为 APPLIED。服务层的 active 只能作为其中一个观察项。

### 9.6 未知处理：保留现场而不是追求绿色

- 停止新请求，保存关联 ID 和日志窗口；
- 确认是否存在重复动作、排队动作或已经改变的 MCU 状态；
- 不执行盲目重试，不清空队列，不删除旧日志；
- 根据幂等契约和对账结果决定恢复、回滚或人工裁决；
- 交接包中保留 UNKNOWN 的原始原因。

### 9.7 回滚：恢复旧状态并验证

回滚不是把旧目录切回去就结束。至少要确认：

- 旧 App、配置、unit 和 Bridge 契约是否互相兼容；
- 服务是否按预期启动并稳定；
- 队列没有继续接收新控制；
- 缓存和日志没有把新旧版本混在一起；
- MCU 或执行器已经回到明确的安全状态；
- 回滚验证的证据独立于触发回滚的错误日志。

验证完成后才使用 ROLLED_BACK。如果回滚命令执行了，但服务、Bridge 或硬件状态仍然无法确认，结果仍然是 UNKNOWN 或未决。

### 9.8 收尾：关闭变更而不是删除痕迹

- 记录最终 revision、状态、健康门结论和回滚结论；
- 标记仍需后续处理的日志、性能、权限和硬件项；
- 将证据包脱敏并按组织规定保存；
- 把交接包链接到第四篇、第五篇或第九篇的下一阶段；
- 不删除导致问题的原始证据，不用“清理完成”掩盖未验证项。

## 10. 故障处理矩阵

| 故障 | 可能位置 | 立即动作 | 结果状态 | 需要的证据 |
| --- | --- | --- | --- | --- |
| 目标身份缺失 | 范围/资产 | 停止，不建立受控连接 | REJECTED | 缺失字段和运行批次 |
| App 与配置 revision 不一致 | 发布身份 | 保持旧版本，重新核对清单 | REJECTED | 两个 revision 和清单摘要 |
| service 为 active 但业务不健康 | 应用/Bridge | 停止扩大范围，抓取业务层观察 | UNKNOWN 或 REJECTED | unit、日志、业务探针 |
| Bridge 请求超时 | Router/传输/MCU | 冻结同类请求，按关联 ID 对账 | UNKNOWN | 请求 ID、时间、最后状态 |
| 队列持续增长 | 背压/worker/外部依赖 | 停止接收新控制，保留队列统计 | REJECTED 或 UNKNOWN | 队列深度、年龄、丢弃策略 |
| 日志时间不可比 | 时钟/时区/采集 | 不比较跨源延迟，先修正时间证据 | REJECTED | 时间源、时区和 boot 标识 |
| 凭据出现在日志或参数中 | 安全边界 | 立即停止，按泄露流程处理 | REJECTED | 只保留脱敏事件，不复制秘密 |
| 回滚命令执行但状态未恢复 | 回滚/依赖 | 停止清理，人工接管并扩大观察 | UNKNOWN | 旧版本、回滚日志和健康门 |
| MCU 输出未进入安全状态 | MCU/Bridge/硬件 | 停止 Linux 侧控制，执行既定安全动作 | REJECTED 或 UNKNOWN | MCU 状态、请求关联和现场记录 |
| 证据包缺少版本或操作者 | 交接 | 不关闭批次，补齐责任和版本字段 | REJECTED | manifest 和补录记录 |

## 11. Linux 与 Python Bridge 综合验证矩阵

以下编号接续第 7 章的验证矩阵。矩阵记录的是验证规格，不是本环境已经完成的实机结果。

| 编号 | 验证层 | 验证问题 | 通过证据 | 当前边界 |
| --- | --- | --- | --- | --- |
| LNX-53 | 静态 | 第 8 章 front matter、标题和导航是否一致？ | 文件、元数据和 SUMMARY 检查 | 可在仓库内完成 |
| LNX-54 | 静态 | Fig-23 源文件与正文占位是否一致？ | Mermaid 源文件、锚点和图示索引 | 可在仓库内完成 |
| LNX-55 | 本地概念 | 运行记录是否拒绝空标识和非法状态？ | Python 示例输出和负向用例 | 不等于设备日志 |
| LNX-56 | 本地概念 | 交接门是否保留拒绝、未知和回滚？ | 四组固定输入的状态输出 | 不等于现场放行 |
| LNX-57 | Linux 只读 | 设备、网络、服务、日志和时间是否可对账？ | 脱敏命令输出和采集时间 | 需要目标 UNO Q |
| LNX-58 | Bridge 契约 | 请求状态是否能与 Router/Bridge 和 MCU 状态关联？ | 请求 ID、响应、MCU 观察 | 需要目标 UNO Q 和联调 |
| LNX-59 | 受控运行 | 单变量激活后健康门是否通过？ | 变更前后快照、健康门和独立观察 | 需要授权窗口 |
| LNX-60 | 回滚闭环 | UNKNOWN 或健康门失败后能否恢复并验证？ | 旧版本、回滚记录和恢复观察 | 需要现场部署和安全回滚演练 |

不要用 LNX-53～LNX-60 的“验证问题”替代真实证据。完成静态项后只能提高仓库层信心；LNX-57～LNX-60 仍必须在目标设备上执行。

## 12. 与后续篇章的交接

### 12.1 交给第四篇 Python Bridge

交接给第四篇时，至少应带出：

- Bridge/RPC 的方法名、参数约束和结果状态契约；
- 请求关联、幂等、超时和 UNKNOWN 处理规则；
- Linux 进程、队列、重连和证据字段的约束；
- 一个不含秘密的请求/响应样例；
- 尚未完成的连接、并发、性能和 MCU 联调项。

交接入口为[第四篇：Python Bridge](../第4篇_PythonBridge/README.md)。第三篇只提供运行和治理边界，不提前承担 Bridge 业务 API 的完整实现。

### 12.2 交给第五篇 App Lab

交接给第五篇时，至少应带出：

- App 的 Linux Python、Sketch、Brick 和容器边界；
- App revision、配置、启动项和运行日志的版本关系；
- Network Mode、USB/ADB、SSH 和 App Lab 入口的权限边界；
- App 运行前的预检、启动后健康门和停止/回滚策略；
- 不能把 App 出现在列表中、服务 active 或 Python 进程存活解释成硬件功能已经正确。

交接入口为[第五篇：App Lab](../第5篇_AppLab/README.md)。App Lab 的 App specification 说明 App 目录和 Linux/MCU 组件关系；具体工具版本、镜像行为和目标设备能力仍要在对应章节单独核验。

### 12.3 交给第九篇 Project

交接给第九篇时，应把本篇的运行批次、证据包、故障矩阵和回滚边界变成项目级验收条件：

- 需求中的每个控制动作都有结果状态；
- 现场部署有健康门和恢复路径；
- 性能预算、日志、资源和安全约束被写入项目验收；
- 真实设备验证和未决项不会被项目演示视频替代；
- 失败后仍然能够说明当前设备处于什么状态。

交接入口为[第九篇：Project](../第9篇_Project/README.md)。综合项目可以选择更高风险的硬件和网络场景，但不能因此降低状态、证据和回滚要求。

## 13. 本章验证结果

本章提交前需要完成以下仓库层检查：

- front matter 的 title、part、chapter、status、last_verified 和扩展字段存在；
- 第 8 章已加入 SUMMARY.md 和第三篇 README；
- Fig-23 在 Mermaid 源文件、正文锚点、占位说明和图片索引中唯一；
- 两个 Python 示例的代码说明字段完整，示例不调用网络、设备或外部命令；
- 第 6、7 章的链接和第四篇、第五篇、第九篇的交接入口可解析；
- UTF-8、关键标题、Git 空白和 Mermaid 源文本检查通过。

当前不能据此声称已经完成以下事项：

- Arduino CLI 编译、上传或 App Lab 运行；
- UNO Q Linux 设备、网络、服务和资源实机盘点；
- ADB、SSH、Network Mode 或 App Lab 入口验证；
- systemd unit 安装、启用、重启或安全分析；
- Python Bridge/Router 重连、远程写入、队列压力、性能压测或故障注入；
- MCU 联调、执行器安全状态和硬件闭环验证。

因此，本章的状态保持为 draft。后续若要提升为 review，应先补齐独立的链接/渲染检查和章节审稿；若要提升为 published，还需按照 LNX-57～LNX-60 补充目标设备证据。

## 14. 常见问题

### Q1：为什么第三篇还要增加综合运行章？前面的章节不是已经讲过这些内容了吗？

前面的章节按主题拆开讲了入口、队列、测试和部署；综合运行章解决的是跨主题的顺序和证据问题。它不再定义新的队列算法或 systemd 字段，而是规定什么时候观察、什么时候模拟、什么时候允许受控动作，以及结果如何交接。

### Q2：active 是否足以证明部署成功？

不足。active 通常只说明服务管理器认为进程处于运行状态。还需要业务层、Bridge 层、资源层和必要的 MCU 侧观察；任何一个层次缺失，都应降低结论强度。

### Q3：Dry-run 的输出能不能直接作为现场放行证据？

不能。Dry-run 能证明计划可以被解析、范围可以被计算或本地规则可以通过；它不能证明目标设备接受了动作，更不能证明执行器已经达到安全状态。

### Q4：结果 UNKNOWN 时为什么不直接重试？

因为未知的动作可能已经生效。重试前必须通过请求关联、目标状态、队列和 MCU 状态对账，证明重复动作是安全且幂等的；如果不能证明，就应保持冻结并人工裁决。

### Q5：能不能把完整 journal 或配置文件放进交接包？

通常不应直接放入 Git 仓库或普通交接渠道。日志和配置可能包含凭据、网络地址、设备标识和个人信息。仓库应保存脱敏摘要、时间窗口、版本和受控存储引用。

### Q6：本章的 Python 示例能否直接改成生产运行器？

不能直接改。示例缺少权限模型、并发控制、时钟策略、持久化、密钥管理、重试契约和现场回滚集成。它们的价值是把状态和证据规则变成可以被本地检查的最小函数。

### Q7：如果没有 UNO Q，第三篇是否就不能完成？

可以完成正文初稿、来源边界、静态检查和本地概念实验；不能完成目标设备层面的事实验证。学习材料应把“文档/代码完成”和“现场验证完成”分别记录，而不是为了显示完成度而越过证据边界。

### Q8：第 8 章完成后，是否可以直接开始第四篇？

可以开始第四篇的正文设计和 Bridge 业务实现，但应把本章列出的 LNX-57～LNX-60 作为持续未决项。后续篇章可以在替身环境中推进，同时保留真实设备验证的独立任务。

## 15. 本章小结

第三篇的核心不是记住更多 Linux 命令，而是建立一套可解释的运行方法：

1. 先锁定范围、身份、版本、时间窗口和回滚点；
2. 先做只读盘点，再做本地 Dry-run；
3. 一次只改变一个变量，并用独立观察判断结果；
4. 将服务、业务、Bridge、队列、资源和 MCU 状态分层记录；
5. 将 UNKNOWN 当作需要对账的状态，不自动重试；
6. 用脱敏证据包交接已确认事实、未决项和下一步；
7. 只有在回滚后的旧状态也得到独立验证时，才使用 ROLLED_BACK；
8. 把第三篇的治理边界交给第四篇、第五篇和第九篇，而不是把尚未验证的能力写成已完成事实。

至此，第三篇从 Linux 基础、设备与网络、可观测性、远程 Bridge、现场自动化、测试性能、部署治理走到了综合运行和篇末交接，形成第 1～8 章的完整正文初稿范围。

## 16. 延伸阅读与交叉引用

- [第三篇本篇导读](./README.md)
- [第三篇第 4 章：Linux 远程运维与 Python Bridge](./第4章_Linux远程运维与Python_Bridge_从安全命令到可验证请求.md)
- [第三篇第 5 章：Linux 现场自动化与 Python Bridge](./第5章_Linux现场自动化与Python_Bridge_队列重连与状态缓存.md)
- [第三篇第 6 章：Linux 与 Python Bridge 现场测试与性能治理](./第6章_Linux与Python_Bridge现场测试与性能治理_从基准压测到故障注入.md)
- [第三篇第 7 章：Linux 与 Python Bridge 现场部署与服务化治理](./第7章_Linux与Python_Bridge现场部署与服务化治理_从systemd配置分层到安全回滚.md)
- [第四篇：Python Bridge](../第4篇_PythonBridge/README.md)
- [第五篇：App Lab](../第5篇_AppLab/README.md)
- [第九篇：Project](../第9篇_Project/README.md)
- [参考资料索引](../../resources/references.md)
- [Arduino UNO Q User Manual](https://github.com/arduino/docs-content/blob/main/content/hardware/02.uno/boards/uno-q/tutorials/01.user-manual/content.md)
- [Arduino App specification](https://github.com/arduino/arduino-app-cli/blob/main/docs/app-specification.md)
- [systemd.service](https://github.com/systemd/systemd/blob/main/man/systemd.service.xml)
- [systemd.exec](https://github.com/systemd/systemd/blob/main/man/systemd.exec.xml)
- [Python json](https://docs.python.org/3/library/json.html)
- [Python asyncio tasks and timeouts](https://docs.python.org/3/library/asyncio-task.html)
- [Python subprocess](https://docs.python.org/3/library/subprocess.html)

本章使用的官方来源、适用版本和版权边界见[参考资料索引](../../resources/references.md)。链接用于事实核对和延伸阅读，本章不复制外部文档正文、配置、代码或图片。
