# 第八篇第5章代码：IoT 远程命令与受控维护

本目录以本地 Python 教学门模拟命令契约、主体权限映射、到期判断、命令 ID 幂等、冲突分流和结果查询。

## 文件

- `remote_command_gate.py`：标准库模拟器和固定离线演示入口。
- `commands.jsonl`：有限的合成命令序列，不含真实凭据或设备地址。
- `test_remote_command_gate.py`：30 项行为与集成测试。

## 运行

从仓库根目录执行：

```powershell
python -B "code/第8篇_IoT/第5章_IoT远程命令与受控维护/remote_command_gate.py"
python -B -m unittest discover -s "code/第8篇_IoT/第5章_IoT远程命令与受控维护" -p "test_*.py" -v
```

演示输出 10 行合成状态，测试运行于 Python 标准库 `unittest`。命令有效期上限、正文大小、账本容量和模拟配置范围均为教学策略，不是通用生产要求。

## 安全与验证边界

`principal` 是预先提供给模拟器的上下文；代码不实现身份认证、密钥管理、签名、TLS、Broker ACL 或授权服务。账本只驻留内存，进程退出即清空；没有网络、MQTT、Bridge/RPC、UNO Q、MCU、传感器、执行器、持久化恢复或 OTA。`APPLIED` 仅表示模拟变量改变，`UNKNOWN` 不授权盲目重发。不得将本目录当作生产远程控制服务。

[返回第八篇第5章正文](../../../book/第8篇_IoT/第5章_IoT远程命令与受控维护_从授权请求到结果对账.md)
