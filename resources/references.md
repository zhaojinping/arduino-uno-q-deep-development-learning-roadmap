# 参考资料索引

本表是全书外部来源的登记入口。正文引用外部文档、代码、图片、规格说明或数据前，先添加一行并核验 URL、用途和许可边界。日期使用 `YYYY-MM-DD`；无法确认许可时写明“待核验”，不要推断为可再分发。

| 类别 | 名称 | URL | 用途 | 版本/分支（核验时） | 许可证/声明 | 最后核验日期 |
|---|---|---|---|---|---|---|
| 官方数据表 | Arduino UNO Q ADC/模拟输入边界（ABX00162-ABX00173） | https://docs.arduino.cc/resources/datasheets/ABX00162-ABX00173-datasheet.pdf | 核对第二篇第3章 A0～A5 映射、3.3 V 模拟域、VREF+、0～VREF+范围和 ADC 模式下的 5 V 电气边界。 | ABX00162-ABX00173 PDF（核验时） | 官方数据表；本项目只链接和原创解释，不复制表格或图片。 | 2026-09-21 |
| 官方配置 | ArduinoCore-zephyr UNO Q ADC overlay | https://github.com/arduino/ArduinoCore-zephyr/blob/main/variants/arduino_uno_q_stm32u585xx/arduino_uno_q_stm32u585xx.overlay | 核对第二篇第3章 A0～A5 的 adc-pin-gpios、io-channels 和 ADC1 通道当前 main 分支描述；不把当前映射承诺为未来版本或实机测量。 | main | Arduino 官方仓库；本项目只链接和原创解释，不复制配置文件。 | 2026-09-21 |
| 官方代码 | ArduinoCore-zephyr wiring_analog.cpp | https://github.com/arduino/ArduinoCore-zephyr/blob/main/cores/arduino/wiring_analog.cpp | 核对第二篇第3章 analogRead() 的逻辑引脚映射、分辨率设置、通道配置和 adc_read() 代码边界。 | main | Arduino 官方仓库；本项目只链接和原创解释，不复制代码。 | 2026-09-21 |
| 官方参考 | Arduino analogRead 参考 | https://github.com/arduino/reference-en/blob/master/Language/Functions/Analog%20IO/analogRead.adoc | 核对第二篇第3章 Arduino 模拟读取的通用语义和不同板卡的分辨率/电压差异；不把通用表格当作 UNO Q 实测。 | master | Arduino 官方参考仓库；本项目只链接和原创重述。 | 2026-09-21 |
| 官方 API | Zephyr ADC API 参考 | https://docs.zephyrproject.org/latest/doxygen/html/group__adc__interface.html | 核对第二篇第3章 adc_dt_spec、adc_channel_setup_dt、adc_sequence_init_dt、adc_read_dt、参考获取和原始码换算接口。 | 网页内容（核验时） | Zephyr 官方文档；本项目只链接和原创解释。 | 2026-09-21 |
| 官方示例 | Zephyr ADC 示例索引 | https://docs.zephyrproject.org/latest/samples/drivers/adc/index.html | 核对第二篇第3章 sequence、Devicetree 和 stream 示例的职责边界；不把通用示例当作 UNO Q 原生工程验证。 | 网页内容（核验时） | Zephyr 官方文档；本项目只链接和原创重述。 | 2026-09-21 |
| 官方 API | Zephyr adc_sequence 结构说明 | https://docs.zephyrproject.org/latest/doxygen/html/structadc__sequence.html | 核对第二篇第3章 channels、buffer、resolution、oversampling 和采样选项含义。 | 网页内容（核验时） | Zephyr 官方文档；本项目只链接和原创解释。 | 2026-09-21 |
| 官方参考 | Arduino Serial.begin() 参考 | https://github.com/arduino/reference-en/blob/master/Language/Functions/Communication/Serial/begin.adoc | 核对第二篇第4章波特率、数据位、校验位、停止位和默认 8N1 的通用语义；不把通用参考当作 UNO Q 实测。 | master | Arduino 官方参考仓库；本项目只链接和原创重述。 | 2026-09-21 |
| 官方参考 | Arduino Serial.available() 参考 | https://github.com/arduino/reference-en/blob/master/Language/Functions/Communication/Serial/available.adoc | 核对第二篇第4章接收缓冲区字节可用数量和 read() 配合方式；不把通用缓冲大小承诺为 UNO Q Core 固定值。 | master | Arduino 官方参考仓库；本项目只链接和原创重述。 | 2026-09-21 |
| 官方配置 | ArduinoCore-zephyr 变体配置说明 | https://github.com/arduino/ArduinoCore-zephyr/blob/main/documentation/variants.md | 核对第二篇第4章 serials 属性与 Serial、Serial1 等对象实例化的通用规则；不把通用规则替代 UNO Q 实机路由验证。 | main | Arduino 官方仓库；本项目只链接和原创解释，不复制配置文件。 | 2026-09-21 |
| 官方配置 | ArduinoCore-zephyr UNO Q 当前 UART overlay | https://github.com/arduino/ArduinoCore-zephyr/blob/main/variants/arduino_uno_q_stm32u585xx/arduino_uno_q_stm32u585xx.overlay | 核对第二篇第4章 router-serial、serials、USART3 pinctrl、D20/D21 和当前 UART 资源声明；不把 main 分支声明当作实机回环结果。 | main | Arduino 官方仓库；本项目只链接和原创解释，不复制配置文件。 | 2026-09-21 |
| 官方板卡文档 | Zephyr UNO Q 板级 DTS | https://github.com/zephyrproject-rtos/zephyr/blob/main/boards/arduino/uno_q/arduino_uno_q.dts | 核对第二篇第4章 UNO Q Zephyr console 的板级来源；不把 console 设备文件等同于任意物理 UART 排针。 | main | Zephyr 官方仓库；本项目只链接和原创解释，不复制配置文件。 | 2026-09-21 |
| 官方 API | ArduinoCore-API HardwareSerial 接口 | https://github.com/arduino/ArduinoCore-API/blob/master/api/HardwareSerial.h | 核对第二篇第4章 HardwareSerial 的 begin、available、read、flush、write 抽象和串口配置常量。 | master | Arduino 官方仓库；本项目只链接和原创解释，不复制代码。 | 2026-09-21 |
| 官方文档 | Zephyr UART 外设文档 | https://docs.zephyrproject.org/latest/hardware/peripherals/uart.html | 核对第二篇第4章轮询、中断驱动和异步/DMA 三类 API，以及同一 UART 外设不能混用中断与异步回调的边界。 | 网页内容（核验时） | Zephyr 官方文档；本项目只链接和原创解释。 | 2026-09-21 |
| 官方 API | Zephyr 轮询 UART API | https://docs.zephyrproject.org/latest/doxygen/html/group__uart__polling.html | 核对第二篇第4章 uart_poll_in() 的非阻塞语义、uart_poll_out() 的阻塞语义和错误边界。 | 网页内容（核验时） | Zephyr 官方文档；本项目只链接和原创解释。 | 2026-09-21 |
| 官方 API | Zephyr 中断 UART API | https://docs.zephyrproject.org/latest/doxygen/html/group__uart__interrupt.html | 核对第二篇第4章回调、FIFO、收发中断和错误中断的接口边界。 | 网页内容（核验时） | Zephyr 官方文档；本项目只链接和原创解释。 | 2026-09-21 |
| 官方 API | Zephyr 异步 UART API | https://docs.zephyrproject.org/latest/doxygen/html/group__uart__async.html | 核对第二篇第4章 uart_rx_enable、缓冲请求/释放、UART_RX_RDY、UART_TX_DONE 和 UART_TX_ABORTED 等事件。 | 网页内容（核验时） | Zephyr 官方文档；本项目只链接和原创解释。 | 2026-09-21 |
| 官方示例 | Zephyr UART 示例索引 | https://docs.zephyrproject.org/latest/samples/drivers/uart/README.html | 核对第二篇第4章 echo、passthrough、TTY 和异步示例的职责边界；不把通用示例当作 UNO Q 原生工程验证。 | 网页内容（核验时） | Zephyr 官方文档；本项目只链接和原创重述。 | 2026-09-21 |
| 官方文档 | Zephyr PWM 文档 | https://docs.zephyrproject.org/latest/hardware/peripherals/pwm.html | 核对第二篇第 2 章的 PWM 周期、脉宽、占空比、时间单位辅助宏、Devicetree pwms 和 pwm_set/pwm_set_dt 通用 API 边界。 | 网页内容（核验时） | Zephyr 官方文档，按项目声明使用；本项目只链接和原创解释，不复制示例正文。 | 2026-09-21 |
| 官方示例 | Zephyr PWM Blinky 示例说明 | https://github.com/zephyrproject-rtos/zephyr/blob/main/samples/basic/blinky_pwm/README.rst | 核对第二篇第 2 章中 pwm_led0 别名和板级 PWM 示例所需的 Devicetree 前提；不将通用示例当作 UNO Q 实测。 | main | Zephyr 官方仓库，按仓库声明使用；本项目只链接和原创重述。 | 2026-09-21 |
| 官方 API | Zephyr pwm_dt_spec API 说明 | https://docs.zephyrproject.org/latest/doxygen/html/structpwm__dt__spec.html | 核对第二篇第 2 章中 PWM 设备、通道、周期和标志的资源描述。 | 网页内容（核验时） | Zephyr 官方文档，按项目声明使用；本项目只链接和原创解释。 | 2026-09-21 |
| 官方 API | Zephyr PWM API 参考 | https://docs.zephyrproject.org/latest/doxygen/html/group__pwm__interface.html | 核对第二篇第 2 章中 pwm_set_dt 和 PWM 接口调用边界。 | 网页内容（核验时） | Zephyr 官方文档，按项目声明使用；本项目只链接和原创解释。 | 2026-09-21 |
| 官方参考 | Arduino analogWrite 参考 | https://github.com/arduino/reference-en/blob/master/Language/Functions/Analog%20IO/analogWrite.adoc | 核对第二篇第 2 章中 Arduino 高层 PWM 入口的通用语义；UNO Q 的实际映射和参数范围仍回到目标 Core 核验。 | master | Arduino 官方参考仓库，按仓库声明使用；本项目只链接和原创重述。 | 2026-09-21 |
| 官方配置 | ArduinoCore-zephyr UNO Q 变体 overlay | https://github.com/arduino/ArduinoCore-zephyr/blob/main/variants/arduino_uno_q_stm32u585xx/arduino_uno_q_stm32u585xx.overlay | 核对第二篇第 2 章中当前仓库分支的 UNO Q 板级 PWM/引脚描述入口；不把当前 main 的映射承诺为未来版本或实机测量结果。 | main | Arduino 官方仓库，按仓库声明使用；本项目只链接和原创解释，不复制配置文件。 | 2026-09-21 |
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

| 官方参考 | Arduino SPI 官方参考 | https://github.com/arduino/reference-en/blob/master/Language/Functions/Communication/SPI.adoc | 核对第二篇第5章 SPISettings、begin、beginTransaction、endTransaction、transfer、usingInterrupt 以及不同板卡默认 SPI 引脚说明；不把其他板卡引脚表当作 UNO Q 实测。 | master | Arduino 官方参考仓库；本项目只链接和原创重述。 | 2026-09-21 |
| 官方配置 | ArduinoCore-zephyr UNO Q 当前 SPI overlay | https://github.com/arduino/ArduinoCore-zephyr/blob/main/variants/arduino_uno_q_stm32u585xx/arduino_uno_q_stm32u585xx.overlay | 核对第二篇第5章 spis = <&spi2>, <&spi3>、SPI 延迟初始化、device0 节点及当前 GPIO 资源声明；不把源代码声明当作实物接线、CS 或波形结果。 | main | Arduino 官方仓库；本项目只链接和原创解释，不复制配置文件。 | 2026-09-21 |
| 官方配置 | ArduinoCore-zephyr 变体配置说明 | https://github.com/arduino/ArduinoCore-zephyr/blob/main/documentation/variants.md | 核对第二篇第5章变体资源数组和 Arduino 外设对象配置的边界；不把通用规则替代 UNO Q 当前 overlay 和构建结果。 | main | Arduino 官方仓库；本项目只链接和原创解释，不复制配置文件。 | 2026-09-21 |
| 官方文档 | Zephyr SPI 外设文档 | https://docs.zephyrproject.org/latest/hardware/peripherals/spi.html | 核对第二篇第5章 controller/peripheral、SDO/SDI/CS 术语和旧术语兼容边界。 | 网页内容（核验时） | Zephyr 官方文档；本项目只链接和原创解释。 | 2026-09-21 |
| 官方 API | Zephyr SPI API 参考 | https://docs.zephyrproject.org/latest/doxygen/html/group__spi__interface.html | 核对第二篇第5章 spi_dt_spec、SPI_DT_SPEC_GET、spi_buf、spi_buf_set、spi_is_ready_dt、spi_transceive_dt、操作标志、CS 保持和锁相关接口。 | Zephyr API 网页（核验时） | Zephyr 官方文档；本项目只链接和原创解释。 | 2026-09-21 |
| 官方 API | Zephyr Devicetree SPI API | https://docs.zephyrproject.org/latest/doxygen/html/group__devicetree-spi.html | 核对第二篇第5章 cs-gpios、SPI 外设 reg/CS 索引以及 CS 查询宏的关系。 | Zephyr API 网页（核验时） | Zephyr 官方文档；本项目只链接和原创解释。 | 2026-09-21 |
| 官方迁移说明 | Zephyr 4.5 SPI 术语迁移 | https://docs.zephyrproject.org/latest/releases/migration-guide-4.5.html | 核对第二篇第5章 controller/peripheral inclusive API 名称迁移及旧 master/slave 宏的版本边界。 | 网页内容（核验时） | Zephyr 官方文档；本项目只链接和原创解释。 | 2026-09-21 |

