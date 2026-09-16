# Arduino UNO Q 第 2 章 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在已有书稿基础上新增可独立阅读的第 2 章“什么是 Arduino UNO Q”，用官方资料解释 UNO Q 的产品定位、双处理器责任域和协同入口，并把章节纳入全书维护路径。

**Architecture:** 章节正文只负责概念模型、任务分配和学习边界；Mermaid 源文件单独保存并在正文内以内联图示呈现。导航、图示登记、来源登记和项目进度分别由索引文件维护，避免把正文、资源元数据和临时验证混在一起。

**Tech Stack:** Markdown、Mermaid、PowerShell、Git；本轮不引入构建工具、运行时依赖或硬件上传流程。

**Spec:** `docs/superpowers/specs/2026-09-15-arduino-uno-q-book-design.md`，并以用户在 2026-09-16 明确提出的“继续在仓库上更新后续章节”作为对原首期范围的迭代扩展。

## Global Constraints

- 项目根目录固定为 `Arduino UNO Q 深度开发学习路线/`。
- UNO Q 的事实优先回到 Arduino 官方文档核验；社区仓库只作为案例和结构参考。
- 正文、原创图示与外部材料严格分开，不复制外部教程的大段文字、图片或章节结构。
- 第一次出现使用产品全称 **Arduino UNO Q**；后文可简称 **UNO Q**，不要写成 “UNOQ” 或混用其他大小写；目录标识 `第1篇_认识UNOQ` 是固定路径例外。
- 每章正文开头必须包含 `title`、`part`、`chapter`、`status`、`last_verified` 五个 YAML 字段；本章日期使用 `2026-09-16`。
- 正文必须依次覆盖学习目标、背景与边界、操作或实验、验证结果、常见问题和延伸阅读；没有适用内容时明确写“无”。
- Mermaid 源码使用 `flowchart` 等显式图类型声明；正文中的每张图必须有唯一图号占位说明，且源文件可追溯。
- 外部材料先登记到 `resources/references.md`，正文只使用可识别的来源名称或资源编号并保留许可边界。
- 仓库内引用使用相对路径和描述性链接文本；不制造目标尚未创建的失效章节链接。
- 无法连接硬件或工具未安装时，只报告静态检查或待硬件验证，不把静态检查描述成运行成功。

---

## 文件结构与职责

- `book/第1篇_认识UNOQ/第2章_什么是Arduino_UNO_Q.md`：第 2 章的出版正文、概念图、任务分类练习、验证边界和来源说明。
- `diagrams/uno-q-execution-boundary.mmd`：第 2 章“按任务选择执行侧”的可复用 Mermaid 源文件。
- `SUMMARY.md`：把已经存在的第 2 章追加到第一篇的第 1 章之后。
- `book/第1篇_认识UNOQ/README.md`：把“UNO Q 定位”预留主题更新为第 2 章正式入口，其余未创建主题继续保持预留说明。
- `images/第1篇_认识UNOQ/README.md`：登记 Fig-03 的占位说明、目标文件和原创重绘边界。
- `resources/references.md`：登记本章新增使用的官方产品页和数据表，并保留已有官方手册、核心仓库记录。
- `README.md`：只更新当前进度和已核验文件清单，不改项目定位或版权边界。
- `docs/superpowers/plans/2026-09-16-arduino-uno-q-chapter-2.md`：本轮长期维护计划和审阅依据。

### Task 1: 撰写第 2 章与执行边界图

**Files:**
- Create: `book/第1篇_认识UNOQ/第2章_什么是Arduino_UNO_Q.md`
- Create: `diagrams/uno-q-execution-boundary.mmd`

**Interfaces:**
- Consumes: 现有第 1 章、`docs/writing-guidelines.md`、`resources/references.md`，以及 Arduino 官方 UNO Q 产品页、User Manual、数据表和 ArduinoCore-zephyr 板卡定义。
- Produces: 可被 `SUMMARY.md` 和第一篇 README 链接的第 2 章文件，以及可被正文和未来硬件/软件章节复用的任务分配图源。

- [ ] **Step 1: 写入章节元数据和固定入口**

使用以下元数据，并把标题、章节号和路径保持一致：

```yaml
---
title: 什么是 Arduino UNO Q
part: 1
chapter: 2
status: draft
last_verified: 2026-09-16
---
```

