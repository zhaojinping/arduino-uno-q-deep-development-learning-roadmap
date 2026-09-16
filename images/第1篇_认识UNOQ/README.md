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

## 图 1-3：UNO Q 任务执行侧决策图
- 图号：Fig-03
- 状态：占位说明
- 目标文件：ch02-fig03-uno-q-execution-boundary.svg
- 图源：[任务执行侧决策图 Mermaid 源文件](../../diagrams/uno-q-execution-boundary.mmd)
- 正文位置：[第 2 章第 6 节：任务应该放在哪里执行](../../book/第1篇_认识UNOQ/第2章_什么是Arduino_UNO_Q.md#6-任务应该放在哪里执行)
- 内容要求：覆盖任务需求到 MCU、MPU 或双侧协同的分流
- 来源边界：基于官方资料原创重绘；不直接复制外部图片

## 图 1-4：UNO Q 硬件资源分层图
- 图号：Fig-04
- 状态：占位说明（Mermaid 源文件已存在）
- 目标文件：ch03-fig04-uno-q-hardware-map.svg
- 图源：[UNO Q 硬件资源分层图 Mermaid 源文件](../../diagrams/uno-q-hardware-map.mmd)
- 正文位置：[第 3 章第 8 节：硬件关系图：资源、协同与边界](../../book/第1篇_认识UNOQ/第3章_UNO_Q的硬件架构.md#fig-04-uno-q-hardware-map)
- 内容要求：展示 QRB2210 MPU、STM32U585 MCU、无线模块、UNO headers、Qwiic、底部高速扩展资源，以及 Arduino Bridge / RPC 的逻辑协同与 1.8 V/3.3 V 电气域边界
- 来源边界：基于已登记的 Arduino 官方资料原创重绘；不直接复制官方产品图、数据表框图或第三方图片
