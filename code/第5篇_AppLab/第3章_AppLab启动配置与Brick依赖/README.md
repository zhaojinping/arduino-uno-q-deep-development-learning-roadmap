# 第五篇第3章：App Lab 启动配置与 Brick 依赖

[返回项目根目录 README](../../../README.md)

本目录保存本章两个不连接设备的 Python 部署预检实验：

- `deployment_contract.py`：检查 App Descriptor 的端口、Brick 条目、变量和设备引用形状。
- `dependency_resolution.py`：将规范化的 Brick 需求与人工提供的能力快照和端口占用表比较。
- `test_deployment_contract.py`、`test_dependency_resolution.py`：标准库 `unittest` 回归测试。
- `check_chapter.py`：检查正文源码同步、演示输出、Mermaid/SVG、链接、来源和导航。

运行方式（在仓库根目录）：

```text
python -B "code/第5篇_AppLab/第3章_AppLab启动配置与Brick依赖/deployment_contract.py"
python -B "code/第5篇_AppLab/第3章_AppLab启动配置与Brick依赖/dependency_resolution.py"
python -B "code/第5篇_AppLab/第3章_AppLab启动配置与Brick依赖/test_deployment_contract.py"
python -B "code/第5篇_AppLab/第3章_AppLab启动配置与Brick依赖/test_dependency_resolution.py"
python -B "code/第5篇_AppLab/第3章_AppLab启动配置与Brick依赖/check_chapter.py"
```

这些实验只验证本地声明检查和能力快照解析；不解析真实 YAML 文件、不访问 App Lab 或 `arduino-app-cli`、不查询目标 Linux/Brick/端口、不连接 Router/Bridge/MCU，也不写入 UNO Q。`READY` 和 `SIMULATED` 输出都不是部署成功证据。
