# Arduino UNO Q 深度开发学习路线

## 项目定位

本项目是一套面向实践的 Arduino UNO Q 深度开发学习路线，按由浅入深的方式组织硬件认知、软件环境、编程实践、系统联调与项目复盘。仓库同时保存正文入口、示例代码、图示源文件和经过登记的参考资料。

## 适用读者

适合已经接触过 Arduino 或基础嵌入式开发，希望理解 UNO Q 的软硬件协同方式、能够独立复现实验并逐步完成综合项目的学习者。阅读者应具备基本的命令行、Git 和编程概念；每章会明确补充所需前置知识。

## 阅读入口

- [阅读总览（SUMMARY.md）](SUMMARY.md)
- [第一篇：认识 UNO Q（第1篇_认识UNOQ README）](book/第1篇_认识UNOQ/README.md)
- [第二篇：STM32（第2篇_STM32 README）](book/第2篇_STM32/README.md)
- [设计说明](docs/superpowers/specs/2026-09-15-arduino-uno-q-book-design.md)
- [参考资料索引](resources/references.md)
- [写作规范](docs/writing-guidelines.md)

`SUMMARY.md` 是全书阅读顺序的唯一入口；后续章节按篇内编号追加，并同步正文、代码、图示和来源索引。

## 全书路线

1. 建立 UNO Q 的硬件、系统和开发模型认知。
2. 完成开发环境准备，理解示例的运行、验证和故障定位方式。
3. 通过逐步加深的实验掌握 Arduino、Linux 侧能力及两者协同。
4. 进入外设、通信、数据处理和综合项目开发。
5. 以可复现、可验证、可维护为标准完成项目复盘与能力迁移。

## 当前进度

当前状态：**第一篇第 1～5 章已完成，第二篇第 1～9 章已建立为初稿，第三篇第 1～8 章已建立为初稿，第四篇第 1～4 章已建立为初稿，第五篇第 1～7 章已建立为初稿，第六篇第 1～8 章已建立为初稿，第七篇第 1～2 章已建立为初稿**，全书当前共 43 章。第五篇的正文范围已由第 7 章“综合验证：从部署预检到运行复盘”收束，仍保持 `draft`；第 7 章提供 G0～G7 证据门、交接模板和模拟阻断示例，不代表完成现场部署。本环境仍未完成 Arduino CLI 编译、上传、Linux 实机盘点、网络查询、服务观测、资源压力演练、队列压力演练、性能压测、故障注入、安装或启用 systemd unit、Bridge 重启、配置/凭据替换、ADB/SSH/App Lab 入口验证、Router/Bridge 重连、远程写操作、Bridge 联调和硬件实机验证。章节编号按篇重置，每一篇从第 1 章重新开始。

第三篇第 1～8 章的正文范围已建立，但各章仍保持 draft；“正文范围完成”不等于 UNO Q 实机、systemd、Bridge、MCU 联调或现场部署验证完成。

第四篇第 1 章已建立为初稿，围绕 Python App、Router、Bridge/RPC、MCU Sketch 的消息模型、调用边界、超时、幂等和 UNKNOWN 处理展开；本章的标准库概念实验只验证本地逻辑，未完成 Router/Bridge、App Lab、MCU 或 UNO Q 实机联调。

第四篇第 2 章已建立为初稿，围绕有界队列、worker、并发上限、背压、任务取消、超时、对账和 UNKNOWN 冻结展开；两个 asyncio 示例只验证本地调度逻辑，不构成 UNO Q 并发性能或硬件证据。

第四篇第 3 章已建立为初稿，围绕连接复用、连接代次、重连退避、已发送/可能已发送请求的恢复、幂等键和可判定结果展开；连接管理与恢复策略示例只验证本地逻辑，不构成 Router/Bridge、App Lab、MCU 或 UNO Q 实机联调证据。

