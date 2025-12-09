# 加密货币数据查询和图表生成指南

## 功能概述

本系统提供以下核心功能：

1. **按日期+时间查询历史数据** - 简单直接，无需设置开始/结束时间
2. **生成4指标曲线图** - 急涨、急跌、差值、计次
3. **自动计算优先级等级** - 基于最高占比和最低占比

---

## 1. 数据采集和存储

### 使用 `collect_and_store.py` 采集数据

```bash
# 运行数据采集脚本
python3 collect_and_store.py
```

**功能：**
- 自动从Google Drive获取最新数据文件
- 解析所有币种数据
- 计算每个币种的优先级等级
- 将数据存储到SQLite数据库
- 显示采集结果和优先级统计

**输出示例：**
```
文件名            : 2025-12-06_1341.txt
采集时间           : 2025-12-06 13:42:42
急涨             : 1
急跌             : 22
差值             : -21
计次             : 10
计次得分_显示        : ☆☆☆
24h涨幅>=10%     : 0
24h跌幅<=-10%    : 0

优先级统计:
  等级2: 1 个币种
  等级6: 28 个币种
```

---

## 2. 历史数据查询

### 按日期+时间查询单个时间点

```bash
# 格式1: 使用空格和冒号
python3 query_history.py '2025-12-06 13:30'

# 格式2: 使用下划线和4位数字
python3 query_history.py '2025-12-06_1330'

# 格式3: 只要日期和小时也可以
python3 query_history.py '2025-12-06 13'
```

**输出内容：**
- 时间戳
- 文件名
- 急涨、急跌、差值、计次数据
- 比值和市场状态
- 所有币种详细数据（带优先级）

**输出示例：**
```
================================================================================
查询时间: 2025-12-06 13:42
================================================================================

找到数据:
  时间: 2025-12-06 13:42:42
  文件: 2025-12-06_1341.txt
  急涨: 1
  急跌: 22
  差值: -21
  计次: 10
  比值: 21.0
  状态: 震荡无序

币种数据 (共 29 个):
  序号 币种             涨幅      24h涨幅       最高占比       最低占比      优先级
--------------------------------------------------------------------------------
   1 BTC        -0.03%     -2.62%     71.14%    109.63%      等级6
   2 ETH         0.00%     -3.75%     62.62%    114.48%      等级6
  12 BCH        -0.01%     -0.13%     87.29%    126.19%      等级2
  ...
```

---

## 3. 生成曲线图

### 生成指定时间范围的图表

```bash
# 生成从开始时间到现在的图表
python3 query_history.py chart '2025-12-06 10:00'

# 生成指定时间范围的图表
python3 query_history.py chart '2025-12-06 10:00' '2025-12-06 14:00'

# 生成整天的图表
python3 query_history.py chart '2025-12-06 00:00' '2025-12-06 23:59'
```

**图表包含的4个指标：**
1. **急涨** (红色实线) - 急涨币种数量
2. **急跌** (绿色实线) - 急跌币种数量  
3. **差值** (蓝色实线) - 急涨-急跌的差值
4. **计次** (紫色虚线) - 市场波动计次（使用右侧Y轴）

**输出：**
- 自动生成PNG图片文件，格式：`chart_YYYYMMDD_HHMMSS.png`
- 图表包含时间轴、双Y轴、图例、网格线

---

## 4. 优先级等级计算规则

系统会自动根据每个币种的**最高占比**和**最低占比**计算优先级：

### 等级规则（按优先级排序）

| 等级 | 最高占比条件 | 最低占比条件 | 说明 |
|------|------------|------------|------|
| **等级1** | > 90% | > 120% | 最高优先级 |
| **等级2** | > 80% | > 120% | 高优先级 |
| **等级3** | > 90% | > 110% | 中高优先级 |
| **等级4** | > 70% | > 120% | 中等优先级 |
| **等级5** | > 80% | > 110% | 中低优先级 |
| **等级6** | < 80% | < 110% | 低优先级 |

### 优先级含义

- **等级1-3**: 优质币种，最高占比高且最低占比也高，表示价格稳定在高位
- **等级4-5**: 中等币种，具有一定潜力
- **等级6**: 普通币种，占比较低

---

## 5. 数据库结构

### crypto_snapshots 表（快照数据）

存储每次采集的整体市场数据：
- snapshot_time: 快照时间
- rush_up: 急涨数量
- rush_down: 急跌数量
- diff: 差值
- count: 计次
- ratio: 比值
- status: 市场状态

### crypto_coin_data 表（币种数据）

存储每个币种的详细数据：
- symbol: 币种符号
- change: 涨幅
- change_24h: 24小时涨幅
- ratio1: 最高占比
- ratio2: 最低占比
- priority_level: 优先级等级（自动计算）
- high_price: 最高价格
- current_price: 当前价格

