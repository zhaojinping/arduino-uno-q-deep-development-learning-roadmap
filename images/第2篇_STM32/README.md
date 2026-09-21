# 第二篇图示资源登记

## 图 2-2：PWM 资源决策图

- 图号：Fig-08
- 状态：占位说明（Mermaid 源文件已存在，SVG 尚未提交）
- 目标文件：ch02-fig08-uno-q-stm32-pwm-duty-cycle-boundary.svg
- 图源：[PWM 资源决策 Mermaid 源文件](../../diagrams/uno-q-stm32-pwm-duty-cycle-boundary.mmd)
- 正文位置：[第二篇第 2 章第 4 节：PWM 资源决策图](../../book/第2篇_STM32/第2章_PWM与定时输出_从占空比到安全控制.md#fig-08-uno-q-stm32-pwm-duty-cycle-boundary)
- 内容要求：展示 PWM 需求从周期、频率、占空比和极性定义，经过板级资源、定时器通道、Core/Devicetree/驱动、安全初始状态、API 选择、实时责任到波形和负载验证的成功与停止路径
- 来源边界：基于 Arduino、Zephyr 和 ST 官方资料原创重绘；不直接复制官方产品图、数据表框图或第三方图片

## 图 2-3：ADC 采样决策图

- 图号：Fig-09
- 状态：占位说明（Mermaid 源文件已存在，SVG 尚未提交）
- 目标文件：ch03-fig09-uno-q-stm32-adc-measurement-boundary.svg
- 图源：[ADC 采样决策 Mermaid 源文件](../../diagrams/uno-q-stm32-adc-measurement-boundary.mmd)
- 正文位置：[第二篇第 3 章第 4 节：ADC 采样决策图](../../book/第2篇_STM32/第3章_ADC与模拟采样_从电压读数到可验证数据.md#fig-09-uno-q-stm32-adc-measurement-boundary)
- 内容要求：展示 ADC 需求从输入范围和采样率，经过 A0～A5/外部输入选择、电气保护、参考/增益/分辨率/校准、采样序列、原始码换算、MCU/Linux 责任到重复性与故障验证的成功和停止路径
- 来源边界：基于 Arduino、Zephyr 和 ST 官方资料原创重绘；不直接复制官方产品图、数据表框图或第三方图片

## 图 2-4：串口通信决策图

- 图号：Fig-10
- 状态：占位说明（Mermaid 源文件已存在，SVG 尚未提交）
- 目标文件：ch04-fig10-uno-q-stm32-uart-boundary.svg
- 图源：[串口通信边界 Mermaid 源文件](../../diagrams/uno-q-stm32-uart-boundary.mmd)
- 正文位置：[第二篇第 4 章第 6 节：串口通信决策图](../../book/第2篇_STM32/第4章_串口通信_从帧格式到MCU_Linux边界.md#fig-10-uno-q-stm32-uart-boundary)
- 内容要求：展示通信需求从 UART 资源、引脚复用和电气核验，经过波特率/帧格式/校验/超时、轮询/中断/异步 API、缓冲与回环错误验证，到 MCU/Linux 边界和证据记录的成功与停止路径
- 来源边界：基于 Arduino、Zephyr 和 ST 官方资料原创重绘；不直接复制官方产品图、数据表框图或第三方图片

## 图 2-1：STM32 GPIO 任务决策图

- 图号：Fig-07
- 状态：占位说明（Mermaid 源文件已存在，SVG 尚未提交）
- 目标文件：ch01-fig07-uno-q-stm32-gpio-boundary.svg
- 图源：[STM32 GPIO 边界 Mermaid 源文件](../../diagrams/uno-q-stm32-gpio-boundary.mmd)
- 正文位置：[第二篇第 1 章第 4 节：GPIO 任务决策图](../../book/第2篇_STM32/第1章_STM32侧开发基础_GPIO与实时边界.md#fig-07-uno-q-stm32-gpio-boundary)
- 内容要求：展示 GPIO 需求从 MCU 责任、板级资源、STM32/Devicetree 映射、电气核验、API 选择、实时性判断到证据记录的成功与停止路径
- 来源边界：基于 Arduino、Zephyr 和 ST 官方资料原创重绘；不直接复制官方产品图、数据表框图或第三方图片

## 图 2-5：SPI 通信决策图

- 图号：Fig-11
- 状态：占位说明（Mermaid 源文件已存在，SVG 尚未提交）
- 目标文件：ch05-fig11-uno-q-stm32-spi-boundary.svg
- 图源：[SPI 通信边界 Mermaid 源文件](../../diagrams/uno-q-stm32-spi-boundary.mmd)
- 正文位置：[第二篇第 5 章第 6 节：SPI 通信决策图](../../book/第2篇_STM32/第5章_SPI通信_从片选时序到设备驱动边界.md#fig-11-uno-q-stm32-spi-boundary)
- 内容要求：展示 SPI 需求从控制器、引脚和 CS 核验，经过 CPOL/CPHA、位序、字宽、频率、事务和 Arduino/Zephyr API 选择，到设备 ID、逻辑分析、错误注入及 MCU/Linux 所有权记录的成功和停止路径
- 来源边界：基于 Arduino、Zephyr 和 ST 官方资料原创重绘；不直接复制官方产品图、数据表框图或第三方图片

## 图 2-6：I2C 通信与总线恢复决策图

- 图号：Fig-12
- 状态：占位说明（Mermaid 源文件已存在，SVG 尚未提交）
- 目标文件：ch06-fig12-uno-q-stm32-i2c-recovery-boundary.svg
- 图源：[I2C 通信与总线恢复 Mermaid 源文件](../../diagrams/uno-q-stm32-i2c-recovery-boundary.mmd)
- 正文位置：[第二篇第 6 章第 6 节：I2C 通信与总线恢复决策图](../../book/第2篇_STM32/第6章_I2C通信_从设备地址到总线恢复.md#fig-12-uno-q-stm32-i2c-recovery-boundary)
- 内容要求：展示 I2C 需求从 SDA/SCL、电压、上拉和 7 位地址核验，经过 Wire/Zephyr 事务、ACK/NACK、超时、总线恢复和 MCU/Linux 所有权记录的成功与停止路径
- 来源边界：基于 Arduino、Zephyr、NXP 和 ArduinoCore-zephyr 官方资料原创重绘；不直接复制官方产品图、数据表框图或第三方图片