第四篇第 4 章[结果账本与状态查询：从返回值到可验证证据](book/第4篇_PythonBridge/第4章_Python_Bridge结果账本与状态查询_从返回值到可验证证据.md)已建立为 `draft` 初稿；第四篇目前共 4 章。第 4 章提供 SQLite 结果账本、追加式事件、UNKNOWN 查询收敛、两个本地模拟示例、22 项契约测试和章节检查器；Fig-27 展示查询判定与结果收敛边界。本地持久化和查询模型不构成设备执行或硬件验收证据。

第五篇第 1 章[App Lab 开发基础：应用结构、设备入口与验证边界](book/第5篇_AppLab/第1章_App_Lab开发基础_应用结构与验证边界.md)已建立为 `draft` 初稿；第五篇目前共 7 章。第 1 章提供 App 目录契约、启动证据分类、两个本地 Python 实验和 Fig-28；本地结构检查不构成 App Lab、Router/Bridge、MCU 或 UNO Q 实机验收证据。

第五篇第 2 章[App Lab 运行生命周期：导入、启动、运行与停止](book/第5篇_AppLab/第2章_AppLab运行生命周期_导入启动运行与停止.md)已建立为 `draft` 初稿。第 2 章提供生命周期状态机、`run_id` 会话证据分类、两个本地 Python 实验和 Fig-29；本地状态迁移与日志过滤不构成 App Lab、Router/Bridge、MCU 或 UNO Q 实机验收证据。

第五篇第 3 章[App Lab 启动配置与 Brick 依赖：从声明到可部署性检查](book/第5篇_AppLab/第3章_AppLab启动配置与Brick依赖_从声明到可部署性检查.md)已建立为 `draft` 初稿。第 3 章提供声明契约、能力快照解析、两个本地 Python 实验和 Fig-30；`VALID`/`READY` 只代表本地模型结果，不构成 App Lab、Router/Bridge、MCU 或 UNO Q 实机部署证据。

第五篇第 4 章[App Lab 配置分层与多环境运行参数：从开发机到现场板](book/第5篇_AppLab/第4章_AppLab配置分层与多环境运行参数_从开发机到现场板.md)已建立为 `draft` 初稿。第 4 章提供配置覆盖、来源保留、身份锁定、Secret 脱敏快照、两个本地 Python 实验和 Fig-31；配置治理模型不构成 App Lab 内置功能或 UNO Q 实机部署证据。

第五篇第 5 章[App Lab 运行证据包与日志关联：从 run_id 到可检索证据](book/第5篇_AppLab/第5章_AppLab运行证据包与日志关联_从run_id到可检索证据.md)已建立为 `draft` 初稿。第 5 章提供规范化 JSONL 事件关联脚本、陈旧/未关联/配置指纹冲突分类、证据包结构建议和 Fig-32 Mermaid；固定数据为模拟样例，本次未运行脚本、自动测试、App Lab 或 UNO Q 实机验证。

第五篇第 6 章[App Lab 健康观察与故障处置：从信号到安全恢复](book/第5篇_AppLab/第6章_AppLab健康观察与故障处置_从信号到安全恢复.md)已建立为 `draft` 初稿。第 6 章提供信号分层、身份/新鲜度判定、故障与未知处置、人工恢复门、两份离线模拟快照及 Fig-33 Mermaid；本地模型不构成 App Lab 或 UNO Q 实机验收。

第五篇第 7 章[App Lab 综合验证：从部署预检到运行复盘](book/第5篇_AppLab/第7章_AppLab综合验证_从部署预检到运行复盘.md)已建立为 `draft` 初稿。第 7 章串联八个证据门，提供离线分项演练、可复制的复盘/交接模板、故意阻断的模拟记录和 Fig-34 Mermaid；正文范围至此收束，未进行 App Lab 或 UNO Q 实机部署/验收，暂不预设第 8 章。

