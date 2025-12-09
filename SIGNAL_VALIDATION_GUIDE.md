# 信号数据验证机制说明

## 📋 问题背景

在图表显示中发现，当系统从"有信号"状态突然变为"无信号"（做多=0，做空=0）时，可能是因为：

1. **数据未刷新完成**: API 正在更新数据，暂时返回空值
2. **真实无信号**: 市场确实没有信号产生

为了避免将"未刷新完成"的数据误存入数据库，导致图表出现异常的"断崖式下跌"，我们添加了数据验证机制。

---

## 🔍 验证逻辑

### 判断条件

```python
if 前一次总信号 > 0 and 新数据做多 == 0 and 新数据做空 == 0:
    # 判定为数据未刷新完成，拒绝保存
    return False
else:
    # 数据有效，正常保存
    return True
```

### 具体场景

| 前一次状态 | 新数据状态 | 判断结果 | 说明 |
|-----------|-----------|---------|------|
| 做多=138, 做空=35 | 做多=0, 做空=0 | ❌ 拒绝 | 可能未刷新完成 |
| 做多=138, 做空=35 | 做多=140, 做空=33 | ✅ 通过 | 正常数据变化 |
| 做多=138, 做空=35 | 做多=100, 做空=0 | ✅ 通过 | 有部分信号 |
| 做多=0, 做空=0 | 做多=0, 做空=0 | ✅ 通过 | 连续无信号（首次记录） |

---

## 🔄 重试机制

当数据验证失败时，系统会自动重试：

### 重试参数

```python
max_retries = 3        # 最大重试次数
retry_delay = 10       # 重试间隔（秒）
```

### 重试流程

```
第1次采集 → 数据无效 → 等待10秒 → 第2次采集 → 数据无效 → 等待10秒 → 第3次采集
```

### 日志示例

```
2025-12-06 21:30:00 - WARNING - ⚠️  数据验证失败: 前一次有信号(做多=138, 做空=35), 但新数据全为0
2025-12-06 21:30:00 - WARNING -    上次记录时间: 2025-12-06 21:27:00
2025-12-06 21:30:00 - WARNING -    判断: 数据未刷新完成，拒绝保存
2025-12-06 21:30:00 - INFO - 🔄 第 1 次采集数据无效，等待 10 秒后重试...
2025-12-06 21:30:10 - INFO - ✅ 信号采集成功: 做多=138, 做空=35, 总计=173
2025-12-06 21:30:10 - INFO - 💾 数据保存成功: 2025-12-06 21:30:10
2025-12-06 21:30:10 - INFO - ✅ 数据采集并保存成功（第 2 次尝试）
```

---

## 📊 代码实现

### 1. 获取最后一条记录

```python
def get_last_signal(self):
    """获取最后一条信号记录"""
    cursor.execute('''
        SELECT long_signals, short_signals, total_signals, record_time
        FROM trading_signals 
        ORDER BY id DESC 
        LIMIT 1
    ''')
    
    row = cursor.fetchone()
    if row:
        return {
            'long_signals': row[0],
            'short_signals': row[1],
            'total_signals': row[2],
            'record_time': row[3]
        }
    return None
```

### 2. 验证数据有效性

```python
def validate_signal_data(self, signal_data):
    """验证信号数据是否有效"""
    last_signal = self.get_last_signal()
    
    # 如果没有历史记录，直接返回有效
    if not last_signal:
        return True
    
    # 检查是否为"未刷新"的异常数据
    new_long = signal_data['long_signals']
    new_short = signal_data['short_signals']
    last_total = last_signal['total_signals']
    
    # 如果上一次有信号，但新数据全为0，判定为未刷新
    if last_total > 0 and new_long == 0 and new_short == 0:
        logging.warning(f"⚠️  数据验证失败: 前一次有信号，但新数据全为0")
        return False
    
    return True
```

### 3. 带重试的采集方法

```python
def collect_once(self, max_retries=3, retry_delay=10):
    """执行一次采集，失败时自动重试"""
    for attempt in range(max_retries):
        signal_data = self.fetch_signals()
        
        if not signal_data:
            # API 请求失败
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            continue
        
        # 尝试保存（会自动验证）
        if self.save_signal(signal_data):
            logging.info(f"✅ 数据采集并保存成功（第 {attempt + 1} 次尝试）")
            return True
        else:
            # 数据验证失败
            if attempt < max_retries - 1:
                logging.info(f"🔄 第 {attempt + 1} 次采集数据无效，等待 {retry_delay} 秒后重试...")
                time.sleep(retry_delay)
    
    return False
```

---

## 🧪 测试验证

### 运行测试脚本

```bash
cd /home/user/webapp
python3 test_signal_validation.py
```

### 测试输出示例

```
============================================================
测试信号数据验证逻辑
============================================================

📊 最后一条记录:
   时间: 2025-12-06 21:33:51
   做多: 138
   做空: 35
   总计: 173

============================================================
场景1: 新数据有信号（应该通过验证）
============================================================
验证结果: ✅ 通过

============================================================
场景2: 新数据全为0（如果上次有信号，应该拒绝）
============================================================
验证结果: ❌ 拒绝
✅ 正确！检测到数据未刷新，拒绝保存
```

