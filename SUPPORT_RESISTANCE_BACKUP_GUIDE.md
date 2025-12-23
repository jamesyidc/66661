# 支撑压力线系统 - 数据备份与快速部署指南

## 📋 概述

支撑压力线系统的曲线图数据已经**完整保存在数据库中**，包括：

- ✅ **4条趋势曲线数据** (scenario_1_count ~ scenario_4_count)
- ✅ **时间轴数据** (snapshot_time，每3分钟一个点)
- ✅ **详细币种信息** (scenario_X_coins JSON格式)
- ✅ **历史数据** (从2025-12-14 08:00:00开始，共256条记录)

## 🗄️ 数据库表结构

### support_resistance_snapshots 表

```sql
CREATE TABLE support_resistance_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    snapshot_time TEXT NOT NULL,           -- 快照时间 (北京时间)
    snapshot_date TEXT NOT NULL,           -- 快照日期
    scenario_1_count INTEGER DEFAULT 0,    -- 情况1币种数 (接近支撑2)
    scenario_2_count INTEGER DEFAULT 0,    -- 情况2币种数 (接近支撑1)
    scenario_3_count INTEGER DEFAULT 0,    -- 情况3币种数 (接近压力2)
    scenario_4_count INTEGER DEFAULT 0,    -- 情况4币种数 (接近压力1)
    scenario_1_coins TEXT,                 -- 情况1币种详情 (JSON)
    scenario_2_coins TEXT,                 -- 情况2币种详情 (JSON)
    scenario_3_coins TEXT,                 -- 情况3币种详情 (JSON)
    scenario_4_coins TEXT,                 -- 情况4币种详情 (JSON)
    total_coins INTEGER DEFAULT 27,        -- 总监控币种数
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

### 示例数据

```json
{
  "snapshot_time": "2025-12-14 20:46:49",
  "scenario_1_count": 2,
  "scenario_2_count": 2,
  "scenario_3_count": 1,
  "scenario_4_count": 1,
  "scenario_1_coins": "[{\"symbol\":\"ETCUSDT\",\"current_price\":13.02,\"position\":4.99,\"support_2\":13.01,\"resistance_1\":13.21}]"
}
```

## 🔧 备份工具使用

### 1. 基本备份 (最近30天数据)

```bash
cd /home/user/webapp
python3 backup_support_resistance_data.py backup
```

**输出:**
- 文件: `backups/support_resistance_backup_30days_YYYYMMDD_HHMMSS.json.gz`
- 格式: 压缩JSON
- 包含: 所有快照数据、曲线图数据、详细币种信息

### 2. 备份指定天数

```bash
# 备份最近7天
python3 backup_support_resistance_data.py backup --days 7

# 备份最近60天
python3 backup_support_resistance_data.py backup --days 60
```

### 3. 不压缩备份 (方便查看)

```bash
python3 backup_support_resistance_data.py backup --no-compress
```

### 4. 列出所有备份文件

```bash
python3 backup_support_resistance_data.py list
```

**输出示例:**
```
📋 备份文件列表:
序号 | 文件名                                            | 大小        | 修改时间
------------------------------------------------------------------------------------------
   1 | support_resistance_backup_30days_20251214_204900.json.gz | 45.23KB | 2025-12-14 20:49:00
   2 | support_resistance_backup_7days_20251214_120000.json.gz  | 12.45KB | 2025-12-14 12:00:00
```

### 5. 导出CSV格式 (用于Excel分析)

```bash
# 导出最近7天数据
python3 backup_support_resistance_data.py export-csv --days 7
```

**输出:**
- 文件: `backups/support_resistance_export_7days_YYYYMMDD_HHMMSS.csv`
- 格式: UTF-8 BOM编码 (Excel直接打开无乱码)
- 内容: 时间、日期、4种情况的币种数

## 📥 数据恢复

### 1. 追加模式恢复 (不删除现有数据)

```bash
python3 backup_support_resistance_data.py restore --file backups/support_resistance_backup_30days_20251214_204900.json.gz
```

**特点:**
- 自动跳过重复的记录 (根据snapshot_time判断)
- 只插入新数据
- 适合日常恢复

### 2. 清空并恢复 (完全替换)

```bash
python3 backup_support_resistance_data.py restore --file backups/xxx.json.gz --clear
```

**警告:** 会删除所有现有数据，谨慎使用！

## 🚀 快速部署流程

### 场景1: 新服务器部署

```bash
# 1. 复制代码和数据库
scp -r /home/user/webapp user@new-server:/home/user/
cd /home/user/webapp