第六篇第 1 章[OpenCV 开发基础：图像、像素与视觉处理流水线](book/第6篇_OpenCV/第1章_OpenCV开发基础_图像像素与视觉处理流水线.md)已建立为初稿；本章讲解图像数组、行列坐标、BGR/灰度、ROI、阈值处理和采集至反馈的阶段边界，附离线合成图像示例与 Fig-35 Mermaid。示例输出为按代码推导的预期值，本次未运行程序、未渲染 SVG、未验证摄像头或 UNO Q 实机。

第六篇第 2 章[摄像头接入与视频帧采集：从设备确认到帧校验](book/第6篇_OpenCV/第2章_摄像头接入与视频帧采集_从设备确认到帧校验.md)已建立为初稿；提供相机/载板/镜像/后端兼容核对、显式来源的有限帧诊断脚本及 Fig-36 Mermaid。脚本本次未运行，图示未渲染 SVG，未验证任何摄像头、载板或 UNO Q 实机组合。

第六篇第 3 章[图像预处理与边缘提取：从去噪到结构特征](book/第6篇_OpenCV/第3章_图像预处理与边缘提取_从去噪到结构特征.md)已建立为初稿；提供高斯/中值滤波、Canny 边缘候选的离线合成示例、3 项命令行测试和 Fig-37 Mermaid。测试在本机 Python 3.14.6、OpenCV 5.0.0、NumPy 2.4.6 环境通过；未验证目标 UNO Q 软件栈、摄像头或实机性能，图示未渲染 SVG。

第六篇第 4 章[轮廓提取与几何测量：从二值区域到可核验的形状结果](book/第6篇_OpenCV/第4章_轮廓提取与几何测量_从二值区域到形状结果.md)已建立为 `draft` 初稿；区分边缘候选、二值区域和轮廓面积，提供合成掩膜上的外轮廓测量、4 项离线测试及 Fig-38 Mermaid。测试在本机 Python 3.14.6、OpenCV 5.0.0、NumPy 2.4.6 环境通过；未验证真实摄像头、物理标定或 UNO Q 实机，图示未渲染 SVG。

第六篇第 5 章[颜色分割与目标定位：从 HSV 掩膜到可核验的像素候选](book/第6篇_OpenCV/第5章_颜色分割与目标定位_从HSV掩膜到像素候选.md)已建立为 `draft` 初稿；提供 BGR→HSV、颜色掩膜、开运算、单帧最大候选与无候选停止路径，配套 4 项离线测试和 Fig-39 Mermaid。测试在本机 Python 3.14.6、OpenCV 5.0.0、NumPy 2.4.6 环境通过；尚未验证真实摄像头、对象身份、色彩标定或 UNO Q 实机，图示未渲染 SVG。

第六篇第 6 章[跨帧目标关联与视觉事件：从单帧候选到稳定状态](book/第6篇_OpenCV/第6章_跨帧目标关联与视觉事件_从单帧候选到稳定状态.md)已建立为 `draft` 初稿；以合成序列解释来源、帧号、时间与位移门，提供目标丢失、跳变和异常序列的停止路径、7 项标准库测试及 Fig-40 Mermaid。本机 Python 3.14.6 测试通过；不等于对象身份、相机实机或硬件反馈验证，图示未渲染 SVG。

第六篇第 7 章[视觉事件与硬件反馈：从稳定候选到受控动作](book/第6篇_OpenCV/第7章_视觉事件与硬件反馈_从稳定候选到受控动作.md)已建立为 `draft` 初稿；提出来源/会话、错帧、绝对时效、像素区域、反馈幅度及模拟批准的离线审查门，配套 10 项标准库测试和 Fig-41 Mermaid。程序只输出待复核意图或阻断理由，不调用 Bridge/MCU；尚未完成真实身份认证、相机实机、执行器或物理反馈验收，图示未渲染 SVG。

