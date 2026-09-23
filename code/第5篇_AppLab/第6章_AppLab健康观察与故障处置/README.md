# 第五篇第6章：App Lab 健康观察与故障处置

[返回本章正文](../../../book/第5篇_AppLab/第6章_AppLab健康观察与故障处置_从信号到安全恢复.md)

本目录只包含**离线教学模型**和两份固定模拟快照。`evaluate_health.py` 根据运行身份、信号时间和必需/可选检查给出建议标签；它不是 App Lab 探针，不连接设备，也不自动重启或操作输出。

从仓库根目录运行：

~~~text
python -B "code/第5篇_AppLab/第6章_AppLab健康观察与故障处置/evaluate_health.py" --snapshot "code/第5篇_AppLab/第6章_AppLab健康观察与故障处置/sample_stale.json"
python -B "code/第5篇_AppLab/第6章_AppLab健康观察与故障处置/evaluate_health.py" --snapshot "code/第5篇_AppLab/第6章_AppLab健康观察与故障处置/sample_fault.json"
~~~

- `sample_stale.json`：必需 MCU 信号过期，预期 `UNKNOWN`。
- `sample_fault.json`：必需 Python 信号在本次运行内失败，预期 `FAULT_OBSERVED`。

输入中的 `evidence_ref` 是模拟标签，不能回指设备原始日志。脚本只读，不写文件、不访问网络或硬件；结果不构成 UNO Q 实机、App Lab、Router/Bridge、MCU 或安全验收证据。现场使用前必须替换为可追溯采集流程并另行验证时间与风险策略。
