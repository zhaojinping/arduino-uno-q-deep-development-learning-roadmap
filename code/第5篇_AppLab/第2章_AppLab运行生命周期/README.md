# 第五篇第2章：App Lab 运行生命周期

[返回项目根目录 README](../../../README.md)

本目录保存本章两个不连接设备的 Python 生命周期实验：

- `lifecycle.py`：用不可变状态机表示导入、准备、启动、运行、停止和失败迁移。
- `session_evidence.py`：按 `run_id`、通道和事件过滤陈旧日志，分类 `RUNNING`、`FAILED`、`STOPPED` 和 `UNKNOWN`。
- `test_lifecycle.py`、`test_session_evidence.py`：标准库 `unittest` 回归测试。
- `check_chapter.py`：检查正文源码同步、演示输出、Mermaid/SVG、链接、来源和导航。

运行方式（在仓库根目录）：

```text
python -B "code/第5篇_AppLab/第2章_AppLab运行生命周期/lifecycle.py"
python -B "code/第5篇_AppLab/第2章_AppLab运行生命周期/session_evidence.py"
python -B "code/第5篇_AppLab/第2章_AppLab运行生命周期/test_lifecycle.py"
python -B "code/第5篇_AppLab/第2章_AppLab运行生命周期/test_session_evidence.py"
python -B "code/第5篇_AppLab/第2章_AppLab运行生命周期/check_chapter.py"
```

这些实验只验证本地阶段迁移和会话证据分类；不访问 App Lab、不连接 Router/Bridge、不编译或刷写 Sketch，也不写入 UNO Q。`SIMULATED` 输出不能替代目标设备日志或物理观察。
