# Arduino UNO Q 深度开发学习路线：设计说明

> 状态：设计方向已确认，等待规格文档复核
>
> 日期：2026-09-15

## 1. 项目目标

建立一个可长期维护、可公开发布、可持续验证的中文 Markdown 技术书项目，帮助读者从 Arduino 的发展脉络和基础编程出发，逐步掌握 Arduino UNO Q 的双处理器架构、Linux/STM32 协同、Python Bridge、Arduino App Lab、计算机视觉、AI、IoT 和综合项目开发。

项目交付形态为一个独立 Git 仓库，正文、代码、图示、资源索引和后续章节保持清晰分离。首期交付第一篇“认识 Arduino UNO Q”，并完成第 1 章“Arduino 的发展”。

## 2. 调研结论与定位

GitHub 上已经存在几类相关资源，但定位不同：

- [Arduino 官方 UNO Q User Manual](https://github.com/arduino/docs-content/blob/main/content/hardware/02.uno/boards/uno-q/tutorials/01.user-manual/content.md) 是硬件和软件事实基线，覆盖 App Lab、Arduino IDE、双处理器和板载外设，但不是完整学习路线。
- [Mjrovai/ARDUINO-UNO-Q](https://github.com/Mjrovai/ARDUINO-UNO-Q) 已形成 Setup、生成式 AI、多模态 AI、Agentic AI 和固定功能 AI 等课程式内容，适合作为高级实践案例参考。
- [CWTI-Ltd/arduino_uno_q_knowledge_base_and_playground](https://github.com/CWTI-Ltd/arduino_uno_q_knowledge_base_and_playground) 提供了从入门、硬件、软件、部署、示例到参考的知识库结构，但仓库自身注明仍在完善中且不是官方文档。
- [SunFounder/unoq-ai-kit](https://github.com/sunfounder/unoq-ai-kit) 更接近面向初学者的套件课程，适合借鉴实验递进和教学表达。
- [MartinsRepo/Arduino-Uno-Q-Projects](https://github.com/MartinsRepo/Arduino-Uno-Q-Projects) 和 [arduino/app-bricks-examples](https://github.com/arduino/app-bricks-examples) 更偏项目案例与官方示例。

本项目不复制上述项目的正文，而是吸收其结构经验，形成“中文、路线化、出版级、跨层解释、可验证代码”的差异化定位。对外部内容只做链接、摘要、独立改写和必要的来源说明；代码或图片复用前必须单独核对许可证和归属要求。

## 3. 目标读者与学习结果

### 3.1 目标读者

1. 具备基础电脑操作能力、希望系统学习 Arduino 和 UNO Q 的初学者。
2. 已会 Arduino C/C++，希望理解 Linux、Python、Bridge 和 App Lab 的开发者。
3. 需要把传感器、实时控制、AI 推理和网络服务组合成完整项目的工程学习者。

### 3.2 学习结果

完成全书后，读者应能够：

- 解释 Arduino 从 AVR 开发板到 UNO Q 双处理器平台的关键演进。
- 区分 UNO Q 的 Qualcomm QRB2210 MPU、STM32U585 MCU、Debian Linux 和 Zephyr/Arduino 运行边界。
- 使用 Arduino IDE、Arduino App Lab、CLI、ADB、SSH 和 Python 组织开发流程。
- 让 MCU 负责确定性硬件控制，让 MPU 负责 Linux、网络、模型和应用编排。
- 使用 Bridge/RPC 让两个处理器协同工作。
- 从基础实验逐步完成可部署的 IoT、视觉和 AIoT 项目。

## 4. 内容架构

项目根目录使用用户确认的中文项目名称：

```text
Arduino UNO Q 深度开发学习路线/
├── README.md
├── SUMMARY.md
├── book/
│   ├── 第1篇_认识UNOQ/
│   ├── 第2篇_STM32/
│   ├── 第3篇_Linux/
│   ├── 第4篇_PythonBridge/
│   ├── 第5篇_AppLab/
│   ├── 第6篇_OpenCV/
│   ├── 第7篇_AI/
│   ├── 第8篇_IoT/
│   └── 第9篇_Project/
├── code/
├── diagrams/
├── images/
├── resources/
└── docs/
    ├── superpowers/
    │   ├── specs/
    │   └── plans/
    └── writing-guidelines.md
```

### 4.1 各目录职责

- `README.md`：项目定位、适用人群、阅读方式、版本状态、贡献方式和版权边界。
- `SUMMARY.md`：全书唯一目录入口，所有已发布章节都必须在此登记。
- `book/`：出版正文，按照篇和章组织，不直接混入临时草稿。
- `code/`：与章节对应的完整可运行示例，目录名与章节名保持一致。
- `diagrams/`：可复用的 Mermaid 源文件、架构图源文件和图示说明。
- `images/`：最终插图、截图和经过许可的外部图片；每张图记录来源或生成方式。
- `resources/`：官方链接、社区项目、数据手册、术语表和版本记录。
- `docs/`：项目设计、写作规范、计划和维护说明，不作为正文阅读入口。

### 4.2 九篇的职责边界

1. **第一篇：认识 Arduino UNO Q**：Arduino 历史、UNO Q 定位、板卡架构、开发模式和第一个实验。
2. **第二篇：STM32**：MCU、GPIO、PWM、ADC、串口、SPI、I2C、Zephyr 和实时控制。
3. **第三篇：Linux**：MPU、Debian、文件系统、网络、进程、服务、ADB 和 SSH。
4. **第四篇：Python Bridge**：Python 应用、Bridge/RPC、消息边界、并发和错误处理。
5. **第五篇：App Lab**：App、Brick、项目结构、运行、日志、启动项和部署。
6. **第六篇：OpenCV**：摄像头、图像处理、视觉管线和硬件反馈。
7. **第七篇：AI**：模型推理、TinyML、边缘 AI、生成式 AI 和工具调用边界。
8. **第八篇：IoT**：传感器、网络协议、数据上报、可观测性和远程运维。
9. **第九篇：Project**：从需求、架构、实现、测试到部署的完整综合项目。

## 5. 正文写作规范

每章使用统一的章节元数据和结构：

```yaml
---
title: Arduino 的发展
part: 1
chapter: 1
status: draft
last_verified: 2026-09-15
---
```

正文顺序固定为：

1. 学习目标
2. 本章导读
3. 背景与问题
4. 核心概念
5. 架构图或时间线
6. 代码示例或实验
7. 常见误区
8. 与 UNO Q 的连接
9. 本章小结
10. 交叉引用与延伸阅读

章节标题使用“第 N 章_主题.md”格式，代码目录使用“第 N 章_主题/”格式。术语首次出现时给出中文名、英文名和缩写，后续统一使用同一称呼。

## 6. 图示、占位图和代码约定

### 6.1 图示

- 时间线、组件关系、数据流和状态转换优先使用 Mermaid。
- Mermaid 图必须配有一段文字说明，不能只依赖图形表达。
- 需要实拍图或最终插图时，正文先使用明确的占位符，例如：

  > 图 1-1（占位）：Arduino 从经典 AVR 板卡向 UNO Q 双处理器平台演进的时间线。最终图应标注关键代际、平台能力和学习重点。

- 最终图片放入 `images/<篇或章>/`，文件名包含章节号和图号，例如 `ch01-fig01-arduino-evolution.svg`。
- 每张外部图片必须在 `resources/references.md` 或图片旁的说明文件中记录来源、许可证和访问日期。

### 6.2 代码

- 正文中的代码保持短小，用于解释概念；完整项目放在 `code/`。
- 每个示例都包含用途、前置条件、运行方法、预期现象和已知限制。
- 首章使用 Blink 作为 Arduino 编程模型的连续性示例，同时明确说明 UNO Q 上的 Blink 由 MCU 侧执行，不能据此推断 MPU 侧应用已经运行。
- 代码示例的板卡、核心、工具和验证日期必须写明；无法在当前环境实机验证的内容必须标注为静态检查或待硬件验证，而不是声称已经运行。

## 7. 第一阶段交付范围

第一阶段只完成第一篇的基础工程和第一章，不提前填充后续篇章正文：

- 项目级 `README.md`。
- 项目级 `SUMMARY.md`。
- `book/第1篇_认识UNOQ/README.md`，说明本篇目标、章节地图和前置知识。
- `book/第1篇_认识UNOQ/第1章_Arduino的发展.md`。
- `code/第1章_Arduino的发展/` 下的 Blink 示例及其说明。
- 至少一幅 Mermaid 演进时间线和一幅“传统 MCU 开发到 UNO Q 双处理器开发”的关系图。
- `images/` 中的图示占位说明。
- `resources/references.md`，登记官方文档和本次 GitHub 调研得到的参考项目。

### 7.1 第一章内容边界

第一章“Arduino 的发展”包含：

1. Arduino 解决的入门和原型开发问题。
2. 经典 AVR 时代的开发模型：开发板、Bootloader、Arduino API 和示例驱动学习。
3. 32 位 ARM、网络连接和物联网能力带来的变化。
4. 从单 MCU 到“MPU + MCU”协同的需求背景。
5. UNO Q 的定位：Linux/高性能计算与实时硬件控制的结合。
6. Blink 示例作为跨代际的共同起点。
7. 从本章到后续 STM32、Linux、Python Bridge、App Lab 和综合项目的学习路线。

第一章不承担完整的 UNO Q 硬件规格表、全部外设 API、Linux 运维或 AI 模型教程，这些内容分别留给后续篇章。

## 8. 来源、版本和版权策略

- 官方 Arduino 文档是硬件特性、工具行为和 API 说明的首要依据。
- 社区仓库只作为案例、结构和问题线索；关键事实需要回到官方文档核验。
- 每章维护“来源与验证”小节，记录链接、访问日期、适用软件版本和是否已实机验证。
- 不复制外部教程的大段文字、图片或章节结构；对代码只在许可证允许且有明确归属时复用，并优先重写为独立示例。
- 项目自身正文和原创图示使用后续在 `README.md` 中明确声明的许可证；外部材料的许可证不自动延伸到本项目。

## 9. 迭代和质量门槛

每增加一章，都必须完成以下检查：

1. 文件已加入 `SUMMARY.md`，相对链接能够从当前文件位置解析。
2. 章节包含学习目标、正文、示例、总结和来源。
3. Mermaid 代码块具备完整的图类型声明和节点关系。
4. 代码示例具有清晰的运行边界，未把静态检查描述成实机验证。
5. 新增事实与官方文档或明确的社区来源相互对应。
6. 术语、章节编号、图号和代码目录命名没有冲突。
7. 只检查和修改本项目范围内的文件，不覆盖已有用户文件。

首次发布前，再增加 Markdown 链接检查、代码示例静态检查、目录一致性检查和整书渲染预览。Git 提交和远程 GitHub 推送必须由用户单独授权。
