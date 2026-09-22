# 第四篇图示资源登记

状态按各图分别记录：Fig-24、Fig-25 保留既有源图占位；Fig-26、Fig-27 已完成 SVG 渲染与预览审阅。

## 图 4-1：Python Bridge 消息生命周期

- 图号：Fig-24
- 状态：占位说明（Mermaid 源文件已存在，SVG 尚未提交）
- 目标文件：`ch01-fig24-uno-q-python-bridge-message-lifecycle.svg`
- 图源：[Python Bridge 消息生命周期 Mermaid 源文件](../../diagrams/uno-q-python-bridge-message-lifecycle.mmd)
- 正文位置：[第四篇第1章 Fig-24：Python Bridge 消息生命周期](../../book/第4篇_PythonBridge/第1章_Python_Bridge开发基础_消息模型与调用边界.md#fig-24-python-bridge-message-lifecycle)
- 内容要求：展示 Python App 创建请求、Router 转发、Bridge/RPC 调用、MCU Sketch 接受或拒绝、响应关联、证据记录，以及超时或关联错配时冻结自动重试的停止边界
- 来源边界：基于 Arduino App specification、Arduino Router 和本书已登记的 Python 标准库资料原创重绘；不直接复制官方产品图、数据表框图或第三方图片
- 生成边界：当前保留 Mermaid 源文件；本环境未安装 `mmdc`，因此未生成 SVG，也未完成视觉审阅

## 图 4-2：Python Bridge 有界任务生命周期

- 图号：Fig-25
- 状态：占位说明（Mermaid 源文件已存在，SVG 尚未提交）
- 目标文件：`ch02-fig25-uno-q-python-bridge-task-lifecycle.svg`
- 图源：[Python Bridge 任务生命周期 Mermaid 源文件](../../diagrams/uno-q-python-bridge-task-lifecycle.mmd)
- 正文位置：[第四篇第2章 Fig-25：有界任务生命周期](../../book/第4篇_PythonBridge/第2章_Python_Bridge并发与任务生命周期_从单次调用到有界协同.md#fig-25-python-bridge-task-lifecycle)
- 内容要求：展示任务从 CREATED、QUEUED、RUNNING 到 COMPLETED/REJECTED 的正常路径，以及取消、超时、UNKNOWN、对账和安全冻结路径
- 来源边界：基于 Python asyncio 官方资料、第四篇第1章消息契约和本书运行治理原创重绘；不直接复制官方产品图、数据表框图或第三方图片
- 生成边界：当前保留 Mermaid 源文件；本环境未安装 `mmdc`，因此未生成 SVG，也未完成视觉审阅

<a id="fig-26-python-bridge-connection-recovery"></a>

## 图 4-3：Python Bridge 连接恢复状态图

- 图号：Fig-26
- 状态：SVG 已生成并完成预览审阅，Mermaid 源文件与正文一致
- 图源：[连接恢复 Mermaid](../../diagrams/uno-q-python-bridge-connection-recovery.mmd)
- 产物：[连接恢复 SVG](ch03-fig26-uno-q-python-bridge-connection-recovery.svg)
- 正文位置：[第四篇第3章 Fig-26](../../book/第4篇_PythonBridge/第3章_Python_Bridge连接复用与请求恢复_从断线到可判定结果.md#fig-26-python-bridge-connection-recovery)
- 内容要求：连接的建立、方法探测、复用、失效、退避、暂停、显式重启与整体关闭；旧业务请求由正文的恢复决策单独管理
- 生成记录：`2026-09-22`，Mermaid CLI `11.12.0`，本地 Chrome 无界面渲染；使用工作区已有缓存，无全局安装变更
- 来源边界：基于 Arduino Router 与 Python asyncio 官方资料原创建模；`generation` 和恢复状态均为本书应用层设计，不是官方协议承诺
- 验证边界：图示渲染只证明源图可解析且展示清晰，不构成 UNO Q 或真实 Bridge 连接恢复证据

<a id="fig-27-python-bridge-result-ledger"></a>

## 图 4-4：Python Bridge 结果账本与状态查询闭环

- 图号：Fig-27
- 状态：SVG 已生成并完成预览审阅，Mermaid 源文件与正文逐字一致
- 图源：[结果账本与状态查询 Mermaid](../../diagrams/uno-q-python-bridge-result-ledger.mmd)
- 产物：[结果账本与状态查询 SVG](ch04-fig27-uno-q-python-bridge-result-ledger.svg)
- 正文位置：[第四篇第4章 Fig-27](../../book/第4篇_PythonBridge/第4章_Python_Bridge结果账本与状态查询_从返回值到可验证证据.md#fig-27-python-bridge-result-ledger)
- 内容要求：展示 PENDING、SENT、UNKNOWN 和 APPLIED、REJECTED、EXPIRED、NOT_APPLIED_FINAL 四个终态；QUERY 表示身份核验与证据判定边界，不是第八种账本状态；过期禁止发送和重放，但 STOP_EXPIRED 保留 UNKNOWN 以接收迟到权威证据
- 生成记录：`2026-09-22`，缓存 Mermaid CLI `11.12.0`，本地 Chrome 无界面渲染，白色背景；未安装包或修改全局配置
- 预览记录：`2026-09-22`，独立打开生成的 SVG 并截图检查；标签可读、箭头完整、四个终态和 QUERY 判定说明可见，无裁切文字；SVG XML 解析通过，节点和边标签边界检查无越界
- 来源边界：依据[已登记的官方资料](../../resources/references.md)原创建模；状态、QUERY 和账本接口是本书教学设计，不是 Arduino 官方协议图
- 验证边界：本章仍为 draft；渲染及本地测试不证明 Router/Bridge、App Lab、MCU、目标 Linux 镜像或 UNO Q 硬件验收，也不证明设备查询能力、掉电持久性或并发性能
