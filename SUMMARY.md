# Arduino UNO Q 深度开发学习路线

## 第一篇：认识 Arduino UNO Q
- [本篇导读](book/第1篇_认识UNOQ/README.md)
- [第1章 Arduino 的发展](book/第1篇_认识UNOQ/第1章_Arduino的发展.md)
- [第2章 什么是 Arduino UNO Q](book/第1篇_认识UNOQ/第2章_什么是Arduino_UNO_Q.md)
- [第3章 UNO Q 的硬件架构](book/第1篇_认识UNOQ/第3章_UNO_Q的硬件架构.md)
- [第4章 UNO Q 的软件架构](book/第1篇_认识UNOQ/第4章_UNO_Q的软件架构.md)
- [第5章 第一个实验：Blink 验证闭环](book/第1篇_认识UNOQ/第5章_第一个实验_Blink验证闭环.md)

## 第二篇：STM32
- [本篇范围](book/第2篇_STM32/README.md)
- [第1章 STM32 侧开发基础：GPIO、引脚与实时边界](book/第2篇_STM32/第1章_STM32侧开发基础_GPIO与实时边界.md)
- [第2章 PWM 与定时输出：从占空比到安全控制](book/第2篇_STM32/第2章_PWM与定时输出_从占空比到安全控制.md)
- [第3章 ADC 与模拟采样：从电压读数到可验证数据](book/第2篇_STM32/第3章_ADC与模拟采样_从电压读数到可验证数据.md)
- [第4章 串口通信：从帧格式到 MCU/Linux 边界](book/第2篇_STM32/第4章_串口通信_从帧格式到MCU_Linux边界.md)
- [第5章 SPI 通信：从片选时序到设备驱动边界](book/第2篇_STM32/第5章_SPI通信_从片选时序到设备驱动边界.md)
- [第6章 I2C 通信：从设备地址到总线恢复](book/第2篇_STM32/第6章_I2C通信_从设备地址到总线恢复.md)
- [第7章 实时任务与调度：从周期循环到可验证响应](book/第2篇_STM32/第7章_实时任务与调度_从周期循环到可验证响应.md)
- [第8章 硬件验证与故障定位：从接线检查到证据闭环](book/第2篇_STM32/第8章_硬件验证与故障定位_从接线检查到证据闭环.md)
- [第9章 综合实验：传感、控制与 MCU/Linux 协同闭环](book/第2篇_STM32/第9章_综合实验_传感控制与MCU_Linux协同闭环.md)

## 第三篇：Linux
- [本篇范围](book/第3篇_Linux/README.md)
- [第1章 Linux 侧开发基础：文件系统、进程与 MCU 边界](book/第3篇_Linux/第1章_Linux侧开发基础_文件系统进程与MCU边界.md)
- [第2章 Linux 设备、网络与服务：从可见到可用](book/第3篇_Linux/第2章_Linux设备网络与服务_从可见到可用.md)
- [第3章 Linux 可观测性与资源管理：日志、时间与安全回滚](book/第3篇_Linux/第3章_Linux可观测性与资源管理_日志时间与安全回滚.md)
- [第4章 Linux 远程运维与 Python Bridge：从安全命令到可验证请求](book/第3篇_Linux/第4章_Linux远程运维与Python_Bridge_从安全命令到可验证请求.md)
- [第5章 Linux 现场自动化与 Python Bridge：队列、重连与状态缓存](book/第3篇_Linux/第5章_Linux现场自动化与Python_Bridge_队列重连与状态缓存.md)
- [第6章 Linux 与 Python Bridge 现场测试与性能治理：从基准、压测到故障注入](book/第3篇_Linux/第6章_Linux与Python_Bridge现场测试与性能治理_从基准压测到故障注入.md)
- [第7章 Linux 与 Python Bridge 现场部署与服务化治理：从 systemd、配置分层到安全回滚](book/第3篇_Linux/第7章_Linux与Python_Bridge现场部署与服务化治理_从systemd配置分层到安全回滚.md)
- [第8章 Linux 与 Python Bridge 综合运行手册：从预检到篇末交接](book/第3篇_Linux/第8章_Linux与Python_Bridge综合运行手册_从预检到交接.md)

## 第四篇：Python Bridge
- [本篇范围](book/第4篇_PythonBridge/README.md)
- [第1章 Python Bridge 开发基础：消息模型与调用边界](book/第4篇_PythonBridge/第1章_Python_Bridge开发基础_消息模型与调用边界.md)
- [第2章 Python Bridge 并发与任务生命周期：从单次调用到有界协同](book/第4篇_PythonBridge/第2章_Python_Bridge并发与任务生命周期_从单次调用到有界协同.md)
- [第3章 Python Bridge 连接复用与请求恢复：从断线到可判定结果](book/第4篇_PythonBridge/第3章_Python_Bridge连接复用与请求恢复_从断线到可判定结果.md)
- [第4章 Python Bridge 结果账本与状态查询：从返回值到可验证证据](book/第4篇_PythonBridge/第4章_Python_Bridge结果账本与状态查询_从返回值到可验证证据.md)