第六篇第 8 章[OpenCV 综合验证：从合成画面到反馈审查证据包](book/第6篇_OpenCV/第8章_OpenCV综合验证_从合成画面到反馈审查证据包.md)已建立为 `draft` 初稿；复用第 5～7 章代码串联合成画面、时间门与反馈审查，提供九条 JSONL 记录、六项集成测试、交接模板及 Fig-42 Mermaid。第六篇正文范围至此收束，但仅完成本机离线验证；未完成相机、Bridge/MCU 或物理反馈验收，图示未渲染 SVG。

第七篇第 1 章[AI 开发基础：从任务定义到可验证推理](book/第7篇_AI/第1章_AI开发基础_从任务定义到可验证推理.md)已建立为 `draft` 初稿；区分规则、模型推理、TinyML、边缘与生成式 AI 的任务和部署边界，提供手设权重的合成特征实验、九项标准库测试及 Fig-43 Mermaid。示例不是训练或部署真实模型；未验证 UNO Q 实机、模型精度、App Lab、Bridge/MCU 或硬件动作，图示未渲染 SVG。

第七篇第 2 章[数据集与离线评估：从分组切分到混淆矩阵](book/第7篇_AI/第2章_数据集与离线评估_从分组切分到混淆矩阵.md)已建立为 `draft` 初稿；以 20 条人工合成 CSV 演示组隔离、类别中心拟合、验证集弃判门限、测试集混淆矩阵与指标分母，配套 17 项标准库测试及 Fig-44 Mermaid。结果不是现场识别准确率、可部署模型或 UNO Q 实机性能，图示未渲染 SVG。

## 目录结构

```text
book/       正文、章节目录和阅读入口
code/       可复现实验、Arduino 草图及配套脚本
diagrams/   Mermaid 源文件及可追溯的图示产物
images/     正文使用的图片及其说明
resources/  参考资料索引与资源登记
docs/       项目设计说明和写作规范
```

各目录的边界和使用方式见对应的 `README.md`；目录入口不会替代章节级的实验说明和验证记录。

## 来源与版权边界

本项目会为外部文档、代码、图片、规格说明和其他材料登记来源、用途及许可信息。当前版本**尚未授予外部材料再分发许可**：在许可状态完成核验并记录前，不复制或打包分发受限材料；引用时保留原作者、来源和必要的版权声明。Arduino、UNO Q 及其他名称仍归其各自权利人所有，本项目不主张相关商标权利。

## 贡献与更新方式

新增或修改章节时，先按照[写作规范](docs/writing-guidelines.md)补齐元数据、代码说明、图示占位和交叉引用，再同步更新 `SUMMARY.md` 及相关资源记录。新增外部来源必须先登记到[参考资料索引](resources/references.md)，并在提交说明中写清验证日期、许可边界和复现结果。变更保持小步、可复现，并在合并前运行本任务或对应章节规定的检查。

## 当前验证记录

最后验证日期：`2026-09-23`。当前已创建并核验的文件/目录如下：

