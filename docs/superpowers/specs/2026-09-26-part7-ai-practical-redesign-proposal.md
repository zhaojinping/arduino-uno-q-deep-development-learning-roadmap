# 第七篇 AI 实战化改造方案（方案 B 已确认）

> 结构决策已确认：新增“板载 AI 实战”和“DeepSeek API”两章，原安全与综合验证章节顺延为第9、10章。正文迁移与全书编号变更仍须按实施计划执行；实体板实测留待用户接板后进行。

## 现状与问题

第七篇现有 8 章主要围绕合成数据、离线评估、模型工件、数值回归、性能统计、量化、工具安全模拟和综合证据门展开。它们建立了不错的验证意识，但读者尚未沿着 Arduino UNO Q 的 App Lab、AI Bricks 和真实推理入口做完一个板载 AI 应用，也没有从 UNO Q 的 Linux 侧调用公共 LLM API 的完整实例。因而“AI 是本板主打能力”在篇章中尚未得到足够具体的体现。

本方案先区分四类能力，避免把不同处理器和服务混为一谈：

| 能力 | 在 UNO Q 学习路线中的定位 | 需避免的误解 |
| --- | --- | --- |
| App Lab 预制 AI Brick | Linux 侧应用调用已封装的视觉、音频或其他推理服务 | Brick 可用不等于所有模型、输入设备和版本都已兼容 |
| 本地模型推理 | App Lab 本地 LLM Brick 或其他经核验的 Linux 运行时，在板上处理模型输入 | 不把“本地运行”自动等同于特定加速器或实时性能 |
| STM32U585 上的实时逻辑 | Sketch 读取传感器、维护确定性时序并实施独立安全约束 | 不把通用 Linux 模型或 LLM 直接移植到 MCU |
| 公共 LLM API | Linux Python 应用经网络调用云端模型，返回解释、摘要或建议 | 不称为板载推理；不向模型授予硬件权限 |

## 官方资料核验得到的边界

- Arduino UNO Q 由 QRB2210 Linux MPU 与 STM32U585 MCU 组成；App Lab 可在一个应用中编排 Python、Sketch、Bricks，并通过 Bridge 交换数据。
- Qualcomm 对 QRB2210 列出 Cortex-A53 CPU、Adreno 702 GPU、ISP 与 Hexagon DSP，并说明 AI 推理可用 CPU/GPU。没有找到把 UNO Q 明确规格为带独立 NPU 的官方依据，因此正文不得声称“UNO Q 的 NPU”或把 VENTUNO Q 的 NPU 能力套用到本板。
- Arduino 的公开示例包括 `object_detection` Brick（示例说明使用板载 CPU 推理）及 `arduino:llm` 本地模型 Brick。当前公开 Python 实现将本地 LLM 路由到 Genie 或 llama.cpp 模型运行器；具体模型、内存占用、加速路径和可用性必须在目标板及指定版本上核实。
- Arduino `CloudLLM` 当前实现允许 OpenAI 兼容模型前缀和自定义 `base_url`，适合作为 App Lab 中调用兼容 API 的候选入口；UNO Q 目标版本、DeepSeek 参数组合仍需实际验证。
- 截至 2026-09-26，DeepSeek 官方文档列出的 OpenAI 兼容基址为 `https://api.deepseek.com`，Chat Completions 路径为 `/chat/completions`，当前示例模型名为 `deepseek-flash`。正文应在编写/发布时再次检查模型名称、请求字段、限额和费用，不将易变值写成永久规格。

## 备选方案

### 方案 A：维持八章，只补强现有章节

增强第1章的平台能力分类、第5章板载实测方法、第7章 DeepSeek API 与工具安全、第8章端到端证据矩阵；保留章节编号和现有图号。

优点是目录与交叉引用改动较少。缺点是新增的板载 AI、云 API 和安全执行内容会挤进原有章节，实操链条不够完整，正文容易继续停留在概念加模拟层。

### 方案 B：增加两章实战，将原第7、8章顺延（推荐）

保留第1～6章的机器学习评估基础，新增两章，再将现有安全/综合验证章节顺延：

1. 第1章 AI 开发基础：从任务定义到可验证推理
2. 第2章 数据集与离线评估：从分组切分到混淆矩阵
3. 第3章 模型工件与部署契约：从清单到目标预检
4. 第4章 推理回归与数值一致性：从黄金样例到目标验收
5. 第5章 端侧推理性能评估：从测量方案到资源预算
6. 第6章 模型量化与校准验证：从校准数据到资源—精度权衡
7. **UNO Q 板载 AI 实战：App Lab AI Brick 与本地推理**（新增）
8. **UNO Q 接入 DeepSeek API：从云端 LLM 到可验证应用**（新增）
9. 生成式 AI 与工具调用安全边界：从模型建议到受控执行（现第7章顺延）
10. AI 应用综合验证：从端侧基线到云端闭环（现第8章顺延并扩展）

第7章以 `object_detection` 的图像推理作为首个板载实验；再介绍本地 `LargeLanguageModel` Brick 的模型选择和边界，但不预先保证某个具体模型能在用户板卡实时运行。第8章以 UNO Q Linux Python 应用调用 DeepSeek Chat Completions 为主线，涵盖 API key 的本机配置、请求/响应结构、对话上下文、超时与服务错误、资源/隐私限制、离线模拟测试，以及基于合成实验室读数生成“仅供复核”的中文解释。随后才进入工具调用授权与整篇验收。

