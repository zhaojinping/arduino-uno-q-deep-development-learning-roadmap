# 第三篇 Linux 收束章节 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox markers for tracking.

**Goal:** 新增第三篇第 8 章并同步所有导航、图示和验证记录，使第三篇形成完整的 Linux/Python Bridge 综合运行初稿。

**Architecture:** 以现有第 1～7 章为知识前置，不改写其编号和路径；新增第 8 章负责端到端运行闭环、证据交接和跨篇边界。图示源文件单独放在 diagrams/，正文只保留可追溯的 Mermaid/占位入口，项目导航和验证记录在同一变更中同步。

**Tech Stack:** UTF-8 Markdown、YAML front matter、Mermaid、Python 3 标准库概念实验、PowerShell 静态检查、Git。

**Spec:** docs/superpowers/specs/2026-09-22-linux-part3-completion-design.md

## Global Constraints

- 章节编号按篇重置；新章使用 part: 3、chapter: 8。
- 首次出现使用 Arduino UNO Q，后文使用 UNO Q；Python Bridge、systemd、ADB、SSH 保持原始大小写。
- 所有可运行代码块前后提供完整“代码说明”字段；示例只能写本地脱敏记录，不调用真实设备或远程写接口。
- Fig-23 在正文、Mermaid 源文件和 images/第3篇_Linux/README.md 中保持唯一且一致。
- 不修改前 7 章文件名和章节编号，不新增第四篇、第五篇或第九篇正文。
- 不把静态检查、概念脚本或官方文档语义写成 UNO Q 实机结果；现有硬件验证缺口必须保留。
- 远程 GitHub 推送需要用户单独授权；本计划最多产生本地提交。

---

### Task 1: 核对计划输入、来源和现有导航

**Files:**
- Read: docs/superpowers/specs/2026-09-22-linux-part3-completion-design.md
- Read: docs/writing-guidelines.md
- Read: book/第3篇_Linux/README.md
- Read: book/第3篇_Linux/第6章_Linux与Python_Bridge现场测试与性能治理_从基准压测到故障注入.md
- Read: book/第3篇_Linux/第7章_Linux与Python_Bridge现场部署与服务化治理_从systemd配置分层到安全回滚.md
- Read: resources/references.md

**Interfaces:**
- Consumes: 已确认的第三篇 1～7 章结构、术语规则和 Fig-22 登记。
- Produces: 第 8 章的事实边界、链接目标、示例状态值和不重复前置内容清单。

- [ ] **Step 1: 验证基线和工作区状态**

运行：

~~~powershell
git status --short --branch
git log --oneline -5
~~~

预期：当前分支为 main；除本次设计说明和计划外，不覆盖用户已有修改；最近提交仍为第三篇第 7 章部署治理提交。

- [ ] **Step 2: 检查已有来源是否覆盖第 8 章事实**

运行：

~~~powershell
rg -n "Arduino UNO Q User Manual|Arduino App specification|Arduino Router|systemd.service|systemd.exec|Python subprocess|Python json|Python asyncio" resources/references.md
~~~

预期：复用已有官方来源；没有必要的新来源不重复登记，新增来源必须先写入资源索引再进入正文。

- [ ] **Step 3: 固定第 8 章不重复边界**

把第 6 章的“性能基线/故障注入”、第 7 章的“systemd/配置/发布回滚”作为前置链接；第 8 章只负责把它们编排成运行批次、健康门、证据包和交接结果，不再重新定义指标或 unit 语义。

验证：用 Select-String 检查第 6、7 章的关键标题，并把对应相对链接写入第 8 章的“前置阅读”段落。

### Task 2: 撰写第三篇第 8 章

**Files:**
- Create: book/第3篇_Linux/第8章_Linux与Python_Bridge综合运行手册_从预检到交接.md

**Interfaces:**
- Consumes: Task 1 的前置章节、官方来源和验证边界。
- Produces: 一篇具有完整 front matter、18 个固定内容段、两个本地 Python 概念实验、Fig-23 引用和跨篇交接入口的 Markdown 正文。

- [ ] **Step 1: 写入 front matter 和学习目标**

使用以下元数据：

~~~yaml
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
~~~

学习目标必须明确：读者能够定义一次运行批次、区分观察/模拟/受控动作、处理 UNKNOWN、生成脱敏证据包，并将结果交接到后续篇章。

