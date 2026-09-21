# 参考资料索引

本表是全书外部来源的登记入口。正文引用外部文档、代码、图片、规格说明或数据前，先添加一行并核验 URL、用途和许可边界。日期使用 `YYYY-MM-DD`；无法确认许可时写明“待核验”，不要推断为可再分发。

| 类别 | 名称 | URL | 用途 | 版本/分支（核验时） | 许可证/声明 | 最后核验日期 |
|---|---|---|---|---|---|---|
| 官方文档 | Zephyr GPIO 文档 | https://docs.zephyrproject.org/latest/hardware/peripherals/gpio.html | 核对第二篇第 1 章的 GPIO 抽象、输入/输出/上下拉/中断、Devicetree 与 gpio_dt_spec 关系；本项目只原创整理 API 使用边界。 | 网页内容（核验时） | Zephyr 官方文档，按项目声明使用；本项目只链接和原创解释，不复制示例正文。 | 2026-09-21 |
| 官方示例 | Zephyr Blinky 示例说明 | https://github.com/zephyrproject-rtos/zephyr/blob/main/samples/basic/blinky/README.rst | 核对第二篇第 1 章中 led0、gpio_dt_spec、Devicetree 别名和 GPIO 配置流程的通用示例边界；不将通用示例当作 UNO Q 实测。 | main | Zephyr 官方仓库，按仓库声明使用；本项目只链接和原创重述。 | 2026-09-21 |
| 官方板卡文档 | Zephyr Arduino UNO Q board documentation | https://github.com/zephyrproject-rtos/zephyr/blob/main/boards/arduino/uno_q/doc/index.rst | 核对第二篇第 1 章中 UNO Q 的 QRB2210 MPU、STM32U585 MCU、Zephyr 板卡目标和 MCU 侧开发边界。 | main | Zephyr 官方仓库，按仓库声明使用；本项目只链接和原创重述。 | 2026-09-21 |
| 官方配置 | ArduinoCore-zephyr boards.txt | https://github.com/arduino/ArduinoCore-zephyr/blob/main/boards.txt | 核对第二篇第 1 章中 UNO Q 的 Zephyr 目标、STM32U585 变体、FQBN 和上传配置属于板级构建信息的边界。 | main | Arduino 官方仓库，按仓库声明使用；本项目只链接和原创解释，不复制配置文件。 | 2026-09-21 |
| 官方数据表 | STM32U585xx Datasheet | https://www.st.com/resource/en/datasheet/stm32u585oi.pdf | 核对第二篇第 1 章中 STM32U585 的 GPIO/复用功能和电气参数应回到 MCU 数据表核验的边界；不把通用标称值替代具体板级测量。 | DS13086 Rev 10（核验时） | STMicroelectronics 官方数据表；本项目只链接和原创解释，不复制表格或图片。 | 2026-09-21 |
| 官方文档 | Arduino UNO Q 产品页 | https://docs.arduino.cc/hardware/uno-q | 核对第 2 章的产品定位、双处理器与 Arduino IDE/App Lab 分工，以及第 3 章的 WCBN3536A、Wi-Fi 5、Bluetooth 5.1、UNO headers、Qwiic、底部高速连接器、USB-C 高层用途和内置 RPC，以及第 4 章的 App Lab/IDE/Bridge 边界。 | 网页内容（核验时） | 官方网页，按页面声明使用；本项目只链接和原创重述，不取得外部材料再分发许可 | 2026-09-20 |
| 官方数据表 | Arduino UNO Q 数据表 | https://docs.arduino.cc/resources/datasheets/ABX00162-datasheet.pdf | 核对第 2 章的双处理器与 Bridge/RPC 定位，第 3 章的处理器/运行时、1.8 V/3.3 V 电气域、UNO headers、Qwiic、JMEDIA/JMISC 等连接器、USB-C/供电和硬件边界，第 4 章的处理器与 Bridge/RPC 边界，以及第 5 章 Blink LED、App Lab Run、MCU Sketch 与 Linux/Python 日志的验证边界。 | ABX00162 PDF（核验时） | 官方数据表，按页面声明使用；本项目只链接和原创重述，不取得外部材料再分发许可 | 2026-09-21 |
| 官方文档 | Arduino UNO Q User Manual（arduino/docs-content） | https://github.com/arduino/docs-content/blob/main/content/hardware/02.uno/boards/uno-q/tutorials/01.user-manual/content.md | 核对第 2 章的 UNO Q 架构、MPU/MCU、Debian Linux、Zephyr、Arduino IDE/App Lab 与 Blink 执行边界，第 3 章的 Qwiic `I2C4`/`Wire1` 和 3.3 V、USB-C 高层功能、Arduino IDE/App Lab/CLI 工具边界，第 4 章的 Debian/Zephyr/App Lab/IDE 工作流，以及第 5 章的 IDE Blink 操作路径。 | `main` | docs-content README 说明贡献内容采用 CC BY-SA 4.0；本项目只链接并原创重述，不复制正文或图片；访问不等于本项目取得外部材料再分发许可。 | 2026-09-21 |
| 官方代码仓库 | ArduinoCore-zephyr | https://github.com/arduino/ArduinoCore-zephyr | 核对第 2 章的 UNO Q Zephyr core 与 Arduino IDE/CLI/App Lab 支持说明，第 3 章 MCU 侧基于 Zephyr 的 Arduino Core、Sketch 执行侧与工具支持边界，第 4 章 MCU 侧 Zephyr Core 与 IDE/CLI/App Lab 目标支持，以及第 5 章的 `arduino:zephyr:unoq` FQBN。 | `main` | 仓库当前标注 Apache-2.0；本项目只登记和链接，不复制代码。 | 2026-09-21 |
| 官方文档 | Arduino CLI Getting Started | https://docs.arduino.cc/arduino-cli/getting-started | 核对第 5 章 `compile`、`board list` 和 `upload` 的命令行工作流；不把示例命令输出当成本次实测结果。 | 网页内容（核验时） | 官方文档，按页面声明使用；本项目只链接和原创重述，不取得外部材料再分发许可 | 2026-09-21 |
| 官方示例仓库 | app-bricks-examples | https://github.com/arduino/app-bricks-examples | 核对 App Lab、Brick 和 Learn/示例索引的结构入口。 | `main` | 仓库页面标注 MPL-2.0；REUSE.toml 表示 Arduino authored source/docs/assets 为 MPL-2.0，配置文件可为 CC0-1.0，第三方资产按各自声明；本项目仅作结构参考，不打包其材料。 | 2026-09-16 |
| 社区课程 | Mjrovai/ARDUINO-UNO-Q | https://github.com/Mjrovai/ARDUINO-UNO-Q | 核对社区课程化章节和案例组织方式，只作结构参考。 | `main` | 仓库页面标注 GPL-3.0；本项目不复制其代码、图片或课程正文。 | 2026-09-16 |
| 社区知识库 | CWTI-Ltd/arduino_uno_q_knowledge_base_and_playground | https://github.com/CWTI-Ltd/arduino_uno_q_knowledge_base_and_playground | 核对社区知识库/实践场的组织方式，只作结构参考。 | `main` | README 明确非官方、教育/开发用途、进行中项目；当前未见标准再分发许可证声明，许可状态待核验；本项目不复制其内容。 | 2026-09-16 |

核验边界：官方来源用于 UNO Q 事实基线，社区来源只作课程/知识库结构参考。当前本项目只引用链接和原创解释，不打包外部代码、正文、图片或其他材料；任何外部材料的再分发许可仍需按其文件级声明另行核验。