---

## 6. 使用场景示例

### 场景1: 实时数据采集和查询

```bash
# 1. 采集最新数据
python3 collect_and_store.py

# 2. 查询刚才采集的数据
python3 query_history.py '2025-12-06 13:42'
```

### 场景2: 查看历史趋势

```bash
# 查询早上的数据
python3 query_history.py '2025-12-06 09:00'

# 查询中午的数据
python3 query_history.py '2025-12-06 12:00'

# 查询下午的数据
python3 query_history.py '2025-12-06 15:00'
```

### 场景3: 生成日报图表

```bash
# 生成今天的完整图表
python3 query_history.py chart '2025-12-06 00:00' '2025-12-06 23:59'

# 生成最近12小时的图表
python3 query_history.py chart '2025-12-06 02:00'
```

### 场景4: 查找优先级高的币种

```bash
# 查询某个时间点，系统会自动显示各币种的优先级
python3 query_history.py '2025-12-06 13:42'

# 输出中会显示：
# BCH: 等级2 (87.29%, 126.19%)
# BTC: 等级6 (71.14%, 109.63%)
```

---

## 7. 高级用法

### 使用Python直接查询

```python
import sqlite3

# 连接数据库
conn = sqlite3.connect('crypto_data.db')
cursor = conn.cursor()

# 查询所有等级1的币种
cursor.execute("""
    SELECT symbol, ratio1, ratio2, change_24h
    FROM crypto_coin_data
    WHERE priority_level = '等级1'
    ORDER BY snapshot_time DESC
""")

results = cursor.fetchall()
for row in results:
    print(f"{row[0]}: 最高占比={row[1]}, 最低占比={row[2]}, 24h涨幅={row[3]}%")

conn.close()
```

### 导出数据到CSV

```python
import sqlite3
import csv

conn = sqlite3.connect('crypto_data.db')
cursor = conn.cursor()

# 查询数据
cursor.execute("""
    SELECT snapshot_time, symbol, change, change_24h, ratio1, ratio2, priority_level
    FROM crypto_coin_data
    ORDER BY snapshot_time DESC
""")

# 导出到CSV
with open('crypto_export.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['时间', '币种', '涨幅', '24h涨幅', '最高占比', '最低占比', '优先级'])
    writer.writerows(cursor.fetchall())

conn.close()
print("数据已导出到 crypto_export.csv")
```

---

## 8. 常见问题

### Q: 如何查询最新的数据？

A: 先运行 `collect_and_store.py` 采集数据，然后使用当前时间查询：
```bash
python3 collect_and_store.py
python3 query_history.py '2025-12-06 13:45'
```

### Q: 图表为什么只有2个点？

A: 因为数据库中只有2条数据。需要定期运行 `collect_and_store.py` 采集更多数据点，才能生成更详细的趋势图。

### Q: 如何设置自动采集？

A: 使用cron定时任务，每10分钟采集一次：
```bash
# 编辑crontab
crontab -e

# 添加以下行（每10分钟运行一次）
*/10 * * * * cd /home/user/webapp && python3 collect_and_store.py >> collect.log 2>&1
```

### Q: 优先级是如何计算的？

A: 系统根据**最高占比(ratio1)**和**最低占比(ratio2)**自动计算。等级1最好（最高占比>90%, 最低占比>120%），等级6最普通。

---

## 9. 文件说明

### 主要脚本

1. **collect_and_store.py** - 数据采集和存储脚本
   - 从Google Drive获取最新文件
   - 解析数据并存储到数据库
   - 计算优先级等级
   - 显示统计信息

2. **query_history.py** - 历史数据查询和图表生成脚本
   - 按日期+时间查询历史数据
   - 显示币种详细信息和优先级
   - 生成4指标曲线图

3. **collect_with_score.py** - 原始采集脚本（只显示不存储）
   - 快速查看最新数据
   - 不写入数据库

### 数据库文件

- **crypto_data.db** - SQLite数据库
  - crypto_snapshots: 快照表
  - crypto_coin_data: 币种详细数据表

### 其他文件

- **test_count_score.py** - 计次得分测试脚本
- **chart_*.png** - 生成的图表文件

---

## 10. 系统要求

- Python 3.7+
- 依赖包:
  - playwright
  - pytz
  - matplotlib
  - sqlite3 (内置)

---

## 总结

本系统提供了简单直观的方式来：
1. ✅ 按日期+时间查询历史数据（不需要设置开始结束时间）
2. ✅ 生成包含急涨、急跌、差值、计次的4条曲线图
3. ✅ 自动计算每个币种的优先级等级（基于最高占比和最低占比）

所有功能都已实现并测试通过！