| 官方参考 | Arduino Wire 官方参考 | https://github.com/arduino/reference-en/blob/master/Language/Functions/Communication/Wire.adoc | 核对第二篇第6章 7 位地址、SDA/SCL 上拉、Wire 事务、请求读取、超时和通用缓冲边界；不把通用实现细节当作 UNO Q 实测。 | master | Arduino 官方参考仓库；本项目只链接和原创重述。 | 2026-09-21 |
| 官方参考 | Arduino Wire endTransmission() | https://github.com/arduino/reference-en/blob/master/Language/Functions/Communication/Wire/endTransmission.adoc | 核对第二篇第6章 endTransmission(false) 的重复 START 语义和 0～5 返回值；不把返回码映射替代目标 Core 验证。 | master | Arduino 官方参考仓库；本项目只链接和原创重述。 | 2026-09-21 |
| 官方板卡文档 | Arduino UNO Q User Manual | https://github.com/arduino/docs-content/blob/main/content/hardware/02.uno/boards/uno-q/tutorials/01.user-manual/content.md | 核对第二篇第6章 Qwiic 连接到 I2C4、Arduino 侧使用 Wire1 和 3.3 V 电气边界；不把手册连接关系替代实机接线测量。 | main | Arduino 官方文档；本项目只链接和原创重述。 | 2026-09-21 |
| 官方配置 | ArduinoCore-zephyr UNO Q 当前 I2C overlay | https://github.com/arduino/ArduinoCore-zephyr/blob/main/variants/arduino_uno_q_stm32u585xx/arduino_uno_q_stm32u585xx.overlay | 核对第二篇第6章 i2cs = <&i2c2>, <&i2c4>, <&i2c3>、I2C4/I2C3 状态、pinctrl、延迟初始化和 FAST 速率声明；不把源代码声明当作物理波形。 | main | Arduino 官方仓库；本项目只链接和原创解释，不复制配置文件。 | 2026-09-21 |
| 官方配置 | ArduinoCore-zephyr 变体配置说明 | https://github.com/arduino/ArduinoCore-zephyr/blob/main/documentation/variants.md | 核对第二篇第6章 i2cs 数组顺序与 Wire、Wire1、Wire2 对象的通用关系；不把通用顺序替代最终构建核验。 | main | Arduino 官方仓库；本项目只链接和原创解释。 | 2026-09-21 |
| 官方文档 | Zephyr I2C 外设文档 | https://docs.zephyrproject.org/latest/hardware/peripherals/i2c.html | 核对第二篇第6章 controller/target、控制器事务、时钟拉伸、超时配置和目标 API 的支持边界。 | 网页内容（核验时） | Zephyr 官方文档；本项目只链接和原创解释。 | 2026-09-21 |
| 官方 API | Zephyr I2C API 参考 | https://docs.zephyrproject.org/latest/doxygen/html/group__i2c__interface.html | 核对第二篇第6章 i2c_dt_spec、I2C_DT_SPEC_GET、i2c_is_ready_dt、i2c_write_read_dt、i2c_recover_bus、事务标志和错误返回。 | 网页内容（核验时） | Zephyr 官方文档；本项目只链接和原创解释。 | 2026-09-21 |
| 官方协议资料 | NXP UM10204 I2C-bus specification and user manual | https://www.nxp.com/webapp/Download?colCode=UM10204&location=null | 核对第二篇第6章开漏/上拉、START/STOP、ACK/NACK、时钟拉伸、仲裁和总线清理的协议背景。 | UM10204（核验时） | NXP 官方协议资料；本项目只链接和原创解释，不复制正文或图表。 | 2026-09-21 |

| 官方文档 | Zephyr Threads | https://docs.zephyrproject.org/latest/kernel/services/threads/index.html | 核对第二篇第7章线程生命周期、栈、优先级、合作式/可抢占线程和线程上下文边界。 | 网页内容（核验时） | Zephyr 官方文档；本项目只链接和原创解释。 | 2026-09-21 |
| 官方文档 | Zephyr Scheduling | https://docs.zephyrproject.org/latest/kernel/services/scheduling/index.html | 核对第二篇第7章 ready 线程选择、调度点、时间片、k_sleep、k_yield 和合作式线程阻塞风险。 | 网页内容（核验时） | Zephyr 官方文档；本项目只链接和原创解释。 | 2026-09-21 |
| 官方文档 | Zephyr Kernel Timing | https://docs.zephyrproject.org/latest/kernel/services/timing/clocks.html | 核对第二篇第7章 k_uptime_get、k_uptime_get_32、k_timeout_t、k_timer 和 k_work_delayable 的时间语义。 | 网页内容（核验时） | Zephyr 官方文档；本项目只链接和原创解释。 | 2026-09-21 |
| 官方文档 | Zephyr Workqueue Threads | https://docs.zephyrproject.org/latest/kernel/services/threads/workqueue.html | 核对第二篇第7章延迟工作、系统工作队列、阻塞工作处理器和额外工作队列的成本边界。 | 网页内容（核验时） | Zephyr 官方文档；本项目只链接和原创解释。 | 2026-09-21 |
| 官方文档 | Zephyr Message Queues | https://docs.zephyrproject.org/latest/kernel/services/data_passing/message_queues.html | 核对第二篇第7章固定大小消息队列、ISR/线程入队出队、队列满和数据复制语义。 | 网页内容（核验时） | Zephyr 官方文档；本项目只链接和原创解释。 | 2026-09-21 |
| 官方 API | Zephyr Mutex APIs | https://docs.zephyrproject.org/latest/doxygen/html/group__mutex__apis.html | 核对第二篇第7章 k_mutex_lock、k_mutex_unlock、超时和互斥不能在 ISR 中使用的边界。 | 网页内容（核验时） | Zephyr 官方文档；本项目只链接和原创解释。 | 2026-09-21 |
| 官方 API | Zephyr Watchdog API | https://docs.zephyrproject.org/latest/doxygen/html/group__watchdog__interface.html | 核对第二篇第7章 wdt_install_timeout、wdt_setup、wdt_feed 和看门狗错误返回边界。 | 网页内容（核验时） | Zephyr 官方文档；本项目只链接和原创解释。 | 2026-09-21 |
| 官方文档 | Zephyr Task Watchdog | https://docs.zephyrproject.org/latest/services/task_wdt/index.html | 核对第二篇第7章多任务健康监督、任务看门狗通道、硬件看门狗回退和复位边界。 | 网页内容（核验时） | Zephyr 官方文档；本项目只链接和原创解释。 | 2026-09-21 |

| 官方文档 | Arduino CLI Getting Started | https://docs.arduino.cc/arduino-cli/getting-started | 核对第二篇第8章列板、FQBN、compile、upload 和运行验证的阶段边界；不把通用示例输出当作 UNO Q 实测。 | 网页内容（核验时） | Arduino 官方文档；本项目只链接和原创重述。 | 2026-09-21 |
| 官方文档 | Zephyr Application Development | https://docs.zephyrproject.org/latest/develop/application/index.html | 核对第二篇第8章应用目录、prj.conf、overlay、独立 build 目录、west build 和 west flash 的流程边界。 | 网页内容（核验时） | Zephyr 官方文档；本项目只链接和原创解释。 | 2026-09-21 |
| 官方文档 | Zephyr Building, Flashing and Debugging | https://docs.zephyrproject.org/latest/develop/west/build-flash-debug.html | 核对第二篇第8章 west build、west boards、west flash 和构建/刷写产物的证据边界。 | 网页内容（核验时） | Zephyr 官方文档；本项目只链接和原创解释。 | 2026-09-21 |
| 官方文档 | Zephyr Peripherals | https://docs.zephyrproject.org/latest/hardware/peripherals/index.html | 核对第二篇第8章 GPIO、PWM、ADC、UART、SPI、I2C 等外设 API 分类和资源验证的范围边界。 | 网页内容（核验时） | Zephyr 官方文档；本项目只链接和原创解释。 | 2026-09-21 |

| 官方板卡文档 | Arduino UNO Q User Manual（综合实验边界） | https://github.com/arduino/docs-content/blob/main/content/hardware/02.uno/boards/uno-q/tutorials/01.user-manual/content.md | 核对第二篇第9章双处理器、MCU/Linux/Bridge、Qwiic、工具和状态交接的事实边界；不把手册内容替代综合实测。 | main | Arduino 官方文档；本项目只链接和原创重述。 | 2026-09-21 |
| 官方代码仓库 | ArduinoCore-zephyr（综合实验资源边界） | https://github.com/arduino/ArduinoCore-zephyr | 核对第二篇第9章 Arduino Core on Zephyr、UNO Q 变体和 MCU 侧构建资源边界；不把源代码声明当作实机结果。 | main | Arduino 官方仓库；本项目只链接和原创解释。 | 2026-09-21 |

| 官方代码仓库 | Arduino App CLI | https://github.com/arduino/arduino-app-cli | 核对第三篇第1章 App/Bridge 的 Linux 侧管理入口、Linux 与微控制器部分的应用组织和 system check 能力边界；不把仓库说明替代目标镜像实测。 | main | Arduino 官方仓库；仓库标注 GPL-3.0-or-later；本项目只链接和原创解释。 | 2026-09-21 |
| 官方板卡文档 | Arduino UNO Q User Manual（Linux/ADB/SSH 访问边界） | https://github.com/arduino/docs-content/blob/main/content/hardware/02.uno/boards/uno-q/tutorials/01.user-manual/content.md | 核对第三篇第1章 Debian Linux、App Lab Network Mode、mDNS、USB/ADB、SSH、udev 权限、USB 标识和 Linux 环境事实；不把访问成功替代服务或 MCU 控制结果。 | main | Arduino 官方文档；本项目只链接和原创重述。 | 2026-09-21 |
| 官方规范 | Linux Filesystem Hierarchy Standard | https://refspecs.linuxfoundation.org/fhs.shtml | 核对第三篇第1章根目录、用户目录、临时目录、设备、运行时状态、配置和日志路径的通用职责边界；不把规范替代 UNO Q 当前镜像检查。 | 3.0（核验时） | Linux Foundation 规范；本项目只链接和原创解释。 | 2026-09-21 |

| 官方网络文档 | NetworkManager nmcli Reference Manual | https://networkmanager.dev/docs/api/latest/nmcli.html | 核对第三篇第2章 nmcli 状态查询、设备状态、活动连接、连接管理和读写操作边界；不把通用命令输出替代 UNO Q 实机网络结果。 | 1.58.0（核验时） | NetworkManager 官方文档；本项目只链接和原创解释。 | 2026-09-21 |
| 官方服务文档 | systemd.service source documentation | https://github.com/systemd/systemd/blob/main/man/systemd.service.xml | 核对第三篇第2章 service 单元、启动命令、执行环境、退出和重启策略边界；不把 systemd 通用语义替代目标镜像服务管理器实测。 | main | systemd 官方仓库；本项目只链接和原创解释。 | 2026-09-21 |
| 官方服务文档 | systemctl source documentation | https://github.com/systemd/systemd/blob/main/man/systemctl.xml | 核对第三篇第2章 enable/start/stop/restart、system/user 作用域和服务状态观察边界；不在本章默认实验中执行写操作。 | main | systemd 官方仓库；本项目只链接和原创解释。 | 2026-09-21 |

| 官方日志文档 | systemd journal fields | https://github.com/systemd/systemd/blob/main/man/systemd.journal-fields.xml | 核对第三篇第3章 _SYSTEMD_UNIT、_PID、_BOOT_ID、来源实时时间和来源启动后时间等结构化日志字段；不把字段存在替代目标镜像现场核验。 | main | systemd 官方仓库；本项目只链接和原创解释。 | 2026-09-21 |
| 官方日志文档 | journalctl source documentation | https://github.com/systemd/systemd/blob/main/man/journalctl.xml | 核对第三篇第3章时间窗口、服务过滤、UTC、JSON、游标、无分页和有限日志读取等只读观察边界；不在默认实验中清理或改变日志。 | main | systemd 官方仓库；本项目只链接和原创解释。 | 2026-09-21 |
| 官方资源文档 | systemd resource control | https://github.com/systemd/systemd/blob/main/man/systemd.resource-control.xml | 核对第三篇第3章 service/cgroup 资源控制、CPU、内存、任务和 I/O 统计边界；不把通用配置语义当作 UNO Q 当前镜像默认配置。 | main | systemd 官方仓库；本项目只链接和原创解释。 | 2026-09-21 |
| 官方内核文档 | Linux cgroup v2 | https://docs.kernel.org/admin-guide/cgroup-v2.html | 核对第三篇第3章统一 cgroup v2 控制器、资源统计和压力观察的内核边界；不把存在文档当作目标内核已启用某项控制器。 | 网页内容（核验时） | Linux kernel 官方文档；本项目只链接和原创解释。 | 2026-09-21 |
| 官方时间文档 | systemd time documentation | https://github.com/systemd/systemd/blob/main/man/systemd.time.xml | 核对第三篇第3章 systemd 时间表达式和时间相关语义；时间同步、时区和目标镜像配置仍需现场验证。 | main | systemd 官方仓库；本项目只链接和原创解释。 | 2026-09-21 |

