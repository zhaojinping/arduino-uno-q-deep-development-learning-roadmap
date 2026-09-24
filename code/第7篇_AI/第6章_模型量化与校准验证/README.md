# 第七篇第6章代码：模型量化与校准验证

[返回代码索引](../../README.md)

## 文件

- `quantization_demo.py`：对一维合成数值向量进行对称 8 位有符号整数（int8）量化/反量化演示，比较校准范围、截断和重建误差。
- `test_quantization_demo.py`：9 项标准库行为测试，覆盖计算边界、输入拒绝和无阈值报告。

## 运行

Python 3.10 或更新版本；仅使用标准库，不加载模型、不安装推理运行时、不连接设备。

```shell
python -B quantization_demo.py
python -B -m unittest -v test_quantization_demo.py
```

固定合成案例包含 5 个评估标量。窄范围校准 `[−1,1]` 使用 scale `1/127`，发生 2 个截断值；把 `±8` 离群值纳入校准后 scale 增至 `8/127`，本例不再截断，但对 `0.1` 的重建误差变大。此结果只针对本例。

`payload_estimate` 只比较这 5 个数值元素的原始 float32/int8 字节数（20/5）；不包含零点/scale 元数据、模型图、文件结构、对齐或运行时工作区，因此不表示真实模型大小、RAM 节省或速度提升。

脚本始终输出 `REPORT_ONLY` 且 `thresholds_applied=false`。它既不模拟完整网络层/算子，也不生成 ONNX 模型或评估任务准确率；测试通过不能作为 Arduino UNO Q、镜像或执行提供程序兼容证明。
