# 第六篇图示资源登记

本篇图示按章节登记 Mermaid 源文件、正文位置和验证边界。尚未生成 SVG 的图示保留可追溯的 .mmd 源文件，不使用空图片链接或未经审阅的渲染产物。

<a id="fig-35-uno-q-opencv-image-pipeline"></a>

## 图 6-1：视觉处理管线与控制边界

- 图号：Fig-35
- 状态：Mermaid 正文与独立源文件已建立；SVG 待生成并完成预览审阅。
- 图源：[视觉处理管线 Mermaid](../../diagrams/uno-q-opencv-image-pipeline.mmd)
- 正文位置：[第六篇第1章 Fig-35](../../book/第6篇_OpenCV/第1章_OpenCV开发基础_图像像素与视觉处理流水线.md#fig-35-uno-q-opencv-image-pipeline)
- 内容要求：展示图像来源、采集适配、帧有效性、OpenCV 预处理、结果记录或反馈，以及 MCU 侧安全门和无效帧停止路径。
- 来源边界：依据已登记的 Arduino UNO Q 产品资料、UNO Media Carrier 资料和 OpenCV 图像操作教程原创绘制；不是摄像头驱动拓扑、官方通信协议或接线图。
- 验证边界：本次未渲染 SVG，未接入摄像头、载板、MCU 或 UNO Q 实机；图示不证明任何具体相机组合、软件包或实时性能可用。

<a id="fig-36-uno-q-opencv-capture-validation"></a>

## 图 6-2：摄像头采集与帧校验生命周期

- 图号：Fig-36
- 状态：Mermaid 正文与独立源文件已建立；SVG 待生成并完成预览审阅。
- 图源：[摄像头采集校验 Mermaid](../../diagrams/uno-q-opencv-capture-validation.mmd)
- 正文位置：[第六篇第2章 Fig-36](../../book/第6篇_OpenCV/第2章_摄像头接入与视频帧采集_从设备确认到帧校验.md#fig-36-uno-q-opencv-capture-validation)
- 内容要求：展示硬件与软件兼容组合确认、显式来源选择、打开状态、有限取帧、帧校验、失败停止和资源释放；不表达具体设备树或接线定义。
- 来源边界：依据 Arduino UNO Q、UNO Media Carrier 与 OpenCV 官方资料原创绘制；不是官方驱动拓扑或协议图。
- 验证边界：本次未渲染 SVG，未连接摄像头、载板或 UNO Q 实机；流程不证明特定相机组合受支持或实时性能达标。

<a id="fig-37-uno-q-opencv-denoise-canny"></a>

## 图 6-3：去噪到边缘候选的处理流程

- 图号：Fig-37
- 状态：Mermaid 正文与独立源文件已建立；SVG 待生成并完成预览审阅。
- 图源：[去噪与 Canny Mermaid](../../diagrams/uno-q-opencv-denoise-canny.mmd)
- 正文位置：[第六篇第3章 Fig-37](../../book/第6篇_OpenCV/第3章_图像预处理与边缘提取_从去噪到结构特征.md#fig-37-uno-q-opencv-denoise-canny)
- 内容要求：展示输入图像校验、按噪声类型选择高斯或中值滤波、Canny 双阈值和输出契约检查；不表达识别结果或硬件控制协议。
- 来源边界：依据 OpenCV 官方平滑和 Canny 文档原创绘制，不复制官方图表。
- 验证边界：正文与 Mermaid 源码对应；本次未渲染 SVG，且实验不访问摄像头或 UNO Q 实机。

<a id="fig-38-uno-q-opencv-contour-geometry"></a>

## 图 6-4：二值区域到几何记录的验证流程

- 图号：Fig-38
- 状态：Mermaid 正文与独立源文件已建立；SVG 待生成并完成预览审阅。
- 图源：[外轮廓几何 Mermaid](../../diagrams/uno-q-opencv-contour-geometry.mmd)
- 正文位置：[第六篇第4章 Fig-38](../../book/第6篇_OpenCV/第4章_轮廓提取与几何测量_从二值区域到形状结果.md#fig-38-uno-q-opencv-contour-geometry)
- 内容要求：展示二值掩膜输入契约、外轮廓提取、面积与零矩过滤、像素几何测量、下游安全门和失败停止路径。
- 来源边界：依据登记的 OpenCV 官方轮廓教程原创绘制，不复制官方图表，不表示 UNO Q 官方视觉协议。
- 验证边界：本次未渲染 SVG；离线合成掩膜不构成真实摄像头、物理尺寸或硬件动作验证。

<a id="fig-39-uno-q-opencv-hsv-localization"></a>

## 图 6-5：HSV 掩膜到像素候选的验证流程

- 图号：Fig-39
- 状态：Mermaid 正文与独立源文件已建立；SVG 待生成并完成预览审阅。
- 图源：[HSV 颜色定位 Mermaid](../../diagrams/uno-q-opencv-hsv-localization.mmd)
- 正文位置：[第六篇第5章 Fig-39](../../book/第6篇_OpenCV/第5章_颜色分割与目标定位_从HSV掩膜到像素候选.md#fig-39-uno-q-opencv-hsv-localization)
- 内容要求：展示 BGR 输入校验、HSV 颜色分割、开运算、面积门限与最大候选、无候选停止路径。
- 来源边界：依据登记的 OpenCV 官方颜色空间、形态学和轮廓教程原创绘制；不是官方视觉控制协议。
- 验证边界：本次未渲染 SVG；合成图上的像素候选不构成相机实机、对象身份或硬件动作验证。

<a id="fig-40-uno-q-opencv-temporal-gate"></a>

## 图 6-6：单帧候选到视觉事件的时间门

- 图号：Fig-40
- 状态：Mermaid 正文与独立源文件已建立；SVG 待生成并完成预览审阅。
- 图源：[跨帧时间门 Mermaid](../../diagrams/uno-q-opencv-temporal-gate.mmd)
- 正文位置：[第六篇第6章 Fig-40](../../book/第6篇_OpenCV/第6章_跨帧目标关联与视觉事件_从单帧候选到稳定状态.md#fig-40-uno-q-opencv-temporal-gate)
- 内容要求：展示来源与帧元数据校验、连续命中、稳定/继续事件，以及无候选、顺序、时隔和像素跳变拒绝路径。
- 来源边界：依据登记的 OpenCV 视频读取与光流教程，结合本书原创时间门规则绘制；不是 OpenCV 内置跟踪器、官方视觉协议或对象身份保证。
- 验证边界：本次未渲染 SVG；合成帧序列不构成真实采集时间、目标身份、UNO Q 相机或硬件动作验证。