# 2. 安装依赖
pip3 install pytz

# 3. 启动采集器
python3 support_resistance_snapshot_collector.py &

# 4. 启动Flask应用
python3 app_new.py &

# 5. 访问页面
# https://your-domain/support-resistance
```

### 场景2: 数据丢失恢复

```bash
# 1. 列出备份文件
python3 backup_support_resistance_data.py list

# 2. 选择最新的备份文件进行恢复
python3 backup_support_resistance_data.py restore \
  --file backups/support_resistance_backup_30days_20251214_204900.json.gz

# 3. 验证数据
python3 << 'EOF'
import sqlite3
conn = sqlite3.connect('crypto_data.db')
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*), MIN(snapshot_time), MAX(snapshot_time) FROM support_resistance_snapshots")
print(cursor.fetchone())
conn.close()
EOF

# 4. 重启采集器
pkill -f support_resistance_snapshot_collector.py
python3 support_resistance_snapshot_collector.py &
```

### 场景3: 定时备份 (推荐)

```bash
# 添加到crontab
crontab -e

# 每天凌晨2点备份最近30天的数据
0 2 * * * cd /home/user/webapp && python3 backup_support_resistance_data.py backup --days 30 >> /home/user/webapp/backups/backup.log 2>&1

# 每周日凌晨3点备份最近90天的数据
0 3 * * 0 cd /home/user/webapp && python3 backup_support_resistance_data.py backup --days 90 >> /home/user/webapp/backups/backup.log 2>&1
```

## 📊 数据统计

### 当前数据量

```bash
python3 << 'EOF'
import sqlite3
conn = sqlite3.connect('crypto_data.db')
cursor = conn.cursor()

# 总记录数
cursor.execute("SELECT COUNT(*) FROM support_resistance_snapshots")
total = cursor.fetchone()[0]

# 时间范围
cursor.execute("SELECT MIN(snapshot_time), MAX(snapshot_time) FROM support_resistance_snapshots")
time_range = cursor.fetchone()

# 每日记录数 (每3分钟一条 = 每天480条)
cursor.execute("SELECT snapshot_date, COUNT(*) FROM support_resistance_snapshots GROUP BY snapshot_date")
daily_counts = cursor.fetchall()

print(f"📊 数据统计:")
print(f"  总记录数: {total}")
print(f"  时间范围: {time_range[0]} ~ {time_range[1]}")
print(f"  每日记录数:")
for date, count in daily_counts:
    print(f"    {date}: {count} 条")

conn.close()
EOF
```

## 🔍 数据验证

### 检查数据完整性

```bash
python3 << 'EOF'
import sqlite3
import json

conn = sqlite3.connect('crypto_data.db')
cursor = conn.cursor()

# 检查是否有NULL值
cursor.execute("""
    SELECT COUNT(*) 
    FROM support_resistance_snapshots 
    WHERE snapshot_time IS NULL 
       OR scenario_1_count IS NULL 
       OR scenario_2_count IS NULL
""")
null_count = cursor.fetchone()[0]

# 检查JSON格式
cursor.execute("""
    SELECT COUNT(*) 
    FROM support_resistance_snapshots
""")
total = cursor.fetchone()[0]

cursor.execute("SELECT scenario_1_coins FROM support_resistance_snapshots LIMIT 10")
json_valid = 0
for row in cursor.fetchall():
    try:
        json.loads(row[0])
        json_valid += 1
    except:
        pass

print(f"✅ 数据完整性检查:")
print(f"  总记录数: {total}")
print(f"  NULL值记录: {null_count}")
print(f"  JSON格式正确: {json_valid}/10 (抽样检查)")

