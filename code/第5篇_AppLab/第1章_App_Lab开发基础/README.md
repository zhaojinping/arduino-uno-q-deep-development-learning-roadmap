# 第五篇第1章：App Lab 开发基础

[返回项目根目录 README](../../../README.md)

本目录保存本章两个不连接设备的 Python 契约实验：

- `app_contract.py`：检查 `app.yaml`、`python/main.py` 以及可选 `sketch/` 的文件级结构。
- `launch_evidence.py`：根据启动、Python 和 Sketch 日志的本地输入分类证据，不把日志存在当成硬件动作成功。
- `test_app_contract.py`、`test_launch_evidence.py`：标准库 `unittest` 回归测试。
- `check_chapter.py`：检查正文源码同步、演示输出、Mermaid/SVG、链接、来源和导航。

运行方式（在仓库根目录）：

```text
python -B "code/第5篇_AppLab/第1章_App_Lab开发基础/app_contract.py"
python -B "code/第5篇_AppLab/第1章_App_Lab开发基础/launch_evidence.py"
python -B "code/第5篇_AppLab/第1章_App_Lab开发基础/test_app_contract.py"
python -B "code/第5篇_AppLab/第1章_App_Lab开发基础/test_launch_evidence.py"
python -B "code/第5篇_AppLab/第1章_App_Lab开发基础/check_chapter.py"
```

这些实验只验证本地数据结构和判定函数；不需要 YAML 第三方解析器、不访问 App Lab、不连接 Router/Bridge、不编译 Sketch，也不写入 UNO Q。
