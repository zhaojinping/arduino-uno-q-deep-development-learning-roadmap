# 第四篇 Python Bridge 第 1 章 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox markers for tracking.

**Goal:** 新增第四篇第 1 章，建立 Python Bridge 的消息模型、调用边界、超时/幂等规则和可验证的本地概念实验。

**Architecture:** 以第三篇第 8 章的运行治理和交接边界为前置，新增第四篇第 1 章作为 Bridge 业务编程入口。正文、Fig-24 Mermaid 源文件、第四篇图示索引和全书导航在同一变更中保持一致；概念实验只在本地内存中运行，不触碰 UNO Q 或真实 RPC。

**Tech Stack:** UTF-8 Markdown、YAML front matter、Mermaid sequenceDiagram、Python 3.10+ 标准库、PowerShell 静态检查、Git。

**Spec:** docs/superpowers/specs/2026-09-22-python-bridge-chapter1-design.md

## Global Constraints

- 第四篇第一章使用 part: 4、chapter: 1；不得沿用第三篇第 8 章编号。
- 首次出现使用 Arduino UNO Q，后文使用 UNO Q；Python Bridge、Router、Bridge/RPC、MCU Sketch 和 App Lab 保持统一写法。
- 所有可运行 Python 示例都提供完整代码说明字段，并明确为本地 SIMULATED 输出。
- Fig-24 只表达逻辑消息生命周期，不表示物理连线、线程时序保证或实机结果。
- 不修改第三篇既有正文；不新增第四篇第 2 章及以后章节。
- 外部来源只能引用已登记的 Arduino UNO Q User Manual、Arduino App specification、Arduino Router 和 Python 标准库文档。
- 不安装第三方 Python 包，不保存真实凭据、IP、设备序列号或生产配置。
- 新内容先本地验证和提交；远程推送等待用户单独授权。

---

### Task 1: 核对第四篇入口和来源基线

**Files:**
- Read: docs/superpowers/specs/2026-09-22-python-bridge-chapter1-design.md
- Read: docs/writing-guidelines.md
- Read: book/第3篇_Linux/第8章_Linux与Python_Bridge综合运行手册_从预检到交接.md
- Read: book/第4篇_PythonBridge/README.md
- Read: resources/references.md
- Read: SUMMARY.md
- Read: README.md

**Interfaces:**
- Consumes: 已确认的第四篇设计说明、第三篇交接边界和已有官方来源。
- Produces: 第四篇第 1 章的链接目标、术语表、Fig-24 登记位置和不重复内容边界。

- [ ] **Step 1: 验证工作区和分支**

运行：

~~~powershell
git status --short --branch
git log --oneline -3
~~~

预期：当前分支为 main；上一个提交是第三篇收束提交；除本轮设计说明和计划外没有未授权修改。

- [ ] **Step 2: 确认已登记来源**

运行：

~~~powershell
rg -n "Arduino UNO Q User Manual|Arduino App specification|Arduino Router|Python json|Python asyncio|Python subprocess" resources/references.md
~~~

预期：所有计划使用的外部来源均已有登记；不在正文直接引入未登记网址。

- [ ] **Step 3: 固定与第三篇的交接边界**

第 8 章只作为前置阅读，第四篇第 1 章负责消息和调用契约；不要重复第三篇关于 Linux 入口、systemd、队列治理、部署回滚和现场运行手册的长篇解释。新增章节必须链接第三篇第 8 章和第三篇第 4 章，而不是重新复制内容。

### Task 2: 撰写第四篇第 1 章正文

**Files:**
- Create: book/第4篇_PythonBridge/第1章_Python_Bridge开发基础_消息模型与调用边界.md

**Interfaces:**
- Consumes: Task 1 的术语、来源和第三篇交接边界。
- Produces: 一篇包含完整 front matter、17 个正文入口、Fig-24、两个 Python 概念实验、验证矩阵和跨篇交接的初稿。

- [ ] **Step 1: 写入 front matter 和章节入口**

使用：

~~~yaml
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
~~~

