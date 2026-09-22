# Task 1 实施报告：建立测试契约和代码目录

## 状态

`DONE_WITH_CONCERNS`

## 范围

本任务仅处理第四篇第4章代码目录、公共 Python 类型/函数名称和可执行测试契约；未编写章节正文、导航、Mermaid、SVG，也未加入 Router、Bridge、App Lab、网络、硬件或 MCU 调用。

## 已完成文件

- `code/第4篇_PythonBridge/第4章_结果账本与状态查询/README.md`
- `code/第4篇_PythonBridge/第4章_结果账本与状态查询/test_ledger.py`
- `code/第4篇_PythonBridge/第4章_结果账本与状态查询/ledger.py`
- `code/第4篇_PythonBridge/第4章_结果账本与状态查询/reconcile_status.py`

README 说明了两个后续示例、测试命令、Python 3.10+ 下限、标准库依赖边界，以及本地 SQLite 不是 UNO Q 硬件证据。`ledger.py` 建立了 `State`、`RequestSpec`、`Evidence`、`RequestRecord`、`LedgerEvent`、`LedgerConflict` 和 `Ledger` 的公共名称；`reconcile_status.py` 建立了 `Observation`、`Decision` 和 `reconcile` 的公共名称。

测试契约覆盖：初始 `PENDING`、`PENDING -> SENT -> UNKNOWN -> APPLIED`、错误 expected state、非法转换、重复 request ID、身份不匹配，以及关闭/重新打开 SQLite 文件后保留记录和事件历史。

## 验证记录

执行：

```text
python -B "code/第4篇_PythonBridge/第4章_结果账本与状态查询/test_ledger.py"
```

结果：退出码 `1`，共运行 7 个测试，`FAILED (errors=7)`。失败均来自任务允许保留的最小骨架 `NotImplementedError`，明确表明账本持久化、状态转换、读取和状态协调尚未实现；没有把测试断言改弱以制造通过结果。

执行：

```text
git diff --check
```

结果：退出码 `0`。

## 关注事项

后续任务必须实现 SQLite 持久化、事件历史、合法状态转换、重复请求保护、身份校验和 `reconcile` 安全判定，之后同一测试命令才应转为通过。当前提交不是可运行的账本实现，也不提供任何 UNO Q 硬件执行或成功证据。

## 审查修复追加记录

已按审查意见更新：

- 增加 `SENT` 缺少发送证据或使用非发送证据时必须失败的契约测试。
- 增加匹配的 `UNKNOWN` 观察仍产生 `KEEP_UNKNOWN` 的契约测试，并断言 `decision.action`。
- 增加精确七成员 `State` 词汇测试。
- 移除 `ledger.py` 中未使用的 `Any` 导入。
- 将 `Decision` 调整为包含 `action`、`target`、`reason` 的冻结数据类；对齐 `Evidence`、`Observation` 字段及 `Ledger(str | Path)`、`events() -> tuple[...]` 签名。

修复后执行：

```text
python -B "code/第4篇_PythonBridge/第4章_结果账本与状态查询/test_ledger.py"
```

实际输出摘要：

```text
Ran 10 tests in 0.011s
FAILED (errors=9)
TEST_EXIT=1
```

其中 `test_state_vocabulary_is_exactly_seven_members` 为 `ok`；其余 9 项仍因任务范围内明确保留的 `NotImplementedError` 骨架失败。

同时执行：

```text
git diff --check
```

实际输出：`DIFF_CHECK_EXIT=0`。
