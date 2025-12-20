# K线数据库完整指南

## 📊 数据库概览

### 基本信息
- **数据库文件**: `crypto_data.db` (SQLite3格式)
- **K线数据表**: `okex_kline_ohlc`
- **总记录数**: 45,362 条
- **币种数量**: 27 个
- **时间范围**: 2025-12-04 08:00 ~ 2025-12-14 08:00

---

## 🗂️ 表结构详解

### okex_kline_ohlc 表

| 字段名 | 类型 | 说明 | 示例 |
|--------|------|------|------|
| **symbol** | TEXT | 币种标识（主键1） | `BTC-USDT-SWAP` |
| **timeframe** | TEXT | 时间周期（主键2） | `5m`, `1H` |
| **timestamp** | INTEGER | 时间戳，毫秒（主键3） | `1733979000000` |
| **open** | REAL | 开盘价 | `90111.60` |
| **high** | REAL | 最高价 | `90184.60` |
| **low** | REAL | 最低价 | `90085.60` |
| **close** | REAL | 收盘价 | `90105.10` |
| **volume** | REAL | 成交量 | `4222.24` |
| **created_at** | TEXT | 导入时间 | `2025-12-14 07:40:00` |

**主键**: `PRIMARY KEY (symbol, timeframe, timestamp)`

---

## 📈 数据分布

### 时间周期分布
| 周期 | 记录数 | 币种数 | 每个币种K线数 |
|------|--------|--------|---------------|
| 5m   | 38,881 | 27     | 1,440 (约5天) |
| 1H   | 6,481  | 27     | 240 (10天)    |

### 币种列表（27个）
```
AAVE, APT, BCH, BNB, BTC, CFX, CRO, CRV, DOGE, DOT,
EOS, ETH, FIL, LINK, LTC, MATIC, NEAR, SAND, SHIB,
SOL, SUI, TAO, TRX, UNI, WIF, WLD, XRP
```

### 每个币种的数据量
- **5分钟K线**: 1,440 条/币种
- **1小时K线**: 240 条/币种
- **合计**: 1,680 条/币种

---

## ✅ 数据质量验证

### 1. 完整性验证 ✅
- ✅ 所有27个币种数据完整
- ✅ 5分钟K线：1,440 条/币种（标准）
- ✅ 1小时K线：240 条/币种（标准）

### 2. 连续性验证 ✅
- ✅ BTC 5分钟K线：无数据间隙
- ✅ 时间戳连续，无缺失

### 3. 数据合理性验证 ✅
- ✅ 所有OHLC数据满足：`low ≤ open, close ≤ high`
- ✅ 随机抽样10条，100%通过验证

### 4. 数据新鲜度 ✅
- ✅ 最新K线时间：2025-12-14 08:00:00
- ✅ 距离现在：< 1小时（非常新鲜）

---

## 💾 数据导出方法

### 方法1: 使用导出脚本（推荐）

已提供专用导出工具：`export_kline_data.py`

#### 导出为CSV格式（每个币种一个文件）
```bash
python3 export_kline_data.py --format csv --output kline_export
```

**输出结果**：
- 生成 `kline_export/` 目录
- 每个币种2个文件（5m和1H）
- 共54个CSV文件
- 包含EXPORT_REPORT.txt汇总报告

#### 导出为SQL格式（单个文件）
```bash
python3 export_kline_data.py --format sql --output kline_data.sql
```

**输出结果**：
- 生成 `kline_data.sql` 文件（约15-20MB）
- 包含建表语句和所有INSERT语句
- 可直接导入其他SQLite数据库

#### 同时导出CSV和SQL
```bash
python3 export_kline_data.py --format both
```

### 方法2: 直接复制数据库文件
```bash
cp crypto_data.db crypto_data_backup_$(date +%Y%m%d).db
```

### 方法3: 使用SQLite命令
```bash
# 导出整个表为SQL
sqlite3 crypto_data.db ".dump okex_kline_ohlc" > kline_ohlc.sql

# 导出为CSV
sqlite3 crypto_data.db -csv -header "SELECT * FROM okex_kline_ohlc" > kline_all.csv
```

---

## 🔍 常用查询示例

### 查询特定币种的K线数据
```sql
-- BTC最近100根5分钟K线
SELECT * FROM okex_kline_ohlc
WHERE symbol = 'BTC-USDT-SWAP' AND timeframe = '5m'
ORDER BY timestamp DESC
LIMIT 100;
```

### 查询特定时间范围的数据
```sql
-- 查询2025-12-13的所有BTC数据
SELECT * FROM okex_kline_ohlc
WHERE symbol = 'BTC-USDT-SWAP' 
  AND timeframe = '5m'
  AND timestamp >= 1733961600000  -- 2025-12-13 00:00:00
  AND timestamp < 1734048000000   -- 2025-12-14 00:00:00
ORDER BY timestamp;
```

