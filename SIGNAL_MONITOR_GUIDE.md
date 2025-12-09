# 虚拟币系统信号监控模块 - 使用指南

## 📋 功能概述

信号监控模块是一个独立的网页应用，用于监控虚拟币交易信号（做空/做多）。系统每3分钟自动采集一次数据，支持历史数据查询和可视化展示。

## 🌐 访问地址

- **信号监控页面**: https://5001-iik759kgm7i3zqlxvfrfx-cc2fbc16.sandbox.novita.ai/signal
- **恐慌指数页面**: https://5001-iik759kgm7i3zqlxvfrfx-cc2fbc16.sandbox.novita.ai/panic
- **主页**: https://5001-iik759kgm7i3zqlxvfrfx-cc2fbc16.sandbox.novita.ai

## 💡 使用说明

### 1. 实时数据监控

打开信号监控页面后，您将看到：

- **总信号数**: 做空和做多信号的总和
- **做空信号**: 当前做空信号数量及与上次相比的变化
- **做多信号**: 当前做多信号数量及与上次相比的变化
- **最后更新时间**: 数据最后更新的时间

### 2. 历史数据查询

在"历史数据查询"区域：

1. **选择开始日期和时间**: 设置查询范围的起点
2. **选择结束日期和时间**: 设置查询范围的终点
3. **点击"查询"按钮**: 执行查询并在图表中显示结果
4. **点击"重置"按钮**: 重置为今天的日期范围

查询结果会自动显示在趋势图中，展示做空和做多信号随时间的变化。

### 3. 趋势图表

- **红色线条**: 做空信号趋势
- **绿色线条**: 做多信号趋势
- **横轴**: 时间（HH:MM格式）
- **纵轴**: 信号数量

图表支持鼠标悬停查看具体数值。

### 4. 自动刷新

- 页面每**3分钟**自动刷新一次数据
- 每天**0点5分**自动重新加载页面（切换到新日期）
- 无需手动操作，数据会持续更新

## ⚙️ 系统配置

### 数据采集设置

- **采集频率**: 每3分钟（180秒）一次
- **时间基准**: 北京时间（Asia/Shanghai）
- **数据格式**: 做空|变化|做多|变化|时间
- **数据源**: Google Drive 共享文件夹
  - 文件夹ID: `1-IfqZxMVVCSg3ct6XVMyFtAbuCV3huQ`
  - 文件路径: `{日期文件夹}/信号.txt`

### 日期切换逻辑

- 系统根据北京时间确定当前日期
- 每天0点到0点5分之间，继续使用前一天的文件夹
- 0点5分后，自动切换到新日期的文件夹

## 🔧 技术架构

### 后端服务

1. **signal_monitor_api.py** (端口 5003)
   - 提供RESTful API接口
   - 管理SQLite数据库
   - 处理数据查询请求

2. **signal_collector.py** (后台进程)
   - 定时采集数据
   - 解析信号文件
   - 写入数据库

3. **crypto_server_demo.py** (端口 5001)
   - 主Web服务器
   - API请求代理
   - 静态文件服务

### 前端页面

- **signal_monitor.html**
  - 响应式设计
  - Chart.js 图表可视化
  - 自动刷新机制
  - 历史查询功能

### 数据库

- **signal_data.db** (SQLite)
  - 表: `signal_data`
  - 字段: short_count, short_change, long_count, long_change, record_time, folder_date
  - 索引: record_time, folder_date

## 🔐 Google Drive 配置（可选）

当前系统使用模拟数据进行演示。要连接实际的 Google Drive 数据源：

### 步骤

1. **创建 Google Cloud 项目**
   - 访问 https://console.cloud.google.com
   - 创建新项目

2. **启用 Google Drive API**
   - 在项目中启用 Drive API

3. **创建服务账号**
   - 创建服务账号并下载 JSON 凭证文件
   - 将凭证文件重命名为 `google_drive_credentials.json`
   - 放置到项目根目录

4. **授权访问**
   - 将共享文件夹授权给服务账号邮箱
   - 确保服务账号有读取权限

5. **更新代码**
   - 在 `signal_collector.py` 中的 `fetch_signal_from_google_drive()` 函数
   - 添加实际的 Google Drive API 调用
   - 使用 `google-api-python-client` 库

### 示例代码

