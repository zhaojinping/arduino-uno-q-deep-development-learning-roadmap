# 第八篇 IoT 图示登记

本目录登记第八篇章节使用的可追溯 Mermaid 源图。生成 SVG 前需保留源文件并记录渲染工具和版本；当前尚未生成 SVG。

<a id="fig-53-uno-q-iot-telemetry-contract"></a>

## 图 8-1：从采样事件到服务端遥测入口

- 图号：Fig-53
- 状态：正文 Mermaid 与独立源文件已建立；SVG 待生成并完成预览审阅。
- 图源：[IoT 遥测契约 Mermaid](../../diagrams/uno-q-iot-telemetry-contract.mmd)
- 正文位置：[第八篇第1章 Fig-53](../../book/第8篇_IoT/第1章_IoT开发基础_从采样数据到可验证遥测.md#fig-53-uno-q-iot-telemetry-contract)
- 内容要求：区分采样输入、事件契约、边缘结构检查、可选 MCU/Linux 协作、MQTT/HTTP 传输和服务端校验/去重/处置。
- 来源边界：原创参考架构；Arduino 文档用于核对平台分工，OASIS 与 RFC 用于解释协议/载荷边界；不表示这些组织发布或认可本图。
- 验证边界：本章程序只校验固定合成 JSON，不接入图中任何传感器、Bridge/RPC、网络、MQTT Broker、HTTP 服务或数据库；SVG 尚未渲染和目视审阅。

<a id="fig-54-uno-q-mqtt-idempotent-consumer"></a>

## 图 8-2：MQTT 重复投递与消费端事务门

- 图号：Fig-54
- 状态：正文 Mermaid 与独立源文件已建立；SVG 待生成并完成预览审阅。
- 图源：[MQTT 幂等消费者 Mermaid](../../diagrams/uno-q-mqtt-idempotent-consumer.mmd)
- 正文位置：[第八篇第2章 Fig-54](../../book/第8篇_IoT/第2章_MQTT消息上报与幂等消费_从主题设计到重复投递.md#fig-54-uno-q-mqtt-idempotent-consumer)
- 内容要求：展示合成 QoS 1 重投递、契约校验、事件键/载荷摘要分流、单 SQLite 事务及冲突审查；PUBACK 确认次序明确留给实际客户端库核验。
- 来源边界：原创教学流程；MQTT 协议事实见 OASIS 标准，事务事实见 SQLite/Python 官方资料；不表示标准组织发布或认可本图。
- 验证边界：本章只模拟 JSONL 重复输入与离线 SQLite 处理，不运行 MQTT 客户端或 Broker；SVG 尚未渲染和目视审阅。

<a id="fig-55-uno-q-iot-offline-outbox"></a>

## 图 8-3：持久化队列的离线补传与不确定结果恢复

- 图号：Fig-55
- 状态：正文 Mermaid 与独立源文件已建立；SVG 待生成并完成预览审阅。
- 图源：[离线发件箱 Mermaid](../../diagrams/uno-q-iot-offline-outbox.mmd)
- 正文位置：[第八篇第3章 Fig-55](../../book/第8篇_IoT/第3章_离线缓存与补传_从持久化队列到可验证恢复.md#fig-55-uno-q-iot-offline-outbox)
- 内容要求：展示契约校验、事件键去重/冲突、容量上限、过期清理、严格 FIFO、模拟发布结果与保留事件键的退避重试。
- 来源边界：原创教学流程；MQTT QoS/会话依据 OASIS 标准，事务与提交边界依据 Python/SQLite 官方文档；不表示这些组织发布或认可本图。
- 验证边界：本地 SQLite 和脚本化结果模拟；不运行 MQTT 客户端、Broker、网络、传感器或 UNO Q 实机；SVG 尚未渲染和目视审阅。

<a id="fig-56-uno-q-iot-observability-alerts"></a>

## 图 8-4：从健康快照到可操作信号

- 图号：Fig-56
- 状态：正文 Mermaid 与独立源文件已建立；SVG 待生成并完成预览审阅。
- 图源：[IoT 可观测性与告警 Mermaid](../../diagrams/uno-q-iot-observability-alerts.mmd)
- 正文位置：[第八篇第4章 Fig-56](../../book/第8篇_IoT/第4章_IoT可观测性与告警_从设备状态到可操作信号.md#fig-56-uno-q-iot-observability-alerts)
- 内容要求：展示输入契约、设备身份与快照时效检查，随后按队列占比、最老事件年龄和发布窗口信号评估；所有结果停留于本地建议报告，不发告警或操作设备。
- 来源边界：原创教学决策流程；OpenTelemetry 与 Prometheus 官方文档仅用于核对信号、基数和告警设计概念，不表示其组织发布或认可本图。
- 验证边界：四条固定合成快照与标准库离线分类器；不接入 OpenTelemetry Collector、Prometheus、MQTT Broker、网络、传感器或 UNO Q 实机；SVG 尚未渲染和目视审阅。

<a id="fig-57-uno-q-iot-remote-command-lifecycle"></a>

## 图 8-5：远程命令的接纳、执行与结果对账

- 图号：Fig-57
- 状态：正文 Mermaid 与独立源文件已建立；SVG 待生成并完成预览审阅。
- 图源：[远程命令生命周期 Mermaid](../../diagrams/uno-q-iot-remote-command-lifecycle.mmd)
- 正文位置：[第八篇第5章 Fig-57](../../book/第8篇_IoT/第5章_IoT远程命令与受控维护_从授权请求到结果对账.md#fig-57-uno-q-iot-remote-command-lifecycle)
- 内容要求：展示请求契约、目标/操作/权限及有效期门、命令 ID 幂等与冲突、接纳后执行、结果状态和 UNKNOWN 对账停止路径。
- 来源边界：本书原创教学流程；NIST IoT 能力基线用于设计能力参照，OASIS MQTT 5.0 用于核对请求/响应关联属性；不表示 NIST、OASIS 或 Arduino 发布/认可本图。
- 验证边界：30 项本机标准库测试和固定合成命令演示；不认证身份、不运行 MQTT/Broker/网络、不连接 UNO Q、MCU、Bridge、传感器或执行器；账本只在内存，SVG 尚未渲染和目视审阅。

<a id="fig-58-uno-q-iot-device-identity-secure-communication"></a>

## 图 8-6：从连接信任到每设备最小权限

- 图号：Fig-58
- 状态：正文 Mermaid 与独立源文件已建立；SVG 待生成并完成预览审阅。
- 图源：[IoT 设备身份与安全通信 Mermaid](../../diagrams/uno-q-iot-device-identity-secure-communication.mmd)
- 正文位置：[第八篇第6章 Fig-58](../../book/第8篇_IoT/第6章_IoT设备身份与安全通信_从连接信任到最小权限.md#fig-58-uno-q-iot-device-identity-secure-communication)
- 内容要求：展示设备入网、唯一设备身份、TLS 服务名验证、Broker 认证及主体绑定、默认拒绝 MQTT ACL、允许的数据流，以及轮换/吊销和拒绝/审计路径。
- 来源边界：本书原创教学流程；NIST 能力资料、TLS RFC 与 OASIS MQTT 标准用于校准概念边界，不表示上述组织或 Arduino 发布或认可本图。
- 验证边界：本机静态策略检查器与合成配置；未运行真实证书、TLS、Broker ACL、网络、Bridge/RPC、MCU 或 UNO Q 硬件；SVG 尚未渲染和目视审阅。

<a id="fig-59-uno-q-iot-integration-validation"></a>

## 图 8-7：从章节测试聚合到独立目标验收

- 图号：Fig-59
- 状态：正文 Mermaid 与独立源文件已建立；SVG 待生成并完成预览审阅。
- 图源：[IoT 综合验证 Mermaid](../../diagrams/uno-q-iot-integration-validation.mmd)
- 正文位置：[第八篇第7章 Fig-59](../../book/第8篇_IoT/第7章_IoT综合验证_从分章测试到系统级证据.md#fig-59-uno-q-iot-integration-validation)
- 内容要求：展示六章固定本机测试的串行执行、失败/超时/空测试与聚合缺项分支；本机结论不自动触发目标板验收或部署批准。
- 来源边界：本书原创流程图；Python `unittest` 官方文档只核对固定目录发现命令的接口，不表示 Python、Arduino 或其他组织发布或认可本图。
- 验证边界：121 项前六章本机合成/静态测试及本章聚合逻辑；不访问网络、Broker、传感器、Bridge/RPC、MCU、UNO Q 或部署环境；SVG 尚未渲染和目视审阅。
