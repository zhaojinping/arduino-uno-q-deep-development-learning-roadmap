# 第三篇图示资源登记

## 图 3-1：Linux 执行与 MCU 边界图

- 图号：Fig-16
- 状态：占位说明（Mermaid 源文件已存在，SVG 尚未提交）
- 目标文件：ch01-fig16-uno-q-linux-execution-boundary.svg
- 图源：[Linux 执行边界 Mermaid 源文件](../../diagrams/uno-q-linux-execution-boundary.mmd)
- 正文位置：[第三篇第 1 章第 2 节：执行边界图](../../book/第3篇_Linux/第1章_Linux侧开发基础_文件系统进程与MCU边界.md#fig-16-uno-q-linux-execution-boundary)
- 内容要求：展示开发主机经 USB、ADB、SSH 或网络进入 UNO Q Linux/MPU，再经文件系统、进程、权限和 Bridge 连接到 STM32U585 MCU；同时展示观测路径、连接失败诊断和 Linux 不直接绕过 MCU 安全状态机的停止边界
- 来源边界：基于 Arduino UNO Q User Manual、Arduino App CLI 和 Linux FHS 官方资料原创重绘；不直接复制官方产品图、数据表框图或第三方图片

## 图 3-2：Linux 设备、网络与服务边界图

- 图号：Fig-17
- 状态：占位说明（Mermaid 源文件已存在，SVG 尚未提交）
- 目标文件：ch02-fig17-uno-q-linux-device-network-service-boundary.svg
- 图源：[Linux 设备网络服务边界 Mermaid 源文件](../../diagrams/uno-q-linux-device-network-service-boundary.mmd)
- 正文位置：[第三篇第 2 章第 5 节：Linux 设备、网络与服务边界图](../../book/第3篇_Linux/第2章_Linux设备网络与服务_从可见到可用.md#fig-17-uno-q-linux-device-network-service-boundary)
- 内容要求：展示开发主机经 USB、ADB、SSH 或网络进入 Linux/MPU，再分别经过设备、网络和服务层到 App/Bridge，最终回到 MCU/Bridge 状态结果；同时展示访问失败、拒绝、过期、故障和证据记录路径
- 来源边界：基于 Arduino UNO Q User Manual、NetworkManager、systemd 和第二篇 MCU/Bridge 契约原创重绘；不直接复制官方产品图、数据表框图或第三方图片

## 图 3-3：Linux 可观测性、资源与回滚闭环图

- 图号：Fig-18
- 状态：占位说明（Mermaid 源文件已存在，SVG 尚未提交）
- 目标文件：ch03-fig18-uno-q-linux-observability-resource-rollback-boundary.svg
- 图源：[Linux 可观测性资源回滚 Mermaid 源文件](../../diagrams/uno-q-linux-observability-resource-rollback-boundary.mmd)
- 正文位置：[第三篇第 3 章第 7 节：Linux 可观测性、资源与回滚闭环图](../../book/第3篇_Linux/第3章_Linux可观测性与资源管理_日志时间与安全回滚.md#fig-18-uno-q-linux-observability-resource-rollback-boundary)
- 内容要求：展示 Linux/Bridge 事件、journal 字段、realtime/monotonic/boot_id、资源压力、证据包、远程变更、停止点、回滚验证以及 ACCEPTED/APPLIED/REJECTED/UNKNOWN 结果如何回到 MCU 状态机和安全输出
- 来源边界：基于 systemd journal 字段与 journalctl、systemd 资源控制、Linux cgroup v2、Arduino UNO Q User Manual 和第二篇 MCU/Bridge 契约原创重绘；不直接复制官方产品图、数据表框图或第三方图片

## 图 3-4：远程运维与 Python Bridge 请求时序

- 图号：Fig-19
- 状态：占位说明（Mermaid 源文件已存在，SVG 尚未提交）
- 目标文件：ch04-fig19-uno-q-linux-remote-bridge-request-sequence.svg
- 图源：[远程运维与 Python Bridge Mermaid 源文件](../../diagrams/uno-q-linux-remote-bridge-request-sequence.mmd)
- 正文位置：[第三篇第 4 章第 4 节：远程运维与 Python Bridge 请求时序](../../book/第3篇_Linux/第4章_Linux远程运维与Python_Bridge_从安全命令到可验证请求.md#fig-19-linux-remote-bridge-request-sequence)
- 内容要求：展示开发主机经 SSH、ADB 或 App Lab 进入 Linux 服务，再经过 operation 白名单、参数/权限/资源校验和 Python Bridge，分别进入 Linux 只读路径或 MCU RPC 路径，并覆盖 APPLIED、REJECTED、EXPIRED、FAILED、UNKNOWN 和脱敏证据返回。
- 来源边界：基于 Arduino UNO Q User Manual、Android Debug Bridge 官方文档、Python subprocess/json 官方文档和第二篇 MCU/Bridge 契约原创重绘；不直接复制官方产品图、代码或第三方图片。

## 图 3-5：Linux 现场自动化队列、重连与状态缓存闭环图

- 图号：Fig-20
- 状态：占位说明（Mermaid 源文件已存在，SVG 尚未提交）
- 目标文件：ch05-fig20-uno-q-linux-job-queue-reconnect-state-cache.svg
- 图源：[现场自动化队列重连缓存 Mermaid 源文件](../../diagrams/uno-q-linux-job-queue-reconnect-state-cache.mmd)
- 正文位置：[第三篇第 5 章第 4 节：队列、重连与状态缓存闭环](../../book/第3篇_Linux/第5章_Linux现场自动化与Python_Bridge_队列重连与状态缓存.md#fig-20-linux-job-queue-reconnect-state-cache)
- 内容要求：展示请求校验、有界队列、背压、worker 租约、连接状态、退避重连、UNKNOWN、结果分类、状态缓存 freshness、重新查询和脱敏证据归档的闭环。
- 来源边界：基于 Python asyncio Queue/Task 官方文档、systemd.service、Arduino UNO Q User Manual、Arduino App specification、Arduino Router 和第二篇 MCU/Bridge 契约原创重绘；不直接复制官方产品图、代码或第三方图片。