正文一级标题为 `# 第2章 什么是 Arduino UNO Q`，术语第一次出现时解释微处理器（Microprocessor，MPU）、微控制器（Microcontroller，MCU）、远程过程调用（Remote Procedure Call，RPC）和实时操作系统（Real-Time Operating System，RTOS）。

- [ ] **Step 2: 撰写概念主线和章节边界**

按下列顺序写入二级标题，正文使用独立改写，不复制外部页面原句：

```markdown
## 学习目标
## 本章导读
## 背景与边界
## 1. 先建立正确的产品模型
## 2. UNO Q 的双处理器组成
## 3. 两个运行时与两个责任域
## 4. Bridge/RPC：跨处理器的协同边界
## 5. 开发工具如何对应责任域
## 6. 任务应该放在哪里执行
## 7. 纸面实验：给任务选择执行侧
## 操作或实验
## 验证结果
## 常见问题
## 本章小结
## 交叉引用与延伸阅读
## 来源与验证
```

正文至少说明：UNO Q 把 Qualcomm Dragonwing QRB2210 MPU 与 STM32U585 MCU 放在同一开发板上；MPU 运行 Debian Linux，MCU 侧的 Arduino Sketch 运行在 Zephyr 基础上；Bridge/RPC 是两侧交换服务调用、响应和通知的边界；Arduino IDE 主要用于 MCU 侧，App Lab 面向两侧协同，具体工具行为以官方资料为准。明确这是一种职责分工模型，不是把所有任务永久绑定到单一处理器。

本章只做产品定位和决策模型，不展开 STM32 外设 API、Debian 运维、Python Bridge 实现、App Lab 项目文件、OpenCV 或 AI 模型；这些内容链接到已经存在的篇入口作为后续路线，不创建未完成章节链接。

- [ ] **Step 3: 写入 Mermaid 源文件和正文图示**

将以下结构写入 `diagrams/uno-q-execution-boundary.mmd`，并在第 6 节后以内联 Mermaid 代码块呈现同一关系：

~~~mermaid
flowchart TB
    START[任务需求] --> TIMING{是否需要确定性时序或直接 I/O?}
    TIMING -->|是| MCU[MCU\nSTM32U585\nZephyr + Arduino Sketch]
    TIMING -->|否| LINUX{是否依赖 Linux、网络、文件或模型?}
    LINUX -->|是| MPU[MPU\nQualcomm QRB2210\nDebian Linux]
    LINUX -->|否| HYBRID{是否同时需要实时控制与高层计算?}
    HYBRID -->|是| BOTH[MPU + MCU\n通过 Arduino Bridge / RPC]
    HYBRID -->|否| CHOOSE[按数据来源、延迟和维护边界选择]
    MCU --> BOTH
    MPU --> BOTH
~~~

图下解释：这是学习用的决策启发式，不能代替具体硬件、电气和软件接口核验。正文在图后加入单行占位：`图号=Fig-03`、位置、读者要看到的关系和“基于官方资料原创重绘”的来源边界。

- [ ] **Step 4: 写入纸面实验、验证结果和常见问题**

纸面实验给出至少 6 个任务分类案例（例如读取按钮、周期采样、网页服务、文件处理、模型推理、按策略驱动执行器），每项标注首选执行侧和理由，并提供一项“需要两侧协同”的组合题。明确本实验不要求硬件或 CLI，验证方式是读者能解释选择依据；验证结果区分“本次静态检查”和“尚未完成的硬件/CLI 验证”。常见问题至少回答：UNO Q 是否只是更快的 UNO、Linux 是否取代 MCU、Arduino IDE 是否等于完整双侧开发、Bridge 是否等同于普通串口，以及为什么不能仅凭 Blink 证明 Linux 侧已运行。

- [ ] **Step 5: 建立正文交叉引用和来源区**

从本章链接到已存在的 `../第2篇_STM32/README.md`、`../第3篇_Linux/README.md`、`../第4篇_PythonBridge/README.md`、`../第5篇_AppLab/README.md`、上一章 `./第1章_Arduino的发展.md` 和 `../../resources/references.md`。来源区写明核验日期、官方资料用途、静态/实机验证边界和不取得外部材料再分发许可的声明。

- [ ] **Step 6: 静态检查章节本身**

运行以下检查并在实现报告中记录实际输出：

