# 第六篇第4章代码：轮廓提取与几何测量

## 代码清单

- [`measure_contours.py`](measure_contours.py)：合成两个实心矩形与一个小噪点，校验 0/255 掩膜，提取外轮廓并输出像素几何量。
- [`test_measure_contours.py`](test_measure_contours.py)：4 项离线测试，覆盖已知矩形几何值、噪点剔除、非法输入、空前景与命令行稳定性。

## 运行方式

需 Python 3、OpenCV Python bindings（`cv2`）和 NumPy。进入本目录执行：

```text
python measure_contours.py
python -m unittest -v test_measure_contours.py
```

`--min-area` 接受正的有限数值；默认 `100` 只是合成样例门限。程序不读取或写入图像文件，不访问摄像头、网络、GPIO、MCU 或 Arduino UNO Q。`contourArea` 是边界点几何面积，不是前景像素个数；输出也不能换算成毫米。

本次本机环境：Python 3.14.6、OpenCV 5.0.0、NumPy 2.4.6；4 项测试通过。目标板依赖和实机性能尚未验证。正文：[第4章 轮廓提取与几何测量](../../../book/第6篇_OpenCV/第4章_轮廓提取与几何测量_从二值区域到形状结果.md)。