| 官方平台文档 | Android Debug Bridge | https://developer.android.com/tools/adb | 核对第三篇第4章 ADB client、server、device daemon、设备列表和 shell 入口的分层边界；不把通用 ADB 文档替代 UNO Q 实机授权和权限验证。 | 网页内容（核验时） | Android Developers 官方文档；本项目只链接和原创解释。 | 2026-09-21 |
| 官方 Python 文档 | Python subprocess | https://docs.python.org/3/library/subprocess.html | 核对第三篇第4章固定 argv、shell=False、capture_output、timeout、TimeoutExpired 和子进程输出处理边界；不把概念脚本替代目标镜像现场测试。 | Python 3 文档（核验时） | Python 官方文档；本项目只链接和原创解释。 | 2026-09-21 |
| 官方 Python 文档 | Python json | https://docs.python.org/3/library/json.html | 核对第三篇第4章 JSON 编解码和不可信 JSON 输入的大小/资源风险；不把 JSON 格式正确替代协议授权和 MCU 结果验证。 | Python 3 文档（核验时） | Python 官方文档；本项目只链接和原创解释。 | 2026-09-21 |
| 官方板卡文档 | Arduino UNO Q User Manual（远程入口与 Bridge） | https://github.com/arduino/docs-content/blob/main/content/hardware/02.uno/boards/uno-q/tutorials/01.user-manual/content.md | 核对第三篇第4章 Network Mode、USB/ADB、Linux、App Lab 和 Bridge/RPC 的产品事实边界；不把访问成功替代授权、结果或硬件验证。 | main | Arduino 官方文档；本项目只链接和原创重述。 | 2026-09-21 |

| 官方 Python 文档 | Python asyncio queues | https://docs.python.org/3/library/asyncio-queue.html | 核对第三篇第5章 Queue、maxsize、qsize、put/get、task_done、join 和有界队列边界；不把概念队列替代现场负载测试。 | Python 3 文档（核验时） | Python 官方文档；本项目只链接和原创解释。 | 2026-09-21 |
| 官方 Python 文档 | Python asyncio tasks and timeouts | https://docs.python.org/3/library/asyncio-task.html | 核对第三篇第5章 wait_for、Task、取消和超时处理边界；不把协程超时替代外部 MCU 状态确认。 | Python 3 文档（核验时） | Python 官方文档；本项目只链接和原创解释。 | 2026-09-21 |
| 官方服务文档 | systemd.service（现场自动化服务边界） | https://github.com/systemd/systemd/blob/main/man/systemd.service.xml | 核对第三篇第5章 service unit、进程监督、启动/停止、重启和资源控制关联边界；不在默认实验中安装或重启现场服务。 | main | systemd 官方仓库；本项目只链接和原创解释。 | 2026-09-21 |
| 官方应用规范 | Arduino App specification（队列与 Bridge 交接） | https://github.com/arduino/arduino-app-cli/blob/main/docs/app-specification.md | 核对第三篇第5章 Arduino Sketch、Python、Linux App 和 RPC/Router 的组件边界；不把 App 运行态替代队列、缓存和 MCU 结果验证。 | main | Arduino 官方仓库；本项目只链接和原创解释。 | 2026-09-21 |
| 官方代码仓库 | Arduino Router | https://github.com/arduino/arduino-router | 核对第三篇第5章 Router/MessagePack RPC 传输和 Linux/MCU 连接基础；不把 Router 连接成功替代业务请求 APPLIED。 | main | Arduino 官方仓库；本项目只链接和原创解释。 | 2026-09-21 |
| 官方 Python 文档 | Python time | https://docs.python.org/3/library/time.html | 核对第三篇第6章 monotonic、perf_counter_ns、process_time_ns 和时间源边界；不把主机计时器结果当作 UNO Q 实机性能。 | Python 3 文档（核验时） | Python 官方文档；本项目只链接和原创解释。 | 2026-09-21 |
| 官方 Python 文档 | Python statistics | https://docs.python.org/3/library/statistics.html | 核对第三篇第6章 median、quantiles、样本量和分位数计算边界；不把小样本插值当作稳定的现场尾延迟结论。 | Python 3 文档（核验时） | Python 官方文档；本项目只链接和原创解释。 | 2026-09-21 |
| 官方内核文档 | Linux perf security | https://docs.kernel.org/admin-guide/perf-security.html | 核对第三篇第6章 perf/performance counter 的权限、安全和敏感信息边界；不为测量而修改目标设备安全策略或提升权限。 | 网页内容（核验时） | Linux kernel 官方文档；本项目只链接和原创解释。 | 2026-09-21 |
| 官方 Python 文档 | Python asyncio tasks and timeouts（测试运行器） | https://docs.python.org/3/library/asyncio-task.html | 核对第三篇第6章 wait_for、Task 取消、超时和异步测试替身边界；不把协程超时替代 Bridge/MCU 最终状态确认。 | Python 3 文档（核验时） | Python 官方文档；本项目只链接和原创解释。 | 2026-09-21 |
| 官方服务文档 | systemd.exec | https://github.com/systemd/systemd/blob/main/man/systemd.exec.xml | 核对第三篇第7章执行环境、WorkingDirectory、目录管理、NoNewPrivileges、ProtectSystem、ProtectHome、凭据和服务进程边界；不把主机支持的字段直接当作 UNO Q 当前镜像能力。 | main | systemd 官方仓库；本项目只链接和原创解释。 | 2026-09-21 |
| 官方服务文档 | systemd credentials | https://github.com/systemd/systemd/blob/main/docs/CREDENTIALS.md | 核对第三篇第7章凭据注入、秘密不入 unit/日志和目标支持边界；不在本项目保存或分发真实凭据。 | main | systemd 官方仓库；本项目只链接和原创解释。 | 2026-09-21 |
| 官方服务文档 | systemd-analyze | https://github.com/systemd/systemd/blob/main/man/systemd-analyze.xml | 核对第三篇第7章 unit verify、security 审查和工具输出的辅助性质；不把安全分析结果替代现场风险评估。 | main | systemd 官方仓库；本项目只链接和原创解释。 | 2026-09-21 |

## 第四篇第3章补充核验

| 类型 | 来源 | 地址 | 用途与边界 | 版本基线 | 版权处理 | 核验日期 |
| --- | --- | --- | --- | --- | --- | --- |
| 官方代码仓库 | Arduino Router README（连接生命周期） | https://github.com/arduino/arduino-router#readme | 核对方法注册、客户端断开后移除注册、转发消息编号映射；不推定客户端自动恢复或业务恰好一次执行。 | main 页面，核验时 | 官方仓库标注 GPL-3.0-or-later；只链接和原创重述，不复制源码。 | 2026-09-22 |
| 官方应用规范 | Arduino App specification（双侧职责） | https://github.com/arduino/arduino-app-cli/blob/main/docs/app-specification.md | 核对 Linux/Python 与 MCU Sketch 的 RPC 协作；应用恢复模型不冒充官方内置 API。 | main 页面，核验时 | 只链接和原创解释。 | 2026-09-22 |
| 官方 Python 文档 | Python 3.10 Synchronization Primitives | https://docs.python.org/3.10/library/asyncio-sync.html | 核对 asyncio.Lock 互斥及非线程安全边界，用于单事件循环共享恢复。 | Python 3.10 文档 | Python 官方文档，只链接和原创解释。 | 2026-09-22 |
| 官方 Python 文档 | Python 3.10 Coroutines and Tasks | https://docs.python.org/3.10/library/asyncio-task.html | 核对 wait_for 超时取消、等待清理可能超过期限、gather 和取消传播；不把本地取消当远端撤销。 | Python 3.10 文档 | Python 官方文档，只链接和原创解释。 | 2026-09-22 |
| 官方 Python 文档 | Python 3.10 time | https://docs.python.org/3.10/library/time.html | 核对 monotonic 起点未定义、适合经过时间；不把不兼容的时钟值跨进程重启或设备比较。 | Python 3.10 文档 | Python 官方文档，只链接和原创解释。 | 2026-09-22 |
| 官方 Python 文档 | Python 3.10 random | https://docs.python.org/3.10/library/random.html | 核对 uniform 区间采样；退避上限、抖动策略和随机种子使用范围为本书原创设计。 | Python 3.10 文档 | Python 官方文档，只链接和原创解释。 | 2026-09-22 |

## 第四篇第4章补充核验

| 类型 | 来源 | 地址 | 用途与边界 | 版本基线 | 版权处理 | 核验日期 |
| --- | --- | --- | --- | --- | --- | --- |
| 官方 Python 文档 | Python 3.10 sqlite3 | https://docs.python.org/3.10/library/sqlite3.html | 核对标准库数据库接口、参数绑定、事务与连接上下文的提交/回滚行为；本章本地账本不提供 Router/Bridge 或设备执行证据，也不构成掉电持久性或并发性能验收。 | Python 3.10 文档 | Python 官方文档，只链接和原创解释，不复制外部代码或图表；Fig-27 为本书原创教学设计。 | 2026-09-22 |
| 官方 Python 文档 | Python 3.10 dataclasses | https://docs.python.org/3.10/library/dataclasses.html | 核对 frozen 数据类对字段赋值的限制，用于请求、记录、事件、观察和决策；不把 frozen=True 当作输入验证、数据库防篡改或绝对不可变保证。 | Python 3.10 文档 | Python 官方文档，只链接和原创解释，不复制外部代码或图表。 | 2026-09-22 |

## 第五篇第2章补充核验

| 类型 | 来源 | 地址 | 用途与边界 | 版本基线 | 版权处理 | 核验日期 |
| --- | --- | --- | --- | --- | --- | --- |
| 官方规范 | Arduino App specification（组件与运行边界） | https://github.com/arduino/arduino-app-cli/blob/main/docs/app-specification.md | 核对第五篇第2章 App 由 Python、Sketch、Brick/容器组成以及 Linux/MCU/RPC 的职责边界；本章状态机和证据字段是原创教学模型，不冒充官方运行状态。 | main 页面，核验时 | 官方仓库标注 GPL-3.0-or-later；本项目只链接和原创解释，不复制源码或图表。 | 2026-09-23 |
| 官方用户文档 | Arduino App CLI user documentation | https://github.com/arduino/arduino-app-cli/blob/main/docs/user-documentation.md | 核对 App 用户目录、运行时目录和环境变量参考；不把文档中的默认路径直接当作 UNO Q 当前镜像或生产权限事实。 | main 页面，核验时 | 官方仓库标注 GPL-3.0-or-later；本项目只链接和原创解释，不复制源码或图表。 | 2026-09-23 |
| 官方教程 | Arduino App Lab examples | https://docs.arduino.cc/software/app-lab/tutorials/examples/ | 核对示例选择、Run、等待启动和交互的公开操作流程；不把示例运行说明替代本章的本地测试或实机验收。 | 页面内容（核验时） | 官方文档；本项目只链接和原创重述，不复制正文或截图。 | 2026-09-23 |
| 官方数据表 | Arduino UNO Q datasheet | https://docs.arduino.cc/resources/datasheets/ABX00162-datasheet.pdf | 核对 Run 操作构建 Linux 组件、刷写 MCU Sketch、部署 Brick、启动组件以及控制台观察的产品级说明；不把产品说明写成当前环境实测。 | ABX00162 PDF（核验时） | 官方数据表；本项目只链接和原创重述，不复制表格或图片。 | 2026-09-23 |
| 官方产品页 | Arduino UNO Q | https://docs.arduino.cc/hardware/uno-q | 核对双处理器、App Lab 和 Bridge 的产品层角色；不把产品页替代目标设备、版本或物理动作验证。 | 页面内容（核验时） | 官方网页；本项目只链接和原创解释。 | 2026-09-23 |

核验边界：官方来源用于 UNO Q 事实基线，社区来源只作课程/知识库结构参考。当前本项目只引用链接和原创解释，不打包外部代码、正文、图片或其他材料；任何外部材料的再分发许可仍需按其文件级声明另行核验。

## 第五篇第1章补充核验