### 计算K线统计数据
```sql
-- 计算BTC今日价格统计
SELECT 
    MIN(low) as lowest_price,
    MAX(high) as highest_price,
    AVG(close) as avg_close_price,
    (MAX(high) - MIN(low)) as daily_range,
    ((MAX(high) - MIN(low)) / MIN(low) * 100) as range_pct
FROM okex_kline_ohlc
WHERE symbol = 'BTC-USDT-SWAP'
  AND timeframe = '5m'
  AND timestamp >= 1733961600000;
```

### 查询48小时高低点
```sql
-- 查询BTC最近48小时的高低点
SELECT 
    MAX(high) as high_48h,
    MIN(low) as low_48h,
    (MAX(high) - MIN(low)) as amplitude_48h
FROM okex_kline_ohlc
WHERE symbol = 'BTC-USDT-SWAP'
  AND timeframe = '5m'
  AND timestamp >= (strftime('%s', 'now') - 172800) * 1000;  -- 48小时前
```

---

## 🔧 数据导入到其他数据库

### 导入到新的SQLite数据库
```bash
# 使用SQL文件导入
sqlite3 new_database.db < kline_data.sql

# 或从原数据库直接复制表
sqlite3 new_database.db "
ATTACH DATABASE 'crypto_data.db' AS source;
CREATE TABLE okex_kline_ohlc AS SELECT * FROM source.okex_kline_ohlc;
DETACH DATABASE source;
"
```

### 导入到MySQL
```bash
# 先导出为SQL
python3 export_kline_data.py --format sql

# 修改SQL语法（需要手动调整）
# SQLite的INTEGER -> MySQL的BIGINT
# SQLite的REAL -> MySQL的DECIMAL(20,8)

# 然后导入MySQL
mysql -u user -p database < kline_data_mysql.sql
```

### 导入到PostgreSQL
```sql
-- 1. 创建表
CREATE TABLE okex_kline_ohlc (
    symbol VARCHAR(50),
    timeframe VARCHAR(10),
    timestamp BIGINT,
    open NUMERIC(20,8),
    high NUMERIC(20,8),
    low NUMERIC(20,8),
    close NUMERIC(20,8),
    volume NUMERIC(20,8),
    created_at TIMESTAMP,
    PRIMARY KEY (symbol, timeframe, timestamp)
);

-- 2. 使用CSV导入
\COPY okex_kline_ohlc FROM 'kline_all.csv' WITH (FORMAT csv, HEADER true);
```

---

## 📋 CSV文件格式说明

### 字段顺序
```
timestamp, datetime, open, high, low, close, volume, created_at
```

### 数据示例
```csv
timestamp,datetime,open,high,low,close,volume,created_at
1733979000000,2025-12-12 10:10:00,90111.60,90184.60,90085.60,90105.10,4222.24,2025-12-14 07:40:00
```

### 字段说明
- **timestamp**: 毫秒时间戳（整数）
- **datetime**: 可读时间格式（方便查看）
- **open/high/low/close**: 浮点数价格
- **volume**: 浮点数成交量
- **created_at**: 数据导入时间

---

## 🚀 实时数据更新

目前数据库中的K线数据是**静态历史数据**。如需持续更新，可以：

### 选项1: 使用已有的导入脚本
```bash
# 重新运行导入脚本（会覆盖旧数据）
python3 import_real_ohlc_data.py
```

### 选项2: 增量更新（需要开发）
创建定时任务，每5分钟/1小时获取最新K线并插入数据库。

### 选项3: 使用实时采集器
启动 `okex_websocket_realtime_collector_fixed.py` 进行实时采集。

---

## 📊 数据使用场景

### 1. 技术分析
- 计算MA、MACD、KDJ等指标
- 识别形态（头肩顶、双底等）
- 支撑阻力位分析

### 2. 回测交易策略
- 使用历史K线数据测试策略
- 计算收益率和回撤
- 优化参数

### 3. 机器学习训练
- 价格预测模型
- 趋势分类
- 异常检测

### 4. 可视化分析
- 绘制K线图
- 技术指标图表
- 交易量分析

---

## ⚠️ 注意事项

### 1. 数据时效性
- 当前数据最新至：2025-12-14 08:00
- 建议定期更新以保持数据新鲜

### 2. 时区说明
- 所有时间戳为UTC时间
- `created_at`字段可能是本地时间

### 3. 精度说明
- 价格精度：最多8位小数
- 成交量精度：最多2位小数

### 4. 数据完整性
- OKEx API限制：5分钟K线最多1440根（5天）
- 1小时K线最多240根（10天）
- 更早的数据需要通过历史数据API获取

---

## 🔗 相关文件

- **数据库文件**: `crypto_data.db`
- **导出脚本**: `export_kline_data.py`
- **导入脚本**: `import_real_ohlc_data.py`
- **实时采集器**: `okex_websocket_realtime_collector_fixed.py`

---

## 📞 技术支持

如有问题，请查看：
1. K线数据修复报告：`OHLC_FIX_VERIFICATION.md`
2. 新功能实现报告：`NEW_FEATURES_REPORT.md`
3. GitHub PR：https://github.com/jamesyidc/66661/pull/1

---

**文档版本**: v1.0  
**更新时间**: 2025-12-14  
**数据状态**: ✅ 完整可用
