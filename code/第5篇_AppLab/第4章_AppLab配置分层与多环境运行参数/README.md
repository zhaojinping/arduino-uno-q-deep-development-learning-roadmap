# 第五篇第4章：App Lab 配置分层与多环境运行参数

[返回项目根目录 README](../../../README.md)

本目录保存本章两个不连接设备的 Python 配置治理实验：

- `config_layers.py`：按 `base < environment < runtime` 合并配置，保留来源并阻止锁定键覆盖。
- `run_config_snapshot.py`：为一次 `run_id` 生成脱敏、排序稳定的运行配置快照和指纹。
- `test_config_layers.py`、`test_run_config_snapshot.py`：标准库 `unittest` 回归测试。
- `check_chapter.py`：检查正文源码同步、演示输出、Mermaid/SVG、链接、来源和导航。

运行方式（在仓库根目录）：

```text
python -B "code/第5篇_AppLab/第4章_AppLab配置分层与多环境运行参数/config_layers.py"
python -B "code/第5篇_AppLab/第4章_AppLab配置分层与多环境运行参数/run_config_snapshot.py"
python -B "code/第5篇_AppLab/第4章_AppLab配置分层与多环境运行参数/test_config_layers.py"
python -B "code/第5篇_AppLab/第4章_AppLab配置分层与多环境运行参数/test_run_config_snapshot.py"
python -B "code/第5篇_AppLab/第4章_AppLab配置分层与多环境运行参数/check_chapter.py"
```

这些实验只验证本地配置策略和脱敏快照；不声明这是 App Lab 的内置多环境配置功能，不读取真实 Secret、不调用 App Lab/`arduino-app-cli`、不连接 Router/Bridge/MCU，也不写入 UNO Q。`SIMULATED` 输出不能替代目标环境和现场板证据。