| 类型 | 来源 | 地址 | 用途与边界 | 版本基线 | 版权处理 | 核验日期 |
| --- | --- | --- | --- | --- | --- | --- |
| 官方规范 | Arduino App specification | https://github.com/arduino/arduino-app-cli/blob/main/docs/app-specification.md | 核对 App 根目录、`app.yaml`、Python 入口、可选 Sketch、README、`data/`、`.cache/`、Brick 字段和变量脱敏语义；不把目录规范替代目标板运行结果。 | main | 官方仓库标注 GPL-3.0-or-later；本项目只链接和原创解释，不复制源码或图表。 | 2026-09-23 |
| 官方板卡文档 | Arduino UNO Q User Manual（App Lab 入口与运行观察） | https://github.com/arduino/docs-content/blob/main/content/hardware/02.uno/boards/uno-q/tutorials/01.user-manual/content.md | 核对 PC-hosted、SBC、Network Mode、mDNS、Hello World、启动项和运行入口边界；不把网络发现或日志替代设备行为证据。 | main | 官方文档；本项目只链接和原创重述。 | 2026-09-23 |
| 官方产品页 | Arduino UNO Q | https://docs.arduino.cc/hardware/uno-q | 核对双处理器、App Lab、Arduino IDE 和 Bridge 的产品层角色描述；不把产品介绍当作本地实机测试。 | 页面内容（核验时） | 官方产品资料；本项目只链接和原创解释。 | 2026-09-23 |
| 官方教程 | Arduino App Lab examples | https://docs.arduino.cc/software/app-lab/getting-started/examples | 核对 App Lab 示例入口和示例类型的公开索引；不复制示例源码，也不把示例可见性替代本章验证。 | 页面内容（核验时） | 官方文档；本项目只链接和原创说明。 | 2026-09-23 |
| 官方用户文档 | Arduino App CLI user documentation | https://github.com/arduino/arduino-app-cli/blob/main/docs/user-documentation.md | 核对 App 存储目录、运行时目录和环境变量的参考边界；目标镜像实际路径、权限和版本仍需现场核验。 | main | 官方仓库标注 GPL-3.0-or-later；本项目只链接和原创解释。 | 2026-09-23 |

## 第五篇第3章补充核验

| 类型 | 来源 | 地址 | 用途与边界 | 版本基线 | 版权处理 | 核验日期 |
| --- | --- | --- | --- | --- | --- | --- |
| 官方规范 | Arduino App specification（启动声明与 Brick 选项） | https://github.com/arduino/arduino-app-cli/blob/main/docs/app-specification.md | 核对 `app.yaml`、`ports`、`bricks`、`model`、`variables`、`devices`、`data/`、`.cache/` 和 Secret 脱敏语义；本章检查器是原创教学模型，不替代目标设备验证。 | main | 官方仓库标注 GPL-3.0-or-later；本项目只链接和原创解释，不复制源码或图表。 | 2026-09-23 |
| 官方用户文档 | Arduino App CLI user documentation（目标环境参考） | https://github.com/arduino/arduino-app-cli/blob/main/docs/user-documentation.md | 核对 App CLI 用户目录、运行时目录和环境变量参考；不把文档默认值直接当作当前 UNO Q 镜像、权限或 Brick 清单事实。 | main | 官方仓库标注 GPL-3.0-or-later；本项目只链接和原创解释。 | 2026-09-23 |
| 官方教程 | Arduino App Lab examples | https://docs.arduino.cc/software/app-lab/tutorials/examples/ | 核对 App Lab 示例入口的公开文档边界；不复制示例源码，也不把示例可运行性替代本章本地或实机证据。 | 页面内容（核验时） | 官方文档；本项目只链接和原创说明。 | 2026-09-23 |
| 官方板卡资料 | Arduino UNO Q datasheet | https://docs.arduino.cc/resources/datasheets/ABX00162-datasheet.pdf | 作为 UNO Q 双侧职责和运行观察的硬件资料入口；本章不把数据表替代 App Lab、Linux、MCU 或 Brick 实机验证。 | ABX00162 | 官方资料；本项目只链接和原创解释。 | 2026-09-23 |

## 第五篇第4章补充核验

| 类型 | 来源 | 地址 | 用途与边界 | 版本基线 | 版权处理 | 核验日期 |
| --- | --- | --- | --- | --- | --- | --- |
| 官方规范 | Arduino App specification（App 声明与持久化边界） | https://github.com/arduino/arduino-app-cli/blob/main/docs/app-specification.md | 核对 `app.yaml`、Brick 变量、Secret 脱敏、`data/` 和 `.cache/` 的公开边界；本章配置分层、锁定键和快照是原创治理模型。 | main | 官方仓库标注 GPL-3.0-or-later；本项目只链接和原创解释，不复制源码或图表。 | 2026-09-23 |
| 官方用户文档 | Arduino App CLI user documentation（运行环境参考） | https://github.com/arduino/arduino-app-cli/blob/main/docs/user-documentation.md | 核对 App CLI 用户目录、运行时目录和环境变量参考；不把默认值替代当前目标镜像、权限或 Secret 实测。 | main | 官方仓库标注 GPL-3.0-or-later；本项目只链接和原创解释。 | 2026-09-23 |

## 第五篇第5章补充核验

| 类型 | 来源 | 地址 | 用途与边界 | 版本基线 | 版权处理 | 核验日期 |
| --- | --- | --- | --- | --- | --- | --- |
| 官方数据表 | Arduino UNO Q datasheet（App Lab Console 输出类别） | https://docs.arduino.cc/resources/datasheets/ABX00162-datasheet.pdf | 核对 Start-up、Main (Python)、Sketch (Microcontroller) 三类 Console 标签的官方说明，以及启动成功仍需检查运行日志的边界；本章事件字段与关联规则是原创建议，不推定平台自动导出或关联日志。 | ABX00162 PDF（核验时） | 官方资料；本项目只链接和原创重述，不复制表格或图片。 | 2026-09-23 |

## 第五篇第6章补充核验

| 类型 | 来源 | 地址 | 用途与边界 | 版本基线 | 版权处理 | 核验日期 |
| --- | --- | --- | --- | --- | --- | --- |
| 官方规范 | Arduino App specification（双侧职责与通信） | https://github.com/arduino/arduino-app-cli/blob/main/docs/app-specification.md | 核对 App 的 Python、可选 Sketch、Brick/容器组成及 Linux/MCU RPC 协作；本章健康检查、状态和恢复门均为原创教学模型。 | main 页面，核验时 | 官方资料；只链接和原创解释，不复制源码或图表。 | 2026-09-23 |
| 官方数据表 | Arduino UNO Q datasheet（App Lab Console 与运行边界） | https://docs.arduino.cc/resources/datasheets/ABX00162-datasheet.pdf | 核对三类 Console 输出和启动成功仍可能有运行时错误；不能由此推断 App Lab 自带本章探针、30 秒阈值或自动恢复。 | ABX00162 PDF（核验时） | 官方资料；只链接和原创重述，不复制图表。 | 2026-09-23 |

## 第五篇第7章补充核验

| 类型 | 来源 | 地址 | 用途与边界 | 版本基线 | 版权处理 | 核验日期 |
| --- | --- | --- | --- | --- | --- | --- |
| 官方规范 | Arduino App specification（项目组成和声明） | https://github.com/arduino/arduino-app-cli/blob/main/docs/app-specification.md | 核对 `app.yaml`、Python 入口、可选 Sketch、Brick 和 Linux/MCU 分工；本章 G0～G7 与交接模板不是官方格式。 | main 页面，核验时 | 仅链接和原创解释，不复制源码或图表。 | 2026-09-23 |
| 官方教程 | Arduino App Lab examples | https://docs.arduino.cc/software/app-lab/tutorials/examples/ | 核对选示例、Run、等待启动、交互以及复制示例后编辑的公开流程；本章不将教程步骤当作已执行。 | 页面内容（核验时） | 仅链接和原创重述，不复制截图或示例源码。 | 2026-09-23 |
| 官方数据表 | Arduino UNO Q datasheet（Console 与运行时边界） | https://docs.arduino.cc/resources/datasheets/ABX00162-datasheet.pdf | 核对 Start-up、Main (Python)、Sketch (Microcontroller) 输出和启动后仍可能有运行时错误；交接门、证据等级与回退条件为本书建议。 | ABX00162 PDF（核验时） | 仅链接和原创解释，不复制图表。 | 2026-09-23 |

## 第六篇第1章补充核验

| 类型 | 来源 | 地址 | 用途与边界 | 版本基线 | 版权处理 | 核验日期 |
| --- | --- | --- | --- | --- | --- | --- |
| 官方产品页 | Arduino UNO Q | https://docs.arduino.cc/hardware/uno-q | 核对产品资料列出的 SBC 模式 USB 摄像头与底部高速连接器 MIPI-CSI 相机路线；不推断任意相机、驱动或采集后端均可用。 | 页面内容（核验时） | 官方网页；只链接和原创解释，不复制图表或截图。 | 2026-09-23 |
| 官方配件页 | Arduino UNO Media Carrier | https://docs.arduino.cc/hardware/uno-media-carrier | 核对特定载板的 MIPI-CSI 接口及官方说明的相机兼容范围；不外推为任意 CSI 相机兼容，也不当作本项目实机测试。 | 页面内容（核验时） | 官方网页；只链接和原创解释，不复制图表或截图。 | 2026-09-23 |
| 官方教程 | OpenCV 4.12 Basic Operations on Images | https://docs.opencv.org/4.12.0/d3/df2/tutorial_py_basic_ops.html | 核对 Python 图像数组、NumPy 索引、ROI 切片和 `imread` 彩色图像的 BGR 通道约定；摄像头后端的格式仍需按实际接口核实。 | OpenCV 4.12.0 文档 | OpenCV 官方文档；只链接和原创解释，不复制教程正文或图表。 | 2026-09-23 |

本章示例为本书原创的合成数组操作，不包含外部代码或图像；其预期输出由代码逻辑推导，本次未运行。Mermaid 图为原创教学流程，不是官方硬件架构、相机接线或设备通信协议。

## 第六篇第2章补充核验

| 类型 | 来源 | 地址 | 用途与边界 | 版本基线 | 版权处理 | 核验日期 |
| --- | --- | --- | --- | --- | --- | --- |
| 官方产品页 | Arduino UNO Q | https://docs.arduino.cc/hardware/uno-q | 核对产品资料列出的 SBC 模式 USB 摄像头接入条件及底部高速连接器 MIPI-CSI 相机路线；不推断任意相机、驱动、载板或镜像均兼容。 | 页面内容（核验时） | 官方网页；只链接和原创解释，不复制图表或截图。 | 2026-09-23 |
| 官方配件页 | Arduino UNO Media Carrier | https://docs.arduino.cc/hardware/uno-media-carrier | 核对该载板的双 MIPI-CSI 接口及 IMX219 相机兼容说明；不外推到任意 CSI 相机，也不当作本项目实机验证。 | 页面内容（核验时） | 官方网页；只链接和原创解释，不复制图表或截图。 | 2026-09-23 |
| 官方教程 | OpenCV 4.12 Video Input with OpenCV | https://docs.opencv.org/4.12.0/d5/dc4/tutorial_video_input_psnr_ssim.html | 核对视频文件/设备来源、打开状态、逐帧读取、空帧判断、属性查询和释放生命周期；示例脚本为本书原创 Python 代码。 | OpenCV 4.12.0 文档 | OpenCV 官方文档；只链接和原创解释，不复制教程正文或图表。 | 2026-09-23 |
| 官方 API 文档 | OpenCV 4.12 Video I/O flags | https://docs.opencv.org/4.12.0/d4/d15/group__videoio__flags__base.html | 核对视频采集属性及打开/读取超时属性的适用后端限制；不把特定后端能力推及所有设备。 | OpenCV 4.12.0 文档 | OpenCV 官方文档；只链接和原创解释，不复制文档内容或图表。 | 2026-09-23 |

本章脚本为本书原创，仅接收显式摄像头索引或本地文件，不扫描设备、不接受网络流、不写图像文件，也不控制硬件。代码本次未运行；图示未渲染为 SVG；没有相机、载板或 UNO Q 实机验证。

## 第六篇第3章补充核验

| 类型 | 来源 | 地址 | 用途与边界 | 版本基线 | 版权处理 | 核验日期 |
| --- | --- | --- | --- | --- | --- | --- |
| 官方教程 | OpenCV 4.12 Smoothing Images | https://docs.opencv.org/4.12.0/d4/d13/tutorial_py_filtering.html | 核对高斯、中值及双边平滑的基本机制、核参数约束和去噪/边缘细节权衡；本章离线样例为原创。 | OpenCV 4.12.0 文档 | OpenCV 官方文档；只链接和原创解释，不复制教程正文或图表。 | 2026-09-23 |
| 官方教程 | OpenCV 4.12 Canny Edge Detector | https://docs.opencv.org/4.12.0/da/d5c/tutorial_canny_detector.html | 核对 Canny 的噪声抑制、梯度、非极大值抑制、滞后阈值和候选边缘输出；阈值比例仅作为调参起点，不当作通用验收标准。 | OpenCV 4.12.0 文档 | OpenCV 官方文档；只链接和原创解释，不复制教程正文或图表。 | 2026-09-23 |

本章脚本与测试为本书原创，使用确定性合成数组，不读取/写入图片，不访问相机、网络、GPIO、MCU 或 UNO Q。3 项测试和示例在本机 Python 3.14.6、OpenCV 5.0.0、NumPy 2.4.6 环境验证；目标系统和实机未验证。Fig-37 Mermaid 为原创教学图，本次未渲染 SVG。

## 第六篇第4章补充核验

