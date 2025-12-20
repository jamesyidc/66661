# 高级技术指标采集系统

## 📋 系统概述

**高级技术指标采集系统**是一个独立的数据采集模块，专门负责从Binance获取K线数据并计算各种技术指标，为交易信号系统提供关键的技术分析数据。

## 🎯 主要功能

### 1. K线数据采集
- **5分钟K线**：获取最近100根5分钟K线数据
- **1小时K线**：获取最近100根1小时K线数据
- **数据来源**：Binance REST API
- **采集频率**：可配置（建议每5分钟）

### 2. 技术指标计算

#### 已实现的指标

| 指标 | 说明 | 用途 |
|-----|------|------|
| **RSI** | 相对强弱指标 | 判断超买超卖，买点1/2/3条件 |
| **SAR** | 抛物线转向指标 | 判断趋势反转，买点2条件 |
| **MACD** | 指数平滑异同移动平均线 | 判断趋势强度 |
| **布林带** | Bollinger Bands | 判断波动率和支撑压力 |
| **ATR** | 平均真实波幅 | 判断市场波动性 |

#### 5分钟统计数据

| 统计项 | 说明 | 用途 |
|-------|------|------|
| 连续不创新低 | 连续N根K线不创新低 | 买点3条件 |
| 连续低震荡 | 连续N根震荡≤0.5% | 买点3条件 |
| 平均涨跌幅 | 最近3根K线平均涨跌 | 买点3条件 |
| 平均震荡幅 | 最近3根K线平均震荡 | 买点3条件 |

### 3. 数据库表结构

#### kline_5m / kline_1h
存储K线数据（OHLCV）

```sql
CREATE TABLE kline_5m (
    id INTEGER PRIMARY KEY,
    symbol TEXT NOT NULL,
    timestamp INTEGER NOT NULL,
    open REAL NOT NULL,
    high REAL NOT NULL,
    low REAL NOT NULL,
    close REAL NOT NULL,
    volume REAL NOT NULL,
    close_time INTEGER NOT NULL,
    quote_volume REAL,
    trades INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(symbol, timestamp)
);
```

#### technical_indicators
存储技术指标计算结果

```sql
CREATE TABLE technical_indicators (
    id INTEGER PRIMARY KEY,
    symbol TEXT NOT NULL,
    timeframe TEXT NOT NULL,
    rsi_14 REAL,
    rsi_6 REAL,
    sar REAL,
    sar_trend TEXT,
    sar_quadrant INTEGER,
    macd REAL,
    macd_signal REAL,
    macd_histogram REAL,
    bb_upper REAL,
    bb_middle REAL,
    bb_lower REAL,
    bb_width REAL,
    atr_14 REAL,
    record_time TIMESTAMP NOT NULL,
    UNIQUE(symbol, timeframe, record_time)
);
```

#### kline_5m_stats
存储5分钟统计数据

```sql
CREATE TABLE kline_5m_stats (
    id INTEGER PRIMARY KEY,
    symbol TEXT NOT NULL,
    consecutive_no_new_low INTEGER DEFAULT 0,
    consecutive_low_volatility INTEGER DEFAULT 0,
    avg_change_3bars REAL,
    avg_range_3bars REAL,
    last_new_low_time TIMESTAMP,
    record_time TIMESTAMP NOT NULL,
    UNIQUE(symbol, record_time)
);
```

## 🚀 使用方法

### 1. 安装依赖

```bash
pip install pandas numpy requests pytz
```

### 2. 手动运行一次采集

```bash
cd /home/user/webapp
python3 technical_indicators_collector.py
```

### 3. 设置定时任务（每5分钟）

**方法1：使用cron**

```bash
# 编辑crontab
crontab -e

# 添加以下行（每5分钟运行一次）
*/5 * * * * cd /home/user/webapp && python3 technical_indicators_collector.py >> logs/tech_indicators.log 2>&1
```

**方法2：使用systemd timer**

创建 `/etc/systemd/system/tech-indicators.service`:

```ini
[Unit]
Description=Technical Indicators Collector

[Service]
Type=oneshot
WorkingDirectory=/home/user/webapp
ExecStart=/usr/bin/python3 /home/user/webapp/technical_indicators_collector.py
User=user
```

创建 `/etc/systemd/system/tech-indicators.timer`:

```ini
[Unit]
Description=Run Technical Indicators Collector every 5 minutes

[Timer]
OnBootSec=1min
OnUnitActiveSec=5min

[Install]
WantedBy=timers.target
```

启动定时器：

```bash
sudo systemctl enable tech-indicators.timer
sudo systemctl start tech-indicators.timer
```

**方法3：Python内置循环（推荐用于开发/测试）**

修改 `technical_indicators_collector.py` 的 `main()` 函数：

```python
def main():
    collector = TechnicalIndicatorsCollector()
    
    try:
        while True:
            collector.run_collection_cycle()
            time.sleep(300)  # 5分钟
    except KeyboardInterrupt:
        print("\n⚠️ 收到中断信号，正在退出...")
    finally:
        collector.close()
```

然后在后台运行：

```bash
nohup python3 technical_indicators_collector.py > logs/tech_indicators.log 2>&1 &
```

## 📊 API接口

### 1. 获取最新技术指标

**GET** `/api/technical-indicators/latest`

**参数：**
- `symbol` (可选): 币种（如BTCUSDT），不传则返回所有币种
- `timeframe` (可选): 时间周期（5m/1h），默认5m