正文顺序必须包含：学习目标、背景与边界、双侧应用职责、Fig-24、消息信封、调用边界、超时幂等 UNKNOWN、两个实验、运行手册、故障矩阵、验证矩阵、交接、验证结果、常见问题、小结和延伸阅读。

- [ ] **Step 2: 解释职责模型和消息状态**

正文必须明确：

1. Python App 负责 Linux 侧业务编排、输入校验、请求关联和结果归档。
2. Router 负责消息传输基础，不等同于业务成功。
3. Bridge/RPC 负责逻辑调用和结果返回；请求需要有 request_id、方法名、参数摘要、deadline 和契约版本。
4. MCU Sketch 负责硬件和实时边界；Linux 侧不能绕过 MCU 的安全状态机直接假设输出已生效。
5. call 等待结果，notify 不以响应作为完成证明，provide 暴露 MCU 能力；具体行为必须以目标版本和官方文档为准。
6. APPLIED、REJECTED、UNKNOWN、ROLLED_BACK 的含义与第三篇保持一致。

- [ ] **Step 3: 写入 Fig-24 和调用安全边界**

正文包含显式锚点和占位：

~~~text
> 图示占位：图号=Fig-24；位置=本段之后；内容=Python App、Router/Bridge、MCU Sketch 从请求创建到响应、拒绝、超时和证据归档的消息生命周期；来源=见 ../../diagrams/uno-q-python-bridge-message-lifecycle.mmd。
~~~

必须说明：消息到达不代表 MCU 接受，响应到达不代表执行器安全状态已经确认；超时进入 UNKNOWN，非幂等操作不得盲目重试。

- [ ] **Step 4: 实现第一个本地 Python 概念实验**

实验实现并实际运行以下函数：

~~~python
def build_request(request_id, method, args, deadline_ms):
    if not request_id or not method or deadline_ms <= 0:
        raise ValueError("invalid request envelope")
    return {
        "request_id": request_id,
        "method": method,
        "args": args,
        "deadline_ms": deadline_ms,
        "contract": "bridge-v1",
    }

def classify_response(response, expected_request_id):
    if response.get("request_id") != expected_request_id:
        return {"state": "UNKNOWN", "reason": "request_id_mismatch"}
    if response.get("state") in {"APPLIED", "REJECTED", "UNKNOWN"}:
        return {"state": response["state"], "reason": response.get("reason", "")}
    return {"state": "UNKNOWN", "reason": "unsupported_response_state"}

def redact_request(request):
    safe = dict(request)
    safe["args"] = "[REDACTED]"
    return safe
~~~

实验覆盖有效请求、空 request_id、响应关联错误、APPLIED、REJECTED、UNKNOWN 和参数脱敏；不得调用 Router、网络或设备。

- [ ] **Step 5: 实现第二个本地 Python 概念实验**

实验实现并实际运行以下函数：

~~~python
def decide_retry(state, idempotent, attempts, max_attempts):
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

def summarize_unknown(request_id, reason, last_observation):
    return {
        "request_id": request_id,
        "state": "UNKNOWN",
        "reason": reason,
        "last_observation": last_observation,
        "next_action": "reconcile_or_human_decision",
    }
~~~

实验覆盖已应用、明确拒绝、幂等 UNKNOWN、非幂等 UNKNOWN、达到最大次数和人工裁决；示例输出标明 SIMULATED，不得写成真实 Bridge 结果。

### Task 3: 创建 Fig-24 并同步第四篇导航

**Files:**
- Create: diagrams/uno-q-python-bridge-message-lifecycle.mmd
- Create: images/第4篇_PythonBridge/README.md
- Modify: book/第4篇_PythonBridge/README.md
- Modify: SUMMARY.md
- Modify: README.md

**Interfaces:**
- Consumes: Task 2 的章节标题、文件名、Fig-24 锚点和消息状态。
- Produces: 第四篇第 1 章可从 SUMMARY、第四篇 README 和根 README 导航，Fig-24 可从图片索引追溯到源文件。

- [ ] **Step 1: 创建 Mermaid sequenceDiagram**

