# 开仓逻辑评分系统问题报告

## 📋 问题概述

用户报告了3个问题：
1. **实心星星显示错误**: 明明是5颗实心星星，但页面显示为"+3"
2. **24h涨跌幅数据为0**: "24h涨>10%: 0" 和 "24h跌<-10%: 0"，但实际有16个涨幅≥10%和17个跌幅≤-10%
3. **中趋势限制条件数据来源**: 需要确认数据来源

## 🔍 问题分析

### 问题1: 实心星星显示错误

#### 现状
```sql
-- 当前数据库记录
时间: 2025-12-12 11:36:00
count: 3
count_score_display: ★★  (只有2颗星)
count_score_type: 实心
```

#### 根本原因
查看 `calculate_count_score.py` 第43-58行的计算逻辑：
```python
elif hour < 12:  # 6-12点前（截止12点前）
    # 实心星（表现好）
    if 3 < count <= 4:
        return "★", "实心"
    elif 2 < count <= 3:
        return "★★", "实心"  # ← count=3 返回2颗星
    elif count <= 2:
        return "★★★", "实心"  # ← count≤2 返回3颗星
```

**问题**: 
- count=3 时，符合条件 `2 < count <= 3`，返回 `★★` (2颗星)
- 但用户期望 count=3 应该显示 `★★★` (3颗星)

#### 为什么用户看到5颗星

查看 `opening_logic.py` 第206-216行的**评分计算逻辑**：
```python
# 1. 星星差值判断
star_diff = solid - hollow
if star_diff >= 10:
    score += 5
    details.append({'factor': '实心星星优势', 'level': '很强做多', 'score': 5, 'value': f'+{star_diff}'})
elif star_diff >= 5:
    score += 2
    details.append({'factor': '实心星星优势', 'level': '较强做多', 'score': 2, 'value': f'+{star_diff}'})
elif star_diff >= 3:
    score += 1
    details.append({'factor': '实心星星优势', 'level': '一般做多', 'score': 1, 'value': f'+{star_diff}'})
```

当前实际情况：
- solid_stars = 3 (3个实心星星)
- hollow_stars = 0 (0个空心星星)
- star_diff = 3 - 0 = 3
- 符合条件 `star_diff >= 3`，所以得分是 `+1 分`，等级是 "一般做多"

**用户混淆点**:
- 用户看到的"5颗实心星星"可能是指其他地方的显示
- 开仓逻辑页面显示的是**星星差值得分** (+1, +2, +5)，不是星星数量 (★★)

### 问题2: 24h涨跌幅数据为0

#### 现状
```sql
-- crypto_snapshots表记录
rise_24h_count: 0
fall_24h_count: 0

-- 但crypto_coin_data表统计
24h涨幅≥10%: 16 个币种
24h跌幅≤-10%: 17 个币种
```

#### 根本原因
查看 `gdrive_final_detector.py` 第390-407行：
```python
cursor.execute("""
    INSERT INTO crypto_snapshots 
    (snapshot_time, snapshot_date, rush_up, rush_down, diff, count, status, count_score_display, count_score_type, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now', '+8 hours'))
""", (
    data['snapshot_time'],
    data['snapshot_date'],
    data['rush_up'],
    data['rush_down'],
    data['diff'],
    data['count'],
    data['status'],
    data['count_score_display'],
    data['count_score_type'],
    data['created_at']
))
```

**问题**: INSERT语句**没有包含** `rise_24h_count` 和 `fall_24h_count` 字段！

### 问题3: 中趋势限制条件数据来源

#### 数据来源确认

**24h涨跌幅数据** (`rise_24h_count`, `fall_24h_count`):
- **设计来源**: `opening_logic.py` 的 `get_extreme_change_count()` 函数
- **查询表**: `crypto_coin_data`
- **查询条件**: 
  - `change_24h >= 10` (涨幅≥10%)
  - `change_24h <= -10` (跌幅≤-10%)
- **当前状态**: crypto_coin_data表有正确数据，但crypto_snapshots表未更新

**星星数据** (`solid_stars`, `hollow_stars`):
- **来源**: `crypto_snapshots` 表的 `count` 和 `count_score_type` 字段
- **计算方式**: 
  - 如果 `count_score_type` 包含 "实心" → solid_stars = count
  - 如果 `count_score_type` 包含 "空心" → hollow_stars = count
- **当前状态**: 数据正确，但显示星星数量的逻辑有误

## 🔧 修复方案

### 修复1: 统一星星显示逻辑

**选项A: 修改calculate_count_score.py**
让 count=3 显示3颗星：
```python
elif hour < 12:  # 6-12点前（截止12点前）
    # 实心星（表现好）
    if 3 < count <= 4:
        return "★", "实心"
    elif 2 < count < 3:  # 修改：2 < count < 3
        return "★★", "实心"
    elif count <= 3:  # 修改：count <= 3
        return "★★★", "实心"
```