**响应示例：**

```json
{
  "success": true,
  "data": [
    {
      "symbol": "BTCUSDT",
      "timeframe": "5m",
      "rsi_14": 42.35,
      "sar": 96420.5,
      "sar_trend": "bullish",
      "sar_quadrant": 3,
      "macd": 125.6,
      "macd_signal": 110.2,
      "macd_histogram": 15.4,
      "bb_upper": 97000.0,
      "bb_middle": 96500.0,
      "bb_lower": 96000.0,
      "bb_width": 1.03,
      "atr_14": 150.8,
      "record_time": "2025-12-11 10:00:00"
    }
  ],
  "count": 1,
  "timeframe": "5m"
}
```

### 2. 获取5分钟统计数据

**GET** `/api/technical-indicators/5m-stats`

**响应示例：**

```json
{
  "success": true,
  "data": [
    {
      "symbol": "BTCUSDT",
      "consecutive_no_new_low": 5,
      "consecutive_low_volatility": 3,
      "avg_change_3bars": 0.15,
      "avg_range_3bars": 0.35,
      "record_time": "2025-12-11 10:00:00"
    }
  ],
  "count": 1
}
```

### 3. 获取采集器状态

**GET** `/api/technical-indicators/collector-status`

**响应示例：**

```json
{
  "success": true,
  "data": {
    "collector_running": true,
    "last_collection_time": "2025-12-11 10:00:00"
  }
}
```

## 🔧 配置说明

### 修改监控币种

编辑 `technical_indicators_collector.py`，修改 `SYMBOLS` 列表：

```python
SYMBOLS = [
    'BTCUSDT', 'ETHUSDT', 'BNBUSDT',
    # ... 添加更多币种
]
```

### 修改采集频率

在定时任务或循环中修改 `sleep()` 时间：

```python
time.sleep(300)  # 5分钟 = 300秒
```

### 修改指标参数

在计算函数中修改参数：

```python
rsi = self.calculate_rsi(closes, period=14)  # 修改RSI周期
macd, signal, hist = self.calculate_macd(closes, fast=12, slow=26, signal=9)  # 修改MACD参数
```

## 🔗 与交易信号系统集成

### 在交易信号API中使用技术指标

```python
# 在 api_trading_signals_analyze() 中添加
cursor.execute('''
    SELECT rsi_14, sar_quadrant
    FROM technical_indicators
    WHERE symbol = ? AND timeframe = '5m'
    ORDER BY record_time DESC
    LIMIT 1
''', (symbol + 'USDT',))

tech_row = cursor.fetchone()
if tech_row:
    rsi_5m = tech_row[0]
    sar_quadrant = tech_row[1]
    
    # 使用技术指标进行条件判断
    condition_rsi_5m = rsi_5m < 30
    condition_sar_3rd = sar_quadrant == 3
```

### 在买点条件中使用

```python
# 买点2：回调买入
# 条件：条件123 + 空头>20 + 5分钟SAR第三象限 + 5分钟RSI<30
if (condition1 and condition2 and condition3 and 
    condition_rsi_5m and condition_sar_3rd):
    buy_point_2 = True
```

## 📈 监控面板

系统提供Web监控面板查看技术指标：

**访问地址：** `http://localhost:5000/technical-indicators`

**功能：**
- 实时查看所有币种的技术指标
- 筛选时间周期（5m/1h）
- 查看采集器运行状态
- 查看5分钟统计数据

## ⚠️ 注意事项

### 1. API限流
Binance API有请求频率限制，建议：
- 每次请求后 sleep 0.5-1秒
- 不要过于频繁地采集
- 监控API返回的 429 错误

### 2. 数据存储
K线数据会快速增长，建议：
- 定期清理历史数据（保留最近7天）
- 只存储必要的字段
- 添加数据压缩

### 3. 错误处理
系统已包含基本错误处理，但建议：
- 添加日志记录
- 设置告警机制
- 监控采集成功率

### 4. 性能优化
- 使用批量插入替代单条插入
- 添加数据库索引
- 考虑使用Redis缓存热点数据

## 📝 TODO清单

- [ ] 添加更多技术指标（KDJ、BOLL、DMI等）
- [ ] 支持WebSocket实时数据流
- [ ] 添加市场情绪数据（多空比例、爆仓数据）
- [ ] 实现指标回测功能
- [ ] 添加可视化图表
- [ ] 支持自定义指标公式

## 🐛 故障排查

### 采集器无法运行

1. 检查Python依赖：
```bash
pip list | grep -E "pandas|numpy|requests|pytz"
```

2. 检查网络连接：
```bash
curl https://api.binance.com/api/v3/ping
```

3. 查看日志：
```bash
tail -f logs/tech_indicators.log
```

### 数据库错误

1. 检查表是否存在：
```bash
sqlite3 crypto_data.db ".tables"
```

2. 检查表结构：
```bash
sqlite3 crypto_data.db ".schema technical_indicators"
```

3. 手动创建表：
```bash
python3 -c "from technical_indicators_collector import TechnicalIndicatorsCollector; c = TechnicalIndicatorsCollector()"
```

### API返回空数据

1. 检查采集器是否运行
2. 检查最近采集时间
3. 手动运行一次采集

---

**文档版本**: v1.0  
**更新时间**: 2025-12-11  
**维护者**: GenSpark AI Developer
