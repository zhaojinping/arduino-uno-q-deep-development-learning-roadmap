# App Lab 模拟运行 run-043：阻断交接示例

> `SIMULATED`。此文件仅演示怎样诚实交接不完整证据；无 Arduino UNO Q、App Lab、Router/Bridge 或 MCU 实测。请勿复制为现场验收记录。

## 批次身份

| 字段 | 值 |
| --- | --- |
| `batch_id` | `demo-batch-043` |
| `run_id` | `run-043`（来自第五篇第5章固定样例） |
| 环境 | `staging`（模拟字段，不代表真实目标） |
| 配置指纹 | 样例 `sample_run.json` 中的 64 位零字符串；不是本地真实配置 |
| 目标设备、App 版本、镜像、App Lab/CLI 版本 | `UNKNOWN` / 未接入 |
| 操作者、现场授权、物理输出 | 无；仅纸面演练 |
| 时间 | 样例事件的 2026-09-23 UTC 时间；时钟真实性未验证 |

## 八个门的记录

| 门 | 状态 | 证据与解释 |
| --- | --- | --- |
| G0 范围与安全 | BLOCKED | 无目标设备、现场工作窗口、授权或回退负责人 |
| G1 项目契约 | NOT_RUN | 本 `run_id` 未绑定实际 App 源码或 `app.yaml` |
| G2 目标与配置 | UNKNOWN | 只有模拟元数据；无目标能力快照或 Secret 有效性证据 |
| G3 受控启动 | SIMULATED | `evt-001` 是样例 `launch.started`；无 App Lab Start-up 原文或真实 Run |
| G4 日志与健康 | BLOCKED | 模拟事件中 `evt-002` 为 `app.ready`，`evt-003` 为同一运行的 `camera.init.failed`；本地关联摘要为 `RUNTIME_ERROR`。`evt-004` 属旧运行，`evt-005` 无运行 ID，`evt-006` 指纹冲突，均不得补作本次健康证据 |
| G5 功能与结果 | NOT_RUN | 无请求、Bridge 回执、MCU 回读或物理结果 |
| G6 异常与恢复 | NOT_RUN | 没有目标可执行故障对账或回退 |
| G7 脱敏交接 | SIMULATED | 此 Markdown 示例只交接缺口；不构成现场签收或验收 |

## 本地分项材料

- [`sample_run.json`](../第5章_AppLab运行证据包与日志关联/sample_run.json) 与 [`sample_events.jsonl`](../第5章_AppLab运行证据包与日志关联/sample_events.jsonl) 是本示例唯一直接使用的模拟输入。
- 第四章的 `run-042` 配置快照不是 `run-043` 的配置证明；第六章 `run-044`/`run-045` 健康结果也不属于本批次。
- 事件中的 `raw_ref` 只是样例字符串；对应原始 `logs/` 文件并未在本目录提供，不能声称完成了真实原文追溯。

## 结论与下一步

本批次仅证明固定模拟事件可被本地脚本分类。**设备部署结论：BLOCKED / NOT_VERIFIED。** 下一步必须明确目标与授权、绑定 App 版本和配置，取得目标只读能力快照，建立真实新 `run_id`；在安全窗口内按正文 G0～G7 重新执行并由独立复核者审阅。不得通过重用本模拟批次消除这些缺口。
