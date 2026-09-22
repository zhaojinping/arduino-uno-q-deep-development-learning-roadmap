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

后续章节将继续覆盖并发与任务生命周期、连接复用、错误处理、状态查询和现场联调；每篇的章节编号从第 1 章重新开始。

## 前置知识

建议先完成[第二篇第9章：传感、控制与 MCU/Linux 协同闭环](../第2篇_STM32/第9章_综合实验_传感控制与MCU_Linux协同闭环.md)和[第三篇第8章：Linux 与 Python Bridge 综合运行手册](../第3篇_Linux/第8章_Linux与Python_Bridge综合运行手册_从预检到交接.md)，并具备 Python 基础。

## 当前状态

第 1 章已建立为 `draft` 初稿，包含消息模型、Fig-24 Mermaid 源文件、两个标准库概念实验、故障矩阵和跨篇交接。当前未完成 Router/Bridge 实机联调、App Lab 运行、MCU 硬件验证或 SVG 视觉审阅。
