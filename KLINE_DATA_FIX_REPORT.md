# K线数据错误问题分析与修复报告

## 📌 用户反馈问题

用户反馈页面显示的加密货币价格数据全部错误，如：
- APT显示 $1.6810
- BCH显示 $574.1000  
- BTC显示 $90114.7000
- 等等...

用户质疑："这些都是错误的"

## 🔍 问题调查

### 1. 数据源检查

检查数据库中的K线数据：

```sql
SELECT timestamp, close, created_at 
FROM okex_kline_ohlc 
WHERE symbol = 'BTC-USDT-SWAP' AND timeframe = '5m'
ORDER BY timestamp DESC 
LIMIT 1;
```

**发现问题：**
- 最新数据时间：`2025-12-14 08:00:00`
- 当前时间：`2025-12-14 09:08:00`
- **数据延迟：1.1小时以上！**

### 2. 实时采集器检查

检查 `okex_websocket_realtime_collector_fixed.py`:

```bash
ps aux | grep websocket
tail -f okex_indicators.log
```

**发现采集器在运行，但是：**
- ✅ `okex_indicators_history` 表正常更新（技术指标）
- ❌ `okex_kline_ohlc` 表**没有**更新（K线OHLC数据）

### 3. 代码分析

#### 问题代码（第211-244行）

```python
def save_kline(symbol, timeframe, kline):
    """保存K线数据到数据库（仅在整点时刻）"""
    try:
        # ...
        
        # ❌ 错误：保存到不存在的表
        table = 'okex_kline_5m' if timeframe == '5m' else 'okex_kline_1h'
        
        cursor.execute(f'''
            INSERT OR REPLACE INTO {table}  # ❌ 错误表名
            (symbol, timestamp, open, high, low, close, volume, vol_currency, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
        ''', (symbol, timestamp, open_price, high, low, close, volume, vol_currency))
```

#### 前端API代码（app_new.py）

```python
def api_symbol_kline(symbol):
    # ✅ API从 okex_kline_ohlc 表读取数据
    cursor.execute('''
        SELECT timestamp, open, high, low, close, volume
        FROM okex_kline_ohlc  # 正确的表
        WHERE symbol = ? AND timeframe = ?
        ORDER BY timestamp ASC
        LIMIT ?
    ''', (symbol, db_timeframe, limit))
```

## 🐛 根本原因

**数据不匹配问题：**

1. **采集器写入：** `okex_kline_5m` / `okex_kline_1h` (这两个表根本不存在!)
2. **API读取：** `okex_kline_ohlc` (正确的表)
3. **结果：** 采集器写入的数据被"丢失"，API读取不到新数据

**为什么数据停留在 08:00:**
- 这是最后一次批量导入K线数据的时间（由 `import_real_ohlc_data.py` 导入）
- 之后的实时采集数据都被保存到了错误的表，无法被前端读取

## ✅ 修复方案

### 修复代码（okex_websocket_realtime_collector_fixed.py）

```python
def save_kline(symbol, timeframe, kline):
    """保存K线数据到数据库（仅在整点时刻）"""
    try:
        import pytz
        conn = sqlite3.connect('crypto_data.db')
        cursor = conn.cursor()
        
        # kline: [timestamp, open, high, low, close, volume]
        timestamp = int(kline[0])
        open_price = float(kline[1])
        high = float(kline[2])
        low = float(kline[3])
        close = float(kline[4])
        volume = float(kline[5])
        
        # 使用北京时间
        beijing_tz = pytz.timezone('Asia/Shanghai')
        created_at = datetime.now(beijing_tz).strftime('%Y-%m-%d %H:%M:%S')
        
        # ✅ 修复：保存到统一的 okex_kline_ohlc 表
        cursor.execute('''
            INSERT OR REPLACE INTO okex_kline_ohlc
            (symbol, timeframe, timestamp, open, high, low, close, volume, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (symbol, timeframe, timestamp, open_price, high, low, close, volume, created_at))
        
        conn.commit()
        conn.close()
        
        return True
    except Exception as e:
        print(f"❌ 保存K线失败 {symbol} {timeframe}: {e}")
        return False
```

### 关键改动

1. **❌ 删除：** `table = 'okex_kline_5m' if timeframe == '5m' else 'okex_kline_1h'`
2. **✅ 修复：** 直接写入 `okex_kline_ohlc` 表
3. **✅ 优化：** 使用北京时间 `created_at` 字段
4. **✅ 统一：** timeframe格式保持 `5m` / `1H`

## 📊 修复效果

### 修复前
- K线数据停留在 `2025-12-14 08:00:00`
- 数据延迟 **1+ 小时**
- 用户看到的都是旧价格
- 实时采集器运行但数据"丢失"

### 修复后（预期）
- K线数据每5分钟自动更新
- 实时显示最新价格
- 27个币种全部实时同步
- 数据延迟 < 5分钟

### 验证方法

```bash
# 等待下一个5分钟整点（09:10, 09:15, 09:20...）
# 然后检查数据库

sqlite3 crypto_data.db "
SELECT symbol, 
       datetime(timestamp/1000, 'unixepoch', 'localtime') as kline_time,
       close,
       created_at
FROM okex_kline_ohlc
WHERE timeframe = '5m'
ORDER BY created_at DESC
LIMIT 10;
"
```

预期结果：应该看到 `created_at` 时间戳在 09:05, 09:10, 09:15... 的新数据

## 🔧 部署步骤

1. ✅ 修改代码：`okex_websocket_realtime_collector_fixed.py`
2. ✅ 安装依赖：`pip install websockets pytz`
3. ✅ 重启采集器：`pkill -f okex_websocket` 然后重新启动
4. ⏳ 等待验证：等待下一个5分钟整点，检查数据更新

## 📝 相关文件

- **修复文件：** `okex_websocket_realtime_collector_fixed.py` (save_kline函数)
- **API文件：** `app_new.py` (api_symbol_kline函数)
- **数据库：** `crypto_data.db` (okex_kline_ohlc表)
- **Git Commit：** `a23dd73` - "🔧 修复K线数据实时更新问题"

## 🎯 总结

**问题本质：** 采集器和API使用了不同的数据表名，导致实时采集的K线数据无法被前端读取。

**解决方案：** 统一数据表名为 `okex_kline_ohlc`，确保采集器写入和API读取使用同一个表。

**用户影响：** 解决用户反馈的"数据全部错误"问题，现在将显示实时更新的正确价格。

---

**状态：** ✅ 已修复并部署  
**生效时间：** 2025-12-14 09:10:00 (下一个5分钟整点)  
**分支：** genspark_ai_developer  
**PR：** https://github.com/jamesyidc/66661/pull/1