- [ ] **Step 2: 写入概念、流程和安全边界**

按以下顺序完成正文：

1. 背景与边界：说明综合运行不是“执行更多命令”，而是用状态、授权、健康门和证据把多层系统串起来；明确本章不执行真实设备操作。
2. 对象、状态和证据等级：定义运行批次、目标、动作、观察项、健康门和交接包；至少区分 OBSERVED、SIMULATED、APPLIED、REJECTED、UNKNOWN、ROLLED_BACK。
3. 预检与只读盘点：把范围、设备身份、时间窗口、版本、网络、服务、Bridge 入口和回滚点列成只读清单；任何缺失身份或版本的项停止进入受控阶段。
4. Dry-run 与受控运行：要求一次只改变一个变量，先记录预期，再记录实际，再评估健康门；禁止以进程存活替代业务成功。
5. 健康门、故障分级和 UNKNOWN：为“可继续、可回滚、必须人工裁决”建立矩阵；未知写入结果不得自动重试。
6. 证据包与交接：规定 run_id、时间、目标、版本、动作摘要、结果状态、日志引用、回滚结论和未决项字段；示例数据全部使用脱敏占位值。

- [ ] **Step 3: 写入 Fig-23 说明和 Mermaid 内嵌入口**

正文包含图示说明、唯一占位：

~~~text
> 图示占位：图号=Fig-23；位置=本段之后；内容=Linux、Python Bridge、服务治理、健康门、证据归档与跨篇交接的综合运行闭环；来源=见 ../../diagrams/uno-q-linux-operational-handoff.mmd。
~~~

正文用一段文字解释成功路径和 UNKNOWN/回滚路径，不能只依赖图形。

- [ ] **Step 4: 写入两个本地 Python 概念实验**

实验一实现以下纯标准库函数并输出 JSONL，不调用网络或设备：

~~~python
def new_run_record(run_id, target, version, mode):
    return {
        "run_id": run_id,
        "target": target,
        "version": version,
        "mode": mode,
        "events": [],
    }

def append_event(record, event, state, evidence):
    record["events"].append({"event": event, "state": state, "evidence": evidence})
    return record

def render_evidence_manifest(record):
    return {"run_id": record["run_id"], "target": record["target"], "events": record["events"]}
~~~

实验二实现以下纯函数并覆盖成功、拒绝、未知和回滚四种结果：

~~~python
def evaluate_handoff_gate(observations, required_keys):
    missing = [key for key in required_keys if key not in observations]
    if missing:
        return {"state": "REJECTED", "missing": missing}
    if any(item.get("state") == "UNKNOWN" for item in observations.values()):
        return {"state": "UNKNOWN", "missing": []}
    return {"state": "APPLIED", "missing": []}

def summarize_open_items(observations):
    return [key for key, item in observations.items() if item.get("state") != "APPLIED"]
~~~

代码说明必须逐项填写用途、运行环境、文件位置、依赖、操作步骤、预期输出、故障排查和验证方式；预期输出标为“示例输出”，并写明本次未实测。

- [ ] **Step 5: 写入运行手册、矩阵、常见问题和交接**

运行手册至少包含预检、暂存、Dry-run、健康门、受控动作、收尾、回滚、证据归档八步；故障矩阵至少覆盖身份缺失、版本不一致、服务 active 但业务不健康、Bridge 超时、写入结果未知、日志时间不可比、回滚后仍未恢复；交接章节分别链接第三篇第 4～8 章、第四篇本篇入口、第五篇本篇入口和第九篇本篇入口。

本章验证结果必须区分“正文/链接/代码静态检查通过”和“UNO Q 实机、systemd、Bridge、MCU 联调尚未执行”。

### Task 3: 创建 Fig-23 并同步导航与索引

**Files:**
- Create: diagrams/uno-q-linux-operational-handoff.mmd
- Modify: SUMMARY.md
- Modify: book/第3篇_Linux/README.md
- Modify: README.md
- Modify: images/第3篇_Linux/README.md

**Interfaces:**
- Consumes: Task 2 的文件名、章节标题、状态名和 Fig-23 图示说明。
- Produces: 可从根目录导航到第 8 章、从第三篇 README 导航到完整章节地图、从图示索引追溯到 Mermaid 源文件的统一入口。

- [ ] **Step 1: 创建 Mermaid 源文件**

