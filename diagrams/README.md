# diagrams/：图示源文件

[返回项目根目录 README](../README.md)

## 目录职责

`diagrams/` 保存正文流程图、时序图、架构图等的 Mermaid `.mmd` 源文件，以及在需要时由源文件生成的 SVG 产物。源文件是图示可追溯性的依据。

## 使用约定

每张图只表达一个主要关系或流程，按 [写作规范](../docs/writing-guidelines.md) 编写 Mermaid，使用稳定图号，并在正文中说明图示用途、来源和许可状态。外部素材不得以无法核验来源的截图形式直接进入本目录。

## 新增图示

- [第六篇第1章 Fig-35：视觉处理管线与控制边界](uno-q-opencv-image-pipeline.mmd)：对应正文和图片资源登记见 [images/第6篇_OpenCV/README.md](../images/第6篇_OpenCV/README.md)。
- [第六篇第2章 Fig-36：摄像头采集与帧校验生命周期](uno-q-opencv-capture-validation.mmd)：对应正文和图片资源登记见 [images/第6篇_OpenCV/README.md](../images/第6篇_OpenCV/README.md)。
- [第六篇第3章 Fig-37：去噪到边缘候选的处理流程](uno-q-opencv-denoise-canny.mmd)：对应正文和图片资源登记见 [images/第6篇_OpenCV/README.md](../images/第6篇_OpenCV/README.md)。
- [第六篇第4章 Fig-38：二值区域到几何记录的验证流程](uno-q-opencv-contour-geometry.mmd)：对应正文和图片资源登记见 [images/第6篇_OpenCV/README.md](../images/第6篇_OpenCV/README.md)。
- [第六篇第5章 Fig-39：HSV 掩膜到像素候选的验证流程](uno-q-opencv-hsv-localization.mmd)：对应正文和图片资源登记见 [images/第6篇_OpenCV/README.md](../images/第6篇_OpenCV/README.md)。
- [第六篇第6章 Fig-40：单帧候选到视觉事件的时间门](uno-q-opencv-temporal-gate.mmd)：对应正文和图片资源登记见 [images/第6篇_OpenCV/README.md](../images/第6篇_OpenCV/README.md)。
- [第六篇第7章 Fig-41：视觉事件到离线反馈意图的审查门](uno-q-opencv-feedback-guard.mmd)：对应正文和图片资源登记见 [images/第6篇_OpenCV/README.md](../images/第6篇_OpenCV/README.md)。
- [第六篇第8章 Fig-42：从合成帧到离线审查记录](uno-q-opencv-integrated-evidence.mmd)：对应正文和图片资源登记见 [images/第6篇_OpenCV/README.md](../images/第6篇_OpenCV/README.md)。
- [第七篇第1章 Fig-43：教学推理契约与停止边界](uno-q-ai-inference-evidence-gate.mmd)：对应正文和图片资源登记见 [images/第7篇_AI/README.md](../images/第7篇_AI/README.md)。
