# 第1章代码

## 示例列表

- [Blink：MCU 侧板载 LED 基础示例](Blink/README.md)

## 目录结构

```text
第1章_Arduino的发展/
├── README.md
└── Blink/
    ├── Blink.ino
    └── README.md
```

## 编译与上传前提

需要 Arduino IDE 或等价工具、Arduino UNO Q Zephyr Core；请选择 `UNO Q Board` 并确认目标端口。详细操作步骤见 [Blink 运行说明](Blink/README.md)。

## 验证边界

本目录示例对应正文[第 6 节“用 Blink 看跨代际的编程连续性”](../../book/第1篇_认识UNOQ/第1章_Arduino的发展.md#6-用-blink-看跨代际的编程连续性)。示例面向 Arduino UNO Q 的 STM32U585 MCU 侧；静态检查或 CLI 编译不等同于上传成功，也不等同于实机运行，更不能证明 MPU/Linux 应用或 Bridge/RPC 已工作。