| 类型 | 来源 | 地址 | 用途与边界 | 版本基线 | 版权处理 | 核验日期 |
| --- | --- | --- | --- | --- | --- | --- |
| 官方教程 | OpenCV Contours: Getting Started | https://docs.opencv.org/4.12.0/d4/d73/tutorial_py_contours_begin.html | 核对二值输入、白色前景、`findContours` 的轮廓概念；不把边缘候选自动等同于可信区域掩膜。 | OpenCV 4.12.0 文档 | 仅链接并原创解释，不复制教程正文或图表。 | 2026-09-23 |
| 官方教程 | OpenCV Contour Features | https://docs.opencv.org/4.12.0/dd/d49/tutorial_py_contour_features.html | 核对 `contourArea`、`arcLength`、`boundingRect`、`moments` 及质心语义；像素几何不是标定后的物理尺寸。 | OpenCV 4.12.0 文档 | 仅链接并原创解释，不复制教程正文或图表。 | 2026-09-23 |
| 官方教程 | OpenCV Contours Hierarchy | https://docs.opencv.org/4.12.0/d9/d8b/tutorial_py_contours_hierarchy.html | 核对 `RETR_EXTERNAL` 仅保留最外层轮廓及内部孔洞不进入本章净面积计算的边界。 | OpenCV 4.12.0 文档 | 仅链接并原创解释，不复制教程正文或图表。 | 2026-09-23 |

本章脚本、测试与 Fig-38 Mermaid 为本书原创。4 项测试及脚本在本机 Python 3.14.6、OpenCV 5.0.0、NumPy 2.4.6 环境执行；仅使用合成掩膜，未访问摄像头、网络、文件、GPIO、MCU 或 UNO Q。目标板软件栈、物理标定、真实图像效果和硬件性能未验证；Fig-38 SVG 未渲染审阅。

## 第六篇第5章补充核验

| 类型 | 来源 | 地址 | 用途与边界 | 版本基线 | 版权处理 | 核验日期 |
| --- | --- | --- | --- | --- | --- | --- |
| 官方教程 | OpenCV Changing Colorspaces | https://docs.opencv.org/4.12.0/df/d9d/tutorial_py_colorspaces.html | 核对 BGR→HSV、8 位 H/S/V 范围、`inRange` 颜色掩膜；教程示例参数不是实际摄像头的通用阈值。 | OpenCV 4.12.0 文档 | 仅链接并原创解释，不复制教程源码、正文或图表。 | 2026-09-23 |
| 官方教程 | OpenCV Morphological Transformations | https://docs.opencv.org/4.12.0/d9/d61/tutorial_py_morphological_ops.html | 核对开运算的腐蚀后膨胀与结构元素作用；不能由合成噪点移除推断真实小目标不会被误删。 | OpenCV 4.12.0 文档 | 仅链接并原创解释，不复制教程源码、正文或图表。 | 2026-09-23 |
| 官方教程 | OpenCV Contours: Getting Started | https://docs.opencv.org/4.12.0/d4/d73/tutorial_py_contours_begin.html | 核对二值掩膜、白色前景与外轮廓输入约定；目标身份、跨帧关联和物理位置并非本接口自动提供。 | OpenCV 4.12.0 文档 | 仅链接并原创解释，不复制教程源码、正文或图表。 | 2026-09-23 |

本章脚本、测试与 Fig-39 Mermaid 为本书原创。4 项测试及脚本在本机 Python 3.14.6、OpenCV 5.0.0、NumPy 2.4.6 环境执行；仅使用合成 BGR 数组，未访问摄像头、网络、图像文件、GPIO、MCU 或 UNO Q。目标板软件栈、色彩标定、真实阈值鲁棒性、实时性能和硬件动作未验证；Fig-39 SVG 未渲染审阅。

## 第六篇第6章补充核验

| 类型 | 来源 | 地址 | 用途与边界 | 版本基线 | 版权处理 | 核验日期 |
| --- | --- | --- | --- | --- | --- | --- |
| 官方教程 | OpenCV Getting Started with Videos | https://docs.opencv.org/4.12.0/dd/d43/tutorial_py_video_display.html | 核对 `VideoCapture.read()` 的成功标志、逐帧读取与资源释放；本章的来源 ID、帧号和时间戳是原创教学输入契约，不是该 API 自动提供的可靠证据。 | OpenCV 4.12.0 文档 | 仅链接并原创解释，不复制教程源码、正文或图表。 | 2026-09-23 |
| 官方教程 | OpenCV Optical Flow | https://docs.opencv.org/4.12.0/d4/dee/tutorial_optical_flow.html | 核对光流与 `calcOpticalFlowPyrLK()` 特征点跟踪的用途，界定本章质心时间门并非光流、多目标跟踪或对象重识别。 | OpenCV 4.12.0 文档 | 仅链接并原创解释，不复制教程源码、正文或图表。 | 2026-09-23 |

本章脚本、测试与 Fig-40 Mermaid 为本书原创。7 项测试和脚本在本机 Python 3.14.6 执行；仅使用硬编码合成记录和 Python 标准库，示例不访问摄像头、图像/业务数据文件、网络、GPIO、MCU 或 UNO Q；测试会加载本地脚本并启动子进程。目标板软件栈、真实时间戳与帧率、对象身份、绝对时效、Bridge/MCU 联动和硬件安全未验证；Fig-40 SVG 未渲染审阅。

## 第六篇第7章补充核验

| 类型 | 来源 | 地址 | 用途与边界 | 版本基线 | 版权处理 | 核验日期 |
| --- | --- | --- | --- | --- | --- | --- |
| 官方产品页 | Arduino UNO Q | https://docs.arduino.cc/hardware/uno-q | 核对 Linux/STM32U585 双侧职责与 Bridge/RPC 产品级说明；不把产品页当作本章硬件联调证据。 | 页面内容（核验时） | 仅链接并原创解释，不复制图表、代码或截图。 | 2026-09-23 |
| 官方规范 | Arduino App specification | https://github.com/arduino/arduino-app-cli/blob/main/docs/app-specification.md | 核对 Python 运行于 Linux、Sketch 运行于 MCU、两侧以 RPC 消息协作；本章的反馈审查门与百分数限幅均为原创教学模型。 | main 页面（核验时） | 仅链接并原创重述，不复制正文或示例代码。 | 2026-09-23 |
| 官方源码 | Arduino Python Bridge（app-bricks-py） | https://github.com/arduino/app-bricks-py/blob/main/src/arduino/app_utils/bridge.py | 核对公开 `call`/`notify` 接口语义；本章不导入 SDK，也不据此声称调用、回执或物理动作已经发生。 | main 页面（核验时） | 仅链接并解释接口边界，不复制源码。 | 2026-09-23 |

本章脚本、测试与 Fig-41 Mermaid 为本书原创。10 项测试及脚本在本机 Python 3.14.6 执行；示例只处理合成记录，不调用相机、OpenCV、Bridge、GPIO、MCU、网络或执行器。真实采集时钟、操作者认证、幂等、路由回执、MCU 侧保护与物理输出均未验证；Fig-41 SVG 尚未渲染审阅。

## 第六篇第8章补充核验

| 类型 | 来源 | 地址 | 用途与边界 | 版本基线 | 版权处理 | 核验日期 |
| --- | --- | --- | --- | --- | --- | --- |
| 官方教程 | OpenCV Changing Colorspaces | https://docs.opencv.org/4.12.0/df/d9d/tutorial_py_colorspaces.html | 核对 BGR→HSV 与 `inRange` 颜色掩膜的接口；本章实际调用本仓库第5章脚本，合成阈值不能外推为真实相机参数。 | OpenCV 4.12.0 文档 | 仅链接并原创解释，不复制教程代码、图像或正文。 | 2026-09-23 |
| 官方教程 | OpenCV Contours: Getting Started 与 Contour Features | https://docs.opencv.org/4.12.0/d4/d73/tutorial_py_contours_begin.html · https://docs.opencv.org/4.12.0/dd/d49/tutorial_py_contour_features.html | 核对二值掩膜外轮廓与 `contourArea` 面积语义；像素坐标平方不等于物理面积，20×20 个前景像素不等于本示例的轮廓面积 361.0。 | OpenCV 4.12.0 文档 | 仅链接并原创解释，不复制教程代码、图像或正文。 | 2026-09-23 |
| 官方产品页 | Arduino UNO Q | https://docs.arduino.cc/hardware/uno-q | 核对产品级 Linux/MCU 分工与 Bridge/RPC 能力；不能当作本章相机、Bridge 或硬件联调证据。 | 页面内容（核验时） | 仅链接并原创重述，不复制图表。 | 2026-09-23 |
| 官方规范 | Arduino App specification | https://github.com/arduino/arduino-app-cli/blob/main/docs/app-specification.md | 核对 Python/Linux 与 Sketch/MCU 的职责分界；本章审查门和证据包是原创教学模型，不是官方 App 或安全规范。 | main 页面（核验时） | 仅链接并原创解释，不复制正文或源码。 | 2026-09-23 |

本章综合脚本、六项测试、交接模板与 Fig-42 Mermaid 为本书原创。实际复用本仓库第5～7章代码，在本机 Python 3.14.6、OpenCV 5.0.0、NumPy 2.4.6 环境运行；只创建内存合成图并输出九条 JSONL，不访问相机、网络、Bridge、MCU 或执行器。错会话故障注入复用第3帧，仅进入审查门。目标板、真实相机、时钟、身份认证、物理反馈与 SVG 视觉审阅均未验证。

## 第七篇第1章补充核验

| 类型 | 来源 | 地址 | 用途与边界 | 版本基线 | 版权处理 | 核验日期 |
| --- | --- | --- | --- | --- | --- | --- |
| 官方产品页 | Arduino UNO Q | https://docs.arduino.cc/hardware/uno-q | 核对 QRB2210 Linux 与 STM32U585 MCU 的双侧架构、App Lab 与 Bridge/RPC 产品级定位；页面不证明本章公式运行于板上，也不保证任意模型格式或推理性能。 | 页面内容（核验时） | 仅链接并原创解释，不复制图表、截图或产品正文。 | 2026-09-23 |
| 官方规范 | Arduino App specification | https://github.com/arduino/arduino-app-cli/blob/main/docs/app-specification.md | 核对 Python/Brick/容器运行于 Linux、Sketch 运行于 MCU，二者通过 RPC 协作；本章特征契约、`REPORT_ONLY` 和弃判门均为原创教学规则。 | main 页面（核验时） | 仅链接并原创重述，不复制规范内容或代码。 | 2026-09-23 |
| 官方学习索引 | Arduino Learn 的 Edge AI 栏目 | https://docs.arduino.cc/learn | 核对官方设有 AI/机器学习基础与边缘 AI 工作流学习入口；本章任务分类与模型验证清单是本书综合归纳，不把索引当作具体板卡的实测资料。 | 页面内容（核验时） | 仅链接并原创解释，不复制课程正文或图像。 | 2026-09-23 |

本章 `teaching_inference.py`、九项标准库测试及 Fig-43 Mermaid 为本书原创。程序仅消费人工合成特征，用手设线性公式产生原始间隔、弃判或拒绝结果；没有训练、模型工件、真实图像/传感器输入、概率校准、App Lab、网络、Bridge、MCU 或执行器调用。测试只验证本机 Python 3.14.6 的离线契约；目标板运行时、模型性能、时延和物理安全均未验证，Fig-43 SVG 尚未渲染审阅。

## 第七篇第2章补充核验

| 类型 | 来源 | 地址 | 用途与边界 | 版本基线 | 版权处理 | 核验日期 |
| --- | --- | --- | --- | --- | --- | --- |
| 官方产品页 | Arduino UNO Q | https://docs.arduino.cc/hardware/uno-q | 核对 Linux/MCU 双侧及 App Lab AI 应用的产品背景；不以产品介绍证明本章合成分类器在板上运行或具备准确率。 | 页面内容（核验时） | 仅链接并原创解释，不复制图表或正文。 | 2026-09-23 |
| 官方课程 | Google Machine Learning Crash Course：Dividing the original dataset | https://developers.google.com/machine-learning/crash-course/overfitting/dividing-datasets | 核对训练、验证、测试的职责以及反复使用测试集和重复样本的风险；本章固定 CSV 的组分区与门限策略为原创教学设计。 | 页面内容（核验时） | 页面标注 CC BY 4.0（代码示例另有声明）；本项目只链接和原创重述，不复制课程图文或代码。 | 2026-09-23 |
| 官方文档 | scikit-learn：Cross-validation（grouped data） | https://scikit-learn.org/stable/modules/cross_validation.html | 核对相关样本按组隔离的原则；本章不使用 scikit-learn 或声称完成交叉验证。 | stable 页面（核验时） | 仅链接和原创解释，不复制文档图文或代码。 | 2026-09-23 |
| 官方文档 | scikit-learn：Common pitfalls and recommended practices | https://scikit-learn.org/1.8/common_pitfalls.html | 核对拟合/预处理不得窥视测试集的泄漏边界；本章原始合成特征未拟合预处理器。 | 1.8 页面（核验时） | 仅链接和原创解释，不复制文档图文或代码。 | 2026-09-23 |
| 官方课程 | Google Machine Learning Crash Course：Classification metrics | https://developers.google.com/machine-learning/crash-course/classification/accuracy-precision-recall | 核对 TP/FP/TN/FN、准确率、精确率和召回率；本章的弃判分账和条件指标是原创示例。 | 页面内容（核验时） | 页面标注 CC BY 4.0（代码示例另有声明）；本项目只链接和原创重述。 | 2026-09-23 |

