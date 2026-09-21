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