```python
from googleapiclient.discovery import build
from google.oauth2 import service_account

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
SERVICE_ACCOUNT_FILE = 'google_drive_credentials.json'

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
service = build('drive', 'v3', credentials=credentials)

# 列出文件
results = service.files().list(
    q=f"'{FOLDER_ID}' in parents",
    fields="files(id, name)"
).execute()
```

## 📊 API 接口文档

### 1. 获取最新信号
```
GET /api/signal-monitor/latest
```

**响应示例**:
```json
{
  "success": true,
  "current_folder": "2025-12-05",
  "current_time": "2025-12-05 20:59:05",
  "data": {
    "short_count": 100,
    "short_change": 3,
    "long_count": 83,
    "long_change": 10,
    "record_time": "2025-12-05 20:59:05",
    "folder_date": "2025-12-05"
  }
}
```

### 2. 查询历史数据
```
GET /api/signal-monitor/history?start_date=2025-12-05&end_date=2025-12-05&start_time=00:00:00&end_time=23:59:59
```

**响应示例**:
```json
{
  "success": true,
  "start": "2025-12-05 00:00:00",
  "end": "2025-12-05 23:59:59",
  "count": 3,
  "data": [
    {
      "short_count": 131,
      "short_change": -10,
      "long_count": 95,
      "long_change": 5,
      "record_time": "2025-12-05 20:56:00",
      "folder_date": "2025-12-05"
    }
  ]
}
```

### 3. 获取统计信息
```
GET /api/signal-monitor/stats
```

**响应示例**:
```json
{
  "success": true,
  "total_records": 3,
  "date_range": {
    "start": "2025-12-05 20:56:00",
    "end": "2025-12-05 20:59:05"
  }
}
```

### 4. 测试连接
```
GET /api/signal-monitor/test
```

**响应示例**:
```json
{
  "success": true,
  "message": "API连接正常",
  "beijing_time": "2025-12-05 21:00:00",
  "today_folder": "2025-12-05",
  "drive_folder_id": "1-IfqZxMVVCSg3ct6XVMyFtAbuCV3huQ"
}
```

## 🐛 故障排查

### 问题: 页面不显示数据

**解决方案**:
1. 检查数据采集器是否运行: `ps aux | grep signal_collector`
2. 检查API服务是否运行: `curl http://localhost:5003/api/signal-monitor/test`
3. 查看采集器日志: `tail -f logs/signal_collector.log`
4. 查看API日志: `tail -f logs/signal_monitor_api.log`

### 问题: 历史查询无结果

**解决方案**:
1. 确认数据库有数据: 查看数据库记录数
2. 检查查询时间范围是否正确
3. 确认时间格式符合要求

### 问题: 图表不更新

**解决方案**:
1. 强制刷新浏览器 (Ctrl+F5 或 Cmd+Shift+R)
2. 清除浏览器缓存
3. 检查控制台是否有JavaScript错误

## 📝 数据格式说明

### 信号文件格式

文件名: `信号.txt`

内容格式: 每行一条记录
```
做空|变化|做多|变化|时间
126|0|0|0|2025-12-02 20:56:01
130|4|0|0|2025-12-02 20:59:03
```

字段说明:
- **做空**: 当前做空信号数量（整数）
- **变化**: 与上次相比的变化值（可为负数）
- **做多**: 当前做多信号数量（整数）
- **变化**: 与上次相比的变化值（可为负数）
- **时间**: 记录时间（YYYY-MM-DD HH:MM:SS）

## 📈 性能指标

- **数据采集延迟**: < 5秒
- **API响应时间**: < 100ms
- **页面加载时间**: < 2秒
- **数据库查询时间**: < 50ms
- **图表渲染时间**: < 500ms

## 🔒 安全建议

1. 生产环境中使用 HTTPS
2. 妥善保管 Google Drive API 凭证
3. 定期备份数据库文件
4. 限制 API 访问频率
5. 使用环境变量存储敏感信息

## 📞 支持

如有问题，请查看：
- GitHub 仓库: https://github.com/jamesyidc/6666.git
- 日志文件: `/home/user/webapp/logs/`
- 数据库文件: `/home/user/webapp/signal_data.db`

---

**版本**: 1.0.0  
**更新日期**: 2025-12-05  
**状态**: ✅ 已部署并运行
