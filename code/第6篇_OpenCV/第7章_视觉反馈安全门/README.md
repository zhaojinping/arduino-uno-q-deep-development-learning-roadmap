# 第六篇第7章：视觉反馈安全门

[返回正文](../../../book/第6篇_OpenCV/第7章_视觉事件与硬件反馈_从稳定候选到受控动作.md) · [返回代码索引](../../README.md)

`review_feedback.py` 是纯 Python 标准库的离线教学示例。它把合成帧、第6章格式的时间门事件和抽象指示意图一起审查，输出 `PREVIEW_ONLY` 或 `BLOCKED`。它不导入 OpenCV 或 Arduino Bridge，不接相机、不写引脚、不访问网络；`PREVIEW_ONLY` 不是硬件动作许可。

默认策略固定来源和运行会话，要求帧年龄不超过 100 毫秒、质心处于 `(0,0,160,128)` 像素 ROI、`kind="indicator"` 且 `level≤20`，并需要 `simulated_approval is True`。这些值只供合成实验复算，不是 UNO Q 上的安全参数。`simulated_approval` 不提供身份认证。

## 运行与验证

在本目录执行：

```text
python review_feedback.py
python -m unittest -v test_review_feedback.py
```

预期三个案例分别输出 `PREVIEW_ONLY`、`BLOCKED/stale_or_future_frame` 和 `BLOCKED/approval_missing`；10 项测试覆盖错源、错会话、错帧、过期、越界、幅度和批准条件。当前只在本机 Python 3.14.6 验证，未连接 UNO Q、Bridge、MCU 或实际指示设备。见[Fig-41 源文件](../../../diagrams/uno-q-opencv-feedback-guard.mmd)与[参考资料索引](../../../resources/references.md)。
