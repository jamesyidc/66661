# 采集器启动修复报告

## 问题描述

用户反馈首页显示两个系统"没有启动"：

1. **交易信号监控** - 采集器状态未启动
2. **恐慌清洗指数** - 采集器状态未启动

### 截图显示的问题

**交易信号监控：**
```
总记录数: 1688
数据天数: 7天
最后更新: 17:18
```

**恐慌清洗指数：**
```
总记录数: 1506
数据天数: 7天
最后更新: 17:20
```

## 根本原因

### 数据存在但采集器未运行

检查发现：
1. 数据库中有历史数据（交易信号1688条，恐慌指数1506条）
2. 最后更新时间为 **17:18-17:20**（北京时间）
3. 当前时间：**18:22**（北京时间）
4. 数据延迟：**约62-64分钟**

**原因：**
- `signal_collector.py` 和 `panic_wash_collector.py` 两个采集器进程未运行
- 导致数据停止更新超过1小时

## 采集器信息

### 1. 交易信号采集器

**文件：** `signal_collector.py`

**功能：**
- 每3分钟从 filtered-signals API 采集做多/做空信号数量
- 数据源：`https://8080-im9p8x4s7ohv1llw8snop-dfc00ec5.sandbox.novita.ai`
- 存储到 `trading_signals` 表

**表结构：**
```sql
CREATE TABLE trading_signals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    record_time TEXT NOT NULL,           -- 北京时间
    record_date TEXT NOT NULL,
    long_signals INTEGER DEFAULT 0,      -- 做多信号数
    short_signals INTEGER DEFAULT 0,     -- 做空信号数
    total_signals INTEGER DEFAULT 0,     -- 总信号数
    long_ratio REAL DEFAULT 0,           -- 做多比例
    short_ratio REAL DEFAULT 0,          -- 做空比例
    today_new_high INTEGER DEFAULT 0,    -- 今日新高
    today_new_low INTEGER DEFAULT 0,     -- 今日新低
    raw_data TEXT,                       -- 原始JSON数据
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**采集日志：**
```
2025-12-14 10:24:41 - ✅ 信号采集成功: 总信号=32, 做多=32, 做空=0
2025-12-14 10:24:41 - 💾 数据保存成功: 2025-12-14 18:24:41
2025-12-14 10:24:41 - ✅ 数据采集并保存成功（第 1 次尝试）
2025-12-14 10:24:41 - 🚀 信号采集守护进程启动，采集间隔: 180秒
```

### 2. 恐慌清洗指数采集器

**文件：** `panic_wash_collector.py`

**功能：**
- 每3分钟采集一次爆仓数据
- 计算恐慌清洗指数 = 24小时爆仓人数(万人) / 全网持仓量(亿美元) × 100%
- 数据源：`https://history.btc123.fans/baocang/`
- 存储到 `panic_wash_index` 表

**表结构：**
```sql
CREATE TABLE panic_wash_index (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    record_time TEXT NOT NULL,           -- 北京时间
    record_date TEXT NOT NULL,
    hour_1_amount REAL DEFAULT 0,        -- 1小时爆仓金额
    hour_24_amount REAL DEFAULT 0,       -- 24小时爆仓金额
    hour_24_people INTEGER DEFAULT 0,    -- 24小时爆仓人数
    total_position REAL DEFAULT 0,       -- 全网持仓量
    panic_index REAL DEFAULT 0,          -- 恐慌指数
    raw_data TEXT,                       -- 原始JSON数据
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**采集日志：**
```
2025-12-14 10:26:11 - 📈 恐慌清洗指数计算:
2025-12-14 10:26:11 -    公式: 24小时爆仓人数(万人) / 全网持仓量(亿美元) × 100%
2025-12-14 10:26:11 -    爆仓人数: 71,642人 = 7.1642万人
2025-12-14 10:26:11 -    持仓量: $9,328,454,556.51 = 93.28亿美元
2025-12-14 10:26:11 -    恐慌指数: 7.1642 / 93.28 × 100% = 7.68%
2025-12-14 10:26:11 - ✅ 数据采集成功: 恐慌指数=7.68%
2025-12-14 10:26:11 - 💾 数据保存成功: 2025-12-14 18:26:11
```

## 修复步骤

### 1. 启动交易信号采集器

```bash
cd /home/user/webapp
nohup python3 signal_collector.py > signal_collector_output.log 2>&1 &
```

**启动结果：**
- PID: 22184
- 状态: ✅ 运行中
- 采集间隔: 180秒（3分钟）

**首次采集成功：**
```
时间: 2025-12-14 18:24:41 (北京时间)
总信号: 32
做多信号: 32
做空信号: 0
```

### 2. 启动恐慌清洗指数采集器

```bash
cd /home/user/webapp
nohup python3 panic_wash_collector.py > panic_wash_collector_output.log 2>&1 &
```

**启动结果：**
- PID: 22083
- 状态: ✅ 运行中
- 采集间隔: 180秒（3分钟）

**首次采集成功：**
```
时间: 2025-12-14 18:26:11 (北京时间)
24小时爆仓人数: 71,642人
全网持仓量: $93.28亿
恐慌指数: 7.68%
```

## 验证结果

### 采集器运行状态

```
✅ 运行中    Flask API
✅ 运行中    Google Drive监控
✅ 运行中    支撑/阻力快照
✅ 运行中    K线实时采集
✅ 运行中    交易信号采集       ← 已启动
✅ 运行中    恐慌清洗指数       ← 已启动
```

### 数据更新时间

```
✅ K线指标:       2025-12-14 18:26:39 (延迟 0.0 分钟)
✅ 交易信号:       2025-12-14 18:24:43 (延迟 2.0 分钟)
✅ 恐慌清洗指数:   2025-12-14 18:26:11 (延迟 0.5 分钟)
✅ 支撑/阻力快照:  2025-12-14 18:26:22 (北京时间)
```

### 首页显示效果

**交易信号监控：**
```
✅ 采集器状态: 运行中
   总记录数: 1690 (新增2条)
   数据天数: 7天
   最后更新: 18:24:43
