# 第五篇第5章：App Lab 运行证据包与日志关联

[返回项目根目录 README](../../../README.md)

本目录保存一个不连接设备的 JSONL 事件关联示例及固定模拟输入：

- `correlate_events.py`：校验事件字段，并按 `run_id`、配置指纹分类关联、陈旧、未关联和冲突事件。
- `sample_run.json`、`sample_events.jsonl`：固定演示数据，不来自 UNO Q 或 App Lab 实机。

从仓库根目录运行：

~~~text
python -B "code/第5篇_AppLab/第5章_AppLab运行证据包与日志关联/correlate_events.py" --metadata "code/第5篇_AppLab/第5章_AppLab运行证据包与日志关联/sample_run.json" --events "code/第5篇_AppLab/第5章_AppLab运行证据包与日志关联/sample_events.jsonl"
~~~

脚本只接受已规范化的 JSON Lines，不会采集、解析或清洗 Console 原始日志。示例不写文件、不读取 Secret、不调用 App Lab/App CLI、不连接 Router/Bridge/MCU，也不构成 UNO Q 实机验证。