本章 `synthetic_samples.csv`、`dataset_evaluation.py`、19 项标准库测试和 Fig-44 Mermaid 均为本书原创。20 条手填记录只用于演示数据契约、组隔离、类别中心拟合、验证门限选择和测试计数；`group_id` 不认证采集来源，`model_kind` 不代表模型工件，`raw_score` 不是概率。当前仅有本机 Python 3.14.6 离线测试，不含真实标注、UNO Q、App Lab、Bridge、MCU、执行器或 SVG 目视审阅。

## 第七篇第3章补充核验

| 类型 | 来源 | 地址 | 用途与边界 | 版本基线 | 版权处理 | 核验日期 |
|---|---|---|---|---|---|---|
| 官方产品页 | Arduino UNO Q | https://docs.arduino.cc/hardware/uno-q | 核对 QRB2210 Linux MPU、STM32U585 Zephyr MCU 及产品级 AI/App Lab 定位；不把产品宣传当成任意模型格式、运行时或加速器的兼容证明。 | 页面内容（核验时） | 仅链接和原创解释，不复制图表、截图或正文。 | 2026-09-23 |
| 官方规范 | Arduino App specification | https://github.com/arduino/arduino-app-cli/blob/main/docs/app-specification.md | 核对 Python/Brick/容器的 Linux 侧、Sketch 的 MCU 侧、RPC 协作、`app.yaml` 中 Brick/模型标识及额外文件不会被自动执行；本章 `model_manifest.json` 是本书原创教学清单。 | main 页面（核验时） | 仅链接和原创重述，不复制规范正文或代码。 | 2026-09-23 |
| 官方规范 | ONNX Intermediate Representation Specification | https://onnx.ai/onnx/repo-docs/IR.html | 核对计算图、数据类型、operator set/opset 元数据和外部张量数据边界；本章预检器不解析 ONNX 二进制。 | ONNX 1.24.0 文档（核验时） | 仅链接并原创摘要，不复制规范文本、图表或源码。 | 2026-09-23 |
| 官方文档 | ONNX Runtime compatibility | https://onnxruntime.ai/docs/reference/compatibility.html | 核对运行时版本与平台、依赖、opset 兼容信息；通用兼容表不证明 UNO Q 指定镜像和执行提供程序已验证。 | 页面内容（核验时） | 仅链接和原创解释，不复制文档内容或表格。 | 2026-09-23 |

本章 `model_preflight.py`、教学 JSON 清单、文本占位工件、10 项标准库行为测试及 Fig-45 Mermaid 为本书原创。本机 Python 3.14.6 只验证清单字段/张量形状、模型与运行时格式声明、单文件相对路径和 SHA-256；样例摘要匹配仍产生 `REVIEW_REQUIRED_NOT_DEPLOYABLE`。没有真实模型、ONNX 解析、模型许可核验、运行时安装、UNO Q 目标镜像、App Lab、Bridge、MCU、性能、功耗或硬件动作验证；Fig-45 SVG 尚未渲染和目视审阅。

## 第七篇第4章补充核验

| 类型 | 来源 | 地址 | 用途与边界 | 版本基线 | 版权处理 | 核验日期 |
|---|---|---|---|---|---|---|
| 官方教程 | ONNX Runtime：Export PyTorch model | https://onnxruntime.ai/docs/tutorials/export-pytorch-model.html | 核对框架输出与 ONNX Runtime 输出逐值比较的范例，以及 `assert_allclose` 中绝对/相对容差的用法；页面参数仅属于该教程示例，不是通用模型或 UNO Q 推荐值。 | 页面内容（核验时） | 仅链接并原创归纳，不复制教程代码、正文或图表。 | 2026-09-24 |
| 官方文档 | ONNX Runtime：Quantize ONNX models | https://onnxruntime.ai/docs/performance/model-optimizations/quantization.html | 核对量化可能造成精度变化，以及比较浮点/量化模型权重和激活以定位差异的调试思路；不据此推断特定目标板兼容或精度。 | 页面内容（核验时） | 仅链接并原创归纳，不复制文档正文、表格或源码。 | 2026-09-24 |
| 官方 API 文档 | ONNX Runtime Python API | https://onnxruntime.ai/docs/api/python/api_summary | 核对 `InferenceSession` 输出接口、数据输入/输出表示及执行提供程序配置边界；通用 API 文档不证明 UNO Q 指定镜像/运行时已验证。 | 页面内容（核验时） | 仅链接并原创解释，不复制 API 文档内容或代码。 | 2026-09-24 |

本章 `compare_inference.py`、4 条合成对照记录、17 项标准库行为测试及 Fig-46 Mermaid 为本书原创。比较器仅读取离线分数，不运行模型、预处理、ONNX Runtime 或 UNO Q；容差与 `min_margin` 是教学输入，不是官方规范或产品验收门槛。参考输出质量、真实数据指标、目标运行时、资源/时延、现场环境和硬件动作均未验证；Fig-46 SVG 尚未渲染和目视审阅。

## 第七篇第5章补充核验

| 类型 | 来源 | 地址 | 用途与边界 | 版本基线 | 版权处理 | 核验日期 |
|---|---|---|---|---|---|---|
| 官方文档 | ONNX Runtime：Performance tuning | https://onnxruntime.ai/docs/performance/tune-performance/ | 核对时延、吞吐量、内存利用率和模型/应用大小是随场景选择的常见性能维度；不据此推断特定模型、UNO Q 镜像或执行提供程序的性能。 | 页面内容（核验时） | 仅链接和原创摘要，不复制文档正文、表格或图表。 | 2026-09-24 |
| 官方文档 | ONNX Runtime：Profiling tools | https://onnxruntime.ai/docs/performance/tune-performance/profiling-tools.html | 核对运行时性能 profiling 可输出线程及算子延迟等详细 trace；特定执行提供程序的 profiling 能力须在该提供程序/目标环境验证。 | 页面内容（核验时） | 仅链接和原创摘要，不复制文档正文、代码或 trace 示例。 | 2026-09-24 |
| 官方语言库文档 | Python：`time` — Time access and conversions | https://docs.python.org/3/library/time.html | 核对 `perf_counter_ns()` 适于测量短时差值、绝对参考点无意义，以及 `process_time()` 与经过时间口径不同；不代表本章使用它测量了模型。 | Python 3.14 文档（核验时） | 仅链接和原创解释，不复制文档正文或示例代码。 | 2026-09-24 |

本章 `analyze_benchmark.py`、21 项标准库行为测试、23 条合成记录及 Fig-47 Mermaid 为本书原创。样例分析只计算 20 条合成正式记录的最近秩 P50/P95、均值、最大值及输入的最大 RSS 观测；报告固定 `REPORT_ONLY`，无阈值判定。未运行模型/ONNX Runtime、未采集真实运行时或目标资源、未连接 UNO Q，Fig-47 SVG 尚未渲染并目视审阅。

## 第七篇第6章补充核验

| 类型 | 来源 | 地址 | 用途与边界 | 版本基线 | 版权处理 | 核验日期 |
|---|---|---|---|---|---|---|
| 官方文档 | ONNX Runtime：Quantize ONNX models | https://onnxruntime.ai/docs/performance/model-optimizations/quantization.html | 核对该运行时文档所述线性量化表示、静态校准输入、动态参数计算与量化误差调试；具体格式/算子支持及性能须按目标模型、运行时和设备另行验证，不证明 UNO Q 兼容。 | 页面内容（核验时） | 仅链接并原创摘要，不复制文档正文、表格或源码。 | 2026-09-24 |

本章 `quantization_demo.py`、固定标量向量、9 项标准库行为测试及 Fig-48 Mermaid 为本书原创。程序只模拟对称 int8 的数值量化/反量化，不生成模型工件、不评估任务精度、不测量实际文件/RAM/时延，也不访问 ONNX Runtime 或 UNO Q；Fig-48 SVG 尚未渲染和目视审阅。

## 第七篇第7章 UNO Q 板载 AI 实战补充核验

| 类型 | 来源 | 地址 | 用途与边界 | 版本基线 | 版权处理 | 核验日期 |
| --- | --- | --- | --- | --- | --- | --- |
| 官方硬件数据表 | Arduino UNO Q | https://docs.arduino.cc/resources/datasheets/ABX00162-ABX00173-datasheet.pdf | 核对 ABX00162/ABX00173 的 RAM/eMMC、QRB2210/Linux 与 STM32U585/Zephyr 分工、Bridge、App Lab、可选 Brick 与 4 GB SKU 的资源建议；不证明具体模型兼容或 AI 后端映射。 | ABX00162-ABX00173，PDF 标示 Modified 2026-09-22 | 仅链接并原创解释，不复制表格、图表或产品图片。 | 2026-09-26 |
| 官方示例 | Arduino App Bricks Examples：Object Detection | https://github.com/arduino/app-bricks-examples/tree/main/inspirational/common/object-detection · https://github.com/arduino/app-bricks-examples/blob/main/inspirational/common/object-detection/README.md | 核对当前示例目录、JPG/PNG 上传、标注图/标签、objectdetection 与 web_ui Brick，以及该示例声明 CPU-only/no C++ Sketch；不代表本项目已在板上运行。 | main 分支页面/README（核验时） | 仅链接和原创归纳；代码短片段按接口形态改写，不复制完整示例。 | 2026-09-26 |
| 官方示例代码 | Arduino App Bricks Examples：object detection `main.py` | https://github.com/arduino/app-bricks-examples/blob/main/inspirational/common/object-detection/python/main.py | 核对 `ObjectDetection` Python import、`detect`、`draw_bounding_boxes` 和 `WebUI` 回调接口形态；具体回调/manifest 须与目标版本示例复核。 | main 分支页面（核验时） | 仅链接及原创教学摘述，不复制完整源文件。 | 2026-09-26 |
| 官方应用规范 | Arduino App specification | https://github.com/arduino/arduino-app-cli/blob/main/docs/app-specification.md | 核对 `app.yaml`、`python/main.py`、可选 `sketch/`、Brick ID 与 Brick variables/secret 的规则；不推断通用变量必然传入 Python 进程环境。 | main 分支页面（核验时） | 仅链接并原创说明，不复制规范正文或完整示例。 | 2026-09-26 |
| 官方 Brick 实现 | Arduino App Bricks Python：`LargeLanguageModel` | https://github.com/arduino/app-bricks-py/blob/main/src/arduino/app_bricks/llm/local_llm.py | 核对 `genie:` / `llamacpp:` model 前缀、本地 runner 端点和当前模型列表查询实现；不保证 UNO Q 具体镜像已有 runner、模型或相同接口版本。 | main 分支源文件（核验时） | 仅链接及原创归纳，不复制源文件。 | 2026-09-26 |
| 官方芯片资料 | Qualcomm Dragonwing QRB2210 | https://www.qualcomm.com/internet-of-things/products/q2-series/qrb2210 | 核对 SoC 级 CPU/GPU/DSP 与 AI 能力说明；UNO Q 数据表/Arduino 示例没有说明特定 Brick 的算子后端，不能据 SoC 能力推断 DSP/NPU 被实际调用。 | QRB2210 产品页与产品 brief（核验时） | 仅链接并原创解释，不复制规格表或芯片图。 | 2026-09-26 |

本章原创图号为 Fig-49。短代码片段仅显示官方示例可核对的接口形态；没有复制样例图片、页面、CSS 或完整源码。对象检测实机、模型输出质量、SKU/资源、摄像头、Brick/runner 与加速后端均为 `NOT_RUN`；Fig-49 SVG 尚未渲染审阅。

## 第七篇第8章 UNO Q 接入 DeepSeek API 补充核验

