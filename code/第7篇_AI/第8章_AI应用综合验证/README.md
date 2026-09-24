# 第七篇第8章：AI 应用综合验证

此目录提供一个纯 Python 标准库的离线证据清单检查器，将本篇前七章的主要验证门汇总为 `REPORT_ONLY` 报告。输入中的 `CLAIMED_PASS` 是提交者给出的声明，不代表检查器读取或独立核验了底层证据；无论所有声明如何填写，程序都不会授权部署。

## 文件

- `readiness_gate.py`：限制原始 JSON 输入大小、拒绝重复键并校验固定证据门集合，按规则汇总报告。
- `evidence_manifest.json`：合成案例；七项证据标为 `CLAIMED_PASS`，目标验收为 `NOT_RUN`。
- `test_readiness_gate.py`：14 项标准库测试，覆盖聚合决策、输入边界、拒绝路径和 CLI 输出。

## 运行

要求 Python 3.10 或更新版本；不需要第三方依赖。在本目录执行：

```shell
python -B readiness_gate.py
python -B -m unittest -v test_readiness_gate.py
```

示例应输出 `INCOMPLETE`，因为合成清单没有目标验收证据。即使将每个状态都改成 `CLAIMED_PASS`，结果最多是 `READY_FOR_HUMAN_REVIEW`，`deployment_authorized` 仍固定为 `false`。

## 边界

- 检查器只验证 JSON 解析、字段集合、状态标签和证据引用格式，不打开引用、不校验模型、数据集、日志或设备。
- 16 KiB 上限、UTF-8、重复键拒绝等仅约束此教学解析入口；不构成完整 API 安全、身份认证、密码学完整性或审计系统。
- 离线报告不连接模型服务、网络、Arduino UNO Q、App Lab、Bridge、MCU、GPIO 或执行器；不能用作部署批准或产品验收。
