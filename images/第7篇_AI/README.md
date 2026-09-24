# 第七篇图示资源登记

本篇图示先保存可追溯的 Mermaid 源文件。尚未渲染并审阅的图，不提供空 SVG 链接，也不标为出版完成。

<a id="fig-43-uno-q-ai-inference-evidence-gate"></a>

## 图 7-1：教学推理契约与停止边界

- 图号：Fig-43
- 状态：正文 Mermaid 与独立源文件已建立；SVG 待生成并完成预览审阅。
- 图源：[教学推理证据门 Mermaid](../../diagrams/uno-q-ai-inference-evidence-gate.mmd)
- 正文位置：[第七篇第1章 Fig-43](../../book/第7篇_AI/第1章_AI开发基础_从任务定义到可验证推理.md#fig-43-uno-q-ai-inference-evidence-gate)
- 内容要求：区分输入契约拒绝、前向计算后的弃判和仅供复核报告，并显式停止于硬件/网络执行层之前。
- 来源边界：依据已登记的 Arduino UNO Q 产品资料、Arduino App 规范和本章原创教学代码绘制；不是官方模型架构、加速器拓扑或安全认证流程。
- 验证边界：本次未渲染 SVG；手设权重与合成特征不构成真实模型、App Lab、UNO Q 或物理动作验收。

<a id="fig-44-uno-q-ai-dataset-evaluation-gate"></a>

## 图 7-2：离线评估中的数据隔离与报告边界

- 图号：Fig-44
- 状态：正文 Mermaid 与独立源文件已建立；SVG 待生成并完成预览审阅。
- 图源：[离线评估证据门 Mermaid](../../diagrams/uno-q-ai-dataset-evaluation-gate.mmd)
- 正文位置：[第七篇第2章 Fig-44](../../book/第7篇_AI/第2章_数据集与离线评估_从分组切分到混淆矩阵.md#fig-44-uno-q-ai-dataset-evaluation-gate)
- 内容要求：显示字段/分组审查、训练集拟合、验证集选门限、测试集只计数与两个停止路径。
- 来源边界：依据本章登记的机器学习官方资料及本书原创教学代码绘制；不是 Arduino 官方训练、部署或安全流程。
- 验证边界：本次未渲染 SVG；合成数据的分类计数不是现场精度、App Lab 或 UNO Q 实机验收。

<a id="fig-45-uno-q-ai-model-deployment-contract"></a>

## 图 7-3：模型工件到目标部署的证据门

- 图号：Fig-45
- 状态：正文 Mermaid 与独立源文件已建立；SVG 待生成并完成预览审阅。
- 图源：[模型部署契约 Mermaid](../../diagrams/uno-q-ai-model-deployment-contract.mmd)
- 正文位置：[第七篇第3章 Fig-45](../../book/第7篇_AI/第3章_模型工件与部署契约_从清单到目标预检.md#fig-45-uno-q-ai-model-deployment-contract)
- 内容要求：区分清单/单文件摘要检查与目标运行时、目标板实测及独立发布验收；显示不能部署的阻断路径。
- 来源边界：依据已登记的 Arduino UNO Q/App 规范、ONNX IR/运行时兼容资料和本书原创预检器；不是官方部署、安全认证或自动发布流程。
- 验证边界：本次尚未渲染 SVG；教学文本不是模型，不证明格式、运行时、目标板或部署性能兼容。

<a id="fig-46-uno-q-ai-inference-regression"></a>

## 图 7-4：固定样例推理回归与目标验收边界

- 图号：Fig-46
- 状态：正文 Mermaid 与独立源文件已建立；SVG 待生成并完成预览审阅。
- 图源：[推理回归 Mermaid](../../diagrams/uno-q-ai-inference-regression.mmd)
- 正文位置：[第七篇第4章 Fig-46](../../book/第7篇_AI/第4章_推理回归与数值一致性_从黄金样例到目标验收.md#fig-46-uno-q-ai-inference-regression)
- 内容要求：配对固定参考与候选输出，显示结构阻断、逐值容差、类别/弃判变化，并明确离线结果不等于目标部署验收。
- 来源边界：依据已登记的 ONNX Runtime 官方输出比较/量化资料和本书原创比较器；不是官方阈值、量化验收标准或 UNO Q 部署流程。
- 验证边界：合成记录与本机测试不包含真实模型、标注质量、目标运行时或 UNO Q 实机；SVG 尚未渲染审阅。

<a id="fig-47-uno-q-ai-inference-performance"></a>

## 图 7-5：端侧推理性能记录与离线报告边界

- 图号：Fig-47
- 状态：正文 Mermaid 与独立源文件已建立；SVG 待生成并完成预览审阅。
- 图源：[端侧推理性能评估 Mermaid](../../diagrams/uno-q-ai-inference-performance.mmd)
- 正文位置：[第七篇第5章 Fig-47](../../book/第7篇_AI/第5章_端侧推理性能评估_从测量方案到资源预算.md#fig-47-uno-q-ai-inference-performance)
- 内容要求：明确工作负载/计时边界、环境快照、冷启动独立、预热与正式样本隔离、输入阻断、描述性时延/RSS统计及目标验收仍需另证。
- 来源边界：图示为本书原创测量流程；参考 ONNX Runtime 性能维度和 profiling 文档、Python 计时 API；不是官方 benchmark、UNO Q 性能规范或兼容性声明。
- 验证边界：配套数据为人工合成；本次没有模型、运行时、RSS 工具、UNO Q 板卡或硬件资源测量；SVG 尚未渲染和目视审阅。

<a id="fig-48-uno-q-ai-quantization-calibration"></a>

## 图 7-6：量化校准、候选评估与目标证据门

- 图号：Fig-48
- 状态：正文 Mermaid 与独立源文件已建立；SVG 待生成并完成预览审阅。
- 图源：[量化校准 Mermaid](../../diagrams/uno-q-ai-quantization-calibration.mmd)
- 正文位置：[第七篇第6章 Fig-48](../../book/第7篇_AI/第6章_模型量化与校准验证_从校准数据到资源精度权衡.md#fig-48-uno-q-ai-quantization-calibration)
- 内容要求：分离校准/评估数据，比较浮点基线与量化候选，先审任务质量，再同边界测量资源，并把目标镜像/运行时/算子证据设为独立门槛。
- 来源边界：参考 ONNX Runtime 官方量化文档并采用本书原创的标量教学模拟；不是 ONNX Runtime、Arduino 或 UNO Q 官方量化、性能或发布规范。
- 验证边界：仅有合成数值案例和本机标准库测试；没有模型转换、任务质量评估、真实模型文件/内存对比、目标运行时或 UNO Q 实机验证；SVG 尚未渲染和目视审阅。