| 类型 | 来源 | 地址 | 用途与边界 | 版本基线 | 版权处理 | 核验日期 |
| --- | --- | --- | --- | --- | --- | --- |
| 官方 API 参考 | DeepSeek Chat Completions | https://api-docs.deepseek.com/api/create-chat-completion/ | 核对 endpoint、messages、当前 model IDs、thinking、`max_tokens`、response choices/finish_reason 与错误语义；请求/响应示例由本章标准库客户端做受限实现。 | 页面内容（核验时） | 仅链接和原创实现，不复制完整文档或 SDK 样例。 | 2026-09-26 |
| 官方 API 指南 | DeepSeek Thinking Mode | https://api-docs.deepseek.com/guides/thinking_mode/ | 核对默认开启的思考模式及 `thinking.type=disabled`；本例明确关闭以限制简单摘要任务。 | 页面内容（核验时） | 仅链接并原创摘要，不复制正文或代码。 | 2026-09-26 |
| 官方 API 指南 | DeepSeek Multi-round Conversation | https://api-docs.deepseek.com/guides/multi_round_chat/ | 核对 Chat Completions 无状态及调用方需显式提交历史消息；本章故意不实现多轮上下文。 | 页面内容（核验时） | 仅链接和原创说明，不复制正文或代码。 | 2026-09-26 |
| 官方 API 参考 | DeepSeek Models / Models & Pricing / Change Log | https://api-docs.deepseek.com/api/list-models/ · https://api-docs.deepseek.com/quick_start/pricing/ · https://api-docs.deepseek.com/updates/ | 核验 `deepseek-flash` 当前标识以及 2026-09-10 公告对 V4.1 Flash 与兼容旧模型名的说明；模型路由、可用性、费率和限额易变，正文不固定价格。 | 页面内容（核验时）；公告日期 2026-09-10 | 仅链接与原创说明，不复制价格表。 | 2026-09-26 |
| 官方应用规范 | Arduino App specification | https://github.com/arduino/arduino-app-cli/blob/main/docs/app-specification.md | 核对 App/Python/Brick 结构及 Brick variables/secret 导出脱敏规则；不推断普通 Brick variables 自动注入 Python `os.environ`。 | main 分支页面（核验时） | 仅链接并原创说明，不复制规范正文。 | 2026-09-26 |
| 官方 Brick 实现 | Arduino App Bricks Python：`CloudLLM` | https://github.com/arduino/app-bricks-py/blob/main/src/arduino/app_bricks/cloud_llm/cloud_llm.py | 检查当前候选入口存在云 LLM、api_key/model 和扩展参数接口；不据此宣称 UNO Q/App Lab/DeepSeek 组合已验证。 | main 分支源文件（核验时） | 仅链接及原创归纳，不复制源文件。 | 2026-09-26 |

本章原创代码为 `deepseek_client.py` 与显式双开关 CLI `summarize_readings.py`；测试使用本地 mock transport 与固定合成读数，不读取真实密钥、不产生网络请求。真实 DeepSeek 调用、费用、UNO Q TLS、App Lab Python secret 注入均为 `NOT_RUN`；Fig-50 SVG 尚未渲染审阅。

<a id="part7-ch09-references"></a>

## 第七篇第9章工具调用安全边界补充核验

| 类型 | 来源 | 地址 | 用途与边界 | 版本基线 | 版权处理 | 核验日期 |
| --- | --- | --- | --- | --- | --- | --- |
| 官方 API 指南 | OpenAI Function Calling | https://developers.openai.com/api/docs/guides/function-calling | 核对工具调用的提案—应用执行—结果回传流程，以及应用侧负责执行工具的边界；该流程仅代表 OpenAI API 文档，不是通用协议或设备兼容证明。 | 页面内容（核验时） | 仅链接并原创摘要，不复制正文或代码。 | 2026-09-24 |
| 官方安全指南 | OpenAI Guardrails and human review | https://developers.openai.com/api/docs/guides/agents/guardrails-approvals | 核对输入/输出/工具行为防护与副作用前人工审查暂停点；不把 SDK 工作流当作 Arduino UNO Q 内置功能。 | 页面内容（核验时） | 仅链接并原创摘要，不复制正文或代码。 | 2026-09-24 |
| 社区安全指南 | OWASP GenAI LLM Top 10 2026 | https://genai.owasp.org/resource/owasp-genai-llm-top-10-2026/ | 核对 LLM03“过度代理权”关于工具功能、权限和自主性的风险及缓解方向；所链接 PDF 标示 Version 2026，封面发布日期字段待填写，不是法规、认证或本产品验收标准。 | 资源页及其链接 PDF（核验时） | 仅链接并原创摘要，不复制报告正文或图表。 | 2026-09-24 |
| 社区标准草案/示例 | OWASP Agent Control Standard 与公开仓库 | https://genai.owasp.org/resource/agent-control-standard-acs/ · https://github.com/GenAI-Security-Project/agent-control-standard | 仅作策略钩子概念参考；核验的 v0.1.0 仓库示例包括未认证 Guardian 通道和默认 `proceed` 故障策略，不能当作可直接部署的安全控制。 | 公开仓库 v0.1.0（核验时） | 仅链接并原创说明；不复制源码或误称为认证产品。 | 2026-09-24 |
| 官方风险管理指南 | NIST AI RMF Generative AI Profile | https://doi.org/10.6028/NIST.AI.600-1 | 核对生成式 AI 风险治理、测试、人类监督与记录建议；为自愿风险管理资料，不替代应用威胁建模或合规评估。 | NIST AI 600-1（2024） | 仅链接并原创摘要，不复制正文或图表。 | 2026-09-24 |
| 官方产品资料 | Arduino UNO Q 与 App Lab | https://docs.arduino.cc/hardware/uno-q · https://docs.arduino.cc/software/app-lab/ | 核对产品资料所述 Linux MPU、MCU、App Lab、Python/sketch/AI 组合与 Bridge/RPC 定位；资料不证明通用 LLM 工具安全门已内置、兼容或实机验证。 | 页面内容（核验时） | 仅链接并原创摘要，不复制图表或产品正文。 | 2026-09-24 |

本章文字、`tool_guard.py`、12 项标准库测试和 Fig-51 Mermaid 为本书原创教学材料。模拟器不调用模型/API、网络、App Lab、Bridge、MCU、GPIO 或执行器；测试只验证本机进程内策略契约，不证明真实身份认证、持久重放控制、生产部署或 UNO Q 实机兼容。Fig-51 SVG 尚未渲染和目视审阅。

<a id="part7-ch10-references"></a>

## 第七篇第10章 AI 应用综合验证补充核验

| 类型 | 来源 | 地址 | 用途与边界 | 版本基线 | 版权处理 | 核验日期 |
| --- | --- | --- | --- | --- | --- | --- |
| 官方风险管理指南 | NIST AI RMF Generative AI Profile | https://doi.org/10.6028/NIST.AI.600-1 | 核对该跨行业档案的自愿使用定位、AI 生命周期风险管理目的，以及治理、内容来源、部署前测试、事件披露等关注点；本章八道证据门为本书综合设计，不是 NIST 清单。 | NIST AI 600-1，2024年7月 | 仅链接并原创归纳，不复制报告正文或图表。 | 2026-09-24 |
| 官方产品页 | Arduino UNO Q | https://docs.arduino.cc/hardware/uno-q | 核对 Debian Linux 侧 QRB2210 MPU、Zephyr 侧 STM32U585 MCU、App Lab 与 Bridge/RPC 的产品架构说明；不据此声称本章验收器在板上运行或已兼容。 | 页面内容（核验时） | 仅链接并原创解释，不复制产品图表、截图或正文。 | 2026-09-24 |
| 官方应用规范 | Arduino App specification | https://github.com/arduino/arduino-app-cli/blob/main/docs/app-specification.md | 核对 Arduino App 中 Sketch 的 MCU 侧、Python/Brick/容器的 Linux 侧及 RPC 协作边界；本章证据字段与部署门槛为教程级设计，不是官方规范。 | main 分支页面（核验时） | 仅链接并原创归纳，不复制规范正文或代码。 | 2026-09-24 |

本章 `readiness_gate.py`、合成 `evidence_manifest.json`、14 项标准库测试及 Fig-52 Mermaid 为本书原创。检查器仅核对清单结构和提交者状态声明，不读取证据引用、不验证模型/数据/设备事实，也不授权部署。未调用生成模型、网络、App Lab、Bridge、MCU 或 UNO Q；Fig-52 SVG 尚未渲染和目视审阅。

## 第八篇第1章补充核验

| 类型 | 来源 | 地址 | 用途与边界 | 版本基线 | 版权处理 | 核验日期 |
| --- | --- | --- | --- | --- | --- | --- |
| 官方产品资料 | Arduino UNO Q | https://docs.arduino.cc/hardware/uno-q | 核对双处理器平台、无线连接和产品级职责概况；不证明本章参考架构、特定传感器、网络服务或样例已在目标板运行。 | 页面内容（核验时） | 仅链接与原创说明，不复制图表、截图或正文。 | 2026-09-24 |
| 官方应用规范 | Arduino App specification | https://github.com/arduino/arduino-app-cli/blob/main/docs/app-specification.md | 核对 Sketch/MCU、Python/Brick/容器/Linux 侧与 RPC 协作的应用格式边界；不把本章架构图误作 App Lab 自动配置或 MQTT 集成声明。 | main 分支页面（核验时） | 仅链接并原创归纳，不复制规范正文或代码。 | 2026-09-24 |
| 国际标准 | OASIS MQTT Version 5.0 | https://docs.oasis-open.org/mqtt/mqtt/v5.0/os/mqtt-v5.0-os.html | 核对发布/订阅传输、载荷语义独立性、QoS 0/1/2 和协议确认范围；不推断端到端业务 exactly-once。 | OASIS Standard，2019-03-07 | 仅链接并原创摘要，不复制标准文本或图表。 | 2026-09-24 |
| IETF 标准 | RFC 8259 JSON | https://www.rfc-editor.org/rfc/rfc8259.html | 核对 JSON 对象、数字及重复成员名的互操作注意事项；样例仅采用小型固定教学契约。 | RFC 8259，2017-12 | 仅链接并原创解释，不复制 RFC 正文。 | 2026-09-24 |
| IETF 标准 | RFC 3339 时间戳与 RFC 9557 更新 | https://www.rfc-editor.org/rfc/rfc3339.html · https://www.rfc-editor.org/rfc/rfc9557.html | 核对互联网事件时间的日期/时区偏移格式及后续语义更新；本章校验器只实现受限子集，不支持闰秒，并拒绝 `-00:00` 未知本地偏移约定。 | RFC 3339；RFC 9557 部分更新 | 仅链接并原创解释，不复制 RFC 正文。 | 2026-09-24 |
| 官方语言文档 | Python `json` 模块 | https://docs.python.org/3.14/library/json.html | 核对 `object_pairs_hook` 和 `parse_constant` 可用于自定义重复键及非标准常量处理；不把样例校验器当作通用安全解析器。 | Python 3.14 文档（核验时） | 仅链接并原创说明，不复制文档代码或正文。 | 2026-09-24 |
| 官方语言文档 | Python `datetime` 模块 | https://docs.python.org/3.14/library/datetime.html | 核对 `datetime.fromisoformat()` 的日期时间解析接口；RFC 3339 子集限制由本章另行定义。 | Python 3.14 文档（核验时） | 仅链接并原创说明，不复制文档代码或正文。 | 2026-09-24 |

本章 `validate_telemetry.py`、合成 `telemetry_sample.json`、16 项行为测试和 Fig-53 Mermaid 均为本书原创。校验器只检查 UTF-8/JSON 边界和教学字段契约；未访问传感器、网络、MQTT/HTTP 服务、Bridge/RPC、数据库或 UNO Q，未验证身份、真实性、时钟、校准、幂等和目标环境；Fig-53 SVG 尚未渲染和目视审阅。

## 第八篇第2章补充核验

| 类型 | 来源 | 地址 | 用途与边界 | 版本基线 | 版权处理 | 核验日期 |
| --- | --- | --- | --- | --- | --- | --- |
| 国际标准 | OASIS MQTT Version 5.0 | https://docs.oasis-open.org/mqtt/mqtt/v5.0/mqtt-v5.0.html | 核对第2章主题层级/过滤器（第4.7节）、QoS 0/1/2 和确认流程（第4.3节）、消息保留（第3.3.1.3节）及会话到期（第3.1.2.11.2、4.1节）；不据此推断应用数据库或外部副作用恰好执行一次。 | OASIS Standard，2019-03-07 | 仅链接并原创归纳，不复制标准文本或图表。 | 2026-09-24 |
| 官方语言文档 | Python `sqlite3` 模块 | https://docs.python.org/3.14/library/sqlite3.html | 核对 Python 数据库连接、事务提交/回滚与 `sqlite3` 事务控制接口；本章代码只验证本机教学样例，不表示目标板运行环境已验证。 | Python 3.14 文档（核验时） | 仅链接并原创解释，不复制文档正文或示例代码。 | 2026-09-24 |
| 官方数据库文档 | SQLite Transactions | https://www.sqlite.org/lang_transaction.html | 核对显式事务的 `BEGIN`、`COMMIT`、`ROLLBACK` 语义；不把单库事务扩展为跨 Broker、API 或硬件的原子操作。 | 页面内容（核验时） | 仅链接并原创说明，不复制文档正文或图表。 | 2026-09-24 |
| 官方数据库文档 | SQLite Atomic Commit | https://www.sqlite.org/atomiccommit.html | 核对 SQLite 单个事务原子提交的设计说明及相关存储前提；不据此承诺所有文件系统/设备故障下的数据恢复。 | 页面内容（核验时） | 仅链接并原创归纳，不复制文档正文或图表。 | 2026-09-24 |

本章 `idempotent_consumer.py`、两行合成 `qos1_redelivery.jsonl`、5 项标准库测试及 Fig-54 Mermaid 为本书原创。脚本调用第1章校验器，仅在本机 SQLite 中演示同库账本与模拟效果事务；没有 MQTT 库、QoS 包交换、PUBACK、Broker、网络、TLS/ACL、设备或外部副作用。两个进程测试只证明固定测试条件下本机数据库文件复用和重复抑制，不验证断电/存储故障恢复或生产保留策略；Fig-54 SVG 尚未渲染和目视审阅。

## 第八篇第3章补充核验

