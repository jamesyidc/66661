# 决策-K线指标系统（OKEx版本）

## 📋 系统概述

**决策-K线指标系统**是一个独立的技术指标采集模块，专门用于采集OKEx永续合约的K线数据和技术指标。该系统与主交易系统分离，专注于数据采集而非计算。

## ✨ 核心功能

### 1️⃣ 数据采集范围

- **数据源**：OKEx永续合约API (`https://www.okx.com/api/v5/market/candles`)
- **币种数量**：27个主流币种
  - BTC, ETH, XRP, BNB, SOL, LTC, DOGE, SUI, TRX, TON
  - ETC, BCH, HBAR, XLM, FIL, LINK, CRO, DOT, AAVE, UNI
  - NEAR, APT, CFX, CRV, STX, LDO, TAO
- **时间周期**：5分钟和1小时K线
- **采集频率**：建议每5分钟采集一次

### 2️⃣ 技术指标

| 指标名称 | 说明 | 用途 |
|---------|------|------|
| **RSI (14)** | 相对强弱指数 | 判断超买超卖状态（<30超卖，>70超买） |
| **SAR** | 抛物线转向指标 | 趋势反转点判断 |
| **SAR多空** | K线与SAR位置关系 | 多头（K线在SAR上方）、空头（K线在SAR下方） |
| **SAR象限** | SAR在布林带中的位置 | 1（SAR>UB）、2（UB>SAR>BOLL）、3（BOLL>SAR>LB）、4（SAR<LB） |
| **多空计数** | 多转空/空转多连续计数 | 如"空头02"表示多转空后的第2个周期 |
| **布林带** | UB/BOLL/LB（上中下轨） | 价格波动范围判断 |

### 3️⃣ 5分钟K线额外数据

- **振幅**：`(最高价 - 最低价) / 最低价 × 100%`
- **涨跌幅**：`(收盘价 - 开盘价) / 开盘价 × 100%`

## 🔧 技术实现

### 数据库表结构

#### 1. okex_kline_5m（5分钟K线表）

```sql
CREATE TABLE okex_kline_5m (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL,
    timestamp INTEGER NOT NULL,
    open REAL NOT NULL,
    high REAL NOT NULL,
    low REAL NOT NULL,
    close REAL NOT NULL,
    volume REAL NOT NULL,
    vol_currency REAL,
    amplitude REAL,
    change_pct REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(symbol, timestamp)
);
```

#### 2. okex_kline_1h（1小时K线表）

```sql
CREATE TABLE okex_kline_1h (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL,
    timestamp INTEGER NOT NULL,
    open REAL NOT NULL,
    high REAL NOT NULL,
    low REAL NOT NULL,
    close REAL NOT NULL,
    volume REAL NOT NULL,
    vol_currency REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(symbol, timestamp)
);
```

#### 3. okex_technical_indicators（技术指标表）

```sql
CREATE TABLE okex_technical_indicators (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL,
    timeframe TEXT NOT NULL,
    current_price REAL,
    rsi_14 REAL,
    sar REAL,
    sar_position TEXT,
    sar_quadrant INTEGER,
    sar_count_label TEXT,
    bb_upper REAL,
    bb_middle REAL,
    bb_lower REAL,
    record_time TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(symbol, timeframe, record_time)
);
```

#### 4. okex_sar_tracking（SAR多空计数跟踪表）

```sql
CREATE TABLE okex_sar_tracking (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL,
    timeframe TEXT NOT NULL,
    current_position TEXT,
    position_count INTEGER DEFAULT 1,
    last_change_time TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(symbol, timeframe)
);
```

### SAR多空逻辑详解

#### 多空判断

- 🟢 **多头（bullish）**：当前K线收盘价在SAR上方
- 🔴 **空头（bearish）**：当前K线收盘价在SAR下方

#### 多转空/空转多计数

- **多转空**：SAR从K线下方移动到上方时，开始计数"空头01"、"空头02"...直到SAR再次移动到K线下方
- **空转多**：SAR从K线上方移动到下方时，开始计数"多头01"、"多头02"...直到SAR再次移动到K线上方

**示例流程：**

```
时刻1: K线在SAR上方 → 多头01
时刻2: K线在SAR上方 → 多头02
时刻3: K线在SAR上方 → 多头03
时刻4: K线跌破SAR → 空头01  <-- 多转空
时刻5: K线在SAR下方 → 空头02
时刻6: K线突破SAR → 多头01  <-- 空转多
```

#### SAR象限定义

相对于布林带的位置关系：

- **象限1**：SAR > 布林带上轨（UB）
- **象限2**：布林带上轨（UB） > SAR > 布林带中轨（BOLL）
- **象限3**：布林带中轨（BOLL） > SAR > 布林带下轨（LB）
- **象限4**：SAR < 布林带下轨（LB）

## 🌐 API接口

### 1. 获取最新指标数据

```bash
GET /api/kline-indicators/latest?symbol=BTC-USDT-SWAP&timeframe=5m
```

**参数：**
- `symbol`（可选）：币种，如`BTC-USDT-SWAP`
- `timeframe`（可选）：时间周期，`5m`或`1h`

**响应示例：**

