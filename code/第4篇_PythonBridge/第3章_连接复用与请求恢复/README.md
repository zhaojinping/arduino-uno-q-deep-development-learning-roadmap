# 第四篇第3章配套实验

[返回第三章正文](../../../book/第4篇_PythonBridge/第3章_Python_Bridge连接复用与请求恢复_从断线到可判定结果.md)

本目录保存两个原创标准库实验。运行结果均为 `SIMULATED`，无网络、文件写入或硬件调用。兼容目标为 Python 3.10+；实际验证版本与结果见[本章实施记录](../../../docs/superpowers/plans/2026-09-22-python-bridge-chapter3-plan.md)。

| 文件 | 用途 |
| --- | --- |
| [connection_owner.py](connection_owner.py) | 多个协程共享恢复、限制重试、隔离旧连接代次 |
| [recovery_policy.py](recovery_policy.py) | 依据发送证据、结果身份和期限生成恢复建议 |
| [test_recovery.py](test_recovery.py) | 针对并发竞争、耗尽、取消、超时、错配和过期的回归检查 |
| [check_chapter.py](check_chapter.py) | 正文与代码/图源一致性、元数据、相对链接、锚点与 SVG 检查 |

## 运行方式

在仓库根目录依次执行：

1. `python -B "code/第4篇_PythonBridge/第3章_连接复用与请求恢复/connection_owner.py"`
2. `python -B "code/第4篇_PythonBridge/第3章_连接复用与请求恢复/recovery_policy.py"`
3. `python -B "code/第4篇_PythonBridge/第3章_连接复用与请求恢复/test_recovery.py"`
4. `python -B "code/第4篇_PythonBridge/第3章_连接复用与请求恢复/check_chapter.py"`

`-B` 避免生成 Python 字节码缓存。两个示例的完整代码说明和预期输出均在正文；测试正常结束时输出 `OK`。

## 实验模型的边界

- `open_and_probe()` 是本地替身接口，未调用官方 Bridge；实际适配器负责资源关闭和协议验证。
- `Random(7)` 仅用于教学复现。真实部署的不同实例不能共用固定抖动序列。
- `recovery_policy.py` 接收已经校验的内部数据；示例的参数摘要是标签，未实现认证和规范化哈希。
- `NOT_APPLIED_FINAL` 是应用自定义证据，要求提供方保证旧尝试不会继续执行。`NOT_FOUND` 不满足这一要求。
- 所有恢复建议都不直接执行动作。结果账本持久化、接收端去重和板端验证仍需独立实现。