| 类型 | 来源 | 地址 | 用途与边界 | 版本基线 | 版权处理 | 核验日期 |
| --- | --- | --- | --- | --- | --- | --- |
| 国际标准 | OASIS MQTT Version 5.0 | https://docs.oasis-open.org/mqtt/mqtt/v5.0/mqtt-v5.0.html | 核对第4.1节会话状态和存储限制、第4.3.2节 QoS 1 至少一次交付及 PUBACK 协议边界；不据此推断应用侧本地队列已落盘或端到端业务恰好一次。 | OASIS Standard，2019-03-07 | 仅链接并原创归纳，不复制标准文本或图表。 | 2026-09-24 |
| 官方语言文档 | Python `sqlite3` 模块 | https://docs.python.org/3.14/library/sqlite3.html | 核对数据库连接、事务提交/回滚以及连接上下文管理器不会自动关闭连接的边界；本章实现为每次操作显式关闭连接。 | Python 3.14 文档（2026-09-24 核验） | 仅链接并原创解释，不复制文档正文或示例代码。 | 2026-09-24 |
| 官方数据库文档 | SQLite Transactions | https://www.sqlite.org/lang_transaction.html | 核对 SQLite 显式事务及单写事务边界；不将本地数据库事务扩展为跨 Broker 或消费者的分布式原子提交。 | 页面内容（核验时） | 仅链接并原创说明，不复制文档正文或图表。 | 2026-09-24 |
| 官方数据库文档 | SQLite Atomic Commit | https://www.sqlite.org/atomiccommit.html | 核对 SQLite 单库事务原子提交的模型及其存储环境前提；不据此宣称本章已验证掉电、文件系统或存储介质故障恢复。 | 页面内容（核验时） | 仅链接并原创归纳，不复制文档正文或图表。 | 2026-09-24 |

本章 `outbox.py`、3 条合成 `offline_telemetry.jsonl`、11 项标准库测试及 Fig-55 Mermaid 均为本书原创。SQLite 逻辑队列容量与单条载荷上限不代表数据库物理文件或闪存写入量具有同等硬上限；没有真实 MQTT 包、Broker、网络、UNO Q、传感器、断电注入或目标介质耐久性测试；Fig-55 SVG 尚未生成和目视审阅。

## 第八篇第4章补充核验

| 类型 | 来源 | 地址 | 用途与边界 | 版本基线 | 版权处理 | 核验日期 |
| --- | --- | --- | --- | --- | --- | --- |
| 官方概念文档 | OpenTelemetry Signals | https://opentelemetry.io/docs/concepts/signals/ | 核对指标、日志和追踪作为不同遥测信号的概念；本章报告不是 OpenTelemetry SDK 或 Collector 输出。 | 官方在线文档（核验时） | 仅链接和原创转述，不复制文档正文或图表。 | 2026-09-24 |
| 官方术语文档 | OpenTelemetry Glossary：Cardinality | https://opentelemetry.io/docs/concepts/glossary/ | 核对属性基数及高基数对后端资源的影响；本章只提出标签设计注意事项，不规定通用的设备标识方案。 | 官方在线文档（核验时） | 仅链接和原创转述，不复制文档正文或图表。 | 2026-09-24 |
| 官方实践指南 | Prometheus Instrumentation | https://prometheus.io/docs/practices/instrumentation/ | 核对 counter/gauge、时间戳、队列长度/等待时间和标签基数相关实践；其中建议须结合目标监控系统与设备规模评估。 | 官方在线文档（核验时） | 仅链接和原创归纳，不复制文档示例代码或正文。 | 2026-09-24 |
| 官方实践指南 | Prometheus Metric and label naming | https://prometheus.io/docs/practices/naming/ | 核对指标单位/名称与避免高基数标签的建议；本章没有定义 Prometheus 导出器或实际指标名。 | 官方在线文档（核验时） | 仅链接和原创归纳，不复制文档表格或正文。 | 2026-09-24 |
| 官方实践指南 | Prometheus Alerting | https://prometheus.io/docs/practices/alerting/ | 核对关注症状、留出短暂抖动余量和控制告警噪声等通用实践；本章教学 finding 不是生产告警规则。 | 官方在线文档（核验时） | 仅链接和原创归纳，不复制文档正文或图表。 | 2026-09-24 |

本章 `health_observer.py`、4 条合成 `health_snapshots.jsonl`、14 项标准库行为测试及 Fig-56 Mermaid 均为本书原创。判定器仅处理受限本地 JSONL，并按显式参考时刻输出建议；没有 OpenTelemetry SDK/Collector、Prometheus、指标后端、通知渠道、真实设备身份、Broker、网络或 UNO Q 实机验证。90 秒、300 秒、600 秒、0.80 与重试阈值是固定教学假设；单快照分类没有迟滞、告警去重/确认/恢复状态；Fig-56 SVG 尚未生成和目视审阅。

## 第八篇第5章补充核验

| 类型 | 来源 | 地址 | 用途与边界 | 版本基线 | 版权处理 | 核验日期 |
| --- | --- | --- | --- | --- | --- | --- |
| 官方技术报告 | NISTIR 8259A：IoT Device Cybersecurity Capability Core Baseline | https://csrc.nist.gov/pubs/ir/8259/a/final | 作为按设备用途识别与裁剪 IoT 网络安全能力的基线参考；本章用其校准概念范围，不声明符合性或认证。 | NISTIR 8259A，最终版（2020-05） | 仅链接并原创归纳；不复制报告正文或图表。 | 2026-09-24 |
| 官方能力目录 | NIST IoT Device Cybersecurity Requirement Catalogs：Technical Capabilities | https://pages.nist.gov/IoT-Device-Cybersecurity-Requirement-Catalogs/technical/ | 核对设备识别、配置、数据保护、逻辑访问、软件更新与安全状态感知等能力主题；目录须结合设备与风险配置文件裁剪。 | 官方在线目录（核验时） | 仅链接并原创归纳；不复制目录内容或图表。 | 2026-09-24 |
| 国际标准 | OASIS MQTT Version 5.0 | https://docs.oasis-open.org/mqtt/mqtt/v5.0/mqtt-v5.0.html | 核对请求/响应模式及 Response Topic、Correlation Data 等关联属性；这些协议属性不承担请求者身份认证、应用授权或物理效果证明。 | OASIS Standard，2019-03-07 | 仅链接并原创解释，不复制标准文本或图表。 | 2026-09-24 |

本章 `remote_command_gate.py`、6 条合成 JSONL 命令、30 项标准库测试及 Fig-57 Mermaid 均为本书原创。脚本限制 JSON 输入、命令有效期和进程内账本容量，只演示本地状态逻辑；固定命令样例的未知结果表示本地账本无对应记录，不模拟网络超时或设备回执丢失。没有身份认证、签名/TLS/MQTT ACL、真实 Broker/网络、持久账本、并发/崩溃恢复、Bridge/RPC、MCU、传感器、UNO Q 或物理执行验证。300 秒、4096 字节、64 条与采样周期范围都是教学策略；Fig-57 SVG 尚未生成和目视审阅。

## 第八篇第6章补充核验

| 类型 | 来源 | 地址 | 用途与边界 | 版本基线 | 版权处理 | 核验日期 |
| --- | --- | --- | --- | --- | --- | --- |
| 官方技术报告 | [NIST IR 8259 Rev. 1：IoT 产品制造商基础网络安全活动](https://csrc.nist.gov/pubs/ir/8259/r1/final) | https://csrc.nist.gov/pubs/ir/8259/r1/final | 参考制造商在产品销售前可考虑的网络安全活动；本章将其作为风险管理背景，不把该报告解释为设备认证或本章实现要求。 | NIST IR 8259 Rev. 1 Final，2026-04-20；取代 2020 年 IR 8259 | 仅链接并原创归纳，不复制报告正文或图表。 | 2026-09-25 |
| 官方技术报告 | [NISTIR 8259A：IoT 设备网络安全能力核心基线](https://csrc.nist.gov/pubs/ir/8259/a/final) | https://csrc.nist.gov/pubs/ir/8259/a/final | 作为识别设备网络安全能力的共同核心起点；本章只借鉴唯一识别、数据保护和逻辑访问等概念，不声称符合基线或通过认证。 | NISTIR 8259A Final，2020-05-29 | 仅链接并原创归纳，不复制报告正文或图表。 | 2026-09-25 |
| 官方能力目录 | [NIST IoT Device Cybersecurity Requirement Catalogs：Technical Capabilities](https://pages.nist.gov/IoT-Device-Cybersecurity-Requirement-Catalogs/technical/) | https://pages.nist.gov/IoT-Device-Cybersecurity-Requirement-Catalogs/technical/ | 对照设备标识、配置、数据保护、接口逻辑访问、软件更新、网络安全状态感知和设备安全等能力；目录应按设备、用途和风险裁剪，不是普遍强制清单。 | 官方在线目录；目录说明当前版本为 Spring 2021，页面核验于 2026-09-25 | 仅链接并原创归纳，不复制目录内容或图表。 | 2026-09-25 |
| IETF 标准 | [RFC 9846：TLS 1.3 协议](https://datatracker.ietf.org/doc/rfc9846/) | https://datatracker.ietf.org/doc/rfc9846/ | 核对 TLS 1.3 安全通道协议背景；协议本身不替应用定义服务身份校验或 MQTT 授权，本章代码也未实现或运行 TLS。 | RFC 9846，2026-07；取代 RFC 8446 | 仅链接并原创说明，不复制 RFC 正文。 | 2026-09-25 |
| IETF 标准 | [RFC 9525：TLS 中的服务身份](https://datatracker.ietf.org/doc/html/rfc9525) | https://datatracker.ietf.org/doc/html/rfc9525 | 核对客户端参考身份与服务端呈现身份的匹配原则；该服务身份规则不替代证书链、信任锚或应用授权校验。 | RFC 9525，2023-11；取代 RFC 6125 | 仅链接并原创说明，不复制 RFC 正文。 | 2026-09-25 |
| 国际标准 | [OASIS MQTT Version 5.0](https://docs.oasis-open.org/mqtt/mqtt/v5.0/mqtt-v5.0.html) | https://docs.oasis-open.org/mqtt/mqtt/v5.0/mqtt-v5.0.html | 核对 Client ID、连接认证/授权背景及主题发布订阅边界；本章精确到每设备、每方向的默认拒绝 ACL 是教程策略，不能由 Client ID 自动推导身份或授权。 | OASIS Standard，2019-03-07 | 仅链接并原创归纳，不复制标准文本或图表。 | 2026-09-25 |

本章 `policy_linter.py`、合成 `profiles.json`、45 项本地标准库测试及 Fig-58 Mermaid 为本书原创。检查器只静态审阅固定 JSON 策略并报告 PASS/DENY；不验证密钥、证书链、TLS 握手、Broker 认证/授权、网络连接、Bridge/RPC、MCU 或 UNO Q 实机。Fig-58 SVG 尚未生成和目视审阅。

## 第八篇第7章补充核验

| 类型 | 来源 | 地址 | 用途与边界 | 版本基线 | 版权处理 | 核验日期 |
| --- | --- | --- | --- | --- | --- | --- |
| 官方语言文档 | Python `unittest`：命令行与测试发现 | https://docs.python.org/3.14/library/unittest.html | 核对 `python -m unittest discover`、`-s` 起始目录和 `-p` 文件匹配参数；本章将这些选项用于六个仓库内固定目录，不对目标设备或部署环境作判断。 | Python 3.14.7 官方文档（页面核验于 2026-09-25） | 仅链接并原创说明，不复制文档正文或示例代码。 | 2026-09-25 |

本章 `aggregate_local_tests.py`、第1～6章 121 项测试结果汇总、15 项聚合器/文档契约测试及 Fig-59 Mermaid 均为本书原创。聚合器本身只在本机依次启动仓库内六个固定 `unittest` 目录，不接受任意路径/命令，也不自行建立网络/Broker/硬件连接。测试子进程继承调用环境并以当前用户权限执行，故本工具不是沙箱，只应运行可信仓库的测试代码；本次固定样例未连接网络、Broker、传感器、Bridge/RPC、MCU 或 UNO Q。报告固定为 `LOCAL_TESTS_ONLY`、`target_validation=NOT_RUN` 与 `deployment_authorized=false`；本机测试结果不是目标环境验收或部署批准。Fig-59 SVG 尚未渲染和目视审阅。

## 第九篇第1章 技术背景核验

| 类型 | 来源 | 地址 | 用途与边界 | 版本基线 | 版权处理 | 核验日期 |
|---|---|---|---|---|---|---|
| 官方板卡文档 | [Arduino UNO Q User Manual](https://docs.arduino.cc/tutorials/uno-q/user-manual/) | https://docs.arduino.cc/tutorials/uno-q/user-manual/ | 仅引用官方 UNO Q 用户手册作为目标平台背景入口；本章不据此推断环境传感器已集成，也不把产品文档作为本项目实机、传感器、告警或现场验证证据。 | 页面最近修订 2026-09-22；访问 2026-09-26 | Arduino 官方文档；本项目只链接并原创重述，不复制正文或图片；访问不代表取得外部材料再分发许可。 | 2026-09-26 |
