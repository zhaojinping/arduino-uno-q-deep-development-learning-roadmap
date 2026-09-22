# 第四篇 Python Bridge 第 1 章设计说明

> 状态：已获用户确认，待执行计划复核
>
> 日期：2026-09-22

## 1. 目标

启动第四篇“Python Bridge”，新增篇内第 1 章，建立 Linux Python 应用、Router、Bridge/RPC、MCU Sketch 和业务状态之间的消息模型与调用边界。章节从第三篇的 Linux 运行治理交接进入第四篇的 Bridge 业务编程，不沿用第三篇章节编号。

本次交付指第四篇第 1 章正文初稿完成，不指真实 UNO Q、Bridge、Router 或 MCU 联调已经完成。

## 2. 范围

### 2.1 包含内容

1. 新增第四篇第 1 章，front matter 使用 part: 4、chapter: 1、status: draft。
2. 解释 Python、Linux App、Router、Bridge/RPC、MCU Sketch 的职责和逻辑连接边界。
3. 定义请求、响应、通知、错误、超时、幂等、UNKNOWN 和结果关联。
4. 新增 Fig-24 Mermaid 消息生命周期图和图示登记。
5. 提供两个只使用 Python 标准库的本地概念实验：
   - 请求信封和响应分类；
   - 超时、重试和 UNKNOWN 决策。
6. 更新第四篇 README、SUMMARY.md、根 README 和第四篇图示索引。
7. 在已有官方来源基础上引用 Arduino UNO Q User Manual、Arduino App specification、Arduino Router 和 Python 标准库文档。

### 2.2 不包含内容

- 不新增第四篇第 2 章及以后章节。
- 不修改第三篇既有章节。
- 不调用真实 ADB、SSH、Router、Bridge、网络或 MCU。
- 不把本地 Python 输出写成真实 RPC 响应。
- 不保存真实凭据、设备序列号、IP 地址或生产配置。
- 不安装第三方 Python 依赖。
- 不提升章节状态为 review 或 published。

## 3. 第 1 章结构

拟定文件名：

book/第4篇_PythonBridge/第1章_Python_Bridge开发基础_消息模型与调用边界.md

章节标题：

第1章 Python Bridge 开发基础：消息模型与调用边界

章节结构：

1. 学习目标
2. 背景与边界
3. 双侧应用的职责模型
4. Fig-24：Python Bridge 消息生命周期
5. 消息信封：请求、响应、通知和错误
6. 调用边界：call、notify、provide 与安全执行
7. 超时、幂等与 UNKNOWN
8. 第一个 Python 实验：请求信封与响应分类
9. 第二个 Python 实验：超时与重试决策
10. Bridge 调用运行手册
11. 故障处理矩阵
12. Python Bridge 验证矩阵
13. 与第三篇、第五篇和第九篇的交接
14. 本章验证结果
15. 常见问题
16. 本章小结
17. 延伸阅读与交叉引用

## 4. 图示设计

新建：

diagrams/uno-q-python-bridge-message-lifecycle.mmd

图示使用 sequenceDiagram，覆盖：

- Python App 创建带 request_id 的请求；
- Router/Bridge 传递消息；
- MCU Sketch 接收并执行或拒绝；
- 响应沿原关联返回；
- 超时、拒绝和 UNKNOWN 分支；
- 结果进入证据记录。

图号使用全书唯一编号 Fig-24。图示只表达逻辑消息生命周期，不表示物理连线、线程调度细节或实机结果。保留 Mermaid 源文件和正文占位；mmdc 不存在时不生成伪造 SVG。

## 5. 两个概念实验

### 5.1 请求信封与响应分类

实现纯函数：

- build_request(request_id, method, args, deadline_ms)
- classify_response(response, expected_request_id)
- redact_request(request)

实验覆盖请求 ID 缺失、方法名为空、响应关联错误、APPLIED、REJECTED 和 UNKNOWN；输出脱敏 JSON，不访问外部系统。

### 5.2 超时与重试决策

实现纯函数：

- decide_retry(state, idempotent, attempts, max_attempts)
- summarize_unknown(request_id, reason, last_observation)

实验覆盖明确失败、幂等超时、非幂等超时、达到最大次数和人工裁决；明确禁止对 UNKNOWN 自动重复控制。

## 6. 导航与验证

需要更新：

- book/第4篇_PythonBridge/README.md
- SUMMARY.md
- README.md
- 新建 images/第4篇_PythonBridge/README.md

验证包括 front matter、篇内第 1 章编号、内部链接、Fig-24 唯一性、Mermaid 源文一致性、两个 Python 示例编译/执行、代码说明字段、UTF-8 和 Git 空白检查。

当前证据等级最多达到仓库静态检查和本地概念实验；真实 Bridge/Router/MCU 验证继续列为未完成项。
