# 第四篇 Python Bridge 第 2 章实施计划

> 本计划用于在现有主分支上维护书稿；远端推送与本次新章提交分开处理。

**目标：** 新增第四篇第 2 章，建立 Python Bridge 的并发、任务生命周期、背压、取消、超时和 UNKNOWN 交接基础。

**架构：** 以第四篇第 1 章的消息契约为输入，将一次 `call` 扩展为有界任务流；正文、Fig-25 Mermaid 源文件、图示登记和全书导航同一变更维护；实验只在本地 asyncio 内存模型中运行。

**技术栈：** UTF-8 Markdown、YAML front matter、Mermaid `stateDiagram-v2`、Python 3.10+ 标准库 `asyncio`、PowerShell 静态检查和 Git。

**设计说明：** `docs/superpowers/specs/2026-09-22-python-bridge-chapter2-design.md`

## 任务

### Task 1：基线和范围

- [x] 确认第一章已在 `origin/main`；
- [x] 检查第四篇入口、SUMMARY、Fig-24 图示登记和写作规范；
- [x] 保持本章为 `draft`，不改写第三篇内容。

### Task 2：正文

- [x] 创建 `第2章_Python_Bridge并发与任务生命周期_从单次调用到有界协同.md`；
- [x] 解释任务状态、并发上限、队列、worker、背压、取消、超时和 UNKNOWN；
- [x] 加入两个标准库概念实验及完整代码说明；
- [x] 明确本地模拟、实机观察、Bridge 联调和性能结论的证据边界。

### Task 3：图示与导航

- [x] 创建 `diagrams/uno-q-python-bridge-task-lifecycle.mmd`；
- [x] 登记 Fig-25；
- [x] 更新第四篇 README、SUMMARY、根 README，并补充第一章到第二章的交叉引用。

### Task 4：验证与提交

- [x] 执行两个 Python 代码块；
- [x] 检查 Mermaid 正文与源文件一致；
- [x] 检查内部链接、front matter、代码说明字段、空白和章节编号；
- [x] 检查 `mmdc` 是否可用，缺失时只记录边界；
- [ ] 创建本地提交 `docs: add Python Bridge task lifecycle chapter`；
- [x] 本次新章不自动推送，等待下一次明确推送授权。
