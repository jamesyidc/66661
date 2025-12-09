# 系统架构说明 - 自动从 Google Drive 获取数据

## ✅ 系统已经实现自动从 Google Drive 获取数据

您的系统**完全不依赖本地文件** `panic_wash_latest.txt`，而是**直接从 Google Drive 实时获取数据**！

## 🏗️ 系统架构

```
Google Drive 文件夹
📁 https://drive.google.com/drive/folders/1JNZKKnZLeoBkxSumjS63SOInCriPfAKX
    │
    ├─ 2025-12-06_0006.txt
    ├─ 2025-12-06_0016.txt
    ├─ ...
    └─ 2025-12-06_0819.txt (最新文件)
         ↓
    [Playwright 浏览器自动化]
         ↓
┌─────────────────────────────────────┐
│  panic_wash_reader_v5.py            │
│  - 使用 Playwright 访问 Google Drive │
│  - 自动查找最新 .txt 文件            │
│  - 打开并解析文件内容                │
│  - 提取急涨、急跌等数据              │
└─────────────────────────────────────┘
         ↓
┌─────────────────────────────────────┐
│  auto_gdrive_collector_v2.py        │
│  - 每 10 分钟自动运行一次            │
│  - 调用 panic_wash_reader_v5        │
│  - 将数据保存到数据库                │
│  - 后台守护进程运行                  │
└─────────────────────────────────────┘
         ↓
┌─────────────────────────────────────┐
│  homepage_data.db (SQLite数据库)    │
│  - summary_data 表（汇总数据）       │
│  - coin_details 表（币种详情）       │
└─────────────────────────────────────┘
         ↓
┌─────────────────────────────────────┐
│  crypto_server_demo.py (Flask API)  │
│  - /api/homepage/latest (最新数据)   │
│  - /api/homepage/history (历史数据)  │
│  - 端口: 5001                        │
└─────────────────────────────────────┘
         ↓
    [用户访问]
    - Web界面: http://localhost:5001/live-data
    - API接口: http://localhost:5001/api/homepage/latest
```

## 📊 当前系统状态

### 1. 数据源
- **Google Drive 文件夹**: 1JNZKKnZLeoBkxSumjS63SOInCriPfAKX
- **最新文件**: 2025-12-06_0819.txt (08:19 北京时间)
- **文件数量**: 50 个 txt 文件

### 2. 自动采集器
- **状态**: ✅ 正在运行 (PID: 20775)
- **采集间隔**: 10 分钟
- **最后采集**: 2025-12-06 09:59:01
- **采集方式**: Playwright 浏览器自动化

### 3. 数据库
- **路径**: homepage_data.db
- **最新数据**: 
  - 急涨: 0
  - 急跌: 22
  - 比值: 999.0
  - 差值: -22.0
  - 时间: 2025-12-06 09:59:01

### 4. API 服务
- **服务器**: Flask (端口 5001)
- **状态**: ✅ 正在运行
- **最新数据**: 与数据库一致

## 🔧 核心组件说明

### panic_wash_reader_v5.py
```python
# 核心功能：
# 1. 使用 Playwright 访问 Google Drive
# 2. 滚动页面加载所有文件
# 3. 查找最新的 .txt 文件
# 4. 打开文件并获取内容
# 5. 解析数据（急涨、急跌、币种信息等）
```

**特点**:
- ✅ 无需 Google Drive API 认证
- ✅ 无需下载文件到本地
- ✅ 直接从网页读取最新数据
- ✅ 突破 gdown 的 50 文件限制（通过网页访问）

### auto_gdrive_collector_v2.py
```python
# 核心功能：
# 1. 后台守护进程运行
# 2. 每 10 分钟执行一次采集
# 3. 调用 panic_wash_reader_v5 获取数据
# 4. 将数据保存到 SQLite 数据库
# 5. 支持信号处理（Ctrl+C 安全退出）
```

**管理命令**:
```bash
# 持续运行（生产模式）
python3 auto_gdrive_collector_v2.py

# 执行一次（测试模式）
python3 auto_gdrive_collector_v2.py --once

# 查看状态
python3 auto_gdrive_collector_v2.py --status

# 或使用管理脚本
./start_collector.sh   # 启动
./stop_collector.sh    # 停止
./status_collector.sh  # 查看状态
```

## 🎯 数据流转过程

1. **每 10 分钟一次**：
   - 采集器醒来，准备获取数据

2. **访问 Google Drive**：
   - Playwright 启动无头浏览器
   - 访问文件夹 URL
   - 滚动页面加载文件列表

3. **查找最新文件**：
   - 解析 HTML 获取所有 .txt 文件
   - 按时间排序找到最新文件
   - 例如: 2025-12-06_0819.txt

4. **获取文件内容**：
   - 在页面中定位文件元素
   - 双击打开文件
   - 读取文件文本内容

5. **解析数据**：
   - 提取急涨、急跌、比值、差值
   - 解析币种详细信息
   - 整理为结构化数据

6. **保存数据库**：
   - 插入 summary_data 表
   - 插入 coin_details 表
   - 记录当前北京时间

7. **API 提供数据**：
   - Flask 服务从数据库读取最新记录
   - 返回 JSON 格式数据
   - 前端页面显示

## ❓ 常见问题

### Q1: 系统是否依赖本地文件？
**答**: ❌ 完全不依赖！系统直接从 Google Drive 实时获取数据。

### Q2: 数据多久更新一次？
**答**: 每 10 分钟自动更新一次。

### Q3: 为什么显示的是 08:19 的数据？
**答**: 因为 Google Drive 文件夹中最新的文件就是 2025-12-06_0819.txt。
      如果需要更新的数据，需要有新文件上传到 Google Drive。

### Q4: 如何确认系统在正常工作？
**答**: 运行以下命令：
```bash
# 查看采集器状态
python3 auto_gdrive_collector_v2.py --status

# 查看采集器日志
tail -f logs/collector.log

# 查看数据库最新记录
sqlite3 homepage_data.db "SELECT * FROM summary_data ORDER BY id DESC LIMIT 1;"
```

### Q5: 如何手动触发一次数据采集？
**答**: 
```bash
python3 auto_gdrive_collector_v2.py --once
```

## 🔍 验证系统运行

```bash
# 1. 检查采集器进程
ps aux | grep auto_gdrive_collector_v2.py

# 2. 测试一次采集
python3 auto_gdrive_collector_v2.py --once

# 3. 查看 API 响应
curl http://localhost:5001/api/homepage/latest

# 4. 访问监控页面
# 浏览器打开: http://localhost:5001/live-data
```

## 📝 总结

✅ **系统已经实现自动从 Google Drive 获取数据**
✅ **不依赖任何本地文件**
✅ **采集器正在后台运行**
✅ **数据每 10 分钟自动更新**
✅ **当前显示的就是 Google Drive 最新文件的数据**

**如果需要更新的数据**，请检查：
1. Google Drive 是否在 08:19 后上传了新文件
2. 文件上传程序是否正常工作
3. 是否达到了 50 文件的显示限制

---
文档更新时间: 2025-12-06 10:00