conn.close()
EOF
```

## 📁 文件目录结构

```
/home/user/webapp/
├── crypto_data.db                                    # 主数据库
├── support_resistance_snapshot_collector.py          # 采集器
├── backup_support_resistance_data.py                 # 备份工具
├── app_new.py                                        # Flask应用
├── backups/                                          # 备份目录
│   ├── support_resistance_backup_30days_*.json.gz   # 压缩备份
│   ├── support_resistance_export_7days_*.csv        # CSV导出
│   └── backup.log                                    # 备份日志
└── templates/
    └── support_resistance.html                       # 前端页面
```

## ⚙️ API接口

### 获取最新数据

```bash
curl "http://localhost:5000/api/support-resistance/latest"
```

### 获取历史数据 (所有)

```bash
curl "http://localhost:5000/api/support-resistance/snapshots?all=true"
```

### 获取指定日期数据

```bash
curl "http://localhost:5000/api/support-resistance/snapshots?date=2025-12-14"
```

## 🎯 最佳实践

### 1. 定期备份
- **每日备份**: 保留最近30天数据
- **每周备份**: 保留最近90天数据
- **每月备份**: 保留所有历史数据

### 2. 备份存储
- 本地备份: `/home/user/webapp/backups/`
- 远程备份: 定期同步到云存储 (S3, 阿里云OSS等)
- 版本控制: Git LFS管理大文件

### 3. 数据保留策略
- **实时数据**: 数据库保留最近30天 (约14,400条记录)
- **历史数据**: 压缩备份保存，按需恢复
- **清理策略**: 自动删除30天前的数据 (可选)

### 4. 监控告警
```bash
# 检查最新数据时间
python3 << 'EOF'
import sqlite3
from datetime import datetime, timedelta
import pytz

conn = sqlite3.connect('crypto_data.db')
cursor = conn.cursor()
cursor.execute("SELECT MAX(snapshot_time) FROM support_resistance_snapshots")
latest_time = cursor.fetchone()[0]
conn.close()

beijing_tz = pytz.timezone('Asia/Shanghai')
now = datetime.now(beijing_tz)
latest = beijing_tz.localize(datetime.strptime(latest_time, '%Y-%m-%d %H:%M:%S'))
diff_minutes = (now - latest).total_seconds() / 60

if diff_minutes > 10:
    print(f"⚠️ 警告: 数据已经 {diff_minutes:.1f} 分钟未更新!")
else:
    print(f"✅ 正常: 最新数据是 {diff_minutes:.1f} 分钟前")
EOF
```

## 🆘 故障排查

### 问题1: 采集器停止运行

```bash
# 检查进程
ps aux | grep support_resistance_snapshot_collector.py

# 查看日志
tail -50 support_resistance_snapshot.log

# 重启采集器
pkill -f support_resistance_snapshot_collector.py
python3 support_resistance_snapshot_collector.py &
```

### 问题2: 数据不更新

```bash
# 检查数据库
python3 << 'EOF'
import sqlite3
conn = sqlite3.connect('crypto_data.db')
cursor = conn.cursor()
cursor.execute("SELECT MAX(snapshot_time) FROM support_resistance_snapshots")
print("Latest:", cursor.fetchone()[0])
conn.close()
EOF

# 检查API
curl "http://localhost:5000/api/support-resistance/latest" | jq '.update_time'
```

### 问题3: 备份文件损坏

```bash
# 验证压缩文件
gzip -t backups/support_resistance_backup_*.json.gz

# 查看备份内容 (不解压)
zcat backups/support_resistance_backup_*.json.gz | jq '.record_count'
```

## 📞 支持

如有问题，请检查:
1. 📄 日志文件: `support_resistance_snapshot.log`
2. 📊 数据库状态: SQLite查询
3. 🌐 API响应: curl测试
4. 💻 进程状态: `ps aux | grep support`

---

**最后更新**: 2025-12-14 20:50 Beijing Time  
**版本**: 1.0  
**状态**: ✅ 生产就绪