```text
README.md
SUMMARY.md
docs/writing-guidelines.md
resources/references.md
book/第1篇_认识UNOQ/README.md
book/第1篇_认识UNOQ/第1章_Arduino的发展.md
book/第1篇_认识UNOQ/第2章_什么是Arduino_UNO_Q.md
book/第1篇_认识UNOQ/第3章_UNO_Q的硬件架构.md
book/第1篇_认识UNOQ/第4章_UNO_Q的软件架构.md
book/第1篇_认识UNOQ/第5章_第一个实验_Blink验证闭环.md
book/第2篇_STM32/README.md
book/第2篇_STM32/第1章_STM32侧开发基础_GPIO与实时边界.md
book/第2篇_STM32/第2章_PWM与定时输出_从占空比到安全控制.md
book/第2篇_STM32/第3章_ADC与模拟采样_从电压读数到可验证数据.md
book/第2篇_STM32/第4章_串口通信_从帧格式到MCU_Linux边界.md
book/第2篇_STM32/第5章_SPI通信_从片选时序到设备驱动边界.md
book/第2篇_STM32/第6章_I2C通信_从设备地址到总线恢复.md
book/第2篇_STM32/第7章_实时任务与调度_从周期循环到可验证响应.md
book/第2篇_STM32/第8章_硬件验证与故障定位_从接线检查到证据闭环.md
book/第2篇_STM32/第9章_综合实验_传感控制与MCU_Linux协同闭环.md
book/第3篇_Linux/README.md
book/第3篇_Linux/第1章_Linux侧开发基础_文件系统进程与MCU边界.md
book/第3篇_Linux/第2章_Linux设备网络与服务_从可见到可用.md
book/第3篇_Linux/第3章_Linux可观测性与资源管理_日志时间与安全回滚.md
book/第3篇_Linux/第4章_Linux远程运维与Python_Bridge_从安全命令到可验证请求.md
book/第3篇_Linux/第5章_Linux现场自动化与Python_Bridge_队列重连与状态缓存.md
book/第3篇_Linux/第6章_Linux与Python_Bridge现场测试与性能治理_从基准压测到故障注入.md
book/第3篇_Linux/第7章_Linux与Python_Bridge现场部署与服务化治理_从systemd配置分层到安全回滚.md
book/第3篇_Linux/第8章_Linux与Python_Bridge综合运行手册_从预检到交接.md
book/第4篇_PythonBridge/README.md
book/第4篇_PythonBridge/第1章_Python_Bridge开发基础_消息模型与调用边界.md
book/第4篇_PythonBridge/第2章_Python_Bridge并发与任务生命周期_从单次调用到有界协同.md
book/第4篇_PythonBridge/第3章_Python_Bridge连接复用与请求恢复_从断线到可判定结果.md
code/第4篇_PythonBridge/第3章_连接复用与请求恢复/README.md
code/第4篇_PythonBridge/第3章_连接复用与请求恢复/connection_owner.py
code/第4篇_PythonBridge/第3章_连接复用与请求恢复/recovery_policy.py
code/第4篇_PythonBridge/第3章_连接复用与请求恢复/test_recovery.py
code/第4篇_PythonBridge/第3章_连接复用与请求恢复/check_chapter.py
diagrams/uno-q-python-bridge-connection-recovery.mmd
images/第4篇_PythonBridge/ch03-fig26-uno-q-python-bridge-connection-recovery.svg
book/第4篇_PythonBridge/第4章_Python_Bridge结果账本与状态查询_从返回值到可验证证据.md
code/第4篇_PythonBridge/第4章_结果账本与状态查询/README.md
code/第4篇_PythonBridge/第4章_结果账本与状态查询/ledger.py
code/第4篇_PythonBridge/第4章_结果账本与状态查询/reconcile_status.py
code/第4篇_PythonBridge/第4章_结果账本与状态查询/test_ledger.py
code/第4篇_PythonBridge/第4章_结果账本与状态查询/check_chapter.py
diagrams/uno-q-python-bridge-result-ledger.mmd
images/第4篇_PythonBridge/ch04-fig27-uno-q-python-bridge-result-ledger.svg
book/第5篇_AppLab/README.md
book/第5篇_AppLab/第1章_App_Lab开发基础_应用结构与验证边界.md
code/第5篇_AppLab/第1章_App_Lab开发基础/README.md
code/第5篇_AppLab/第1章_App_Lab开发基础/app_contract.py
code/第5篇_AppLab/第1章_App_Lab开发基础/launch_evidence.py
code/第5篇_AppLab/第1章_App_Lab开发基础/test_app_contract.py
code/第5篇_AppLab/第1章_App_Lab开发基础/test_launch_evidence.py
code/第5篇_AppLab/第1章_App_Lab开发基础/check_chapter.py
diagrams/uno-q-app-lab-app-structure-boundary.mmd
images/第5篇_AppLab/README.md
images/第5篇_AppLab/ch01-fig28-uno-q-app-lab-app-structure-boundary.svg
book/第5篇_AppLab/第2章_AppLab运行生命周期_导入启动运行与停止.md
code/第5篇_AppLab/第2章_AppLab运行生命周期/README.md
code/第5篇_AppLab/第2章_AppLab运行生命周期/lifecycle.py
code/第5篇_AppLab/第2章_AppLab运行生命周期/session_evidence.py
code/第5篇_AppLab/第2章_AppLab运行生命周期/test_lifecycle.py
code/第5篇_AppLab/第2章_AppLab运行生命周期/test_session_evidence.py
code/第5篇_AppLab/第2章_AppLab运行生命周期/check_chapter.py
diagrams/uno-q-app-lab-run-lifecycle.mmd
images/第5篇_AppLab/ch02-fig29-uno-q-app-lab-run-lifecycle.svg
book/第5篇_AppLab/第3章_AppLab启动配置与Brick依赖_从声明到可部署性检查.md
code/第5篇_AppLab/第3章_AppLab启动配置与Brick依赖/README.md
code/第5篇_AppLab/第3章_AppLab启动配置与Brick依赖/deployment_contract.py
code/第5篇_AppLab/第3章_AppLab启动配置与Brick依赖/dependency_resolution.py
code/第5篇_AppLab/第3章_AppLab启动配置与Brick依赖/test_deployment_contract.py
code/第5篇_AppLab/第3章_AppLab启动配置与Brick依赖/test_dependency_resolution.py
code/第5篇_AppLab/第3章_AppLab启动配置与Brick依赖/check_chapter.py
diagrams/uno-q-app-lab-deployability-boundary.mmd
images/第5篇_AppLab/ch03-fig30-uno-q-app-lab-deployability-boundary.svg
book/第5篇_AppLab/第4章_AppLab配置分层与多环境运行参数_从开发机到现场板.md
book/第5篇_AppLab/第5章_AppLab运行证据包与日志关联_从run_id到可检索证据.md
book/第5篇_AppLab/第6章_AppLab健康观察与故障处置_从信号到安全恢复.md
book/第5篇_AppLab/第7章_AppLab综合验证_从部署预检到运行复盘.md
code/第5篇_AppLab/第5章_AppLab运行证据包与日志关联/README.md
code/第5篇_AppLab/第5章_AppLab运行证据包与日志关联/correlate_events.py
code/第5篇_AppLab/第5章_AppLab运行证据包与日志关联/sample_run.json
code/第5篇_AppLab/第5章_AppLab运行证据包与日志关联/sample_events.jsonl
diagrams/uno-q-app-lab-evidence-package.mmd
code/第5篇_AppLab/第6章_AppLab健康观察与故障处置/README.md
code/第5篇_AppLab/第6章_AppLab健康观察与故障处置/evaluate_health.py
code/第5篇_AppLab/第6章_AppLab健康观察与故障处置/sample_stale.json
code/第5篇_AppLab/第6章_AppLab健康观察与故障处置/sample_fault.json
diagrams/uno-q-app-lab-health-and-recovery.mmd
code/第5篇_AppLab/第7章_AppLab综合验证_从部署预检到运行复盘/README.md
code/第5篇_AppLab/第7章_AppLab综合验证_从部署预检到运行复盘/handoff-template.md
code/第5篇_AppLab/第7章_AppLab综合验证_从部署预检到运行复盘/sample-handoff.md
diagrams/uno-q-app-lab-deployment-handoff.mmd
code/第5篇_AppLab/第4章_AppLab配置分层与多环境运行参数/README.md
code/第5篇_AppLab/第4章_AppLab配置分层与多环境运行参数/config_layers.py
code/第5篇_AppLab/第4章_AppLab配置分层与多环境运行参数/run_config_snapshot.py
code/第5篇_AppLab/第4章_AppLab配置分层与多环境运行参数/test_config_layers.py
code/第5篇_AppLab/第4章_AppLab配置分层与多环境运行参数/test_run_config_snapshot.py
code/第5篇_AppLab/第4章_AppLab配置分层与多环境运行参数/check_chapter.py
diagrams/uno-q-app-lab-config-layering.mmd
images/第5篇_AppLab/ch04-fig31-uno-q-app-lab-config-layering.svg
code/第1章_Arduino的发展/README.md
code/第1章_Arduino的发展/Blink/Blink.ino
code/第1章_Arduino的发展/Blink/README.md
diagrams/arduino-evolution.mmd
diagrams/uno-q-dual-brain.mmd
diagrams/uno-q-execution-boundary.mmd
diagrams/uno-q-hardware-map.mmd
diagrams/uno-q-software-architecture.mmd
diagrams/uno-q-first-experiment-validation.mmd
diagrams/uno-q-stm32-gpio-boundary.mmd
diagrams/uno-q-stm32-pwm-duty-cycle-boundary.mmd
diagrams/uno-q-stm32-adc-measurement-boundary.mmd
diagrams/uno-q-stm32-uart-boundary.mmd
diagrams/uno-q-stm32-spi-boundary.mmd
diagrams/uno-q-stm32-i2c-recovery-boundary.mmd
diagrams/uno-q-stm32-realtime-scheduling-boundary.mmd
diagrams/uno-q-stm32-hardware-verification-boundary.mmd
diagrams/uno-q-stm32-integrated-control-boundary.mmd
diagrams/uno-q-linux-execution-boundary.mmd
diagrams/uno-q-linux-device-network-service-boundary.mmd
diagrams/uno-q-linux-observability-resource-rollback-boundary.mmd
diagrams/uno-q-linux-remote-bridge-request-sequence.mmd
diagrams/uno-q-linux-job-queue-reconnect-state-cache.mmd
diagrams/uno-q-linux-test-performance-fault-injection.mmd
diagrams/uno-q-linux-bridge-deployment-rollback.mmd
diagrams/uno-q-linux-operational-handoff.mmd
diagrams/uno-q-python-bridge-message-lifecycle.mmd
diagrams/uno-q-python-bridge-task-lifecycle.mmd
images/第1篇_认识UNOQ/README.md
images/第2篇_STM32/README.md
images/第3篇_Linux/README.md
images/第4篇_PythonBridge/README.md
book/第6篇_OpenCV/README.md
book/第6篇_OpenCV/第1章_OpenCV开发基础_图像像素与视觉处理流水线.md
book/第6篇_OpenCV/第2章_摄像头接入与视频帧采集_从设备确认到帧校验.md
book/第6篇_OpenCV/第3章_图像预处理与边缘提取_从去噪到结构特征.md
book/第6篇_OpenCV/第4章_轮廓提取与几何测量_从二值区域到形状结果.md
book/第6篇_OpenCV/第5章_颜色分割与目标定位_从HSV掩膜到像素候选.md
book/第6篇_OpenCV/第6章_跨帧目标关联与视觉事件_从单帧候选到稳定状态.md
book/第6篇_OpenCV/第7章_视觉事件与硬件反馈_从稳定候选到受控动作.md
code/第6篇_OpenCV/第2章_摄像头接入与视频帧采集/README.md
code/第6篇_OpenCV/第2章_摄像头接入与视频帧采集/inspect_capture.py
diagrams/uno-q-opencv-capture-validation.mmd
code/第6篇_OpenCV/第3章_图像预处理与边缘提取/README.md
code/第6篇_OpenCV/第3章_图像预处理与边缘提取/preprocess_edges.py
code/第6篇_OpenCV/第3章_图像预处理与边缘提取/test_preprocess_edges.py
diagrams/uno-q-opencv-denoise-canny.mmd
code/第6篇_OpenCV/第4章_轮廓提取与几何测量/README.md
code/第6篇_OpenCV/第4章_轮廓提取与几何测量/measure_contours.py
code/第6篇_OpenCV/第4章_轮廓提取与几何测量/test_measure_contours.py
diagrams/uno-q-opencv-contour-geometry.mmd
code/第6篇_OpenCV/第5章_颜色分割与目标定位/README.md
code/第6篇_OpenCV/第5章_颜色分割与目标定位/locate_color.py
code/第6篇_OpenCV/第5章_颜色分割与目标定位/test_locate_color.py
diagrams/uno-q-opencv-hsv-localization.mmd
code/第6篇_OpenCV/第6章_跨帧关联与视觉事件/README.md
code/第6篇_OpenCV/第6章_跨帧关联与视觉事件/temporal_events.py
code/第6篇_OpenCV/第6章_跨帧关联与视觉事件/test_temporal_events.py
diagrams/uno-q-opencv-temporal-gate.mmd
code/第6篇_OpenCV/第7章_视觉反馈安全门/README.md
code/第6篇_OpenCV/第7章_视觉反馈安全门/review_feedback.py
code/第6篇_OpenCV/第7章_视觉反馈安全门/test_review_feedback.py
diagrams/uno-q-opencv-feedback-guard.mmd
code/第6篇_OpenCV/第1章_OpenCV开发基础/README.md
code/第6篇_OpenCV/第1章_OpenCV开发基础/image_basics.py
diagrams/uno-q-opencv-image-pipeline.mmd
images/第6篇_OpenCV/README.md
```

