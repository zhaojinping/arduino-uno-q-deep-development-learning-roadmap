# 第七篇第7章：UNO Q 板载 AI 实战

本章围绕 Arduino 官方 App Bricks Examples 的 `inspirational/common/object-detection` 示例，说明 Linux/Python 侧如何调用 `ObjectDetection` Brick，并将上传图像、检测记录与标注图返回 WebUI。官方示例当前声明使用板上 CPU；正文不把这条示例路径描述为 GPU/DSP/NPU 加速。

## 使用边界

- 目标验证需要 Arduino UNO Q、匹配版本的 App Lab 与 Brick；本地契约测试只读取 Markdown 和 Mermaid，不导入 Arduino 运行库、不加载模型、不访问网络或硬件。
- 不连接真实摄像头，不读取个人图像，不调用 DeepSeek，不执行 Bridge、MCU、GPIO 或执行器操作。
- 代码片段是对官方接口形态的短篇教学说明，不是此仓库内可独立部署的完整 App。运行时以随目标版本提供的官方示例、`app.yaml` 与 Brick 清单为准。
- UNO Q SKU、App Lab/OS/Brick/model/runner 版本、CPU/RSS/时延以及端侧 LLM 兼容性均须实机记录，当前为 `NOT_RUN`。

## 验证

从仓库根目录运行：

```text
python -m pytest -q code/第7篇_AI/第7章_UNO_Q板载AI实战/test_onboard_ai_contract.py
```

契约测试检查章节结构、官方能力边界、Mermaid 双源一致、资源登记、内部链接、导航、图号迁移和凭据样式字符串。它不证明 App Lab 可部署、Brick 可导入、模型可运行或设备性能达标。

## 官方来源

- [Arduino Object Detection 示例说明](https://github.com/arduino/app-bricks-examples/blob/main/inspirational/common/object-detection/README.md)
- [Arduino App specification](https://github.com/arduino/arduino-app-cli/blob/main/docs/app-specification.md)
- [Arduino UNO Q 数据表](https://docs.arduino.cc/resources/datasheets/ABX00162-ABX00173-datasheet.pdf)
- [Qualcomm QRB2210 产品资料](https://www.qualcomm.com/internet-of-things/products/q2-series/qrb2210)
