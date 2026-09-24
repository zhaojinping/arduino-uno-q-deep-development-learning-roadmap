# 第八篇 IoT 图示登记

本目录登记第八篇章节使用的可追溯 Mermaid 源图。生成 SVG 前需保留源文件并记录渲染工具和版本；当前尚未生成 SVG。

<a id="fig-51-uno-q-iot-telemetry-contract"></a>

## 图 8-1：从采样事件到服务端遥测入口

- 图号：Fig-51
- 状态：正文 Mermaid 与独立源文件已建立；SVG 待生成并完成预览审阅。
- 图源：[IoT 遥测契约 Mermaid](../../diagrams/uno-q-iot-telemetry-contract.mmd)
- 正文位置：[第八篇第1章 Fig-51](../../book/第8篇_IoT/第1章_IoT开发基础_从采样数据到可验证遥测.md#fig-51-uno-q-iot-telemetry-contract)
- 内容要求：区分采样输入、事件契约、边缘结构检查、可选 MCU/Linux 协作、MQTT/HTTP 传输和服务端校验/去重/处置。
- 来源边界：原创参考架构；Arduino 文档用于核对平台分工，OASIS 与 RFC 用于解释协议/载荷边界；不表示这些组织发布或认可本图。
- 验证边界：本章程序只校验固定合成 JSON，不接入图中任何传感器、Bridge/RPC、网络、MQTT Broker、HTTP 服务或数据库；SVG 尚未渲染和目视审阅。

<a id="fig-52-uno-q-mqtt-idempotent-consumer"></a>

## 图 8-2：MQTT 重复投递与消费端事务门

- 图号：Fig-52
- 状态：正文 Mermaid 与独立源文件已建立；SVG 待生成并完成预览审阅。
- 图源：[MQTT 幂等消费者 Mermaid](../../diagrams/uno-q-mqtt-idempotent-consumer.mmd)
- 正文位置：[第八篇第2章 Fig-52](../../book/第8篇_IoT/第2章_MQTT消息上报与幂等消费_从主题设计到重复投递.md#fig-52-uno-q-mqtt-idempotent-consumer)
- 内容要求：展示合成 QoS 1 重投递、契约校验、事件键/载荷摘要分流、单 SQLite 事务及冲突审查；PUBACK 确认次序明确留给实际客户端库核验。
- 来源边界：原创教学流程；MQTT 协议事实见 OASIS 标准，事务事实见 SQLite/Python 官方资料；不表示标准组织发布或认可本图。
- 验证边界：本章只模拟 JSONL 重复输入与离线 SQLite 处理，不运行 MQTT 客户端或 Broker；SVG 尚未渲染和目视审阅。
