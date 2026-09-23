# 第六篇第6章：跨帧目标关联与视觉事件

[返回正文](../../../book/第6篇_OpenCV/第6章_跨帧目标关联与视觉事件_从单帧候选到稳定状态.md) · [返回代码索引](../../README.md)

`temporal_events.py` 用标准库演示一条合成单候选流的来源/顺序/时隔/位移门与视觉事件。示例不导入 OpenCV，也不开相机、不读写图像或业务数据文件、不访问网络或控制硬件。它**不是**多目标跟踪器；`STABLE` 只表示规则满足，不证明对象身份。

输入为 `{"source","frame_id","timestamp_ms","candidate"}`。`candidate` 为 `None` 或包含 `centroid` 与 `area` 的字典，格式与[第六篇第5章像素候选](../../../book/第6篇_OpenCV/第5章_颜色分割与目标定位_从HSV掩膜到像素候选.md)衔接。真实集成必须在采集层另行提供可信来源、帧序号及采集时间，并检查绝对时效；不要把代码中的合成元数据当作 OpenCV 自动输出。

## 运行与验证

在本目录运行：

```text
python temporal_events.py
python -m unittest -v test_temporal_events.py
```

预期 8 条事件依次为 `TENTATIVE`、`TENTATIVE`、`STABLE`、`LOST`、`TENTATIVE`、`TENTATIVE`、`STABLE`、`REJECTED_JUMP`。测试共 7 项。`LOST`、`REJECTED_ORDER`、`REJECTED_GAP` 和 `REJECTED_JUMP` 的位置不可复用；非法输入抛 `ValueError` 并清除轨迹。门限 `3 次/10 像素/100 毫秒`仅用于确定性教学数据，不是 UNO Q 实机配置。

本次本机 Python 3.14.6 执行脚本与测试通过；目标板、真实摄像头、持续运行性能和 Bridge/MCU 联动均未验证。见[Fig-40 源文件](../../../diagrams/uno-q-opencv-temporal-gate.mmd)。
