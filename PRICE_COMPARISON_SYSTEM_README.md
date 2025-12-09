# 🎯 加密货币比价系统

## 概述

比价系统是一个自动跟踪和统计加密货币价格创新高低的工具，可以帮助您：
- 维护每个币种的历史最高价和最低价基准
- 自动检测并记录创新高/创新低事件
- 统计每日、3日、7日的创新高低次数
- 计算当前价格与历史高低价的占比

## 功能特性

### 1. 价格基准管理
- **最高价格追踪**：记录每个币种的历史最高价格
- **最低价格追踪**：记录每个币种的历史最低价格
- **计次统计**：统计价格在高低区间徘徊的次数
- **占比计算**：
  - 最高占比 = 当前价格 / 最高价格 × 100%
  - 最低占比 = 当前价格 / 最低价格 × 100%

### 2. 自动比价逻辑

每次数据更新时，系统会自动执行比价：

#### 创新高场景
- **条件**：当前价格 > 历史最高价
- **动作**：
  - 更新最高价为当前价格
  - 最高价计次重置为0
  - 记录创新高事件（币种、旧价格、新价格、时间）
  - 更新每日统计（创新高次数+1）

#### 高位计次场景
- **条件**：最低价格 <= 当前价格 <= 最高价格
- **动作**：
  - 最高价计次+1
  - 更新最高/最低占比

#### 创新低场景
- **条件**：当前价格 < 历史最低价
- **动作**：
  - 更新最低价为当前价格
  - 最低价计次重置为0
  - 记录创新低事件（币种、旧价格、新价格、时间）
  - 更新每日统计（创新低次数+1）

#### 低位计次场景
- **条件**：当前价格 < 最低价格（但不创新低）
- **动作**：
  - 最低价计次+1
  - 更新最高/最低占比

### 3. 统计汇总

#### 每日统计
- 每个币种的当日创新高次数
- 每个币种的当日创新低次数
- 汇总：全部币种的总创新高/低次数

#### 3日统计
- 每个币种过去3天的创新高次数
- 每个币种过去3天的创新低次数
- 汇总：全部币种的总创新高/低次数

#### 7日统计
- 每个币种过去7天的创新高次数
- 每个币种过去7天的创新低次数
- 汇总：全部币种的总创新高/低次数

## 数据库结构