源文件至少表达：

~~~text
participant P as Python App
participant R as Router
participant B as Bridge/RPC
participant M as MCU Sketch
P->>R: request_id + method + args
R->>B: route message
B->>M: invoke
M-->>B: APPLIED or REJECTED
B-->>R: correlated response
R-->>P: result + evidence
P-->>P: UNKNOWN on timeout or mismatch
~~~

加入超时/拒绝/未知路径，且不要画成物理连接图。

- [ ] **Step 2: 更新第四篇 README 和图片索引**

第四篇 README 增加第 1 章链接、学习目标和“第 1 章初稿已建立”的状态；图片索引登记 Fig-24、源文件、正文锚点、占位状态和来源边界。

- [ ] **Step 3: 更新 SUMMARY 和根 README**

在 SUMMARY 第四篇范围入口后追加第 1 章；根 README 将第四篇状态从“范围入口已建立”改为“第 1 章初稿已建立”，并在文件清单、Mermaid 清单、图片目录和验证记录中加入第四篇第 1 章及 Fig-24。

### Task 4: 静态验证并准备本地提交

**Files:**
- Verify: all files changed by Tasks 1–3
- Modify: none unless a concrete verification failure identifies a correction

**Interfaces:**
- Consumes: 第四篇第 1 章、Fig-24、第四篇 README、图片索引和导航。
- Produces: 通过检查的本地变更和一个可回溯的本地提交。

- [ ] **Step 1: 验证 front matter、标题和代码说明**

运行：

~~~powershell
$chapter = 'book/第4篇_PythonBridge/第1章_Python_Bridge开发基础_消息模型与调用边界.md'
Get-Content -LiteralPath $chapter -Encoding UTF8 -TotalCount 14
Select-String -LiteralPath $chapter -Pattern 'part: 4|chapter: 1|status: draft|last_verified: 2026-09-22'
~~~

预期：元数据完整，章节编号为第四篇第 1 章；两个 Python 实验各有完整代码说明字段。

- [ ] **Step 2: 执行两个 Python 代码块并检查 Mermaid 对齐**

使用 Python 从 Markdown 中提取两个 python 围栏，compile 后执行 main；提取 mermaid 围栏并与 diagrams/uno-q-python-bridge-message-lifecycle.mmd 逐字比较。预期两个实验输出 APPLIED、REJECTED、UNKNOWN 和重试决策，Mermaid 对齐通过。

- [ ] **Step 3: 检查内部链接、图号和编码**

运行：

~~~powershell
rg -n "第1章_Python_Bridge开发基础_消息模型与调用边界|Fig-24|part: 4|chapter: 1" SUMMARY.md README.md book/第4篇_PythonBridge images/第4篇_PythonBridge diagrams
git diff --check
~~~

预期：所有入口和图号都存在；没有第三篇旧编号；UTF-8 读取正常；Git 空白检查无输出。

- [ ] **Step 4: 检查 Mermaid 渲染器和仓库状态**

运行：

~~~powershell
Get-Command mmdc -ErrorAction SilentlyContinue
git status --short --branch
git diff --stat
~~~

如果 mmdc 不存在，只保留 Mermaid 源文件并记录未生成 SVG；确认变更只包含本设计说明、执行计划、第 1 章、Fig-24 和导航/索引文件。

- [ ] **Step 5: 创建本地提交**

验证通过后运行：

~~~powershell
git add -- 'README.md' 'SUMMARY.md' 'book/第4篇_PythonBridge/README.md' 'book/第4篇_PythonBridge/第1章_Python_Bridge开发基础_消息模型与调用边界.md' 'images/第4篇_PythonBridge/README.md' 'diagrams/uno-q-python-bridge-message-lifecycle.mmd' 'docs/superpowers/specs/2026-09-22-python-bridge-chapter1-design.md' 'docs/superpowers/plans/2026-09-22-python-bridge-chapter1-plan.md'
git commit -m "docs: add Python Bridge foundations chapter"
~~~

远程推送不在本计划内，等待用户单独授权。