本方案会调整第七篇既有第7/8章路径及篇末交叉引用。原第七篇第1～6章保留 Fig-43～Fig-48；两张新增流程图接续编号为 Fig-49、Fig-50；原安全与综合验证图顺延为 Fig-51、Fig-52。随后原第八篇 Fig-51～Fig-57 全部顺延为 Fig-53～Fig-59，第九篇第1章新图为 Fig-60。须同步正文锚点、`.mmd` 文件登记、图片登记、SUMMARY、根 README、参考资料、测试断言与所有引用。章节编号每篇重置的既定规则不变。

### 方案 C：新内容放入附录或扩展篇

保留第七篇现状，在附录中写板载 AI 与 DeepSeek 实例。

优点是几乎不扰动现目录。缺点是旗舰能力落在主学习路线之外，读者可能把新内容当成可选旁支，且与第九篇项目的知识衔接较弱。

## 推荐设计与具体实验

推荐方案 B。实验路径分两阶段：

1. **无需实机的离线准备**：用合成图像/合成环境数据、固定响应夹具和 mock HTTP 测试验证输入构造、JSON 解析、错误分类、敏感字段脱敏与工具授权边界；任何模型结果均明确标记为 `SYNTHETIC` 或 `MOCK`。
2. **连接用户 UNO Q 后的目标验证**：确认板卡 RAM SKU、系统/App Lab/Brick 版本和模型列表；运行官方 object-detection 示例并记录模型/输入/线程/CPU/RSS/预热/时延，随后选定兼容的本地模型做有限试验；在不暴露 API key 的前提下，从板载 Python 应用发起一次 DeepSeek 请求并记录服务响应元数据、耗时和错误状态。是否扩展到真实相机、Bridge 传感器或其他外设，另行确认。

DeepSeek 实验首选 `CloudLLM` 的 OpenAI 兼容配置；同时说明 REST 请求的语义以便读者理解协议，而不是把 Brick 的 API 包装误认为模型运行在板上。主示例数据为合成实验室读数，例如 `temperature_c`、`humidity_pct`、`sample_age_s`，生成解释而不触发执行器；后续如接入 MCU 的真实读数，必须沿用来源、时间、单位和有效性校验，且在示例中明确数据会离开设备并发往公共 API。

API key 不写入源代码、Git 历史、截图、测试 fixture 或正文。书中只展示从用户在板端/App Lab 本机配置的 secret/environment variable 中读取的变量名；不要求用户把密钥发给助手。网络未知或超时的写操作不得自动重放；本章纯文本只读问答即使可以重试，也要设定超时、调用频率/费用上限与明确错误结果。

## 验收要求

- 第七篇目录清晰区分“本地模型/推理”和“公共云 API”；端侧章节不得把云返回称为板载推理。
- 本地 AI 章节至少有一个对照官方 UNO Q AI Brick 的具体 App Lab 示例，写出输入、Brick 导入/API、结果、失败路径和实机验证表；本地 LLM 运行器作为经核验的可选能力，注明板卡 SKU 与实际模型兼容需现场确认。
- DeepSeek 章节至少有一段可读的 Python 调用实例和可离线单测的隔离 client；字段和模型名有核验日期，密钥不进入版本库；mock 测试不得伪装成真实 API 调用。
- 端侧输出或云端建议均为报告/复核；模型不得直接决定 GPIO/Bridge/执行器动作。若展示 tools/function calling，动作只能经独立白名单、参数/身份检查及明确批准，再由 MCU 重复施加硬约束。
- 整篇证据门分别登记主机单测、UNO Q App Lab 运行、板载模型/视觉推理、真实 API 调用、真实相机或传感器、Bridge/MCU 与安全动作验证；未做的项明确为 `NOT_RUN`。
- 章节号、图号、Mermaid 正文/源文件、图片登记、来源索引、导航和内部链接全部保持一致。既有第七篇旧第7/8章的代码与测试移动后仍由准确路径执行。

## 实机验证需求

写作与 mock 测试不需要立即连接板卡。但要把“AI Brick 在用户这块 UNO Q 上成功运行”“本地模型的延迟/内存”“板上 HTTPS/TLS 到 DeepSeek 成功”写成已验证事实，**需要用户把实体板接入电脑后再验证**。在该阶段仅运行低风险、可观察的 App Lab 示例和一次只读 API 请求；安装模型、更新系统/App Lab、刷写 MCU、访问外设或执行其他会改动设备状态的步骤，先核对范围并逐项说明。用户自行在板端配置 API key，不通过聊天发送。

## 参考资料（写作前重新打开并登记）

- Arduino UNO Q 用户手册与官方数据表：双处理器、App Lab、Bricks 与安装/运行流程。
- Qualcomm QRB2210 官方产品资料：CPU/GPU/DSP/ISP 与公开 AI 推理描述；不得超出资料宣称独立 NPU。
- Arduino `app-bricks-examples` 中 UNO Q 的 object-detection、本地 LLM 与 App Lab 示例。
- Arduino `app-bricks-py` 中 `LargeLanguageModel` 与 `CloudLLM` 当前实现，以及 Arduino App specification 的 variables/secret 规则。
- DeepSeek 官方 Chat Completions、Quick Start、Multi-round、Tool Calls 与 Models 文档；在章节更新时重新确认模型名及接口。
