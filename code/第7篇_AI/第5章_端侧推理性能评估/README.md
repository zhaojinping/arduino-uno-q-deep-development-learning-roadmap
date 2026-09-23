# 第七篇第5章代码：端侧推理性能评估

## 内容

- `analyze_benchmark.py`：只读取一个符合教学 schema 的 JSON 记录，汇总预热后的推理时延和样本所记录的 RSS 观察值。
- `benchmark.json`：人工编写的合成数据；`platform_id`、模型标识和运行时均为教学占位值，不指向真实设备、模型或运行时。
- `test_analyze_benchmark.py`：验证样本契约、最近秩统计、预热隔离、报告状态和命令行错误处理。

## 运行

Python 3.10 或更新版本；仅使用标准库，不需要安装模型、运行时、NumPy、ONNX 或其他软件包。

```shell
python -B analyze_benchmark.py --input benchmark.json
python -B -m unittest -v test_analyze_benchmark.py
```

示例输入包含 3 条预热记录及 20 条正式合成记录。预期报告要点：

```text
status=REPORT_ONLY
warmup_count=3
measured_count=20
latency_ms.quantile_method=nearest_rank
latency_ms.p50_nearest_rank=14.5
latency_ms.p95_nearest_rank=19.0
latency_ms.max=23.0
memory_mib.observed_max_rss=507.4
thresholds_applied=false
```

最近秩分位数在升序样本 `x` 上按 `x[ceil(p × n) - 1]` 计算，报告中的 `p` 分别为 0.50 和 0.95。示例数值只用于复核公式；不是实测时延/内存、目标板参考值或通过门槛。观测 RSS 的最大值仅是输入样本中的最大记录，不保证捕获了进程实际峰值。

分析器不会自行计时、采集 RSS、执行模型、写回输入或访问设备。结构错误通过标准错误返回 `status=BLOCKED` 和退出码 1；结构有效的数据统一返回 `REPORT_ONLY` 和退出码 0。进程退出码 0 不等于目标性能达标。
