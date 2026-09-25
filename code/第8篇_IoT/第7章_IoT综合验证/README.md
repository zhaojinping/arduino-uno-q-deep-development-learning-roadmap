# IoT 本地综合测试聚合器

本目录提供固定范围的离线验证工具。它分别启动第八篇第1～6章的 Python `unittest` 测试目录，汇总每章的本地退出状态和已运行测试数。它不接受自定义目录、脚本、命令、设备地址或服务地址。

## 运行方式

从仓库根目录打开终端执行：

```powershell
python -B "code/第8篇_IoT/第7章_IoT综合验证/aggregate_local_tests.py"
python -B -m unittest discover -s "code/第8篇_IoT/第7章_IoT综合验证" -p "test_*.py"
```

第一条命令顺序运行六个已固定的 `test_*.py` 目录；每个目录都由独立 Python 子进程执行，单个目录最长等待 120 秒。第二条命令只运行本章工具自身的测试。工具依照 Python 官方 `unittest discover` 命令行接口指定起始目录和文件匹配模式；目录值来自脚本中的常量，而不是用户输入。[来源登记](../../../resources/references.md#第八篇第7章补充核验)

## 报告解释

命令成功时输出单行 JSON。关键字段如下：

| 字段 | 含义 |
| --- | --- |
| `scope` | 固定为 `LOCAL_TESTS_ONLY`。 |
| `decision` | 六个章节都发现并运行了至少一个测试且全部返回零，才是 `LOCAL_TESTS_PASS`；出现失败、超时、进程启动错误或空测试目录为 `LOCAL_TESTS_FAIL`；章节结果缺失、额外无效记录或顺序不符为 `LOCAL_TESTS_INCOMPLETE`。 |
| `chapters` | 固定列出第1～6章的状态、子进程退出码和测试项数。 |
| `target_validation` | 固定为 `NOT_RUN`，因为工具没有访问目标板或部署环境。 |
| `deployment_authorized` | 固定为 `false`。 |

每个章节状态 `LOCAL_PASS` 只描述该目录中的本地测试进程。`LOCAL_FAIL`、`LOCAL_TIMEOUT`、`LOCAL_EXECUTION_ERROR` 或 `LOCAL_NO_TESTS` 都会阻止汇总为全绿。退出码 `0` 表示所有固定本地套件通过；`1` 表示失败、超时、启动错误或没有运行测试；`2` 表示传入了额外参数。工具不输出底层测试日志，需定位失败时可进入对应章节目录单独运行其测试。

## 安全与验证边界

- 仅使用 Python 标准库；固定调用 `python -B -m unittest discover`，不用 shell，不启动用户传入的命令。
- 聚合器只选择仓库内第1～6章的固定测试目录，不接受外部路径。它启动的 Python 测试子进程会继承调用进程的环境并以当前用户权限执行；本工具不是操作系统沙箱，不要把它当成秘密隔离边界，也只应运行可信仓库中的测试代码。
- 聚合器本身不建立网络/Broker/设备连接或读取凭据；当前固定测试使用本地合成数据。若后续修改测试目录或测试代码，应先审阅其输入、导入和副作用，再运行。
- 测试样例仍由各章定义；其中 MQTT 重投递、离线补传、遥测、远程命令和设备安全策略均为本地合成或静态模拟。
- 本工具不收集目标板证据，不验证 UNO Q 镜像、TLS 握手、MQTT ACL、Bridge/RPC、MCU、外设或现场安全互锁。
- 即使所有本地测试通过，也不代表集成测试、目标环境验收、风险复核、变更批准或部署授权。

## 文件

- `aggregate_local_tests.py`：固定套件清单、隔离子进程运行和 JSON 汇总。
- `test_aggregate_local_tests.py`：聚合决策、失败/超时/启动错误、额外参数拒绝、真实六目录执行及本章导航/图源契约测试。
- [第7章正文](../../../book/第8篇_IoT/第7章_IoT综合验证_从分章测试到系统级证据.md)。
