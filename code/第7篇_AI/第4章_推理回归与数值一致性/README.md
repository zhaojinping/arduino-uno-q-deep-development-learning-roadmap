# 第七篇第4章代码：推理回归与数值一致性

[返回代码索引](../../../README.md)

## 文件

- `compare_inference.py`：配对离线参考分数与候选分数，按绝对/相对容差逐值比较，并记录类别变化和最小间隔弃判变化。
- `comparison.json`：4 条合成输出记录，故意包含顺序变化、门限跨越和 top-1 翻转。
- `test_compare_inference.py`：17 项标准库行为测试。

## 运行

```shell
python compare_inference.py --input comparison.json
python -m unittest -v test_compare_inference.py
```

样例应报告 `REVIEW_REQUIRED`：所有数值差异均在本例容差内，但有一条记录发生 top-1 翻转，另一条跨过最小间隔弃判门。脚本退出码 `0` 只表示报告成功生成；必须读取 JSON 的 `decision` 字段。

输入必须以 `sample_id` 一对一配对，且配对记录声明相同的 `preprocess_id`、标签及标签顺序。该标识只说明双方声明相同，不证明实际张量字节或预处理实现相同。工具只处理有限数值分数，不读取模型、图像、标签真值，也不执行推理。

输出 `MATCH_WITHIN_TOLERANCE` 仅代表本地样例分数在所声明规则下对齐，不能证明参考输出正确、候选模型质量可接受、目标运行时兼容或 UNO Q 部署获准。容差和最小间隔应从独立验证数据和风险要求制定；不要用测试集反复调参。
