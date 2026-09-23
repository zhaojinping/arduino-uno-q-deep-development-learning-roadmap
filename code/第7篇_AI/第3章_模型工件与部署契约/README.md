# 第七篇第3章：模型工件与部署契约

本目录提供一份**教学用 JSON 清单**和一个离线预检器。它只检查清单结构、输入/输出张量描述、单文件相对路径和 SHA-256；输出始终不会成为部署批准。配套工件是纯文本提示文件，不是模型权重、ONNX 文件或可执行模型。

## 文件

- [`model_manifest.json`](model_manifest.json)：教学清单；Linux MPU 只是候选执行侧，运行时、系统镜像和资源预算明确留空/未固定。
- [`teaching-artifact.txt`](teaching-artifact.txt)：故意不可运行的占位内容，其摘要用于演示文件完整性核对。
- [`model_preflight.py`](model_preflight.py)：Python 标准库命令行检查器；不会导入推理框架、下载文件、解包工件、安装运行时或访问开发板。
- [`test_model_preflight.py`](test_model_preflight.py)：10 项命令行行为测试，覆盖元数据与摘要、格式冲突、张量/标签契约、路径越界、标量/零长度维元数据和畸形 JSON。

## 运行

在本目录使用 Python 3 执行：

```text
python model_preflight.py --manifest model_manifest.json
python -m unittest -v test_model_preflight.py
```

清单结构和文件 SHA-256 均通过时，报告为 `REVIEW_REQUIRED_NOT_DEPLOYABLE`，其中仍列出目标运行时兼容性、实机执行证据、工件来源/许可、评估证据和资源预算等阻断项。命令退出码 `0` 仅表示检查器成功生成了复核报告；它不表示模型可加载、可运行或可发布。格式不匹配、哈希错误、清单缺项、路径越界等输入错误返回 `BLOCKED` 和退出码 `1`。

摘要只能说明文件字节与清单记录相符，不能证明来源可信、许可证有效、文件安全、模型精度或运行时兼容。此教学脚本一次只核对一个文件；若实际模型依赖 ONNX 外部张量数据、插件、自定义算子或其他伴随资源，必须把整个依赖集合纳入正式工件清单并另行验证。本目录不提供该集合的部署支持。

该实验只读本目录中的 JSON 和文本文件，只向标准输出写 JSON，不联网、不访问 App Lab、Bridge、Linux/MCU 目标板或执行器，无系统配置变更，因此无需回滚。更多解释见[第七篇第3章正文](../../../book/第7篇_AI/第3章_模型工件与部署契约_从清单到目标预检.md)。