```json
{
  "success": true,
  "data": [
    {
      "symbol": "BTC-USDT-SWAP",
      "timeframe": "5m",
      "current_price": 93618.8,
      "rsi_14": 70.73,
      "sar": 95123.456,
      "sar_position": "bearish",
      "sar_quadrant": 1,
      "sar_count_label": "空头01",
      "bb_upper": 94000.12,
      "bb_middle": 93500.00,
      "bb_lower": 93000.88,
      "amplitude": 0.14,
      "change_pct": 0.09,
      "record_time": "2025-12-11 12:35:00"
    }
  ],
  "count": 27,
  "timestamp": "2025-12-11 12:35:15"
}
```

### 2. 获取采集器状态

```bash
GET /api/kline-indicators/collector-status
```

**响应示例：**

```json
{
  "success": true,
  "status": "running",
  "last_collection_time": "2025-12-11 12:35:11",
  "minutes_since_last": 2.5,
  "data_counts": {
    "kline_5m": 2700,
    "kline_1h": 2700,
    "indicators": 54
  }
}
```

### 3. 监控页面

```bash
GET /kline-indicators
```

展示完整的K线指标监控界面，包含：
- 采集器运行状态
- 最后采集时间
- 数据统计
- 币种和周期筛选器
- 完整的指标数据表格

## 🚀 部署说明

### 运行采集器（一次性）

```bash
cd /home/user/webapp
python3 okex_indicators_collector.py
```

### 设置定时任务（每5分钟采集）

```bash
# 编辑crontab
crontab -e

# 添加以下行
*/5 * * * * cd /home/user/webapp && python3 okex_indicators_collector.py >> okex_collector.log 2>&1
```

### 查看采集日志

```bash
tail -f /home/user/webapp/okex_collector.log
```

## 📊 在线访问

| 项目 | URL |
|------|-----|
| **K线指标系统主页** | https://5000-iypypqmz2wvn9dmtq7ewn-583b4d74.sandbox.novita.ai/kline-indicators |
| **API - 全部数据** | https://5000-iypypqmz2wvn9dmtq7ewn-583b4d74.sandbox.novita.ai/api/kline-indicators/latest |
| **API - 5分钟数据** | https://5000-iypypqmz2wvn9dmtq7ewn-583b4d74.sandbox.novita.ai/api/kline-indicators/latest?timeframe=5m |
| **API - BTC数据** | https://5000-iypypqmz2wvn9dmtq7ewn-583b4d74.sandbox.novita.ai/api/kline-indicators/latest?symbol=BTC-USDT-SWAP |
| **API - 采集器状态** | https://5000-iypypqmz2wvn9dmtq7ewn-583b4d74.sandbox.novita.ai/api/kline-indicators/collector-status |

## 🎯 与买点系统的集成建议

该K线指标系统可以为**决策-交易信号系统**提供缺失的技术指标数据：

### 买点2条件补充
- 5分钟RSI < 30（从`okex_technical_indicators`表查询）
- 5分钟SAR在第三象限（`sar_quadrant = 3`）

### 买点3条件补充
- 1小时RSI < 15（从`okex_technical_indicators`表查询）
- 连续5个5分钟K线不创新低（需要额外实现逻辑）

### 集成示例代码

```python
# 在交易信号系统中查询技术指标
def check_buy_point_2_conditions(symbol):
    cursor.execute('''
        SELECT rsi_14, sar_quadrant
        FROM okex_technical_indicators
        WHERE symbol = ? AND timeframe = '5m'
        ORDER BY record_time DESC
        LIMIT 1
    ''', (symbol + '-USDT-SWAP',))
    
    row = cursor.fetchone()
    if row:
        rsi_5m = row['rsi_14']
        sar_quad = row['sar_quadrant']
        
        condition_5m_rsi = rsi_5m < 30
        condition_sar_q3 = sar_quad == 3
        
        return condition_5m_rsi and condition_sar_q3
    return False
```

## 📁 核心文件

| 文件 | 说明 |
|------|------|
| `okex_indicators_collector.py` | OKEx数据采集器（Python脚本） |
| `templates/kline_indicators.html` | 监控页面（前端UI） |
| `app_new.py` | Flask应用（包含3个新API路由） |
| `KLINE_INDICATORS_SYSTEM.md` | 系统文档（本文档） |

## 🐛 故障排查

### 问题1：采集器无法启动

**可能原因：**
- 缺少依赖包

**解决方案：**
```bash
pip3 install requests pandas numpy pytz
```

### 问题2：API返回空数据

**可能原因：**
- 数据库表为空
- 采集器未运行

**解决方案：**
```bash
# 手动运行一次采集器
python3 okex_indicators_collector.py

# 检查数据库内容
python3 -c "import sqlite3; conn = sqlite3.connect('crypto_data.db'); cursor = conn.cursor(); cursor.execute('SELECT COUNT(*) FROM okex_technical_indicators'); print('指标数据条数:', cursor.fetchone()[0])"
```

### 问题3：OKEx API限流

**可能原因：**
- 请求频率过高

**解决方案：**
- 在`okex_indicators_collector.py`中增加`time.sleep(0.5)`延迟
- 减少采集频率（如改为每10分钟一次）

## 📝 更新日志

### v1.0.0 - 2025-12-11
- ✅ 初始版本发布
- ✅ 支持27个币种的5分钟/1小时K线采集
- ✅ 实现SAR多空判断和象限划分
- ✅ 实现多转空/空转多连续计数
- ✅ 创建完整的监控页面
- ✅ 提供3个API接口

## 👥 维护者

- GenSpark AI Developer Team

## 📄 许可证

本项目为内部使用系统，仅供学习和研究使用。