**选项B: 修改opening_logic页面显示**
明确告知用户显示的是"星星差值得分"，不是星星数量。

**推荐**: 选项A - 让count值直接对应星星数量更直观

### 修复2: 添加24h涨跌幅统计到gdrive_final_detector.py

**步骤1**: 在数据提取时计算24h极端涨跌
```python
def calculate_extreme_changes():
    """计算24h极端涨跌数量"""
    import sqlite3
    
    conn = sqlite3.connect('crypto_data.db')
    cursor = conn.cursor()
    
    # 24h涨≥10%
    cursor.execute("SELECT COUNT(*) FROM crypto_coin_data WHERE change_24h >= 10")
    rise_count = cursor.fetchone()[0] or 0
    
    # 24h跌≤-10%
    cursor.execute("SELECT COUNT(*) FROM crypto_coin_data WHERE change_24h <= -10")
    fall_count = cursor.fetchone()[0] or 0
    
    conn.close()
    return rise_count, fall_count
```

**步骤2**: 在INSERT语句中包含这些字段
```python
rise_24h, fall_24h = calculate_extreme_changes()

cursor.execute("""
    INSERT INTO crypto_snapshots 
    (snapshot_time, snapshot_date, rush_up, rush_down, diff, count, status, 
     count_score_display, count_score_type, rise_24h_count, fall_24h_count, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now', '+8 hours'))
""", (
    data['snapshot_time'],
    data['snapshot_date'],
    data['rush_up'],
    data['rush_down'],
    data['diff'],
    data['count'],
    data['status'],
    data['count_score_display'],
    data['count_score_type'],
    rise_24h,  # 新增
    fall_24h,  # 新增
    data['created_at']
))
```

### 修复3: 更新历史数据

创建脚本回填历史数据的24h涨跌幅统计：
```python
# backfill_24h_counts.py
import sqlite3
from datetime import datetime

conn = sqlite3.connect('crypto_data.db')
cursor = conn.cursor()

# 获取所有需要更新的记录
cursor.execute("""
    SELECT id FROM crypto_snapshots 
    WHERE rise_24h_count IS NULL OR fall_24h_count IS NULL
""")

records = cursor.fetchall()
for (record_id,) in records:
    # 从crypto_coin_data获取统计
    cursor.execute("SELECT COUNT(*) FROM crypto_coin_data WHERE change_24h >= 10")
    rise_count = cursor.fetchone()[0] or 0
    
    cursor.execute("SELECT COUNT(*) FROM crypto_coin_data WHERE change_24h <= -10")
    fall_count = cursor.fetchone()[0] or 0
    
    # 更新记录
    cursor.execute("""
        UPDATE crypto_snapshots 
        SET rise_24h_count = ?, fall_24h_count = ?
        WHERE id = ?
    """, (rise_count, fall_count, record_id))

conn.commit()
conn.close()
```

## 📊 修复结果预期

### 修复后的数据
```
实心星星数量: 3 ← count值
星星显示: ★★★ ← 3颗星
星星差值: 3 - 0 = 3 ← solid - hollow
趋势得分: +1 分 ← "一般做多"

24h涨≥10%: 16 个币种 ← 实时统计
24h跌≤-10%: 17 个币种 ← 实时统计
```

### 页面显示改善
```
当前趋势得分: +8

📊 得分构成详情
┌──────────────┐
│ 实心星星优势 │
│  一般做多    │
│  当前: +3    │
│   +1 分      │
└──────────────┘

┌──────────────┐
│  BTC涨幅     │
│  很强做多    │
│  当前: 3.18% │
│   +5 分      │
└──────────────┘

┌──────────────┐
│  ETH涨幅     │
│  较强做多    │
│  当前: 2.24% │
│   +2 分      │
└──────────────┘

⚠️ 中趋势限制条件
- 24h涨≥10%币种数: 16 ← 正确显示
- 24h跌≤-10%币种数: 17 ← 正确显示
```

## 📁 需要修改的文件

1. **calculate_count_score.py** - 修改星星显示逻辑
2. **gdrive_final_detector.py** - 添加24h涨跌幅统计
3. **backfill_24h_counts.py** (新建) - 回填历史数据

## ✅ 验证步骤

1. 修改代码后重启gdrive-monitor
2. 等待下一次数据采集
3. 查询数据库验证:
   ```sql
   SELECT count, count_score_display, rise_24h_count, fall_24h_count
   FROM crypto_snapshots
   ORDER BY snapshot_time DESC
   LIMIT 5;
   ```
4. 访问开仓逻辑页面确认显示正确

---

**报告生成时间**: 2025-12-12 11:45 (北京时间)  
**问题优先级**: 高 (影响用户决策)  
**修复复杂度**: 中等 (需要修改多个文件)
