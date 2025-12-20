# Telegram信号推送系统

**更新时间**: 2025-12-15 17:51:00

---

## ✅ 系统概述

自动监控并推送3大类交易信号到Telegram群组：

1. **支撑压力线系统** - 抄底/逃顶信号
2. **计次预警系统** - 每小时计次监控
3. **交易信号系统** - 买点1-4 + 卖点1 + 7日/48h高低点

---

## 📊 三大系统详解

### 1️⃣ 支撑压力线系统

**数据源**: `https://5000-iz6uddj6rs3xe48ilsyqq-cbeee0f9.sandbox.novita.ai/support-resistance`

**API**: `/api/support-resistance/latest-signal`

**信号类型**:
- 🔵 **抄底信号** (scenario_1) - 支撑压力线买入信号
- 🔴 **逃顶信号** (scenario_2) - 支撑压力线卖出信号

**触发条件**: 
- 信号时间在2小时内
- 未重复发送

**推送格式**:
```
🔵 【抄底信号】

币种: BTC
价格: $42,000.00
时间: 2025-12-15 17:45:00
类型: 支撑压力线 - 抄底

查看详情 (链接)
```

---

### 2️⃣ 计次预警系统

**数据源**: `https://5000-iz6uddj6rs3xe48ilsyqq-cbeee0f9.sandbox.novita.ai/query`

**API**: `/api/latest`

**预警逻辑**:
1. 每小时整点（±2分钟）记录基准值
2. 例如：9点整记录计次=5
3. 10点前如果计次≥7（基准+2），触发预警
4. 10点整再次记录新基准

**触发条件**:
- 当前计次 >= 本小时基准值 + 2
- 未重复发送

**推送格式**:
```
⚠️ 【计次预警】

运算时间: 2025-12-15 09:30:00
当前计次: 7
基准值: 5
阈值: 7

完整数据:
急涨: 18
急跌: 5
本轮急涨: 18
本轮急跌: 5
计次得分: ☆
状态: 震荡无序
差值: 13
比价最低: 0
比价创新高: 0
24h涨≥10%: 0
24h跌≤-10%: 0

查看详情 (链接)
```

---

### 3️⃣ 交易信号系统

**数据源**: 
- 买点1-3: `https://5000-iz6uddj6rs3xe48ilsyqq-cbeee0f9.sandbox.novita.ai/trading-signals`
- 买点4+卖点1: `https://5000-iz6uddj6rs3xe48ilsyqq-cbeee0f9.sandbox.novita.ai/kline-indicators`

**API**:
- `/api/trading-signals/analyze` - 买点1-3
- `/api/kline-indicators/signals` - 买点4, 卖点1, 7日/48h高低点

**信号类型**:
- 🟢 **买点1** - 交易信号系统
- 🟢 **买点2** - 交易信号系统
- 🟢 **买点3** - 交易信号系统
- 🟢 **买点4** - K线指标系统（5分钟+7日低点+2根不破+RSI<20）
- 🔴 **卖点1** - K线指标系统（5分钟+30K高点+6根不破+RSI≥60）
- 📊 **7日高点/低点** - K线指标系统
- 📊 **48小时高点/低点** - K线指标系统

**触发条件**:
- 信号时间在2小时内
- 未重复发送

**推送格式（买点4示例）**:
```
🟢 【买点4】

币种: ETH
价格: $2,200.00
时间: 2025-12-15 17:40:00
RSI: 18.5
7日低点: $2,195.00

查看详情 (链接)
```

---

## 📂 文件结构

```
telegram_signal_system.py          # 主程序
telegram_signals.db                # 信号记录数据库
telegram_signal_system.log         # 运行日志
telegram_signal_system_output.log  # 输出日志

start_telegram_signal_system.sh    # 启动脚本
stop_telegram_signal_system.sh     # 停止脚本
test_telegram_signals.py           # 测试脚本
```

---

## 🚀 使用方法

### 启动服务

```bash
./start_telegram_signal_system.sh
```

输出：
```
✅ Telegram信号推送系统已启动 (PID: 12345)
📝 日志文件: telegram_signal_system.log
📊 输出文件: telegram_signal_system_output.log

查看日志: tail -f telegram_signal_system.log
停止服务: ./stop_telegram_signal_system.sh
```

### 停止服务

```bash
./stop_telegram_signal_system.sh
```

### 查看日志

```bash
# 实时查看日志
tail -f telegram_signal_system.log

# 查看最近100行
tail -n 100 telegram_signal_system.log
```

### 测试系统

```bash
python3 test_telegram_signals.py
```

---

## 🔧 配置说明

### Telegram配置

在 `telegram_signal_system.py` 中：

