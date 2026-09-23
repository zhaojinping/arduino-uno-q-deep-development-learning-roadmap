# 第六篇第8章：OpenCV 综合验证

[返回正文](../../../book/第6篇_OpenCV/第8章_OpenCV综合验证_从合成画面到反馈审查证据包.md) · [返回代码索引](../../README.md) · [交接模板](handoff-template.md)

本目录的 `run_visual_handoff.py` 复用第5章 `locate_hsv_region`、第6章 `TemporalGate.process` 和第7章 `review_feedback`。它创建 8 帧 128×160 的内存合成图像，打印 8 条真实管线记录与 1 条第3帧错会话复核探针，格式为每行一个 JSON 对象（JSONL）。复核探针不再经过时间门，不是第9帧。

脚本无摄像头、网络、Bridge、MCU 或输出设备调用，不写结果文件。唯一可通过的反馈结果是 `PREVIEW_ONLY`，含义仍是“待独立硬件审查”，不是执行许可。第7章的模拟批准位不是身份认证。程序运行时按路径读取本仓库第5～7章 Python 源文件；测试还会启动子进程，因此不要把“无业务数据文件写入”误解为“完全不读本地文件”。

## 运行与验证

需要同一 Python 环境中安装 NumPy 和 OpenCV（提供 `cv2`），并保留本仓库的目录结构。在本目录执行：

```text
python run_visual_handoff.py
python -m unittest -v test_run_visual_handoff.py
```

预期第一条命令输出 9 条 JSONL；仅 `fresh_stable` 为 `PREVIEW_ONLY`。`wrong_run_probe`、`target_lost`、`stale_stable`、`jump` 均为 `BLOCKED`；其余预热/重新起算记录也被阻断。第二条命令的 6 项测试需全部通过。可把结果与[正文证据表](../../../book/第6篇_OpenCV/第8章_OpenCV综合验证_从合成画面到反馈审查证据包.md#操作与实验)核对。

本机测试环境为 Python 3.14.6、OpenCV 5.0.0、NumPy 2.4.6。UNO Q 镜像、相机、Bridge、MCU 和物理反馈尚未验证；Fig-42 仅有[Mermaid 源文件](../../../diagrams/uno-q-opencv-integrated-evidence.mmd)，未渲染 SVG。所有门限只适合这组确定性合成样例。
