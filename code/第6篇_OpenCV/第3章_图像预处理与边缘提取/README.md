# 第六篇第3章代码：图像预处理与边缘提取

## 代码清单

- [`preprocess_edges.py`](preprocess_edges.py)：生成固定尺寸、固定随机种子的灰度几何图，分别叠加高斯噪声和椒盐噪声，比较高斯/中值滤波及 Canny 输出。
- [`test_preprocess_edges.py`](test_preprocess_edges.py)：3 项命令行行为测试，覆盖两类噪声误差下降、输出边缘图契约、固定种子复现和非法阈值拒绝。

## 运行方式

依赖 OpenCV Python bindings（导入名 `cv2`）与 NumPy。进入本目录执行：

```text
python preprocess_edges.py
python -m unittest -v test_preprocess_edges.py
```

可通过 `--seed`、`--low-threshold` 和 `--high-threshold` 调整噪声样本与 Canny 参数。高阈值必须严格大于低阈值。

程序不读取或写入图像文件，不访问摄像头、网络、GPIO、MCU 或 UNO Q。示例只验证本机软件环境中的确定性数组操作；目标设备版本、实时性能和真实图像效果仍待在具体环境实测。

本次实测环境：Python 3.14.6、OpenCV 5.0.0、NumPy 2.4.6；3 项测试通过。正文：[第3章 图像预处理与边缘提取](../../../book/第6篇_OpenCV/第3章_图像预处理与边缘提取_从去噪到结构特征.md)
