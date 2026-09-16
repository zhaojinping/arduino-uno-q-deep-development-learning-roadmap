# Arduino UNO Q 深度开发学习路线首期基础工程实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (- [ ]) syntax for tracking.

**Goal:** 在本地建立可持续维护的 Arduino UNO Q 中文 Markdown 书籍仓库，完成首期目录、第一篇入口、第 1 章正文、Blink 代码示例、Mermaid 图示和参考资料索引。

**Architecture:** 采用“正文、代码、图示、图片、资源和项目文档分离”的静态 Markdown 结构。正文以篇和章组织，代码按章节归档，Mermaid 源文件集中在 diagrams/，所有事实来源和版本信息登记在 resources/references.md，根目录 SUMMARY.md 作为唯一阅读目录。

**Tech Stack:** Markdown、Mermaid、Arduino C++、PowerShell、Git；首期不绑定 GitBook、MkDocs 或 PDF 构建工具链。

**Spec:** docs/superpowers/specs/2026-09-15-arduino-uno-q-book-design.md

## Global Constraints

- 项目根目录固定为 Arduino UNO Q 深度开发学习路线/。
- 第一阶段只完成第一篇基础工程和第 1 章，不提前编写后续篇章正文。
- UNO Q 的事实优先回到 Arduino 官方文档核验；社区仓库只作为案例和结构参考。
- 正文、原创图示与外部材料严格分开，不复制外部教程的大段文字、图片或章节结构。
- 代码示例必须说明目标板卡、核心、工具、验证日期和实机验证边界。
- 无法连接硬件时只报告静态检查或未完成实机验证，不把静态检查描述为运行成功。
- 保留当前工作区的 outputs/ 和 work/，只在新项目目录内创建文件。
- 初始化本地 Git 仓库，但不执行 git commit、git push 或远程仓库创建。
- 文件使用 UTF-8；章节标题、图号、代码目录和 SUMMARY.md 链接保持一致。

---

### Task 1: 初始化仓库骨架与根目录文档

**Files:**
- Create: .gitignore
- Create: .gitattributes
- Create: README.md
- Create: docs/writing-guidelines.md
- Create: resources/references.md
- Create: book/README.md
- Create: code/README.md
- Create: diagrams/README.md
- Create: images/README.md
- Create: resources/README.md

**Interfaces:**
- Consumes: docs/superpowers/specs/2026-09-15-arduino-uno-q-book-design.md。
- Produces: 根目录身份、写作约定、资源登记格式，以及供后续任务使用的 book/、code/、diagrams/、images/、resources/ 入口说明。

- [ ] **Step 1: 创建目录并确认项目边界**

从当前工作目录执行：

~~~powershell
$projectRoot = 'Arduino UNO Q 深度开发学习路线'
$directories = @(
  "$projectRoot\book",
  "$projectRoot\code",
  "$projectRoot\diagrams",
  "$projectRoot\images",
  "$projectRoot\resources",
  "$projectRoot\docs\superpowers\specs",
  "$projectRoot\docs\superpowers\plans"
)
foreach ($directory in $directories) {
  New-Item -ItemType Directory -Force -Path $directory | Out-Null
}
Test-Path "$projectRoot\docs\superpowers\specs\2026-09-15-arduino-uno-q-book-design.md"
~~~

Expected: 输出 True，且没有创建项目根目录之外的书籍文件。

- [ ] **Step 2: 初始化本地 Git 元数据**

~~~powershell
Set-Location 'Arduino UNO Q 深度开发学习路线'
if (-not (Test-Path '.git')) { git init }
git status --short --branch
~~~

Expected: 当前目录显示为 Git 仓库；工作区仍未产生提交。

- [ ] **Step 3: 写入编码和忽略规则**

.gitattributes 至少包含：

~~~text
* text=auto eol=lf
*.md text eol=lf
*.mmd text eol=lf
*.ino text eol=lf
*.ps1 text eol=crlf
*.svg text eol=lf
~~~