### 1. price_baseline（价格基准表）
```sql
CREATE TABLE price_baseline (
    symbol TEXT PRIMARY KEY,           -- 币种名称
    highest_price REAL NOT NULL,       -- 最高价格
    highest_count INTEGER DEFAULT 0,   -- 最高价计次
    lowest_price REAL NOT NULL,        -- 最低价格
    lowest_count INTEGER DEFAULT 0,    -- 最低价计次
    last_price REAL,                   -- 最新价格
    highest_ratio REAL,                -- 最高占比
    lowest_ratio REAL,                 -- 最低占比
    last_update_time TIMESTAMP,        -- 最后更新时间
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

### 2. daily_price_records（每日创新高低记录表）
```sql
CREATE TABLE daily_price_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL,              -- 币种名称
    record_date DATE NOT NULL,         -- 记录日期
    record_type TEXT NOT NULL,         -- 记录类型：new_high 或 new_low
    old_price REAL,                    -- 旧价格
    new_price REAL,                    -- 新价格
    record_time TIMESTAMP,             -- 记录时间
    UNIQUE(symbol, record_date, record_type, record_time)
)
```

### 3. daily_statistics（每日统计汇总表）
```sql
CREATE TABLE daily_statistics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL,              -- 币种名称
    record_date DATE NOT NULL,         -- 记录日期
    new_high_count INTEGER DEFAULT 0,  -- 创新高次数
    new_low_count INTEGER DEFAULT 0,   -- 创新低次数
    UNIQUE(symbol, record_date)
)
```

## API接口

### 1. GET /price-comparison
- **说明**：比价系统Web界面
- **返回**：HTML页面

### 2. GET /api/price-comparison/report
- **说明**：获取完整比价报告
- **返回**：
```json
{
    "baseline": [...],          // 价格基准数据
    "today_records": {          // 今日记录
        "date": "2025-12-03",
        "new_highs": [...],     // 创新高列表
        "new_lows": [...],      // 创新低列表
        "new_high_count": 5,
        "new_low_count": 3
    },
    "statistics": [...],        // 统计数据
    "total": {                  // 汇总统计
        "day1_high_total": 5,
        "day1_low_total": 3,
        "day3_high_total": 15,
        "day3_low_total": 10,
        "day7_high_total": 30,
        "day7_low_total": 25
    },
    "generated_at": "2025-12-03 20:50:00"
}
```

### 3. GET /api/price-comparison/baseline
- **说明**：获取价格基准数据
- **返回**：
```json
{
    "success": true,
    "data": [
        {
            "symbol": "BTC",
            "highest_price": 125370.20986,
            "highest_count": 2833,
            "lowest_price": 81359.05775,
            "lowest_count": 738,
            "last_price": 92401.66197,
            "highest_ratio": 73.69,
            "lowest_ratio": 113.55,
            "last_update_time": "2025-12-03 20:25:46"
        },
        ...
    ]
}
```

### 4. GET /api/price-comparison/today
- **说明**：获取今日创新高低记录
- **返回**：
```json
{
    "success": true,
    "data": {
        "date": "2025-12-03",
        "new_highs": [
            {
                "symbol": "BTC",
                "old_price": 125000.0,
                "new_price": 126000.0,
                "record_time": "2025-12-03 15:30:15"
            }
        ],
        "new_lows": [...],
        "new_high_count": 5,
        "new_low_count": 3
    }
}
```

## 使用说明

### 1. 初始化数据
```bash
# 导入基准数据（只需执行一次）
python3 import_baseline_data.py
```

### 2. 启动服务
```bash
# 服务会自动启动，比价系统已集成到主服务中
python3 home_data_api_v2.py
```

### 3. 访问界面
- 比价系统：https://5003-ivx1gqv2svtq7f2kvor6q-b32ec7bb.sandbox.novita.ai/price-comparison
- 实时监控：https://5003-ivx1gqv2svtq7f2kvor6q-b32ec7bb.sandbox.novita.ai/live
- 历史数据：https://5003-ivx1gqv2svtq7f2kvor6q-b32ec7bb.sandbox.novita.ai/history

### 4. 自动更新
- 系统每3分钟自动更新一次数据
- 每次更新后自动触发比价检查
- 前端页面每3分钟自动刷新一次

## 初始数据

系统已导入29个币种的基准数据：

| 币种 | 最高价格 | 最高计次 | 最低价格 | 最低计次 |
|------|----------|----------|----------|----------|
| BTC | 125370.21 | 2833 | 81359.06 | 738 |
| ETH | 4830.00 | 7531 | 2642.00 | 738 |
| BNB | 1377.48 | 2297 | 796.78 | 738 |
| SOL | 253.36 | 4367 | 122.88 | 738 |
| XRP | 3.19 | 5121 | 1.84 | 738 |
| ... | ... | ... | ... | ... |

完整的币种列表：
BTC, ETH, BNB, SOL, XRP, ADA, DOGE, TRX, TON, LINK, DOT, BCH, LTC, UNI, XLM, AAVE, FIL, HBAR, SUI, NEAR, ETC, APT, STX, CRO, LDO, CRV, TAO, CFX, OKB

## 技术栈

- **后端**：Python 3, Flask
- **数据库**：SQLite3
- **前端**：HTML5, CSS3, JavaScript (原生)
- **集成**：home_data_api_v2.py

## 文件结构

```
/home/user/webapp/
├── price_comparison_system.py      # 比价系统核心逻辑
├── import_baseline_data.py         # 基准数据导入脚本
├── price_comparison.html           # Web界面
├── home_data_api_v2.py            # 主服务（已集成比价系统）
└── crypto_data.db                 # SQLite数据库
```

## 更新日志

### V1.0 (2025-12-03)
- ✅ 创建比价系统数据库表结构
- ✅ 实现价格基准管理
- ✅ 实现自动比价逻辑
- ✅ 实现每日创新高低统计
- ✅ 实现3日/7日统计汇总
- ✅ 创建Web界面
- ✅ 集成到主服务
- ✅ 导入29个币种的基准数据

## 注意事项

1. **时区**：所有时间均为北京时间（UTC+8）
2. **精度**：价格保留8位小数
3. **更新频率**：每3分钟更新一次
4. **数据持久化**：所有数据保存在SQLite数据库中
5. **自动触发**：比价检查在每次数据更新后自动执行

## 未来优化

1. 添加价格预警功能（接近历史高低价时发送通知）
2. 添加历史趋势图表
3. 添加导出功能（Excel/CSV）
4. 添加自定义统计周期
5. 添加多维度分析（振幅、波动率等）

---

**开发时间**：2025-12-03
**版本**：V1.0
**状态**：✅ 已部署运行