```powershell
$chapter = Get-Content 'book\第1篇_认识UNOQ\第2章_什么是Arduino_UNO_Q.md' -Raw
$required = @('title: 什么是 Arduino UNO Q','part: 1','chapter: 2','status: draft','last_verified: 2026-09-16','## 学习目标','## 验证结果','## 常见问题','## 交叉引用与延伸阅读','## 来源与验证','Fig-03','```mermaid')
$missing = $required | Where-Object { $chapter -notmatch [regex]::Escape($_) }
if ($missing) { throw "Missing chapter requirements: $($missing -join ', ')" }
$diagram = Get-Content 'diagrams\uno-q-execution-boundary.mmd' -Raw
if ($diagram -notmatch '^flowchart TB') { throw 'Mermaid flowchart declaration missing' }
```

### Task 2: 同步导航、图示登记、参考资料和进度

**Files:**
- Modify: `SUMMARY.md`
- Modify: `book/第1篇_认识UNOQ/README.md`
- Modify: `images/第1篇_认识UNOQ/README.md`
- Modify: `resources/references.md`
- Modify: `README.md`

**Interfaces:**
- Consumes: Task 1 已创建且通过静态检查的第 2 章和 Mermaid 源文件。
- Produces: 无失效本地入口的第一篇导航、唯一的 Fig-03 登记、完整的官方来源记录和与实际仓库内容相符的项目进度。

- [ ] **Step 1: 追加 SUMMARY 和第一篇阅读顺序**

在第 1 章链接之后追加：

```markdown
- [第2章 什么是 Arduino UNO Q](book/第1篇_认识UNOQ/第2章_什么是Arduino_UNO_Q.md)
```

把第一篇 README 的“UNO Q 定位——”预留说明替换为指向第 2 章的描述；硬件架构、软件架构和第一个实验仍保留为未创建正文的主题说明。

- [ ] **Step 2: 登记 Fig-03**

在 `images/第1篇_认识UNOQ/README.md` 添加“图 1-3：UNO Q 任务执行侧决策图”，目标文件为 `ch02-fig03-uno-q-execution-boundary.svg`，状态为“占位说明”，内容要求覆盖任务需求到 MCU、MPU 或双侧协同的分流，来源边界为“基于官方资料原创重绘；不直接复制外部图片”。图号不得与现有 Fig-01、Fig-02 冲突。

- [ ] **Step 3: 登记新增官方来源**

把下列两条加入 `resources/references.md`，最后核验日期均为 `2026-09-16`，并写明本项目仅链接/原创重述，不取得外部材料再分发许可：

```text
Arduino UNO Q 产品页 | https://docs.arduino.cc/hardware/uno-q | 核对产品定位、双处理器和 IDE/App Lab 分工 | 官方网页，按页面声明使用 | 2026-09-16
Arduino UNO Q 数据表 | https://docs.arduino.cc/resources/datasheets/ABX00162-datasheet.pdf | 核对 Bridge/RPC 的服务调用、响应和通知边界 | 官方数据表，按页面声明使用 | 2026-09-16
```

- [ ] **Step 4: 更新项目进度**

在根 README 的“当前进度”和已创建文件清单中加入第 2 章与 `diagrams/uno-q-execution-boundary.mmd`，把首期表述改为“第一篇持续写作中”。保留“未完成 Arduino CLI 编译、上传或硬件实机运行”的真实限制。

- [ ] **Step 5: 验证全部本地入口**

使用 PowerShell 解析 `SUMMARY.md`、第一篇 README、第 2 章和图示登记中的相对 Markdown 链接，以各文件所在目录为基准运行 `Test-Path`；检查结果必须为 0 个缺失目标。另检查所有 Markdown 文件为 UTF-8，且本轮项目文件中的 Fig-03 只出现在第 2 章正文和对应图示登记中（计划文档中的验收描述不计入图示登记）。

## 本轮完成条件

- 第 2 章正文、Mermaid 源文件和入口同步存在于当前 Git 分支。
- 章节元数据、固定标题、术语边界、图号、外部来源和相对链接通过静态检查。
- 没有把未执行的 CLI 编译、上传或硬件运行写成成功结果。
- 变更经过每个任务的独立审阅和一次整分支审阅后，再由当前任务提交并推送到已授权的 GitHub `main` 分支。
