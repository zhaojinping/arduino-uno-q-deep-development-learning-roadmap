# 第七篇第8章：UNO Q 接入 DeepSeek API

本目录给出一个 Python 标准库 Chat Completions 客户端和固定合成读数示例。客户端仅接受三个有范围的数值，调用当前 REST endpoint，并把输出作为 `REPORT_ONLY` 文本。UNO Q Linux/App Lab 网络、TLS、Python secret 注入及 DeepSeek 实际响应仍为 `NOT_RUN`。

## 内容

- `deepseek_client.py`：HTTPS 请求、限时/限长、response schema 校验、错误脱敏和 transport 注入边界。
- `summarize_readings.py`：合成值 CLI。默认 dry run 不读取凭据、不创建客户端、不联网；真实请求需要同时指定 `--send-request` 与 `--confirm-network-and-cost`。
- `test_deepseek_client.py`：使用本地 RecordingTransport 的离线测试，不导入外网，不调用默认 `urllib` transport，不需真实 API key。

从仓库根目录执行离线测试：

```text
python -m pytest -q code/第7篇_AI/第8章_DeepSeek_API实战/test_deepseek_client.py
```

默认 dry run：

```text
python code/第7篇_AI/第8章_DeepSeek_API实战/summarize_readings.py
```

要发送真实请求，调用者必须事先在本机安全配置 `DEEPSEEK_API_KEY`，并明确审阅数据、同意向 DeepSeek 公共服务传输及可能费用。只有带齐两个显式开关才会建立客户端并发出一次请求：

```text
python code/第7篇_AI/第8章_DeepSeek_API实战/summarize_readings.py --send-request --confirm-network-and-cost
```

此命令不是测试命令，不要在 CI、书稿校验或无人值守任务中运行。超时后不自动重试，以免对远端已经处理的请求重复发送/计费。

## 安全与验证边界

- 不存储、打印或记录 API key；测试中仅用明示为 synthetic 的哨兵值验证错误脱敏。
- request body 只包含固定提示和三项合成数字，设有模型、thinking、输出 token、body、response 和 timeout 限制。
- Arduino App specification 的 Brick variables 有容器作用域；不能假设它们自动成为 App Python 进程的环境变量。具体 App Lab 版本未验证时，不要把 key 写入 `app.yaml` 或源码。
- 真实 DeepSeek API、账号费用、UNO Q TLS、App Lab 秘密注入、目标板运行与 Bridge/MCU 均为 `NOT_RUN`。MOCK 不代表真实响应。

## 官方来源

- [DeepSeek Chat Completions API](https://api-docs.deepseek.com/api/create-chat-completion/)
- [DeepSeek Thinking Mode](https://api-docs.deepseek.com/guides/thinking_mode/)
- [DeepSeek Models](https://api-docs.deepseek.com/api/list-models/) · [Pricing](https://api-docs.deepseek.com/quick_start/pricing/)
- [Arduino App specification](https://github.com/arduino/arduino-app-cli/blob/main/docs/app-specification.md)
- [Arduino CloudLLM 当前源码](https://github.com/arduino/app-bricks-py/blob/main/src/arduino/app_bricks/cloud_llm/cloud_llm.py)
