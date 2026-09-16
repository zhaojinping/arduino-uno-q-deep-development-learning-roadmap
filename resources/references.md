# 参考资料索引

本表是全书外部来源的登记入口。正文引用外部文档、代码、图片、规格说明或数据前，先添加一行并核验 URL、用途和许可边界。日期使用 `YYYY-MM-DD`；无法确认许可时写明“待核验”，不要推断为可再分发。

| 类别 | 名称 | URL | 用途 | 版本/分支（核验时） | 许可证/声明 | 最后核验日期 |
|---|---|---|---|---|---|

| 官方文档 | Arduino UNO Q User Manual（arduino/docs-content） | https://github.com/arduino/docs-content/blob/main/content/hardware/02.uno/boards/uno-q/tutorials/01.user-manual/content.md | 核对 UNO Q 架构、MPU/MCU、Debian Linux、Zephyr、Arduino IDE、App Lab 和 Blink 的执行边界；网页正文核验到 QRB2210 MPU、STM32U585 MCU、IDE 仅编程 MCU。 | `main` | docs-content README 说明贡献内容采用 CC BY-SA 4.0；本项目只链接并原创重述，不复制正文或图片；访问不等于本项目取得外部材料再分发许可。 | 2026-09-16 |
| 官方代码仓库 | ArduinoCore-zephyr | https://github.com/arduino/ArduinoCore-zephyr | 核对 UNO Q Zephyr core、Arduino IDE/CLI/App Lab 支持说明及代码执行边界。 | `main` | 仓库当前标注 Apache-2.0；本项目只登记和链接，不复制代码。 | 2026-09-16 |
| 官方示例仓库 | app-bricks-examples | https://github.com/arduino/app-bricks-examples | 核对 App Lab、Brick 和 Learn/示例索引的结构入口。 | `main` | 仓库页面标注 MPL-2.0；REUSE.toml 表示 Arduino authored source/docs/assets 为 MPL-2.0，配置文件可为 CC0-1.0，第三方资产按各自声明；本项目仅作结构参考，不打包其材料。 | 2026-09-16 |
| 社区课程 | Mjrovai/ARDUINO-UNO-Q | https://github.com/Mjrovai/ARDUINO-UNO-Q | 核对社区课程化章节和案例组织方式，只作结构参考。 | `main` | 仓库页面标注 GPL-3.0；本项目不复制其代码、图片或课程正文。 | 2026-09-16 |
| 社区知识库 | CWTI-Ltd/arduino_uno_q_knowledge_base_and_playground | https://github.com/CWTI-Ltd/arduino_uno_q_knowledge_base_and_playground | 核对社区知识库/实践场的组织方式，只作结构参考。 | `main` | README 明确非官方、教育/开发用途、进行中项目；当前未见标准再分发许可证声明，许可状态待核验；本项目不复制其内容。 | 2026-09-16 |

核验边界：官方来源用于 UNO Q 事实基线，社区来源只作课程/知识库结构参考。当前本项目只引用链接和原创解释，不打包外部代码、正文、图片或其他材料；任何外部材料的再分发许可仍需按其文件级声明另行核验。
