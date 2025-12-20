# 📍 数据写入位置说明

## 🎯 您的问题："你最新的数据写入在哪里？"

### ✅ 简短回答

**数据库文件**: `/home/user/webapp/crypto_data.db`  
**表名**: `support_resistance_snapshots`  
**采集器**: `support_resistance_snapshot_collector.py`  
**PM2服务名**: `support-resistance-snapshot-collector`

---

## 📊 数据采集流程

### 1. 采集器脚本

**文件位置**: `/home/user/webapp/support_resistance_snapshot_collector.py`  
**文件大小**: 9.8 KB  
**最后修改**: 2025-12-12 15:47

**采集频率**: 每 **3分钟** 一次

### 2. PM2 服务状态

```bash
# 服务名称
support-resistance-snapshot-collector

# 运行状态
Status: ✅ Online
Uptime: 2小时+
Restarts: 0次（稳定运行）
Memory: 13.4 MB
```

### 3. 数据写入位置

#### 数据库文件
```bash
路径: /home/user/webapp/crypto_data.db
类型: SQLite3 数据库
权限: -rw-r--r--
```

#### 数据表结构
```sql
CREATE TABLE support_resistance_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    snapshot_time TEXT NOT NULL,           -- UTC时间: 2025-12-12 17:49:21
    snapshot_date TEXT NOT NULL,           -- UTC日期: 2025-12-12
    scenario_1_count INTEGER DEFAULT 0,    -- 情况1数量
    scenario_2_count INTEGER DEFAULT 0,    -- 情况2数量
    scenario_3_count INTEGER DEFAULT 0,    -- 情况3数量
    scenario_4_count INTEGER DEFAULT 0,    -- 情况4数量
    scenario_1_coins TEXT,                 -- 情况1币种列表(JSON)
    scenario_2_coins TEXT,                 -- 情况2币种列表(JSON)
    scenario_3_coins TEXT,                 -- 情况3币种列表(JSON)
    scenario_4_coins TEXT,                 -- 情况4币种列表(JSON)
    total_coins INTEGER DEFAULT 27,        -- 总币种数
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

### 4. 最新数据记录

**截至**: 2025-12-13 03:50 (北京时间) / 2025-12-12 19:50 (UTC)

```
📊 最新的5条快照记录:
  2025-12-12 17:49:21 (date: 2025-12-12) | 总数: 2
  2025-12-12 17:46:21 (date: 2025-12-12) | 总数: 2
  2025-12-12 17:43:21 (date: 2025-12-12) | 总数: 0
  2025-12-12 17:40:21 (date: 2025-12-12) | 总数: 0
  2025-12-12 17:37:21 (date: 2025-12-12) | 总数: 0

📅 各日期数据统计:
  2025-12-12: 362 条记录
```

---

## 📝 采集器日志

### 日志文件位置

**主日志**: `/home/user/webapp/support_resistance_snapshot.log`  
**错误日志**: `/home/user/webapp/logs/support-resistance-snapshot-error-11.log`  
**输出日志**: `/home/user/webapp/logs/support-resistance-snapshot-out-11.log`

### 最新日志内容

```log
[2025-12-12 17:49:21] ============================================================
[2025-12-12 17:49:21] 📸 开始采集支撑压力线快照
[2025-12-12 17:49:21] 📊 获取到 27 个币种的最新数据
[2025-12-12 17:49:21] 📈 情况1（接近支撑2）: 1 个币种
[2025-12-12 17:49:21] 📈 情况2（接近支撑1）: 1 个币种
[2025-12-12 17:49:21] 📉 情况3（接近压力2）: 0 个币种
[2025-12-12 17:49:21] 📉 情况4（接近压力1）: 0 个币种
[2025-12-12 17:49:21] ✅ 快照保存成功: 2025-12-12 17:49:21 | 情况1:1 情况2:1 情况3:0 情况4:0
[2025-12-12 17:49:21] ============================================================
[2025-12-12 17:49:21] ⏳ 等待3分钟后进行下一次采集...
```

---

## 🔄 数据采集工作流程

```
每3分钟执行一次:
    ↓
