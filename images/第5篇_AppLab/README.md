# 第五篇图示资源登记

本篇图示按章节登记源文件、SVG 产物、正文锚点、渲染版本和验证边界。当前 Fig-28 已完成 SVG 渲染与独立预览；图示是本书原创教学设计，不是 Arduino 官方协议或硬件连线图。

<a id="fig-28-uno-q-app-lab-app-structure-boundary"></a>

## 图 5-1：App Lab 项目结构与设备入口

- 图号：Fig-28
- 状态：SVG 已生成并完成预览审阅，Mermaid 源文件与正文逐字一致
- 图源：[App Lab 项目结构 Mermaid](../../diagrams/uno-q-app-lab-app-structure-boundary.mmd)
- 产物：[App Lab 项目结构 SVG](ch01-fig28-uno-q-app-lab-app-structure-boundary.svg)
- 正文位置：[第五篇第1章 Fig-28](../../book/第5篇_AppLab/第1章_App_Lab开发基础_应用结构与验证边界.md#fig-28-uno-q-app-lab-app-structure-boundary)
- 内容要求：展示 `app.yaml`、`python/main.py`、可选 `sketch/`、`data/`、`.cache/` 与 App Lab、Linux、MCU、Bridge、证据分层的逻辑关系
- 生成记录：`2026-09-23`，缓存 Mermaid CLI `11.12.0`，本地 Chrome 无界面渲染，白色背景；未安装包或修改全局配置
- 预览记录：`2026-09-23`，独立打开生成的 SVG 并截图检查；中文标签可读、箭头完整、结构边界清楚、无裁切文字；`viewBox` 越界检查为空
- 来源边界：依据已登记的 Arduino App specification、UNO Q User Manual 和产品页原创绘制；不复制官方图表或内部连线
- 验证边界：图示只证明 Mermaid 可解析和视觉布局可读，不证明 App Lab、Router/Bridge、MCU、目标 Linux 镜像或 UNO Q 实机验收

<a id="fig-29-uno-q-app-lab-run-lifecycle"></a>

## 图 5-2：App Lab 运行生命周期与证据窗口

- 图号：Fig-29
- 状态：SVG 已生成并完成独立预览审阅，Mermaid 源文件与正文逐字一致
- 图源：[App Lab 运行生命周期 Mermaid](../../diagrams/uno-q-app-lab-run-lifecycle.mmd)
- 产物：[App Lab 运行生命周期 SVG](ch02-fig29-uno-q-app-lab-run-lifecycle.svg)
- 正文位置：[第五篇第2章 Fig-29](../../book/第5篇_AppLab/第2章_AppLab运行生命周期_导入启动运行与停止.md#fig-29-uno-q-app-lab-run-lifecycle)
- 内容要求：展示导入、准备、启动、运行、停止请求、停止、失败、未知，以及按 `run_id` 过滤到证据窗口的关系
- 生成记录：`2026-09-23`，缓存 Mermaid CLI `11.12.0`，本地 Chrome 无界面渲染，白色背景；未安装包或修改全局配置
- 预览记录：`2026-09-23`，独立打开生成的 SVG 并截图检查；中文标签可读、箭头完整、状态分支清楚、无裁切文字；`viewBox` 为 `0 0 1451.078125 427`
- 来源边界：依据已登记的 Arduino App specification、App CLI user documentation、App Lab examples 和 UNO Q 数据表原创绘制；不复制官方图表或 UI 截图
- 验证边界：图示只证明 Mermaid 可解析和视觉布局可读，不证明 App Lab、Router/Bridge、MCU、目标 Linux 镜像或 UNO Q 实机验收

<a id="fig-30-uno-q-app-lab-deployability-boundary"></a>

## 图 5-3：App Lab 启动配置、Brick 依赖与可部署性边界

- 图号：Fig-30
- 状态：SVG 待生成并完成独立预览审阅，Mermaid 源文件与正文需逐字一致
- 图源：[App Lab 可部署性边界 Mermaid](../../diagrams/uno-q-app-lab-deployability-boundary.mmd)
- 产物：[App Lab 可部署性边界 SVG](ch03-fig30-uno-q-app-lab-deployability-boundary.svg)
- 正文位置：[第五篇第3章 Fig-30](../../book/第5篇_AppLab/第3章_AppLab启动配置与Brick依赖_从声明到可部署性检查.md#fig-30-uno-q-app-lab-deployability-boundary)
- 内容要求：展示 App 根目录和 `app.yaml` 的声明检查、Brick/模型/设备/端口能力快照、`READY`/`MISSING_*`/`CONFLICTING_PORT`/`UNKNOWN` 分支，以及目标预检和 `data/`、`.cache/`、Secret 边界
- 来源边界：依据已登记的 Arduino App specification、App CLI user documentation 和 UNO Q 数据表原创绘制；不复制官方图表、部署协议或 UI 截图
- 验证边界：图示只证明 Mermaid 可解析和视觉布局可读，不证明 Brick 已安装、模型可加载、端口空闲、App Lab 部署或 UNO Q 实机验收

<a id="fig-31-uno-q-app-lab-config-layering"></a>

## 图 5-4：App Lab 配置分层与运行快照

- 图号：Fig-31
- 状态：SVG 待生成并完成独立预览审阅，Mermaid 源文件与正文需逐字一致
- 图源：[App Lab 配置分层 Mermaid](../../diagrams/uno-q-app-lab-config-layering.mmd)
- 产物：[App Lab 配置分层 SVG](ch04-fig31-uno-q-app-lab-config-layering.svg)
- 正文位置：[第五篇第4章 Fig-31](../../book/第5篇_AppLab/第4章_AppLab配置分层与多环境运行参数_从开发机到现场板.md#fig-31-uno-q-app-lab-config-layering)
- 内容要求：展示 App 声明、基础层、环境层、运行层、类型校验、锁定键、Secret 注入、脱敏快照、`run_id`、生命周期和结果账本边界
- 来源边界：依据已登记的 Arduino App specification、App CLI user documentation 和 UNO Q 数据表原创绘制；配置分层是本书工程治理模型，不是官方 UI 或部署拓扑
- 验证边界：图示只证明 Mermaid 可解析和视觉布局可读，不证明 App Lab 内置配置覆盖、Secret 可用、目标环境一致或 UNO Q 实机运行
