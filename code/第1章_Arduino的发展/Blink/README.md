# Blink

## 目标与边界

这是与[第 1 章第 6 节](../../../book/第1篇_认识UNOQ/第1章_Arduino的发展.md#6-用-blink-看跨代际的编程连续性)对应的最小 Arduino Sketch。目标板卡是 Arduino UNO Q，目标执行侧是 STM32U585 MCU；在 UNO Q 章节语境下，Sketch 运行在 MCU 侧的 Zephyr 环境。`LED_BUILTIN` 对应的具体物理指示灯由目标板卡定义。

## 代码说明

- 用途：以约 1 秒间隔反转一次 LED 输出，演示 `setup()`、`loop()`、`pinMode()` 和 `digitalWrite()`。
- 运行环境：Arduino UNO Q 的 STM32U585 MCU 侧。
- 文件位置：`code/第1章_Arduino的发展/Blink/Blink.ino`。
- 依赖：Arduino UNO Q Zephyr Core 提供的板级定义和 Arduino API；无外部库。
- 操作步骤：在 Arduino IDE 中安装 Arduino UNO Q Zephyr Core，选择 `UNO Q Board`，打开本目录中的 `.ino` 并编译、上传；或在 Arduino App Lab 中复制为可编辑 App 后运行 Sketch。上传前确认目标板卡和端口，停止条件由工具报告的错误决定。
- 预期输出：示例现象为板载用户 LED 约每秒切换一次；这是预期现象说明，不是本次实测结果。
- 故障排查：先核对核心、板卡和端口，再查看编译或上传错误；`LED_BUILTIN` 的物理位置和指示灯含义以目标板卡资料为准。若仅完成编译，不应据此判断硬件已运行。
- 验证方式：分别记录源代码静态检查、`arduino-cli` 编译、上传和实机观察；任一项不能替代其他项。

## 当前验证状态（2026-09-16）

- 静态检查：已通过本地源代码级检查，结果详见 Task 4 报告。
- CLI 编译：本环境未发现 `arduino-cli`，CLI 编译未执行/未完成。
- 实机运行：未执行，不能声称 LED 已实际切换。

## 限制

本示例只覆盖 MCU 侧 Sketch 路径，不证明 MPU/Linux 应用、Arduino App Lab 的完整项目协同或 Bridge/RPC 已经工作。
