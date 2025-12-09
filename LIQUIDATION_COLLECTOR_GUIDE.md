# 爆仓金额自动采集器使用指南

## 📋 功能概述

自动采集1小时和24小时爆仓金额数据，每3分钟更新一次，使用北京时间（UTC+8）。

---

## 🚀 快速启动

### 启动采集器
```bash
cd /home/user/webapp
./liquidation_amount_control.sh start
```

### 查看状态
```bash
./liquidation_amount_control.sh status
```

### 查看实时日志
```bash
./liquidation_amount_control.sh logs
```

### 停止采集器
```bash
./liquidation_amount_control.sh stop
```

---

## 📖 命令详解

| 命令 | 说明 |
|------|------|
| `./liquidation_amount_control.sh start` | 启动采集器（后台运行） |
| `./liquidation_amount_control.sh stop` | 停止采集器 |
| `./liquidation_amount_control.sh restart` | 重启采集器 |
| `./liquidation_amount_control.sh status` | 查看运行状态和最近日志 |
| `./liquidation_amount_control.sh logs` | 实时查看日志（Ctrl+C退出） |
| `./liquidation_amount_control.sh test` | 测试运行（单次采集） |

---

## 🔧 技术细节

### 数据源

#### 1小时爆仓 API
```
https://api.btc123.fans/bicoin.php?from=1hbaocang
```
- 返回字段: `totalBlastCny`
- **单位**: 万元 (CNY)
- 转换公式: `万元 × 10000 ÷ 7 ÷ 100000000 = 亿美元`

#### 24小时爆仓 API
```
https://api.btc123.fans/bicoin.php?from=24hbaocang
```
- 返回字段: `totalBlastCny`
- **单位**: 元 (CNY)（注意：不是万元！）
- 转换公式: `元 ÷ 7 ÷ 100000000 = 亿美元`

### 数据存储

**数据库表**: `panic_wash_index`

**更新字段**:
- `hour_1_amount`: 1小时爆仓金额（亿美元）
- `hour_24_amount`: 24小时爆仓金额（亿美元）
- `record_time`: 更新时间（北京时间）

### 显示格式

**前端展示**:
- 1小时爆仓: 显示为 **"万美元"** (例: $56,163.71万)
- 24小时爆仓: 显示为 **"亿美元"** (例: $1.29亿)

**API 返回**:
```json
{
  "hour_1_amount": 56163.71,  // 万美元
  "hour_24_amount": 1.29       // 亿美元
}
```

---

## ⏱️ 运行机制

### 采集周期
- **间隔**: 每3分钟
- **时区**: 北京时间 (UTC+8)
- **运行方式**: 后台守护进程

### 日志输出
- **日志文件**: `liquidation_amount_collector.log`
- **日志级别**: INFO
- **包含信息**:
  - 采集时间（北京时间）
  - API 返回的原始数据
  - 转换后的美元金额
  - 数据库更新状态

### 示例日志
```
2025-12-06 13:27:31,404 - INFO - ============================================================
2025-12-06 13:27:31,404 - INFO - 开始采集数据 - 2025-12-06 21:27:31 (北京时间)
2025-12-06 13:27:31,404 - INFO - ============================================================
2025-12-06 13:27:32,239 - INFO - ✅ 1小时爆仓: 393,146万元 = $5.6164亿 = $56163.71万
2025-12-06 13:27:39,291 - INFO - ✅ 24小时爆仓: 906,041,498元 = $1.29亿
2025-12-06 13:27:39,294 - INFO - ✅ 数据库已更新 (ID: 28)
2025-12-06 13:27:39,294 - INFO -    1小时: $56163.71万 ($5.6164亿)
2025-12-06 13:27:39,294 - INFO -    24小时: $1.29亿
2025-12-06 13:27:39,294 - INFO - ✅ 本轮采集完成
2025-12-06 13:27:39,294 - INFO - ⏳ 等待3分钟后进行下一次采集...
```

---

## 🛠️ 故障排查

### 采集器无法启动

1. **检查PID文件**:
```bash
cat liquidation_amount_collector.pid
ps -p $(cat liquidation_amount_collector.pid)
```

2. **清理旧进程**:
```bash
./liquidation_amount_control.sh stop
./liquidation_amount_control.sh start
```

3. **查看错误日志**:
```bash
tail -50 liquidation_amount_collector.log
```

### API 返回失败

**可能原因**:
- 网络连接问题
- API 限流
- API 数据格式变化

**解决方案**:
```bash
# 测试单次采集
./liquidation_amount_control.sh test

# 手动测试 API
curl -s "https://api.btc123.fans/bicoin.php?from=1hbaocang" | python3 -m json.tool
```

