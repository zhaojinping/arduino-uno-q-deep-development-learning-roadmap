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