1. 从 support_resistance_levels 表读取最新数据
    ↓
2. 计算每个币种是否符合4种情况:
   • 情况1: 接近支撑线2（position_s2_r1 <= 5%）
   • 情况2: 接近支撑线1（position_s1_r2 <= 5%）
   • 情况3: 接近压力线2（position_s1_r2_upper <= 5%）
   • 情况4: 接近压力线1（position_s1_r1 <= 5%）
    ↓
3. 统计各情况的币种数量和列表
    ↓
4. 写入 support_resistance_snapshots 表
    ↓
5. 记录日志
    ↓
6. 等待3分钟，继续下一次循环
```

---

## 📍 文件路径速查

| 项目 | 路径 |
|-----|------|
| **采集器脚本** | `/home/user/webapp/support_resistance_snapshot_collector.py` |
| **数据库文件** | `/home/user/webapp/crypto_data.db` |
| **主日志** | `/home/user/webapp/support_resistance_snapshot.log` |
| **错误日志** | `/home/user/webapp/logs/support-resistance-snapshot-error-11.log` |
| **PM2配置** | PM2服务: `support-resistance-snapshot-collector` (ID: 11) |

---

## 🔧 管理命令

### 查看实时日志
```bash
# 主日志
tail -f /home/user/webapp/support_resistance_snapshot.log

# PM2日志
pm2 logs support-resistance-snapshot-collector

# PM2错误日志
pm2 logs support-resistance-snapshot-collector --err
```

### 查看服务状态
```bash
# 详细状态
pm2 describe support-resistance-snapshot-collector

# 简要状态
pm2 list | grep snapshot
```

### 重启采集器
```bash
pm2 restart support-resistance-snapshot-collector
```

### 查看数据库记录
```bash
cd /home/user/webapp
python3 << 'EOF'
import sqlite3
conn = sqlite3.connect('crypto_data.db')
cursor = conn.cursor()

# 查看最新10条记录
cursor.execute('''
    SELECT snapshot_time, 
           scenario_1_count, scenario_2_count, 
           scenario_3_count, scenario_4_count
    FROM support_resistance_snapshots
    ORDER BY id DESC
    LIMIT 10
''')

print("最新10条记录:")
for row in cursor.fetchall():
    print(f"  {row[0]}: 情况1={row[1]} 情况2={row[2]} 情况3={row[3]} 情况4={row[4]}")

conn.close()
EOF
```

---

## 📊 数据统计

### 当前数据量

| 日期 | 记录数 | 时间跨度 |
|-----|--------|---------|
| 2025-12-12 | 362条 | 00:00 - 17:49 (UTC) |
| 2025-12-13 | 0条 | 等待08:00后记录 |

**备注**: `snapshot_date` 字段使用UTC日期，北京时间00:00-08:00的数据会被记录到前一天。

### 采集间隔

- **设计间隔**: 3分钟
- **实际间隔**: ~3分钟（稳定）
- **每小时**: ~20条记录
- **每天**: ~480条记录（理论值）

---

## 🚨 注意事项

### 时区问题

⚠️ **snapshot_date 使用UTC日期**，这导致：

```
北京时间: 2025-12-13 01:00
UTC时间: 2025-12-12 17:00
snapshot_date: "2025-12-12"  ← 使用UTC日期

结果: 12-13凌晨的数据被记录为12-12
```

### 数据查询

**API查询** `/api/support-resistance/snapshots`:
- 使用 `start_hour` 和 `end_hour` 参数（北京时间）
- API会自动转换为UTC时间查询数据库
- 返回的 `snapshot_time` 已转换为北京时间

---

## 📈 数据可视化

**前端页面**: https://5000-xxx.sandbox.novita.ai/support-resistance

**显示方式**:
- 12小时分页显示
- X轴: 北京时间
- Y轴: 各情况币种数量
- 可点击数据点查看详细币种列表

---

**文档生成时间**: 2025-12-13 03:50 (北京时间)  
**数据库最新记录**: 2025-12-12 17:49:21 (UTC) = 2025-12-13 01:49:21 (北京)  
**采集器状态**: ✅ 运行正常
