# 第七篇第2章：数据集与离线评估

本目录只演示**人工合成数据**上的类别中心拟合、分组隔离、验证集选弃判门限和测试集计数。它不读取相机或真实业务数据，不下载或保存模型工件，不访问网络、App Lab、Bridge、MCU 或执行器；输出固定为 `REPORT_ONLY`，不得用于硬件动作授权。

## 文件与输入契约

- [`synthetic_samples.csv`](synthetic_samples.csv)：20 条手工填写的样本；字段恰为 `sample_id,group_id,split,label,color_fraction,shape_score`。
- [`dataset_evaluation.py`](dataset_evaluation.py)：审查 CSV、只从 `train` 估计两类中心、只用 `validation` 选择 `0.00/0.12/0.36` 中的教学门限，然后在 `test` 输出四格计数、弃判与条件指标。
- [`test_dataset_evaluation.py`](test_dataset_evaluation.py)：17 项标准库测试，包含跨分区组泄漏、畸形数据、训练/测试隔离、零分母和命令行复现性。

每条记录的两个特征必须是有限的 0～1 数值，标签只能是 `candidate_like` 或 `other`。同一 `group_id` 不得出现在多个分区，各分区需含两类。`group_id` 和 `sample_id` 是教学字符串，不是来源认证、内容去重或签名。脚本没有训练/部署真实模型，输出中的 `model_kind` 也不是可验证模型工件。

## 运行

在本目录使用 Python 3 执行：

```text
python dataset_evaluation.py
python -m unittest -v test_dataset_evaluation.py
```

预期 `centroids` 为 `candidate_like=[0.8,0.8]`、`other=[0.2,0.2]`；选择门限 `0.36`；测试集 `TP=2、FP=1、TN=2、FN=1`，正/负类各弃判 1 条，覆盖率 `6/8`。本次本机 Python 3.14.6 实测与[第七篇第2章正文](../../../book/第7篇_AI/第2章_数据集与离线评估_从分组切分到混淆矩阵.md)的手算一致。该结果只证明离线教学脚本可复现，不证明真实准确率或目标板性能。

如 CSV 被修改而审查失败，应复核字段、唯一 ID、组隔离、标签与数值范围。若验证集没有 `FP=0` 的候选，脚本停止；不能回头利用测试集找门限并称其为独立测试。脚本只读 CSV、标准输出 JSON，不更改系统和硬件，不需要回滚；异常时不继续后续部署。