```

**恐慌清洗指数：**
```
✅ 采集器状态: 运行中
   总记录数: 1508 (新增2条)
   数据天数: 7天
   最后更新: 18:26:11
```

## 采集器特点

### 自动采集策略

| 采集器 | 采集间隔 | 数据源 | 存储表 |
|--------|---------|--------|--------|
| 交易信号 | 3分钟 | Filtered Signals API | trading_signals |
| 恐慌指数 | 3分钟 | BTC123爆仓数据 | panic_wash_index |
| 支撑/阻力 | 3分钟 | 本地计算 | support_resistance_snapshots |
| K线数据 | 实时 | OKEx WebSocket | okex_kline_ohlc |

### 容错机制

两个采集器都实现了：
1. **重试机制：** API调用失败时最多重试4次
2. **错误日志：** 详细记录所有异常
3. **数据验证：** 采集前验证数据完整性
4. **守护进程：** 自动循环采集，无需手动重启

### 日志文件

- `signal_collector.log` - 交易信号采集日志
- `panic_wash_collector.log` - 恐慌指数采集日志
- `signal_collector_output.log` - 标准输出
- `panic_wash_collector_output.log` - 标准输出

## 数据示例

### 交易信号最新数据

```json
{
  "record_time": "2025-12-14 18:24:43",
  "long_signals": 32,
  "short_signals": 0,
  "total_signals": 32,
  "long_ratio": 100.0,
  "short_ratio": 0.0,
  "today_new_high": 1,
  "today_new_low": 0
}
```

**指标解读：**
- 当前市场做多信号100%
- 无做空信号
- 今日出现1次新高

### 恐慌清洗指数最新数据

```json
{
  "record_time": "2025-12-14 18:26:11",
  "hour_24_people": 71642,
  "total_position": 9328454556.51,
  "panic_index": 7.68
}
```

**指标解读：**
- 24小时爆仓人数：71,642人
- 全网持仓量：$93.28亿
- 恐慌指数：7.68%（中等水平）

## 监控建议

### 1. 定期检查采集器状态

```bash
# 检查进程是否运行
ps aux | grep -E "signal_collector|panic_wash_collector" | grep -v grep

# 查看最新日志
tail -20 /home/user/webapp/signal_collector.log
tail -20 /home/user/webapp/panic_wash_collector.log
```

### 2. 设置自动重启

建议使用 supervisor 或 systemd 管理采集器进程：

```ini
[program:signal_collector]
command=python3 /home/user/webapp/signal_collector.py
directory=/home/user/webapp
autostart=true
autorestart=true
startsecs=10

[program:panic_wash_collector]
command=python3 /home/user/webapp/panic_wash_collector.py
directory=/home/user/webapp
autostart=true
autorestart=true
startsecs=10
```

### 3. 数据延迟告警

建议设置数据延迟监控：
- 交易信号：延迟 > 10分钟告警
- 恐慌指数：延迟 > 10分钟告警

## 相关文件

### 采集器脚本
- `signal_collector.py` - 交易信号采集器
- `panic_wash_collector.py` - 恐慌清洗指数采集器

### 日志文件
- `signal_collector.log` - 交易信号日志
- `panic_wash_collector.log` - 恐慌指数日志
- `signal_collector_output.log` - 输出日志
- `panic_wash_collector_output.log` - 输出日志

### 数据库表
- `trading_signals` - 交易信号数据
- `panic_wash_index` - 恐慌指数数据

## 总结

✅ **问题已完全解决**
- 交易信号采集器已启动并正常运行
- 恐慌清洗指数采集器已启动并正常运行
- 所有6个监控系统全部运行正常

✅ **数据更新正常**
- 交易信号：最新 18:24:43（延迟 < 3分钟）
- 恐慌指数：最新 18:26:11（延迟 < 1分钟）
- 所有数据实时更新中

✅ **首页显示正确**
- 交易信号监控：显示"运行中"
- 恐慌清洗指数：显示"运行中"
- 数据统计和时间均正确

---

**修复时间：** 2025-12-14 10:26 UTC / 18:26 北京时间  
**启动进程：**
- signal_collector.py (PID: 22184)
- panic_wash_collector.py (PID: 22083)

**文档版本：** 1.0
