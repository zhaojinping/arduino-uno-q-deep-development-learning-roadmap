# 第八篇第1章：IoT 开发基础

本目录包含一条离线、合成数据教学示例：

- `telemetry_sample.json`：人工编写的单条遥测载荷，不来自传感器。
- `validate_telemetry.py`：受限 JSON 结构与字段契约检查器；不连接 MQTT、HTTP、网络、UNO Q 或硬件。
- `test_validate_telemetry.py`：标准库 `unittest` 行为测试。

在本目录运行：

```shell
python -B validate_telemetry.py
python -B -m unittest -v test_validate_telemetry.py
```

报告范围固定为 `OFFLINE_SCHEMA_ONLY`。`VALID` 仅表示样例符合本章定义的教学结构，不证明设备身份、时间准确、单位真实、校准有效、数据未被篡改、消息已送达或业务处理已完成。