```python
TG_BOT_TOKEN = "8437045462:AAFePnwdC21cqeWhZISMQHGGgjmroVqE2H0"
TG_CHAT_ID = "-1003227444260"
```

### API配置

```python
API_BASE = "http://localhost:5000"
```

### 检查频率

```python
# 主循环每60秒检查一次
time.sleep(60)
```

---

## 📊 数据库结构

### support_resistance_signals

存储支撑压力线信号：

```sql
CREATE TABLE support_resistance_signals (
    id INTEGER PRIMARY KEY,
    signal_type TEXT,      -- 'buy' (抄底) 或 'sell' (逃顶)
    symbol TEXT,
    price REAL,
    signal_time TEXT,
    sent_at TIMESTAMP,
    UNIQUE(symbol, signal_type, signal_time)
);
```

### count_alerts

存储计次预警：

```sql
CREATE TABLE count_alerts (
    id INTEGER PRIMARY KEY,
    record_time TEXT,
    count_value INTEGER,
    threshold INTEGER,
    full_data TEXT,        -- JSON格式完整数据
    sent_at TIMESTAMP,
    UNIQUE(record_time)
);
```

### count_baselines

存储每小时计次基准：

```sql
CREATE TABLE count_baselines (
    id INTEGER PRIMARY KEY,
    hour_time TEXT,        -- YYYY-MM-DD HH:00:00
    count_value INTEGER,
    created_at TIMESTAMP,
    UNIQUE(hour_time)
);
```

### trading_signals

存储交易信号：

```sql
CREATE TABLE trading_signals (
    id INTEGER PRIMARY KEY,
    signal_type TEXT,      -- buy_point_1/2/3/4, sell_point_1, etc.
    symbol TEXT,
    price REAL,
    signal_time TEXT,
    rsi REAL,
    additional_info TEXT,  -- JSON格式额外信息
    sent_at TIMESTAMP,
    UNIQUE(symbol, signal_type, signal_time)
);
```

---

## 🎯 工作流程

```
┌─────────────────────────────────────────────────────────┐
│              Telegram信号推送系统流程图                    │
└─────────────────────────────────────────────────────────┘

每1分钟执行一次:
  │
  ├─ 1️⃣ 检查支撑压力线信号
  │    ├─ 调用 /api/support-resistance/latest-signal
  │    ├─ 筛选2小时内的抄底/逃顶信号
  │    ├─ 检查是否已发送（数据库去重）
  │    └─ 发送TG消息
  │
  ├─ 2️⃣ 检查计次预警
  │    ├─ 调用 /api/latest
  │    ├─ 整点记录基准值
  │    ├─ 检查是否超过阈值（基准+2）
  │    ├─ 检查是否已发送
  │    └─ 发送TG预警消息
  │
  └─ 3️⃣ 检查交易信号
       ├─ 调用 /api/trading-signals/analyze
       ├─ 调用 /api/kline-indicators/signals
       ├─ 筛选2小时内的买卖点信号
       ├─ 检查是否已发送
       └─ 发送TG消息
```

---

## 📈 监控数据展示

系统启动后会发送启动消息：

```
🤖 【系统启动】

Telegram信号推送系统已启动
监控间隔: 1分钟
启动时间: 2025-12-15 17:50:00

监控模块:
1️⃣ 支撑压力线系统 (抄底/逃顶)
2️⃣ 计次预警系统
3️⃣ 交易信号系统 (买点1-4 + 卖点1)
```

---

## 🔍 故障排查

### 1. 服务未启动

```bash
# 检查进程
ps aux | grep telegram_signal_system

# 查看日志
tail -n 50 telegram_signal_system.log
```

### 2. API连接失败

```bash
# 测试API
curl http://localhost:5000/api/support-resistance/latest-signal
curl http://localhost:5000/api/latest
curl http://localhost:5000/api/trading-signals/analyze
curl http://localhost:5000/api/kline-indicators/signals
```

### 3. TG消息发送失败

检查日志中的错误信息：
```
❌ 消息发送失败: Unauthorized
❌ 消息发送失败: Chat not found
```

解决方法：
- 检查 TG_BOT_TOKEN 是否正确
- 检查 TG_CHAT_ID 是否正确
- 确认Bot已加入群组

---

## ✅ 系统状态

- 🟢 **运行中**: 正常监控和推送
- 🟡 **等待**: 无信号需要推送
- 🔴 **异常**: 查看日志排查问题

---

## 📝 更新日志

**2025-12-15**:
- ✅ 初始版本发布
- ✅ 三大系统整合完成
- ✅ 数据库去重机制
- ✅ 2小时时间窗口
- ✅ 计次预警整点记录

---

**文档版本**: v1.0  
**最后更新**: 2025-12-15 17:51:00
