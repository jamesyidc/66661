# 首页TG消息推送系统接口说明

## 📱 功能概述

在系统首页（`/` 路径）已经集成了TG消息推送系统的实时状态监控卡片，用户可以直观地看到TG Bot的运行状态和推送统计信息。

## 🎯 接口位置

**前端入口**: 首页 https://5000-iypypqmz2wvn9dmtq7ewn-583b4d74.sandbox.novita.ai/

**后端API**: `/api/telegram/status`

## 📊 显示内容

### 卡片信息包括：

1. **运行状态**
   - ✅ 运行中 / ❌ 已停止
   - 实时检测telegram_notifier.py进程状态

2. **已推送数量**
   - 统计所有成功发送的消息数量
   - 数据来源：telegram_notifier.log

3. **最近消息类型**
   - 显示最近3条推送的消息类型
   - 包括：计次预警、支撑压力线、交易信号、买点4

4. **最后更新时间**
   - 显示最近一次检测的时间戳
   - 格式：HH:MM（北京时间）

## 🔌 API接口详情

### 请求
```
GET /api/telegram/status
```

### 响应示例
```json
{
  "success": true,
  "is_running": true,
  "status": "运行中",
  "last_update": "2025-12-13 13:24:47",
  "total_sent": 1,
  "last_messages": [],
  "bot_name": "@jamesyi9999_bot",
  "group_id": "-1003227444260",
  "check_interval": "60秒",
  "monitoring_items": [
    "支撑压力线系统 (8+币种触发)",
    "计次预警 (1小时增加≥2)",
    "高频交易信号 (15+币种做多)",
    "买点4 (7日新低+市场情绪)"
  ]
}
```

### 响应字段说明

| 字段 | 类型 | 说明 |
|-----|------|-----|
| `success` | boolean | API请求是否成功 |
| `is_running` | boolean | TG推送系统是否在运行 |
| `status` | string | 运行状态中文描述 |
| `last_update` | string | 最后更新时间（YYYY-MM-DD HH:MM:SS） |
| `total_sent` | integer | 累计发送消息数量 |
| `last_messages` | array | 最近3条消息类型列表 |
| `bot_name` | string | Telegram机器人名称 |
| `group_id` | string | 推送群组ID |
| `check_interval` | string | 检测间隔时间 |
| `monitoring_items` | array | 监控项目列表 |

## 🎨 前端实现

### 卡片特性

1. **自动刷新**
   - 每30秒自动刷新一次状态
   - 与其他卡片同步更新

2. **状态指示**
   - 运行中：绿色 ✅
   - 已停止：红色 ❌
   - 检测失败：橙色 ⚠️

3. **交互功能**
   - 点击卡片主体：跳转到Telegram Bot
   - 底部按钮：直接打开 @jamesyi9999_bot

### 样式设计

```css
/* 特殊渐变背景 */
background: linear-gradient(135deg, rgba(34, 139, 230, 0.95) 0%, rgba(29, 78, 216, 0.95) 100%);

/* 按钮样式 */
background: linear-gradient(135deg, #228be6 0%, #1d4ed8 100%);
```

## 🔄 数据流程

```
telegram_notifier.py (后台运行)
       ↓
telegram_notifier.log (日志记录)
       ↓
/api/telegram/status (API解析)
       ↓
首页JavaScript (前端展示)
       ↓
每30秒自动刷新
```

## 📋 监控项目

### 1. 支撑压力线系统
- **触发条件**: 8+币种接近支撑线/压力线
- **数据源**: `support_resistance_snapshots` 表

### 2. 计次预警（急涨急跌系统）
- **触发条件**: 1小时内计次增加 ≥ 2
- **数据源**: `crypto_snapshots` 表
- **显示内容**: 当前计次、1小时前计次、增加量、星级评分、市场情绪

### 3. 高频交易信号
- **触发条件**: 15+币种出现做多信号
- **数据源**: `trading_signals` 表

### 4. 买点4信号
- **触发条件**: 7日新低 + 市场情绪判断
- **数据源**: 多表联合查询

## 🛠️ 相关文件

### 核心文件
- `templates/index.html` - 首页模板（line 760-785）
- `app_new.py` - 后端API（line 7152-7233）
- `telegram_notifier.py` - TG推送服务
- `telegram_notifier.log` - 运行日志

### 管理脚本
- `start_telegram_notifier.sh` - 启动脚本
- `stop_telegram_notifier.sh` - 停止脚本

## 🎯 测试验证

### 1. 测试API接口
```bash
curl http://localhost:5000/api/telegram/status | python3 -m json.tool
```

### 2. 访问首页
```
https://5000-iypypqmz2wvn9dmtq7ewn-583b4d74.sandbox.novita.ai/
```

### 3. 检查日志
```bash
tail -f telegram_notifier.log
```

### 4. 检查进程
```bash
ps aux | grep telegram_notifier
```

## ✅ 功能状态

- [x] API接口实现完成
- [x] 前端卡片集成完成
- [x] 自动刷新功能正常
- [x] 状态指示器正常
- [x] 数据统计准确
- [x] 日志解析正常
- [x] 在线部署成功

## 📝 总结

首页TG消息推送系统接口已完整实现，可以：
- ✅ 实时显示TG Bot运行状态
- ✅ 统计累计推送消息数量
- ✅ 展示最近消息类型
- ✅ 自动刷新保持数据最新
- ✅ 直接跳转到Telegram Bot

**在线访问**: https://5000-iypypqmz2wvn9dmtq7ewn-583b4d74.sandbox.novita.ai/

---

📅 创建时间: 2025-12-13  
🔧 开发者: GenSpark AI Developer  
📱 Bot: @jamesyi9999_bot
