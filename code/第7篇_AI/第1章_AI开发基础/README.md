# 第七篇第1章：AI 开发基础

[返回正文](../../../book/第7篇_AI/第1章_AI开发基础_从任务定义到可验证推理.md) · [返回代码索引](../../README.md)

`teaching_inference.py` 是只依赖 Python 标准库的离线教学示例：六条合成特征记录经过来源、会话、特征版本、时间与数值检查，然后用**人工指定**的线性权重计算原始间隔分数 `margin = 2 × color_fraction + shape_score − 1.5`。`|margin| < 0.5` 时弃判；其余情况只输出 `REPORT_ONLY`，不触发任何硬件或网络动作。

这组权重没有经过训练，`margin` 不是准确率、概率或已校准置信度；`model_id` 只是本章公式的标签，不是经过签名的模型工件。`source`、`run_id`、`sample_id` 也仅是合成记录中的文本字段，不提供认证、抗重放或去重。`timestamp_ms` 与 `observed_at_ms` 属于同一人为设定的模拟时钟域；100 毫秒门限不能移植为 UNO Q 实测参数。

## 运行与验证

在本目录执行：

```text
python teaching_inference.py
python -m unittest -v test_teaching_inference.py
```

第一条命令应产生六条严格 JSON Lines 记录：两条 `REPORT_ONLY`、一条 `ABSTAIN`、三条 `REJECTED`。第二条命令验证前向计算、拒绝路径、无标签弃判、元数据回传和命令行确定性。脚本不读图像、模型文件或业务数据，不下载依赖、不访问摄像头、网络、App Lab、Bridge 或 MCU，也不写结果文件；运行时 Python 会读取本地源文件。

本章只完成本机离线逻辑验证，未在 Arduino UNO Q、App Lab、任何模型运行时或真实传感器上执行。图示源文件见[Fig-43 Mermaid](../../../diagrams/uno-q-ai-inference-evidence-gate.mmd)；SVG 尚未渲染审阅。
