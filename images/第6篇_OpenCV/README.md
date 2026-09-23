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
