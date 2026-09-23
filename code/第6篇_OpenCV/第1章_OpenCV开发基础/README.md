# 第六篇第1章代码：图像、像素与视觉处理流水线

## 代码清单

- [`image_basics.py`](image_basics.py)：在内存中创建 4×6 BGR 合成图像，查看形状和像素，转换灰度并执行阈值化。

## 运行边界

运行环境需安装可用的 OpenCV Python bindings（导入名 `cv2`）和 NumPy。请按当前 Python 环境和目标系统的包管理方式核对兼容版本；本目录不宣称 UNO Q 镜像已预装这些依赖，也不建议未经验证直接改动开发板系统包。

从本目录执行：

```text
python image_basics.py
```

预期示例输出：

```text
shape=(4, 6, 3) dtype=uint8
pixel_bgr[1, 2]=(0, 0, 255)
gray[1, 2]=76 threshold_nonzero=6
```

本程序不访问摄像头、文件、网络、GPIO 或 MCU；上述输出是按代码逻辑推导的预期输出。本次未运行程序，未执行自动化测试或 UNO Q 实机验证。

章节正文：[OpenCV 开发基础：图像、像素与视觉处理流水线](../../../book/第6篇_OpenCV/第1章_OpenCV开发基础_图像像素与视觉处理流水线.md)
