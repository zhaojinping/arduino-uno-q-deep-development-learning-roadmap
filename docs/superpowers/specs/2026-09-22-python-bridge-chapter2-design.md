# 第四篇 Python Bridge 第 2 章设计说明

## 目标

在第一章消息模型的基础上，新增第四篇第 2 章《Python Bridge 并发与任务生命周期：从单次调用到有界协同》，说明 Python App 如何管理多个调用、队列、worker、超时、取消、背压和 UNKNOWN 交接。

## 范围

本章包含：

1. `call` 与任务对象的关系；
2. `CREATED`、`QUEUED`、`RUNNING`、`CANCEL_REQUESTED`、`COMPLETED`、`REJECTED`、`UNKNOWN` 等生命周期状态；
3. 有界队列、并发上限、worker、顺序、公平性和背压；
4. 本地任务取消与远端动作取消的差异；
5. 超时、`asyncio.shield`、对账和 UNKNOWN 冻结策略；
6. 两个只使用 Python 标准库的概念实验；
7. Fig-25 任务生命周期 Mermaid 源文件、图示登记、SUMMARY 和项目进度更新。

## 不在范围内

- 不实现真实 Router、Bridge/RPC、ADB、SSH、网络、串口或 UNO Q 硬件调用；
- 不承诺某个当前固件、Python 客户端或 App Lab 版本的并发实现细节；
- 不在本章引入第三方异步框架、数据库队列或生产级服务守护；
- 不把本地 asyncio 输出写成 MCU、Bridge 或现场性能证据；
- 不提前展开第四篇第 3 章及以后的连接复用、重连和 App Lab 实机流程。

## 章节结构

1. 学习目标、背景与边界；
2. 任务、调用和结果状态；
3. Fig-25：有界任务生命周期；
4. 并发上限、队列和背压；
5. 超时、取消和 UNKNOWN；
6. 概念实验一：有界队列与 worker；
7. 概念实验二：超时、对账与协作式取消；
8. 并发调用运行手册；
9. 故障矩阵和验证矩阵；
10. 与第一章、第三篇和后续章节的交接；
11. FAQ、小结与延伸阅读。

## 设计决定

- 本章继续使用 `part: 4`、`chapter: 2`，不沿用第三篇的章节编号；
- 图号使用全书下一个编号 Fig-25；
- 图使用 `stateDiagram-v2`，表达任务生命周期和停止路径，不表达真实线程或物理连接；
- 概念实验的时间间隔保持很短且可重复，所有输出明确标注为本地模拟；
- 并发上限和队列大小是策略参数，不能从概念实验推导现场性能预算；
- `UNKNOWN` 是冻结和交接状态，不是可通过多次重试自动消除的异常标签。

## 验收标准

- 新章节 front matter 为 `part: 4`、`chapter: 2`、`status: draft`；
- 章节包含两个完整 Python 示例，并分别提供八项代码说明；
- 章节内 Mermaid 与 `diagrams/uno-q-python-bridge-task-lifecycle.mmd` 完全一致；
- Fig-25 在 `images/第4篇_PythonBridge/README.md` 中登记；
- `SUMMARY.md`、第四篇 README 和根 README 指向新章节；
- 新链接存在，代码可编译并执行，`git diff --check` 通过；
- 未声称完成 `mmdc` SVG 渲染或 UNO Q 实机验证。
