# 第八篇第2章：MQTT 消息上报与幂等消费

本目录使用合成 JSONL 事件离线演示消费者幂等：

- `qos1_redelivery.jsonl`：同一事件的两行副本，用于模拟重复投递，不是 MQTT 抓包。
- `idempotent_consumer.py`：调用第1章遥测契约校验器，以 SQLite 事务同时写事件账本和模拟业务效果；不连接 Broker、网络、UNO Q 或硬件。
- `test_idempotent_consumer.py`：5 项标准库行为测试，包含两个独立进程共用临时账本、冲突阻断和事务回滚。

在本目录运行：

```shell
python -B idempotent_consumer.py
python -B -m unittest -v test_idempotent_consumer.py
```

默认演示只在临时目录创建数据库，退出时清理。脚本支持 `--database` 与 `--deliveries` 成对指定；使用该模式会在指定位置创建或更新 SQLite 文件，应只传入明确的本地测试路径。JSONL 每条最多 4096 字节，最多处理 1000 行。

输出范围固定为 `OFFLINE_QOS1_REDELIVERY_SIMULATION`。`APPLIED` 只表示本地事务提交了演示账本和模拟记录；`DUPLICATE_IGNORED` 只表示相同事件键和载荷摘要已存在；`CONFLICT_REVIEW` 不覆盖已有记录。程序不实现 MQTT QoS、PUBACK、Broker 会话、TLS/ACL 或任何外部副作用。
