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

当前状态：**第一篇第 1～5 章已完成，第二篇第 1 章正在持续写作**。Blink 示例和 Mermaid 源文件已存在；第一篇第 5 章提供 IDE、CLI、App Lab 的验证闭环，但本环境仍未完成 Arduino CLI 编译、上传和硬件实机验证。章节编号按篇重置，第二篇不使用“第 6 章”。

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
images/第1篇_认识UNOQ/README.md
images/第2篇_STM32/README.md
```

本次检查覆盖第一篇与第二篇第 1 章的文件存在性、相对 Markdown 链接、篇内章节元数据、Mermaid 声明、图示占位、代码说明字段和 UTF-8；Mermaid 源文件已完成一致性检查，但当前环境未安装 `mmdc`，未生成或验证 SVG，也未执行 `arduino-cli` 编译、上传或硬件实机运行。
