# 参考资料索引

本表是全书外部来源的登记入口。正文引用外部文档、代码、图片、规格说明或数据前，先添加一行并核验 URL、用途和许可边界。日期使用 `YYYY-MM-DD`；无法确认许可时写明“待核验”，不要推断为可再分发。

| 类别 | 名称 | URL | 用途 | 版本/分支（核验时） | 许可证/声明 | 最后核验日期 |
|---|---|---|---|---|---|---|
| 官方文档 | Arduino UNO Q 产品页 | https://docs.arduino.cc/hardware/uno-q | 核对第 2 章的产品定位、双处理器与 Arduino IDE/App Lab 分工，以及第 3 章的 WCBN3536A、Wi-Fi 5、Bluetooth 5.1、UNO headers、Qwiic、底部高速连接器、USB-C 高层用途和内置 RPC。 | 网页内容（核验时） | 官方网页，按页面声明使用；本项目只链接和原创重述，不取得外部材料再分发许可 | 2026-09-20 |
| 官方数据表 | Arduino UNO Q 数据表 | https://docs.arduino.cc/resources/datasheets/ABX00162-datasheet.pdf | 核对第 2 章的双处理器与 Bridge/RPC 定位，以及第 3 章的处理器/运行时、1.8 V/3.3 V 电气域、UNO headers、Qwiic、JMEDIA/JMISC 等连接器、USB-C/供电、Bridge/RPC 与常见问题所引用的硬件边界。 | ABX00162 PDF（核验时） | 官方数据表，按页面声明使用；本项目只链接和原创重述，不取得外部材料再分发许可 | 2026-09-20 |
| 官方文档 | Arduino UNO Q User Manual（arduino/docs-content） | https://github.com/arduino/docs-content/blob/main/content/hardware/02.uno/boards/uno-q/tutorials/01.user-manual/content.md | 核对第 2 章的 UNO Q 架构、MPU/MCU、Debian Linux、Zephyr、Arduino IDE/App Lab 与 Blink 执行边界，以及第 3 章的 Qwiic `I2C4`/`Wire1` 和 3.3 V、USB-C 高层功能、Arduino IDE/App Lab/CLI 工具边界。 | `main` | docs-content README 说明贡献内容采用 CC BY-SA 4.0；本项目只链接并原创重述，不复制正文或图片；访问不等于本项目取得外部材料再分发许可。 | 2026-09-20 |
| 官方代码仓库 | ArduinoCore-zephyr | https://github.com/arduino/ArduinoCore-zephyr | 核对第 2 章的 UNO Q Zephyr core 与 Arduino IDE/CLI/App Lab 支持说明，以及第 3 章 MCU 侧基于 Zephyr 的 Arduino Core、Sketch 执行侧与工具支持边界。 | `main` | 仓库当前标注 Apache-2.0；本项目只登记和链接，不复制代码。 | 2026-09-20 |
| 官方示例仓库 | app-bricks-examples | https://github.com/arduino/app-bricks-examples | 核对 App Lab、Brick 和 Learn/示例索引的结构入口。 | `main` | 仓库页面标注 MPL-2.0；REUSE.toml 表示 Arduino authored source/docs/assets 为 MPL-2.0，配置文件可为 CC0-1.0，第三方资产按各自声明；本项目仅作结构参考，不打包其材料。 | 2026-09-16 |
| 社区课程 | Mjrovai/ARDUINO-UNO-Q | https://github.com/Mjrovai/ARDUINO-UNO-Q | 核对社区课程化章节和案例组织方式，只作结构参考。 | `main` | 仓库页面标注 GPL-3.0；本项目不复制其代码、图片或课程正文。 | 2026-09-16 |
| 社区知识库 | CWTI-Ltd/arduino_uno_q_knowledge_base_and_playground | https://github.com/CWTI-Ltd/arduino_uno_q_knowledge_base_and_playground | 核对社区知识库/实践场的组织方式，只作结构参考。 | `main` | README 明确非官方、教育/开发用途、进行中项目；当前未见标准再分发许可证声明，许可状态待核验；本项目不复制其内容。 | 2026-09-16 |

核验边界：官方来源用于 UNO Q 事实基线，社区来源只作课程/知识库结构参考。当前本项目只引用链接和原创解释，不打包外部代码、正文、图片或其他材料；任何外部材料的再分发许可仍需按其文件级声明另行核验。
