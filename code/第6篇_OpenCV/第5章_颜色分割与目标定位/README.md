# 第六篇第5章代码：颜色分割与目标定位

## 代码清单

- [`locate_color.py`](locate_color.py)：生成受控 BGR 彩色图，执行 HSV 范围分割、3×3 开运算和外轮廓筛选；只输出单帧像素候选或 `NO_CANDIDATE`。
- [`test_locate_color.py`](test_locate_color.py)：4 项离线测试，覆盖颜色区分、噪点清理、无候选、输入拒绝与 CLI 行为。

## 运行方式

需要 Python 3、OpenCV Python bindings（`cv2`）和 NumPy。进入本目录执行：

```text
python locate_color.py
python locate_color.py --min-area 100000
python -m unittest -v test_locate_color.py
```

`--min-area` 只接受正的有限值；默认 `100` 是合成场景的教学参数，不是生产阈值。HSV 范围固定为绿色样例 `(35,80,80)～(85,255,255)`；如需跨 0 的红色范围，必须另行实现双掩膜和测试。

程序不读取或写入图像文件，不访问摄像头、网络、GPIO、MCU 或 Arduino UNO Q；它既不作语义身份识别，也不输出物理尺寸或控制命令。本次本机环境：Python 3.14.6、OpenCV 5.0.0、NumPy 2.4.6；4 项测试通过。正文：[第5章 颜色分割与目标定位](../../../book/第6篇_OpenCV/第5章_颜色分割与目标定位_从HSV掩膜到像素候选.md)。
