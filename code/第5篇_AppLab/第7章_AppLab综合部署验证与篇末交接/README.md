# 第五篇第7章：综合部署验证与篇末交接

[返回本章正文](../../../book/第5篇_AppLab/第7章_AppLab综合部署验证与篇末交接_从预检到交接.md)

本目录不提供自动部署脚本。第7章沿用第3～6章的离线示例，并提供两份 Markdown 交接材料：

- [handoff-template.md](handoff-template.md)：真实批次可复制的记录模板，初始状态均为 `NOT_RUN`；现场填写时应使用受限存储。
- [sample-handoff.md](sample-handoff.md)：仅利用第5章模拟 `run-043` 事件填写的**阻断**示例，不代表 Arduino UNO Q 实机运行或完成部署。

从仓库根目录可复跑第5章的模拟事件关联：

~~~text
python -B "code/第5篇_AppLab/第5章_AppLab运行证据包与日志关联/correlate_events.py" --metadata "code/第5篇_AppLab/第5章_AppLab运行证据包与日志关联/sample_run.json" --events "code/第5篇_AppLab/第5章_AppLab运行证据包与日志关联/sample_events.jsonl"
~~~

第4章 `run-042` 配置样例、第5章 `run-043` 日志样例和第6章 `run-044`/`run-045` 健康样例属于不同模拟运行，不得拼接为一次部署的通过证据。交接前审阅脱敏状态与接收范围；不要把真实凭据、个人信息或设备序列号提交至公开仓库。