---

## 📈 图表效果对比

### 修复前（无验证）

```
信号数量
   ↑
130|     ┌─────┬─────┬─────┐
   |     │     │     │     │
   |     │     │     │     │
 90|─────┤     │     │     │
   |     │     │     │     │
 30|     └─────┴─────┴─────┘
   |                    ↓ 突然归零（未刷新数据）
  0|────────────────────×────→ 时间
```

### 修复后（有验证）

```
信号数量
   ↑
130|     ┌─────┬─────┬─────┬─────┐
   |     │     │     │     │     │
   |     │     │     │     │     │
 90|─────┤     │     │     │     │
   |     │     │     │     │     │
 30|     └─────┴─────┴─────┴─────┘
   |                              （平滑过渡）
  0|────────────────────────────────→ 时间
```

---

## ⚙️ 配置参数

可以在 `signal_collector.py` 中修改以下参数：

```python
# collect_once 方法参数
max_retries = 3        # 最大重试次数（1-10）
retry_delay = 10       # 重试间隔秒数（5-60）

# 调用示例
collector.collect_once(max_retries=5, retry_delay=15)
```

### 参数建议

| 场景 | max_retries | retry_delay | 说明 |
|-----|-------------|-------------|------|
| **标准配置** | 3 | 10 | 默认配置，适合大多数情况 |
| **快速响应** | 2 | 5 | 减少等待时间，但可能遗漏数据 |
| **稳定优先** | 5 | 15 | 增加重试次数和间隔，确保数据完整 |

---

## 🔧 故障排查

### 问题1: 数据持续无法保存

**现象**: 日志显示持续验证失败

```
⚠️  数据验证失败: 前一次有信号，但新数据全为0
❌ 已达到最大重试次数 (3)，本轮采集失败
```

**可能原因**:
1. API 服务异常
2. 数据源真的没有信号了
3. 重试次数/间隔不够

**解决方案**:
```bash
# 1. 手动测试 API
curl "https://8080-xxx.sandbox.novita.ai/api/filtered-signals/stats?limit=200"

# 2. 增加重试次数（修改代码）
collector.collect_once(max_retries=5, retry_delay=15)

# 3. 查看详细日志
tail -f /home/user/webapp/signal_collector.log
```

### 问题2: 图表仍出现断崖

**现象**: 即使启用验证，图表仍有异常下跌

**排查步骤**:
```bash
# 1. 检查数据库记录
python3 << 'EOF'
import sqlite3
conn = sqlite3.connect('crypto_data.db')
cursor = conn.cursor()
cursor.execute("""
    SELECT record_time, long_signals, short_signals, total_signals
    FROM trading_signals 
    ORDER BY id DESC LIMIT 20
""")
for row in cursor.fetchall():
    print(f"{row[0]}: 做多={row[1]}, 做空={row[2]}, 总计={row[3]}")
EOF

# 2. 检查采集器是否运行
./signal_control.sh status

# 3. 查看采集器日志
./signal_control.sh logs
```

---

## 📝 最佳实践

### 1. 监控采集状态

定期检查采集器运行状态：

```bash
# 每小时检查一次
0 * * * * cd /home/user/webapp && ./signal_control.sh status > /tmp/signal_status.log
```

### 2. 数据质量检查

定期验证数据连续性：

```bash
python3 << 'EOF'
import sqlite3
from datetime import datetime, timedelta

conn = sqlite3.connect('crypto_data.db')
cursor = conn.cursor()

# 检查最近1小时的数据
cursor.execute("""
    SELECT COUNT(*) 
    FROM trading_signals 
    WHERE datetime(record_time) > datetime('now', '-1 hour')
""")

count = cursor.fetchone()[0]
expected = 20  # 1小时 / 3分钟 = 20条

if count < expected * 0.8:  # 少于80%
    print(f"⚠️  警告: 最近1小时只采集到 {count} 条数据（预期 {expected} 条）")
else:
    print(f"✅ 数据正常: 最近1小时采集了 {count} 条数据")
EOF
```

### 3. 日志管理

定期清理日志文件：

```bash
# 备份并清理日志（每周）
cd /home/user/webapp
cp signal_collector.log signal_collector.log.$(date +%Y%m%d)
> signal_collector.log
```

---

## 🎯 总结

### 核心价值

✅ **防止异常数据入库**: 避免"未刷新"数据污染图表  
✅ **自动重试机制**: 智能等待数据刷新完成  
✅ **详细日志记录**: 便于问题排查和监控  
✅ **无缝集成**: 不影响现有采集流程  

### 适用场景

- ✅ API 数据更新有延迟
- ✅ 需要保证图表数据连续性
- ✅ 对数据质量要求高
- ✅ 需要自动化容错机制

### 注意事项

⚠️ 首次运行时（数据库无记录）不会触发验证  
⚠️ 连续多次"无信号"状态会正常保存  
⚠️ 重试会延长单次采集时间（最多30秒）  

---

**最后更新**: 2025-12-06  
**版本**: v1.0  
**相关文件**: `signal_collector.py`, `test_signal_validation.py`
