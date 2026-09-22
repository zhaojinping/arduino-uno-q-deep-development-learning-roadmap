# 第四篇第4章配套实验

[返回第四章正文](../../../book/第4篇_PythonBridge/第4章_Python_Bridge结果账本与状态查询_从返回值到可验证证据.md)

本目录提供两个原创标准库示例：

| 文件 | 用途 |
| --- | --- |
| `ledger.py` | 定义结果账本的请求、证据、状态转换和事件历史接口。 |
| `reconcile_status.py` | 根据账本记录与查询观察结果生成安全的状态判定。 |

`test_ledger.py` 是这两个示例的可执行测试契约。测试命令为：

```text
python -B "code/第4篇_PythonBridge/第4章_结果账本与状态查询/test_ledger.py"
```

`check_chapter.py` 检查正文元数据、章节结构、代码与 Mermaid 逐字同步、两个示例的精确输出、Python 3.10 AST 语法、SVG XML、内部链接、来源登记和导航。运行：

```text
python -B "code/第4篇_PythonBridge/第4章_结果账本与状态查询/check_chapter.py"
```

检查器仅在本机执行上述模拟示例；账本示例使用并清理临时数据库，不访问网络或开发板。Python 3.10 AST 检查不等于在 Python 3.10 解释器或目标 Linux 镜像上执行。

代码兼容 Python 3.10 及以上版本，仅使用 Python 标准库，不引入第三方依赖。示例中的 SQLite 只用于验证本地持久化和事件历史；本地 SQLite 行为不是 Arduino UNO Q 硬件证据，也不代表 Router、Bridge、App Lab 或 MCU 已经执行或确认了操作。

`SENT` 仅表示发送证据，`UNKNOWN` 不是成功状态，不能据此自动重放请求。
