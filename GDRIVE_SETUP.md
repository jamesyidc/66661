# Google Drive API 配置指南

## 概述
本系统可以自动从 Google Drive 共享文件夹读取最新的监控数据。如果未配置 Google Drive API，系统会自动回退到演示数据。

## 功能说明

### 自动数据读取流程
1. **优先从 Google Drive 读取**
   - 自动查找今天日期的文件夹（北京时间，格式：YYYY-MM-DD）
   - 读取 `信号.txt` 和 `恐慌清洗.txt` 文件
   - 自动解析数据并返回

2. **失败时自动回退**
   - 如果 Google Drive API 未配置或读取失败
   - 自动使用演示数据（固定数据）
   - 系统继续正常运行

### 当前数据源
- **信号数据**: `126|0|0|0|2025-12-02 20:56:01`
- **恐慌清洗数据**: `10.77-绿|5-多头主升区间-99305-2.26-92.18-2025-12-02 20:58:50`

## 配置 Google Drive API（可选）

### 步骤 1: 创建 Google Cloud 项目
1. 访问 [Google Cloud Console](https://console.cloud.google.com/)
2. 创建新项目或选择现有项目
3. 记录项目 ID

### 步骤 2: 启用 Google Drive API
1. 在 Google Cloud Console 中
2. 导航到 "APIs & Services" > "Library"
3. 搜索 "Google Drive API"
4. 点击 "Enable"（启用）

### 步骤 3: 创建服务账号
1. 导航到 "APIs & Services" > "Credentials"
2. 点击 "Create Credentials" > "Service Account"
3. 填写服务账号详情：
   - 名称: `crypto-monitor-reader`
   - 描述: `用于读取加密货币监控数据`
4. 点击 "Create and Continue"
5. 角色选择: 无需特殊角色（基本读取权限即可）
6. 点击 "Done"

### 步骤 4: 下载服务账号密钥
1. 在 Credentials 页面，找到刚创建的服务账号
2. 点击服务账号名称进入详情页
3. 切换到 "Keys" 标签
4. 点击 "Add Key" > "Create new key"
5. 选择 "JSON" 格式
6. 点击 "Create" 下载密钥文件
7. **将下载的 JSON 文件重命名为 `gdrive_credentials.json`**

### 步骤 5: 配置文件
1. 将 `gdrive_credentials.json` 上传到 `/home/user/webapp/` 目录
2. 确保文件权限正确：
   ```bash
   chmod 600 /home/user/webapp/gdrive_credentials.json
   ```

### 步骤 6: 共享文件夹权限
1. 打开 `gdrive_credentials.json` 文件
2. 找到 `client_email` 字段（类似 `xxx@xxx.iam.gserviceaccount.com`）
3. 复制这个邮箱地址
4. 打开 Google Drive 共享文件夹
5. 点击 "共享" 按钮
6. 将服务账号邮箱添加为查看者（Viewer）
7. 确保服务账号有权限访问文件夹及其子文件夹

### 步骤 7: 重启服务器
```bash
# 停止现有服务器
pkill -f crypto_server_demo.py

# 启动服务器
python3 crypto_server_demo.py
```

## 验证配置

### 检查 API 是否工作
```bash
# 测试信号数据 API
curl http://localhost:5001/api/monitor/signal

# 测试恐慌清洗数据 API
curl http://localhost:5001/api/monitor/panic
```

### 查看服务器日志
服务器会打印以下消息：
- ✅ `Google Drive 读取器已初始化` - 配置成功
- ✅ `从 Google Drive 读取信号数据成功` - 数据读取成功
- ⚠️  `使用演示数据` - 未配置或读取失败，使用演示数据

## 文件夹结构要求

Google Drive 共享文件夹结构必须符合以下格式：

```
共享文件夹 (ID: 1-IfqZxMV9VCSg3ct6XVMyFtAbuCV3huQ)
├── 2025-12-02/          # 日期文件夹（格式：YYYY-MM-DD，北京时间）
│   ├── 信号.txt         # 信号数据文件
│   └── 恐慌清洗.txt     # 恐慌清洗数据文件
├── 2025-12-03/
│   ├── 信号.txt
│   └── 恐慌清洗.txt
└── ...
```

### 文件格式

#### 信号.txt
```
126|0|0|0|2025-12-02 20:56:01
做空|变化|做多|变化|时间
```

#### 恐慌清洗.txt
```
10.77-绿|5-多头主升区间-99305-2.26-92.18-2025-12-02 20:58:50
恐慌清洗指标|趋势评级-市场区间-24h爆仓人数-24h爆仓金额-全网持仓量-时间
```

## 故障排除

### 问题 1: 未找到日期文件夹
**症状**: 日志显示 "❌ 未找到日期文件夹: YYYY-MM-DD"

**解决方案**:
1. 确认 Google Drive 中存在今天日期的文件夹
2. 确认文件夹名称格式为 `YYYY-MM-DD`（例如：`2025-12-02`）
3. 确认服务账号有权限访问该文件夹

### 问题 2: 未找到数据文件
**症状**: 日志显示 "❌ 未找到 信号.txt 文件"

**解决方案**:
1. 确认文件名称正确（区分大小写）
2. 确认文件在正确的日期文件夹中
3. 确认文件不在子文件夹中

### 问题 3: Google Drive API 未初始化
**症状**: 日志显示 "⚠️  Google Drive API 未初始化"

**解决方案**:
1. 检查 `gdrive_credentials.json` 文件是否存在
2. 检查 JSON 文件格式是否正确
3. 检查文件权限（应为 600 或 644）
4. 重新下载服务账号密钥

### 问题 4: 权限被拒绝
**症状**: API 调用返回权限错误

**解决方案**:
1. 确认服务账号邮箱已添加到共享文件夹
2. 确认服务账号至少有 "查看者" 权限
3. 等待几分钟让权限生效

## 测试工具

### 手动测试 Google Drive 读取
```bash
cd /home/user/webapp
python3 gdrive_reader.py
```

### 查看详细日志
服务器启动时会打印详细的日志信息，包括：
- Google Drive API 初始化状态
- 文件夹查找结果
- 文件下载状态
- 数据解析结果

## 注意事项

1. **时区**: 系统使用北京时间（Asia/Shanghai）来确定今天的日期
2. **自动回退**: 如果 Google Drive 读取失败，系统自动使用演示数据，不会影响服务运行
3. **缓存**: 每次 API 调用都会重新读取 Google Drive，确保数据最新
4. **配额**: Google Drive API 有每日配额限制，正常使用不会超出

## API 端点

### 信号监控 API
- **URL**: `GET /api/monitor/signal`
- **响应**:
  ```json
  {
    "success": true,
    "data": {
      "short": "126",
      "short_change": "0",
      "long": "0",
      "long_change": "0",
      "update_time": "2025-12-02 20:56:01"
    }
  }
  ```

### 恐慌清洗监控 API
- **URL**: `GET /api/monitor/panic`
- **响应**:
  ```json
  {
    "success": true,
    "data": {
      "panic_indicator": "10.77-绿",
      "trend_rating": "5",
      "market_zone": "多头主升区间",
      "liquidation_24h_count": "99305",
      "liquidation_24h_amount": "2.26",
      "total_position": "92.18",
      "update_time": "2025-12-02 20:58:50"
    }
  }
  ```

## 监控页面

### 信号监控页面
- **URL**: `/signal` 或 `/signal_monitor.html`
- **功能**: 实时显示做空/做多信号数据
- **刷新**: 每 10 秒自动刷新

### 恐慌清洗监控页面
- **URL**: `/panic` 或 `/panic_monitor.html`
- **功能**: 实时显示恐慌清洗指标和市场数据
- **刷新**: 每 10 秒自动刷新

## 相关文件

- `gdrive_reader.py` - Google Drive 数据读取核心模块
- `monitor_data_reader.py` - 监控数据读取封装（支持自动回退）
- `crypto_server_demo.py` - Flask 服务器（集成数据读取）
- `signal_monitor.html` - 信号监控前端页面
- `panic_monitor.html` - 恐慌清洗监控前端页面
- `gdrive_credentials.json` - Google Drive API 服务账号密钥（需自行配置）

## 总结

- ✅ **无需配置即可使用** - 系统自动使用演示数据
- ✅ **可选配置 Google Drive** - 配置后自动读取最新数据
- ✅ **自动回退机制** - 读取失败时使用演示数据
- ✅ **实时更新** - 每次请求都读取最新数据
- ✅ **容错设计** - 确保服务始终可用
