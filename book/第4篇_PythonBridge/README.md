# 第4篇：Python Bridge

## 本篇定位

本篇聚焦 Linux 侧 Python 应用与 MCU 侧能力之间的 Bridge/RPC 协同。重点不是把一次消息发送包装成“硬件已经完成”，而是建立可关联、可验证、可停止和可交接的调用边界。

## 学习目标

完成本篇后，读者应能够：

- 设计 Python App、Router、Bridge/RPC 与 MCU Sketch 之间的消息契约；
- 组织并发调用、超时、取消、重连和结果缓存；
- 区分 APPLIED、REJECTED、UNKNOWN 等状态，并为副作用动作建立幂等策略；
- 将本地概念实验与 UNO Q 实机、App Lab 和综合项目的证据边界分开。

## 章节地图

- [第1章 Python Bridge 开发基础：消息模型与调用边界](./第1章_Python_Bridge开发基础_消息模型与调用边界.md)
- [第2章 Python Bridge 并发与任务生命周期：从单次调用到有界协同](./第2章_Python_Bridge并发与任务生命周期_从单次调用到有界协同.md)
- [第3章 Python Bridge 连接复用与请求恢复：从断线到可判定结果](./第3章_Python_Bridge连接复用与请求恢复_从断线到可判定结果.md)

后续章节将继续覆盖结果账本、状态查询、一致性、错误处理和现场联调；每篇的章节编号从第 1 章重新开始。

## 前置知识

建议先完成[第二篇第9章：传感、控制与 MCU/Linux 协同闭环](../第2篇_STM32/第9章_综合实验_传感控制与MCU_Linux协同闭环.md)和[第三篇第8章：Linux 与 Python Bridge 综合运行手册](../第3篇_Linux/第8章_Linux与Python_Bridge综合运行手册_从预检到交接.md)，并具备 Python 基础。

## 当前状态

第 1～3 章已建立为 `draft` 初稿。第 1 章覆盖消息模型和调用边界；第 2 章覆盖有界并发、任务生命周期与取消；第 3 章覆盖连接复用、退避、旧代次隔离与请求恢复，并提供独立 Python 示例和测试。

Fig-24～Fig-26 的产物状态见[图示登记](../../images/第4篇_PythonBridge/README.md)。本地代码验证与 Router/Bridge、App Lab、MCU 实机联调分别记录；本篇尚未完成板端验证。
