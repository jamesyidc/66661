# 加密货币数据库使用指南

## 概述

系统使用SQLite数据库存储加密货币的历史数据，支持按日期+时间查询，方便进行历史数据分析。

## 数据库结构

### 1. crypto_snapshots（快照表）

存储每个时间点的统计数据快照。

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键，自增 |
| snapshot_time | TEXT | 快照时间 (YYYY-MM-DD HH:MM:SS) |
| snapshot_date | TEXT | 快照日期 (YYYY-MM-DD) |
| rush_up | INTEGER | 急涨总数 |
| rush_down | INTEGER | 急跌总数 |
| diff | INTEGER | 差值 (急涨-急跌) |
| count | INTEGER | 计次 |
| ratio | REAL | 比值 |
| status | TEXT | 状态 (如：震荡无序) |
| green_count | INTEGER | 绿色数量 |
| percentage | TEXT | 百分比 |
| filename | TEXT | 源文件名 |
| created_at | TIMESTAMP | 创建时间 |

**索引**: snapshot_time, snapshot_date

### 2. crypto_coin_data（币种数据表）

存储每个币种在每个时间点的详细数据。

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键，自增 |
| snapshot_id | INTEGER | 关联快照ID |
| snapshot_time | TEXT | 快照时间 |
| symbol | TEXT | 币种代码 (BTC, ETH等) |
| change | REAL | 涨幅 |
| rush_up | INTEGER | 急涨 |
| rush_down | INTEGER | 急跌 |
| update_time | TEXT | 更新时间 |
| high_price | REAL | 历史高价 |
| high_time | TEXT | 高价时间 |
| decline | REAL | 跌幅 |
| change_24h | REAL | 24小时变化 |
| rank | INTEGER | 排行 |
| current_price | REAL | 当前价格 |
| ratio1 | TEXT | 最高占比 |
| ratio2 | TEXT | 最低占比 |
| priority_level | TEXT | 优先级等级 (1-6或-) |
| created_at | TIMESTAMP | 创建时间 |

**索引**: snapshot_time, symbol

## API接口

### 1. 获取数据库统计

```bash
GET /api/database/stats
```

**响应示例**:
```json
{
  "success": true,
  "stats": {
    "total_snapshots": 4,
    "start_time": "2025-12-02 20:56:13",
    "end_time": "2025-12-02 21:02:17",
    "total_coins": 29,
    "total_records": 116
  }
}
```

### 2. 查询指定日期的所有快照

```bash
GET /api/database/snapshots/<date>
```

**示例**:
```bash
curl http://localhost:5001/api/database/snapshots/2025-12-02
```

**响应示例**:
```json
{
  "success": true,
  "date": "2025-12-02",
  "count": 4,
  "snapshots": [
    {
      "snapshot_time": "2025-12-02 20:56:13",
      "rush_up": 17,
      "rush_down": 4,
      "diff": 13,
      "count": 7
    },
    ...
  ]
}
```

### 3. 查询指定时间的快照详情

```bash
GET /api/database/snapshot/<snapshot_time>
```

**示例**:
```bash
curl http://localhost:5001/api/database/snapshot/2025-12-02%2020:56:13
```

**响应示例**:
```json
{
  "success": true,
  "snapshot": {
    "stats": {
      "rushUp": "17",
      "rushDown": "4",
      "diff": "13",
      "count": "7",
      ...
    },
    "data": [
      {
        "symbol": "BTC",
        "current_price": "86500.4",
        "ratio1": "69%",
        "priority_level": "6",
        ...
      },
      ...
    ]
  }
}
```

### 4. 查询币种历史数据

```bash
GET /api/database/coin/<symbol>
```

**示例**:
```bash
curl http://localhost:5001/api/database/coin/BTC
```

**响应示例**:
```json
{
  "success": true,
  "symbol": "BTC",
  "count": 4,
  "history": [
    {
      "snapshot_time": "2025-12-02 20:56:13",
      "current_price": 86500.4,
      "change": 0.2,
      "change_24h": 0.13,
      "ratio1": "69%",
      "ratio2": "106.32%",
      "priority_level": "6"
    },
    ...
  ]
}
```

## Python代码示例

### 1. 基本使用

```python
from crypto_database import CryptoDatabase

# 初始化数据库
db = CryptoDatabase('crypto_data.db')

# 获取统计信息
stats = db.get_statistics()
print(f"快照总数: {stats['total_snapshots']}")
```

### 2. 保存数据

```python
# 准备数据
data = [
    {
        'symbol': 'BTC',
        'currentPrice': 86500.4,
        'change': 0.2,
        'ratio1': '69%',
        'ratio2': '106.32%',
        'priorityLevel': '6',
        ...
    },
    ...
]

stats = {
    'rushUp': '17',
    'rushDown': '4',
    'diff': '13',
    'count': '7',
    ...
}

# 保存快照
snapshot_id = db.save_snapshot(
    data=data,
    stats=stats,
    snapshot_time='2025-12-02 20:56:13',
    filename='2025-12-02_2056.txt'
)
```

### 3. 查询数据

```python
# 查询某天的所有快照
snapshots = db.get_snapshots_by_date('2025-12-02')
for snap in snapshots:
    print(f"{snap['snapshot_time']}: 急涨={snap['rush_up']}")

# 查询特定时间的快照
snapshot = db.get_snapshot_by_time('2025-12-02 20:56:13')
if snapshot:
    print(f"币种数量: {len(snapshot['data'])}")

# 查询币种历史
history = db.get_coin_history('BTC', '2025-12-01', '2025-12-02')
for record in history:
    print(f"{record['snapshot_time']}: {record['current_price']}")
```

## 数据自动保存

系统已配置为自动保存：

1. **演示服务器**: 每次调用 `/api/crypto-data` 时自动保存
2. **真实服务器**: 每10分钟自动从Google Drive读取并保存

## 数据库维护

### 查看数据库文件

```bash
ls -lh crypto_data.db
```

### 备份数据库

```bash
cp crypto_data.db crypto_data_backup_$(date +%Y%m%d_%H%M%S).db
```

### 使用SQLite命令行工具

```bash
sqlite3 crypto_data.db

# 查询快照数量
SELECT COUNT(*) FROM crypto_snapshots;

# 查看最新快照
SELECT * FROM crypto_snapshots ORDER BY snapshot_time DESC LIMIT 1;

# 查询BTC历史价格
SELECT snapshot_time, current_price, ratio1 
FROM crypto_coin_data 
WHERE symbol = 'BTC' 
ORDER BY snapshot_time;
```

## 注意事项

1. **唯一约束**: 同一时间点只能有一个快照，重复保存会覆盖
2. **数据完整性**: snapshot_id关联确保数据一致性
3. **索引优化**: 已为常用查询创建索引，提高查询速度
4. **时间格式**: 统一使用 `YYYY-MM-DD HH:MM:SS` 格式
5. **数据类型**: 价格等数值保存为REAL，占比保存为TEXT（含%号）

## 未来扩展

可以基于现有数据库实现：

1. **趋势分析**: 分析币种价格走势
2. **优先级统计**: 统计各等级币种分布
3. **告警功能**: 价格变化超过阈值时告警
4. **数据导出**: 导出为CSV、Excel等格式
5. **图表展示**: 生成价格走势图、占比变化图等

---

**数据库文件位置**: `/home/user/webapp/crypto_data.db`
**版本**: v7.4
**更新日期**: 2025-12-02
