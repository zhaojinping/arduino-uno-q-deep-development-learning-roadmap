# 第九篇第1章文档契约测试

本目录包含本章的离线结构测试，不含可部署到 Arduino UNO Q 的固件、传感器驱动或告警服务。

## 测试入口

在仓库根目录运行：

```powershell
python -B -m pytest -q code/第9篇_Project/第1章_项目立项与需求基线/test_chapter_contract.py
```

测试只读取本仓库的章节、导航和图示登记文件；不会访问网络、凭据、UNO Q、传感器、Broker、Bridge 或执行器。测试通过表示文档契约满足静态检查，不代表章节事实已获项目方批准、Mermaid SVG 已渲染或目标硬件已经验证。