本次检查覆盖第一篇、第二篇第 1～9 章、第三篇第 1～8 章、第四篇第 1～4 章和第五篇第 1～3 章的文件存在性、相对 Markdown 链接、篇内章节元数据、Mermaid 声明、图示占位、代码说明字段和 UTF-8；第五篇第 1 章另检查 App 结构契约、启动证据分类，第 2 章另检查生命周期状态机、`run_id` 证据过滤，第 3 章另检查声明契约、能力快照解析和发布边界；三章均检查 Python 3.10 AST 语法、演示输出、Mermaid 与 SVG 一致性、来源登记和导航入口。当前仍未执行 Arduino CLI 编译、上传、App Lab 真实导入/运行、Linux 实机盘点、网络查询、服务观测、资源压力演练、队列压力演练、性能压测、故障注入、systemd unit 安装/启用/重启、配置或凭据替换、ADB/SSH、Router/Bridge 重连、远程写操作、Bridge 联调或硬件实机运行。

第四篇第 1～4 章的 Markdown 链接、代码说明、Python 3.10 AST 语法兼容性、针对性示例/测试和 Fig-26、Fig-27 资源登记已完成本地检查；第五篇第 1 章的两个结构/日志实验、11 项 Python 测试、章节检查、Fig-28 SVG 和来源登记已完成本地检查；第五篇第 2 章的两个生命周期/会话证据实验、10 项 Python 测试、章节检查、Fig-29 SVG 和来源登记已完成本地检查；第五篇第 3 章的两个声明/依赖实验、11 项 Python 测试、章节检查、Fig-30 SVG 和来源登记已完成本地检查；第五篇第 4 章的两个配置/快照实验、10 项 Python 测试、章节检查、Fig-31 SVG 和来源登记已完成本地检查。Fig-26～Fig-31 使用缓存 Mermaid CLI 11.12.0 生成 SVG 并完成预览审阅。章节仍为 draft；SVG 生成与本地测试不等于 Python 3.10 解释器、目标 UNO Q Linux 镜像、Router/Bridge、App Lab、MCU 或 UNO Q 硬件验收，这些验证当前仍未执行。

第六篇第1～7章的 Markdown 正文、配套代码、目录和来源登记已建立；第3章的 3 项测试、第4章和第5章各 4 项测试、第6章的 7 项、第7章的 10 项测试在本机环境通过。Fig-35～Fig-41 保留 Mermaid 源文件，尚未渲染 SVG。本次未验证相机驱动、真实摄像头采集、目标 UNO Q OpenCV/NumPy 版本、色彩/几何标定、对象身份、Bridge/MCU 联动或硬件性能。
