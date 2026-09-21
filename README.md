# Arduino UNO Q 深度开发学习路线

## 项目定位

本项目是一套面向实践的 Arduino UNO Q 深度开发学习路线，按由浅入深的方式组织硬件认知、软件环境、编程实践、系统联调与项目复盘。仓库同时保存正文入口、示例代码、图示源文件和经过登记的参考资料。

## 适用读者

适合已经接触过 Arduino 或基础嵌入式开发，希望理解 UNO Q 的软硬件协同方式、能够独立复现实验并逐步完成综合项目的学习者。阅读者应具备基本的命令行、Git 和编程概念；每章会明确补充所需前置知识。

## 阅读入口

- [阅读总览（SUMMARY.md）](SUMMARY.md)
- [第一篇：认识 UNO Q（第1篇_认识UNOQ README）](book/第1篇_认识UNOQ/README.md)
- [第二篇：STM32（第2篇_STM32 README）](book/第2篇_STM32/README.md)
- [设计说明](docs/superpowers/specs/2026-09-15-arduino-uno-q-book-design.md)
- [参考资料索引](resources/references.md)
- [写作规范](docs/writing-guidelines.md)

`SUMMARY.md` 和第一篇正文入口的路径先固定，正文目录将在后续任务中按本仓库的章节顺序补齐。

## 全书路线

1. 建立 UNO Q 的硬件、系统和开发模型认知。
2. 完成开发环境准备，理解示例的运行、验证和故障定位方式。
3. 通过逐步加深的实验掌握 Arduino、Linux 侧能力及两者协同。
4. 进入外设、通信、数据处理和综合项目开发。
5. 以可复现、可验证、可维护为标准完成项目复盘与能力迁移。

## 当前进度

当前状态：**第一篇第 1～5 章已完成，第二篇第 1～9 章已建立为初稿，第三篇第 1～2 章已建立为初稿**。Blink 示例和 Mermaid 源文件已存在；第一篇第 5 章提供 IDE、CLI、App Lab 的验证闭环，第二篇第 2 章补充 PWM 与定时输出的资源核验框架，第二篇第 3 章补充 ADC 采样、输入保护和数据证据框架，第二篇第 4 章补充 UART 资源、帧格式、缓冲和 MCU/Linux 边界框架，第二篇第 5 章补充 SPI 时序、片选、Devicetree 设备节点和 MCU/Linux 总线所有权框架，第二篇第 6 章补充 I2C 电气模型、7 位地址、Wire/Zephyr 事务、总线恢复和 MCU/Linux 所有权框架，第二篇第 7 章补充周期任务、Zephyr 调度、同步对象、超载、看门狗和 MCU/Linux 实时责任框架，第二篇第 8 章补充硬件验证等级、工具链、外设验证向量、故障隔离和证据归档框架，第二篇第 9 章补充传感、控制、状态机、Bridge 数据契约、故障注入和第二篇到第三篇交接框架，第三篇第 1 章补充 Linux/MPU、MCU、Bridge、文件系统、进程、访问入口和证据分层框架，第三篇第 2 章补充设备可见性、网络分层、NetworkManager、服务状态、日志和 Bridge 结果关联框架，但本环境仍未完成 Arduino CLI 编译、上传、Linux 实机盘点、网络查询、服务观测、ADB/SSH 联调和硬件实机验证。章节编号按篇重置，每一篇从第 1 章重新开始。

## 目录结构

```text
book/       正文、章节目录和阅读入口
code/       可复现实验、Arduino 草图及配套脚本
diagrams/   Mermaid 源文件及可追溯的图示产物
images/     正文使用的图片及其说明
resources/  参考资料索引与资源登记
docs/       项目设计说明和写作规范
```

各目录的边界和使用方式见对应的 `README.md`；目录入口不会替代章节级的实验说明和验证记录。

## 来源与版权边界

本项目会为外部文档、代码、图片、规格说明和其他材料登记来源、用途及许可信息。当前版本**尚未授予外部材料再分发许可**：在许可状态完成核验并记录前，不复制或打包分发受限材料；引用时保留原作者、来源和必要的版权声明。Arduino、UNO Q 及其他名称仍归其各自权利人所有，本项目不主张相关商标权利。

## 贡献与更新方式