源文件使用 flowchart LR，至少包含以下节点和路径：

~~~text
范围确认 -> 只读盘点 -> Dry-run -> 健康门
健康门 -- 通过 --> 受控运行 -> 证据归档 -> 交接
健康门 -- 拒绝 --> 停止并保留证据
受控运行 -- UNKNOWN --> 人工裁决
人工裁决 -- 回滚 --> 回滚验证 -> 证据归档
~~~

使用虚线关系表示交接目标：第四篇 Python Bridge、第五篇 App Lab、第九篇 Project；图中不表示物理连接或已完成实机部署。

- [ ] **Step 2: 更新第三篇 README 和 SUMMARY**

在第 7 章之后追加第 8 章链接和摘要；删除“后续章节按第 8 章继续编号”的未完成提示，改为“第 1～8 章正文初稿范围完成，状态仍为 draft”；在 SUMMARY.md 的第三篇末尾追加同一相对路径。

- [ ] **Step 3: 更新根 README 和图片索引**

根 README 将第三篇进度从“第 1～7 章初稿”改为“第 1～8 章初稿”，在全书路线中补充综合运行/交接作用，并在验证记录中加入第 8 章、Fig-23 和“未进行实机/现场验证”的说明。图片索引登记 Fig-23、源文件相对路径、当前为 Mermaid 源文件/正文占位和来源状态。

### Task 4: 静态验证并准备本地交付

**Files:**
- Verify: all files changed by Tasks 1–3
- Modify: none unless a verification failure identifies a concrete correction

**Interfaces:**
- Consumes: 完整第三篇第 8 章、Fig-23、导航和索引。
- Produces: 可复查的验证输出、无未登记链接/图号/元数据错误的工作树，以及可选的本地 Git 提交。

- [ ] **Step 1: 检查文件存在、元数据和关键标题**

运行以下 PowerShell 检查：

~~~powershell
$chapter = 'book/第3篇_Linux/第8章_Linux与Python_Bridge综合运行手册_从预检到交接.md'
Test-Path -LiteralPath $chapter
Get-Content -LiteralPath $chapter -Encoding UTF8 -TotalCount 14
Select-String -LiteralPath $chapter -Pattern '^## (学习目标|背景与边界|.*本章小结|延伸阅读与交叉引用)$'
~~~

预期：文件存在，front matter 字段齐全，固定入口标题存在。

- [ ] **Step 2: 检查链接、图号和章节编号**

运行：

~~~powershell
rg -n "第8章_Linux与Python_Bridge综合运行手册_从预检到交接|Fig-23|chapter: 8|part: 3" SUMMARY.md README.md book/第3篇_Linux images/第3篇_Linux diagrams
rg -n "第 8 章|第8章" book/第3篇_Linux/README.md SUMMARY.md
~~~

预期：第 8 章路径、标题、part/chapter 和 Fig-23 都能在应有文件中找到，且没有旧的“后续章节”提示。

- [ ] **Step 3: 检查代码说明、Mermaid 和文本质量**

运行：

~~~powershell
rg -n "代码说明|用途：|运行环境：|文件位置：|依赖：|操作步骤：|预期输出：|故障排查：|验证方式：" book/第3篇_Linux/第8章_Linux与Python_Bridge综合运行手册_从预检到交接.md
Get-Content -Raw -LiteralPath 'diagrams/uno-q-linux-operational-handoff.mmd' -Encoding UTF8
git diff --check
~~~

预期：两个实验均有完整字段，Mermaid 以 flowchart LR 开始，Git 空白检查无输出。

- [ ] **Step 4: 尝试 Mermaid 渲染并记录边界**

运行：

~~~powershell
Get-Command mmdc -ErrorAction SilentlyContinue
~~~

如果找到 mmdc，再渲染 Fig-23 并检查生成文件；如果未找到，只报告“渲染器未安装，已完成源文件静态检查”，不生成伪造 SVG。

- [ ] **Step 5: 检查 Git 差异并准备提交**

运行：

~~~powershell
git status --short
git diff --stat
git diff -- SUMMARY.md 'book/第3篇_Linux/README.md' README.md 'images/第3篇_Linux/README.md'
~~~

确认变更只包含设计说明、执行计划、第 8 章、Fig-23 和明确的导航/索引更新后，再创建本地提交；远程推送等待用户单独授权。