### 数据库更新失败

**检查数据库**:
```bash
python3 << 'EOF'
import sqlite3
conn = sqlite3.connect('crypto_data.db')
cursor = conn.cursor()
cursor.execute("SELECT * FROM panic_wash_index ORDER BY id DESC LIMIT 1")
print(cursor.fetchone())
conn.close()
EOF
```

---

## 📊 监控和维护

### 查看当前数据
```bash
python3 << 'EOF'
import sqlite3
conn = sqlite3.connect('crypto_data.db')
cursor = conn.cursor()
cursor.execute("""
    SELECT record_time, hour_1_amount, hour_24_amount 
    FROM panic_wash_index 
    ORDER BY id DESC LIMIT 1
""")
row = cursor.fetchone()
if row:
    print(f"时间: {row[0]}")
    print(f"1小时: ${row[1]*10000:.2f}万")
    print(f"24小时: ${row[2]:.2f}亿")
conn.close()
EOF
```

### 定期检查
建议每天检查采集器运行状态：
```bash
./liquidation_amount_control.sh status
```

### 日志清理
如果日志文件过大，可定期备份清理：
```bash
# 备份日志
cp liquidation_amount_collector.log liquidation_amount_collector.log.backup

# 清空当前日志
> liquidation_amount_collector.log

# 或重启采集器（会创建新日志）
./liquidation_amount_control.sh restart
```

---

## 🔄 系统集成

### 与 Panic Wash Collector 的关系

本采集器与 `panic_wash_collector.py` 是**互补关系**：

| 采集器 | 功能 | 更新内容 |
|--------|------|---------|
| **panic_wash_collector** | 采集恐慌指数 | `panic_index`, `hour_24_people`, `total_position` |
| **liquidation_amount_collector** | 采集爆仓金额 | `hour_1_amount`, `hour_24_amount` |

两个采集器都更新同一张表 `panic_wash_index`，但更新不同的字段。

### 推荐配置

1. **同时运行两个采集器**:
```bash
# 启动恐慌指数采集器
./panic_wash_control.sh start

# 启动爆仓金额采集器
./liquidation_amount_control.sh start
```

2. **查看所有采集器状态**:
```bash
echo "=== 恐慌指数采集器 ==="
./panic_wash_control.sh status

echo -e "\n=== 爆仓金额采集器 ==="
./liquidation_amount_control.sh status
```

---

## ⚙️ 配置说明

### 采集器配置

**文件**: `liquidation_amount_collector.py`

可修改的配置项：
```python
# 采集间隔（秒）
INTERVAL = 180  # 3分钟

# 数据库路径
self.db_path = 'crypto_data.db'

# 汇率
EXCHANGE_RATE = 7  # 1 USD = 7 CNY
```

### 重启生效
修改配置后需要重启采集器：
```bash
./liquidation_amount_control.sh restart
```

---

## 📝 注意事项

1. **API 单位差异**:
   - 1小时 API: 返回"万元"
   - 24小时 API: 返回"元"
   - 必须使用不同的转换公式！

2. **时区**:
   - 所有时间使用北京时间 (UTC+8)
   - 数据库中的 `record_time` 也是北京时间

3. **汇率**:
   - 当前使用固定汇率 1 USD = 7 CNY
   - 可根据需要修改代码中的汇率

4. **数据更新策略**:
   - 采集器只更新最新的一条记录
   - 如果需要保留历史记录，需修改 `update_database` 方法

---

## 🎯 常见用例

### 1. 系统启动时自动启动采集器

创建启动脚本 `start_all_collectors.sh`:
```bash
#!/bin/bash
cd /home/user/webapp

# 启动恐慌指数采集器
./panic_wash_control.sh start

# 启动爆仓金额采集器
./liquidation_amount_control.sh start

echo "✅ 所有采集器已启动"
```

### 2. 定时检查并自动重启

使用 cron job:
```bash
# 每小时检查一次，如果未运行则启动
0 * * * * cd /home/user/webapp && ./liquidation_amount_control.sh start
```

### 3. 手动测试数据采集

不启动后台进程，只测试一次：
```bash
./liquidation_amount_control.sh test
```

---

## 📞 技术支持

如有问题，请查看：
1. 日志文件: `liquidation_amount_collector.log`
2. PID 文件: `liquidation_amount_collector.pid`
3. 数据库: `crypto_data.db` (表: `panic_wash_index`)

---

**最后更新**: 2025-12-06  
**版本**: v1.0  
**作者**: GenSpark AI Developer