新增或修改章节时，先按照[写作规范](docs/writing-guidelines.md)补齐元数据、代码说明、图示占位和交叉引用，再同步更新 `SUMMARY.md` 及相关资源记录。新增外部来源必须先登记到[参考资料索引](resources/references.md)，并在提交说明中写清验证日期、许可边界和复现结果。变更保持小步、可复现，并在合并前运行本任务或对应章节规定的检查。

## 当前验证记录

最后验证日期：`2026-09-21`。当前已创建并核验的文件/目录如下：

```text
README.md
SUMMARY.md
docs/writing-guidelines.md
resources/references.md
book/第1篇_认识UNOQ/README.md
book/第1篇_认识UNOQ/第1章_Arduino的发展.md
book/第1篇_认识UNOQ/第2章_什么是Arduino_UNO_Q.md
book/第1篇_认识UNOQ/第3章_UNO_Q的硬件架构.md
book/第1篇_认识UNOQ/第4章_UNO_Q的软件架构.md
book/第1篇_认识UNOQ/第5章_第一个实验_Blink验证闭环.md
book/第2篇_STM32/README.md
book/第2篇_STM32/第1章_STM32侧开发基础_GPIO与实时边界.md
book/第2篇_STM32/第2章_PWM与定时输出_从占空比到安全控制.md
book/第2篇_STM32/第3章_ADC与模拟采样_从电压读数到可验证数据.md
book/第2篇_STM32/第4章_串口通信_从帧格式到MCU_Linux边界.md
book/第2篇_STM32/第5章_SPI通信_从片选时序到设备驱动边界.md
book/第2篇_STM32/第6章_I2C通信_从设备地址到总线恢复.md
book/第2篇_STM32/第7章_实时任务与调度_从周期循环到可验证响应.md
book/第2篇_STM32/第8章_硬件验证与故障定位_从接线检查到证据闭环.md
book/第2篇_STM32/第9章_综合实验_传感控制与MCU_Linux协同闭环.md
book/第3篇_Linux/README.md
book/第3篇_Linux/第1章_Linux侧开发基础_文件系统进程与MCU边界.md
book/第3篇_Linux/第2章_Linux设备网络与服务_从可见到可用.md
code/第1章_Arduino的发展/README.md
code/第1章_Arduino的发展/Blink/Blink.ino
code/第1章_Arduino的发展/Blink/README.md
diagrams/arduino-evolution.mmd
diagrams/uno-q-dual-brain.mmd
diagrams/uno-q-execution-boundary.mmd
diagrams/uno-q-hardware-map.mmd
diagrams/uno-q-software-architecture.mmd
diagrams/uno-q-first-experiment-validation.mmd
diagrams/uno-q-stm32-gpio-boundary.mmd
diagrams/uno-q-stm32-pwm-duty-cycle-boundary.mmd
diagrams/uno-q-stm32-adc-measurement-boundary.mmd
diagrams/uno-q-stm32-uart-boundary.mmd
diagrams/uno-q-stm32-spi-boundary.mmd
diagrams/uno-q-stm32-i2c-recovery-boundary.mmd
diagrams/uno-q-stm32-realtime-scheduling-boundary.mmd
diagrams/uno-q-stm32-hardware-verification-boundary.mmd
diagrams/uno-q-stm32-integrated-control-boundary.mmd
diagrams/uno-q-linux-execution-boundary.mmd
diagrams/uno-q-linux-device-network-service-boundary.mmd
images/第1篇_认识UNOQ/README.md
images/第2篇_STM32/README.md
images/第3篇_Linux/README.md
```

本次检查覆盖第一篇、第二篇第 1 章、第二篇第 2 章、第二篇第 3 章、第二篇第 4 章、第二篇第 5 章、第二篇第 6 章、第二篇第 7 章、第二篇第 8 章、第二篇第 9 章、第三篇第 1 章和第三篇第 2 章的文件存在性、相对 Markdown 链接、篇内章节元数据、Mermaid 声明、图示占位、代码说明字段和 UTF-8；GPIO、PWM、ADC、UART、SPI、I2C、实时任务、硬件验证、综合实验、Linux 执行边界和 Linux 设备网络服务边界 Mermaid 源文件已完成一致性检查，但当前环境未安装 mmdc，未生成或验证 SVG，也未执行 arduino-cli 编译、上传、Linux 实机盘点、网络查询、服务观测、ADB/SSH 联调或硬件实机运行。