.gitignore 至少忽略以下临时内容，同时不忽略 Markdown、Arduino、Mermaid 或 SVG 文件：

~~~text
.DS_Store
Thumbs.db
*.tmp
*.bak
.idea/
.vscode/*.log
site/
build/
dist/
~~~

- [ ] **Step 4: 写入项目 README**

README.md 必须包含以下标题，并明确当前状态为“第一阶段写作中”：

~~~markdown
# Arduino UNO Q 深度开发学习路线

## 项目定位
## 适用读者
## 阅读入口
## 全书路线
## 当前进度
## 目录结构
## 来源与版权边界
## 贡献与更新方式
~~~

README 要链接到 SUMMARY.md、第一篇 README、设计说明和参考资料索引；当前版本明确说明尚未授予外部材料再分发许可。

- [ ] **Step 5: 写入写作规范和资源入口说明**

docs/writing-guidelines.md 必须固定章节元数据、章节顺序、术语写法、代码说明字段、Mermaid 要求、图示占位格式和交叉引用格式。resources/references.md 使用下列字段登记每条来源：

~~~markdown
| 类别 | 名称 | URL | 用途 | 许可证/声明 | 最后核验日期 |
|---|---|---|---|---|---|
~~~

book/README.md、code/README.md、diagrams/README.md、images/README.md、resources/README.md 分别说明目录职责，并链接回根目录 README。

- [ ] **Step 6: 验证根目录文档**

~~~powershell
$required = @(
  'README.md', 'docs\writing-guidelines.md', 'resources\references.md',
  'book\README.md', 'code\README.md', 'diagrams\README.md',
  'images\README.md', 'resources\README.md'
)
$missing = $required | Where-Object { -not (Test-Path $_) }
if ($missing) { throw "Missing root files: $($missing -join ', ')" }
rg -n '^## |SUMMARY.md|第1篇_认识UNOQ|版权|来源' $required
~~~

Expected: 所有文件存在，README 和目录说明包含项目身份、入口、来源及版权边界。

- [ ] **Step 7: 记录检查点，不提交 Git**

~~~powershell
git status --short
~~~

Expected: 只显示当前项目的新文件；不执行提交。

### Task 2: 建立九篇目录和第一篇阅读入口

**Files:**
- Create: SUMMARY.md
- Create: book/第1篇_认识UNOQ/README.md
- Create: book/第2篇_STM32/README.md
- Create: book/第3篇_Linux/README.md
- Create: book/第4篇_PythonBridge/README.md
- Create: book/第5篇_AppLab/README.md
- Create: book/第6篇_OpenCV/README.md
- Create: book/第7篇_AI/README.md
- Create: book/第8篇_IoT/README.md
- Create: book/第9篇_Project/README.md

**Interfaces:**
- Consumes: Task 1 的目录说明和设计说明中的九篇职责边界。
- Produces: 所有篇的稳定链接目标，以及第一篇到第 1 章的正式阅读入口。

- [ ] **Step 1: 创建九个篇目录**

~~~powershell
$parts = @(
  '第1篇_认识UNOQ', '第2篇_STM32', '第3篇_Linux', '第4篇_PythonBridge',
  '第5篇_AppLab', '第6篇_OpenCV', '第7篇_AI', '第8篇_IoT', '第9篇_Project'
)
foreach ($part in $parts) {
  New-Item -ItemType Directory -Force -Path "book\$part" | Out-Null
}
~~~

- [ ] **Step 2: 写入后续篇章的范围 README**

每个后续篇章 README 使用同一结构：

~~~markdown
# 第N篇：标题

## 本篇定位
## 学习目标
## 章节地图
## 前置知识
## 当前状态
~~~

后续篇章只写设计说明中规定的职责边界和路线位置，不写具体教程正文；章节地图使用明确的范围说明，不放入模糊承诺或不可执行的任务描述。

- [ ] **Step 3: 写入第一篇 README**

book/第1篇_认识UNOQ/README.md 必须包含：

~~~markdown
# 第一篇：认识 Arduino UNO Q

## 本篇目标
## 阅读顺序
## 前置知识
## 章节地图
## 实验与工具边界
## 本篇来源
~~~

章节地图至少链接到第 1 章，并预留“UNO Q 定位、硬件架构、软件架构、第一个实验”四个明确主题入口；尚未创建的章节使用文字说明，不制造失效链接。

- [ ] **Step 4: 写入 SUMMARY**

SUMMARY.md 只登记已存在的链接目标，结构固定为：

~~~markdown
# Arduino UNO Q 深度开发学习路线

## 第一篇：认识 Arduino UNO Q
- [本篇导读](book/第1篇_认识UNOQ/README.md)
- [第1章 Arduino 的发展](book/第1篇_认识UNOQ/第1章_Arduino的发展.md)

## 第二篇：STM32
- [本篇范围](book/第2篇_STM32/README.md)

## 第三篇：Linux
- [本篇范围](book/第3篇_Linux/README.md)

## 第四篇：Python Bridge
- [本篇范围](book/第4篇_PythonBridge/README.md)

## 第五篇：App Lab
- [本篇范围](book/第5篇_AppLab/README.md)

## 第六篇：OpenCV
- [本篇范围](book/第6篇_OpenCV/README.md)

## 第七篇：AI
- [本篇范围](book/第7篇_AI/README.md)

## 第八篇：IoT
- [本篇范围](book/第8篇_IoT/README.md)

## 第九篇：Project
- [本篇范围](book/第9篇_Project/README.md)
~~~

- [ ] **Step 5: 验证目录链接目标**

~~~powershell
$summary = Get-Content 'SUMMARY.md' -Raw
$links = [regex]::Matches($summary, '\]\(([^)]+)\)') | ForEach-Object { $_.Groups[1].Value }
$missing = $links | Where-Object { -not (Test-Path $_) }
if ($missing) { throw "Broken SUMMARY targets: $($missing -join ', ')" }
~~~

Expected: 输出为空且退出码为 0。

### Task 3: 撰写第 1 章“Arduino 的发展”并建立图示占位

**Files:**
- Create: book/第1篇_认识UNOQ/第1章_Arduino的发展.md
- Modify: book/第1篇_认识UNOQ/README.md（章节文件创建后，将预留文字更新为真实章节链接）
- Modify: docs/writing-guidelines.md（将批准规格中的五字段元数据定义为必填，其余字段作为可选扩展）
- Create: diagrams/arduino-evolution.mmd
- Create: diagrams/uno-q-dual-brain.mmd
- Create: images/第1篇_认识UNOQ/README.md

**Interfaces:**
- Consumes: Task 1 的写作规范、Task 2 的第一篇链接目标、Arduino 官方资料和 GitHub 参考项目索引。
- Produces: 一篇可独立阅读的首章正文，两个可复用 Mermaid 源文件，以及不伪装成最终图片的图示占位登记。

- [ ] **Step 1: 核验并登记首章事实来源**

至少核验并登记以下来源，访问日期使用实际执行日期：

1. Arduino 官方 UNO Q User Manual：
   https://github.com/arduino/docs-content/blob/main/content/hardware/02.uno/boards/uno-q/tutorials/01.user-manual/content.md
2. Arduino 官方 App Bricks 示例：
   https://github.com/arduino/app-bricks-examples
3. Mjrovai UNO Q 教程课程：
   https://github.com/Mjrovai/ARDUINO-UNO-Q
4. CWTI UNO Q Knowledge Base：
   https://github.com/CWTI-Ltd/arduino_uno_q_knowledge_base_and_playground

历史部分只写经过来源核验的高层转折，不编造未经证实的精确年份、销量或性能对比；硬件规格和软件版本只在正文明确引用官方资料时出现。

- [ ] **Step 2: 写入章节元数据和固定标题**

章节开头必须使用：

~~~yaml
---
title: Arduino 的发展
part: 1
chapter: 1
status: draft
last_verified: 2026-09-16
---
~~~

正文标题顺序固定为：

~~~markdown
# 第1章 Arduino 的发展
## 学习目标
## 本章导读
## 1. Arduino 解决了什么问题
## 2. 从 AVR 开发板到 Arduino 生态
## 3. 32 位、联网与物联网能力的扩展
## 4. 为什么需要 MPU 与 MCU 协同
## 5. UNO Q：从单片机体验走向双处理器平台
## 6. 用 Blink 看跨代际的编程连续性
## 7. 本书后续路线
## 常见误区
## 本章小结
## 交叉引用与延伸阅读
## 来源与验证
~~~

- [ ] **Step 3: 写入第一张 Mermaid 演进图**

将下列结构写入 diagrams/arduino-evolution.mmd，并在章节第 2～5 节附近以内联 Mermaid 代码形式呈现：

~~~mermaid
flowchart LR
    A[早期微控制器开发\\n门槛高、工具分散] --> B[Arduino AVR 时代\\n开发板 + Bootloader + Arduino API]
    B --> C[32 位 ARM 与联网平台\\n更多算力、外设与连接能力]
    C --> D[AIoT 应用需求\\nLinux、模型、网络与实时控制同时存在]
    D --> E[Arduino UNO Q\\nMPU/Linux + MCU/Zephyr]
~~~

图下必须解释：这是一条“开发模型和能力边界”的演进线，不是把所有 Arduino 产品按单一性能排序。

- [ ] **Step 4: 写入第二张 Mermaid 双处理器关系图**

将下列结构写入 diagrams/uno-q-dual-brain.mmd，并在第 5 节或第 6 节附近以内联形式呈现：

~~~mermaid
flowchart TB
    subgraph UNOQ[Arduino UNO Q]
        MPU[MPU\\nQualcomm QRB2210\\nDebian Linux\\n应用、网络、模型]
        MCU[MCU\\nSTM32U585\\nZephyr/Arduino\\n实时 I/O、传感器、执行器]
        BRIDGE[Bridge / RPC\\n跨处理器调用与数据交换]
        MPU <--> BRIDGE <--> MCU
    end
    USER[开发者] --> APP[Arduino App Lab / CLI / IDE]
    APP --> MPU
    APP --> MCU
~~~

图下必须明确：Arduino IDE 侧的 UNO Q 支持重点是 MCU 编程；MPU 侧 Linux 应用需要通过 App Lab 或相应 CLI/开发流程管理；Blink 只证明 MCU 侧程序路径。

- [ ] **Step 5: 撰写第一章正文**

正文必须做到：

- 用“降低入门门槛、统一开发体验、快速原型”解释 Arduino 的历史价值，而不是只罗列产品型号。
- 解释 AVR、32 位 ARM、联网平台和双处理器平台之间的能力边界。
- 把 UNO Q 的出现写成需求变化的结果：高层计算和实时控制需要协同，而不是简单地把 UNO Q 称为“更快的 Arduino”。
- 在第一次出现时解释 MPU、MCU、Linux、Zephyr、Bridge/RPC 的中英文和缩写。
- 通过 Blink 连接传统 Arduino 学习经验，同时说明代码执行位置和验证边界。
- 保持 docs/writing-guidelines.md 与本章元数据契约一致：title、part、chapter、status、last_verified 为必填，updated、prerequisites、outcomes、tags 为可选扩展。
- 链接到 ../第2篇_STM32/README.md、../第3篇_Linux/README.md、../第4篇_PythonBridge/README.md 和 ../第5篇_AppLab/README.md。
- 更新第一篇 README 中关于第 1 章“尚未创建”的预留文字，改为指向已创建的第 1 章正文。
- 包含至少一个“常见误区”小节，明确区分 MCU 侧控制、MPU 侧应用和双处理器协同。
- 不把尚未创建的后续章节写成可点击的失效链接。

- [ ] **Step 6: 写入图示占位说明**

images/第1篇_认识UNOQ/README.md 至少登记：

~~~markdown
# 第一篇图示资源登记

## 图 1-1：Arduino 能力演进时间线
- 状态：占位说明
- 目标文件：ch01-fig01-arduino-evolution.svg
- 内容要求：标注开发模型、平台能力和学习重点
- 来源边界：原创重绘，不直接复制外部图片

## 图 1-2：UNO Q 双处理器关系图
- 状态：占位说明
- 目标文件：ch01-fig02-uno-q-dual-brain.svg
- 内容要求：标注 MPU、MCU、Linux、Zephyr 和 Bridge/RPC
- 来源边界：基于官方文字资料独立绘制
~~~

- [ ] **Step 7: 验证章节结构和链接**

~~~powershell
$chapter = Get-Content 'book\第1篇_认识UNOQ\第1章_Arduino的发展.md' -Raw
$headings = @(
  '## 学习目标', '## 本章导读', '## 1. Arduino 解决了什么问题',
  '## 2. 从 AVR 开发板到 Arduino 生态', '## 3. 32 位、联网与物联网能力的扩展',
  '## 4. 为什么需要 MPU 与 MCU 协同', '## 5. UNO Q：从单片机体验走向双处理器平台',
  '## 6. 用 Blink 看跨代际的编程连续性', '## 7. 本书后续路线',
  '## 常见误区', '## 本章小结', '## 交叉引用与延伸阅读', '## 来源与验证'
)
$missing = $headings | Where-Object { $chapter -notmatch [regex]::Escape($_) }
if ($missing) { throw "Missing chapter headings: $($missing -join ', ')" }
~~~

Expected: 所有固定标题存在，章节中的相对链接目标均已创建，两个 Mermaid 文件均以 flowchart 开始。

### Task 4: 添加第 1 章 Blink 代码示例

**Files:**
- Create: code/第1章_Arduino的发展/README.md
- Create: code/第1章_Arduino的发展/Blink/Blink.ino
- Create: code/第1章_Arduino的发展/Blink/README.md

**Interfaces:**
- Consumes: Task 3 对 Blink 执行边界的说明。
- Produces: 一个与首章对应、可单独复制到 Arduino IDE 或 App Lab 进行验证的最小示例。

- [ ] **Step 1: 写入示例代码**

Blink.ino 使用无阻塞外部依赖的经典结构，完整内容为：

~~~cpp
const unsigned long kIntervalMs = 1000;
bool ledState = false;

void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
}

void loop() {
  ledState = !ledState;
  digitalWrite(LED_BUILTIN, ledState ? HIGH : LOW);
  delay(kIntervalMs);
}
~~~

代码说明必须指出：LED_BUILTIN 的具体物理指示灯由目标板卡定义；在 UNO Q 章节语境下，该 Sketch 运行在 STM32 MCU 侧。

- [ ] **Step 2: 写入代码目录 README**

code/第1章_Arduino的发展/README.md 必须包含：

~~~markdown
# 第1章代码

## 示例列表
## 目录结构
## 验证边界
~~~

并链接到 Blink/README.md 和正文第 6 节。

- [ ] **Step 3: 写入示例运行说明**

Blink/README.md 必须明确填写：

- 目标板卡：Arduino UNO Q。
- 目标执行侧：STM32U585 MCU。
- Arduino IDE：安装 Arduino UNO Q Zephyr Core 后选择 UNO Q Board。
- Arduino App Lab：复制为可编辑 App 后运行 Sketch。
- 预期现象：板载用户 LED 约每秒切换一次。
- 当前验证：记录执行日期，以及“静态检查”“CLI 编译”或“实机运行”中的真实状态。
- 限制：不以该示例证明 MPU/Linux 应用或 Bridge 已经工作。

- [ ] **Step 4: 运行代码静态检查或 CLI 编译**

先检查 CLI 是否可用：

~~~powershell
if (Get-Command arduino-cli -ErrorAction SilentlyContinue) {
  arduino-cli version
  arduino-cli compile --fqbn arduino:zephyr:unoq '.\code\第1章_Arduino的发展\Blink'
} else {
  Write-Output 'arduino-cli unavailable: performed source-level validation only.'
  $source = Get-Content '.\code\第1章_Arduino的发展\Blink\Blink.ino' -Raw
  if ($source -notmatch 'void setup\s*\(') { throw 'setup() missing' }
  if ($source -notmatch 'void loop\s*\(') { throw 'loop() missing' }
  if ($source -notmatch 'LED_BUILTIN') { throw 'LED_BUILTIN missing' }
}
~~~

如果 CLI 或 UNO Q 核心未安装，必须在 README 中保留“未完成 CLI 编译/实机验证”的真实状态，不伪造 PASS。

### Task 5: 首期整体验证与交付检查

**Files:**
- Modify: README.md（只补充实际验证日期和首期文件清单）
- Modify: SUMMARY.md（只在确认文件存在后保持目录一致）
- Modify: resources/references.md（只补充实际核验日期、许可证声明和版本信息）

**Interfaces:**
- Consumes: Task 1 至 Task 4 的全部文件。
- Produces: 一份通过结构、链接、章节、Mermaid 和代码边界检查的本地首期工程；任何未验证项明确标注。

- [ ] **Step 1: 检查首期文件清单**

~~~powershell
$required = @(
  'README.md', 'SUMMARY.md', 'docs\writing-guidelines.md', 'resources\references.md',
  'book\第1篇_认识UNOQ\README.md', 'book\第1篇_认识UNOQ\第1章_Arduino的发展.md',
  'code\第1章_Arduino的发展\README.md',
  'code\第1章_Arduino的发展\Blink\Blink.ino',
  'code\第1章_Arduino的发展\Blink\README.md',
  'diagrams\arduino-evolution.mmd', 'diagrams\uno-q-dual-brain.mmd',
  'images\第1篇_认识UNOQ\README.md'
)
$missing = $required | Where-Object { -not (Test-Path $_) }
if ($missing) { throw "Missing first-stage files: $($missing -join ', ')" }
~~~

- [ ] **Step 2: 检查 SUMMARY 和正文相对链接**

对 SUMMARY.md、第一篇 README、首章正文和代码 README 中的每个相对 Markdown 链接，解析为当前文件所在目录的绝对路径并检查 Test-Path。外部 https:// 链接只登记来源，不把网络不可用误判为本地链接失败。

- [ ] **Step 3: 检查 Markdown 结构和 Mermaid 声明**

~~~powershell
$mermaidFiles = @('diagrams\arduino-evolution.mmd', 'diagrams\uno-q-dual-brain.mmd')
foreach ($file in $mermaidFiles) {
  $content = Get-Content $file -Raw
  if ($content -notmatch '^flowchart\s+(LR|TB)') { throw "Invalid Mermaid declaration: $file" }
}
$chapterContent = Get-Content 'book\第1篇_认识UNOQ\第1章_Arduino的发展.md' -Raw
if (($chapterContent -split '~~~mermaid').Count -lt 3) { throw 'Chapter must contain two Mermaid blocks.' }
~~~

- [ ] **Step 4: 重新核对来源和验证边界**

逐条核对正文的 UNO Q 架构、开发工具和执行侧表述；确保官方资料、社区资料和原创解释分别标识，确保代码 README 的验证状态与实际命令输出一致。

- [ ] **Step 5: 查看最终变更，不提交 Git**

~~~powershell
git status --short
git diff --stat -- .
~~~

Expected: 所有变更都位于 Arduino UNO Q 深度开发学习路线/ 内，未发生提交或远程推送。最终交付说明列出实际创建的文件、验证命令、验证结果和仍需硬件验证的项目。