## 第五篇：App Lab
- [本篇范围](book/第5篇_AppLab/README.md)
- [第1章 App Lab 开发基础：应用结构、设备入口与验证边界](book/第5篇_AppLab/第1章_App_Lab开发基础_应用结构与验证边界.md)
- [第2章 App Lab 运行生命周期：导入、启动、运行与停止](book/第5篇_AppLab/第2章_AppLab运行生命周期_导入启动运行与停止.md)
- [第3章 App Lab 启动配置与 Brick 依赖：从声明到可部署性检查](book/第5篇_AppLab/第3章_AppLab启动配置与Brick依赖_从声明到可部署性检查.md)
- [第4章 App Lab 配置分层与多环境运行参数：从开发机到现场板](book/第5篇_AppLab/第4章_AppLab配置分层与多环境运行参数_从开发机到现场板.md)
- [第5章 App Lab 运行证据包与日志关联：从 run_id 到可检索证据](book/第5篇_AppLab/第5章_AppLab运行证据包与日志关联_从run_id到可检索证据.md)
- [第6章 App Lab 健康观察与故障处置：从信号到安全恢复](book/第5篇_AppLab/第6章_AppLab健康观察与故障处置_从信号到安全恢复.md)
- [第7章 App Lab 综合验证：从部署预检到运行复盘](book/第5篇_AppLab/第7章_AppLab综合验证_从部署预检到运行复盘.md)

## 第六篇：OpenCV
- [本篇范围](book/第6篇_OpenCV/README.md)
- [第1章 OpenCV 开发基础：图像、像素与视觉处理流水线](book/第6篇_OpenCV/第1章_OpenCV开发基础_图像像素与视觉处理流水线.md)
- [第2章 摄像头接入与视频帧采集：从设备确认到帧校验](book/第6篇_OpenCV/第2章_摄像头接入与视频帧采集_从设备确认到帧校验.md)
- [第3章 图像预处理与边缘提取：从去噪到结构特征](book/第6篇_OpenCV/第3章_图像预处理与边缘提取_从去噪到结构特征.md)
- [第4章 轮廓提取与几何测量：从二值区域到可核验的形状结果](book/第6篇_OpenCV/第4章_轮廓提取与几何测量_从二值区域到形状结果.md)
- [第5章 颜色分割与目标定位：从 HSV 掩膜到可核验的像素候选](book/第6篇_OpenCV/第5章_颜色分割与目标定位_从HSV掩膜到像素候选.md)
- [第6章 跨帧目标关联与视觉事件：从单帧候选到稳定状态](book/第6篇_OpenCV/第6章_跨帧目标关联与视觉事件_从单帧候选到稳定状态.md)
- [第7章 视觉事件与硬件反馈：从稳定候选到受控动作](book/第6篇_OpenCV/第7章_视觉事件与硬件反馈_从稳定候选到受控动作.md)
- [第8章 OpenCV 综合验证：从合成画面到反馈审查证据包](book/第6篇_OpenCV/第8章_OpenCV综合验证_从合成画面到反馈审查证据包.md)

## 第七篇：AI
- [本篇范围](book/第7篇_AI/README.md)
- [第1章 AI 开发基础：从任务定义到可验证推理](book/第7篇_AI/第1章_AI开发基础_从任务定义到可验证推理.md)
- [第2章 数据集与离线评估：从分组切分到混淆矩阵](book/第7篇_AI/第2章_数据集与离线评估_从分组切分到混淆矩阵.md)
- [第3章 模型工件与部署契约：从清单到目标预检](book/第7篇_AI/第3章_模型工件与部署契约_从清单到目标预检.md)
- [第4章 推理回归与数值一致性：从黄金样例到目标验收](book/第7篇_AI/第4章_推理回归与数值一致性_从黄金样例到目标验收.md)
- [第5章 端侧推理性能评估：从测量方案到资源预算](book/第7篇_AI/第5章_端侧推理性能评估_从测量方案到资源预算.md)
- [第6章 模型量化与校准验证：从校准数据到资源—精度权衡](book/第7篇_AI/第6章_模型量化与校准验证_从校准数据到资源精度权衡.md)
- [第7章 UNO Q 板载 AI 实战：App Lab AI Brick 与本地推理](book/第7篇_AI/第7章_UNO_Q板载AI实战_App_Lab_AI_Brick与本地推理.md)
- [第8章 UNO Q 接入 DeepSeek API：从云端 LLM 到可验证应用](book/第7篇_AI/第8章_UNO_Q接入DeepSeek_API_从云端LLM到可验证应用.md)
- [第9章 生成式 AI 与工具调用安全边界：从模型建议到受控执行](book/第7篇_AI/第9章_生成式AI与工具调用安全边界_从模型建议到受控执行.md)
- [第10章 AI 应用综合验证：从端侧基线到云端闭环](book/第7篇_AI/第10章_AI应用综合验证_从端侧基线到云端闭环.md)

## 第八篇：IoT
- [本篇范围](book/第8篇_IoT/README.md)
- [第1章 IoT 开发基础：从采样数据到可验证遥测](book/第8篇_IoT/第1章_IoT开发基础_从采样数据到可验证遥测.md)
- [第2章 MQTT 消息上报与幂等消费：从主题设计到重复投递](book/第8篇_IoT/第2章_MQTT消息上报与幂等消费_从主题设计到重复投递.md)
- [第3章 离线缓存与补传：从持久化队列到可验证恢复](book/第8篇_IoT/第3章_离线缓存与补传_从持久化队列到可验证恢复.md)
- [第4章 IoT 可观测性与告警：从设备状态到可操作信号](book/第8篇_IoT/第4章_IoT可观测性与告警_从设备状态到可操作信号.md)
- [第5章 IoT 远程命令与受控维护：从授权请求到结果对账](book/第8篇_IoT/第5章_IoT远程命令与受控维护_从授权请求到结果对账.md)
- [第6章 IoT 设备身份与安全通信：从连接信任到最小权限](book/第8篇_IoT/第6章_IoT设备身份与安全通信_从连接信任到最小权限.md)
- [第7章 IoT 综合验证：从分章测试到系统级证据](book/第8篇_IoT/第7章_IoT综合验证_从分章测试到系统级证据.md)

## 第九篇：Project
- [本篇范围](book/第9篇_Project/README.md)
