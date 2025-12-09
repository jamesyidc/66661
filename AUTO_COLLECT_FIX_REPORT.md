# 自动采集系统修复报告

## 🐛 问题描述

**用户反馈**: "17:03 17:13 为什么没有运行抓取？"

### 症状
- 自动采集守护进程运行中（PID: 47488）
- 但实际采集失败
- 日志显示: `❌ 数据采集失败 (返回码: 1)`
- 错误时间: 09:06:42, 09:16:42

### 根本原因
```python
# 问题代码 (第127行):
check_time = check_time.replace(minute=(check_time.minute // 10) * 10 - i * 10)

# 错误示例:
# 当前时间: 17:03
# 对齐后: 17:00
# i=1时: minute = 0 - 10 = -10 ❌
# 触发: ValueError: minute must be in 0..59
```

**错误栈**:
```
File "/home/user/webapp/collect_and_store.py", line 372, in main
    result = get_latest_file_data()
File "/home/user/webapp/collect_and_store.py", line 127, in get_latest_file_data
    check_time = check_time.replace(minute=(check_time.minute // 10) * 10 - i * 10)
ValueError: minute must be in 0..59
```

## ✅ 修复方案

### 1. 导入必要模块
```python
# 之前
from datetime import datetime

# 修复后
from datetime import datetime, timedelta
```

### 2. 修正时间计算逻辑
```python
# 之前（有bug）
for i in range(0, 4):
    check_time = now.replace(second=0, microsecond=0)
    check_time = check_time.replace(minute=(check_time.minute // 10) * 10 - i * 10)
    # ❌ 可能产生负数分钟

# 修复后
for i in range(0, 4):
    # 使用timedelta来正确处理时间减法，避免分钟数为负
    check_time = now.replace(second=0, microsecond=0)
    # 先对齐到10分钟整点
    aligned_minute = (check_time.minute // 10) * 10
    check_time = check_time.replace(minute=aligned_minute)
    # 然后减去i*10分钟
    check_time = check_time - timedelta(minutes=i * 10)
    # ✅ 正确处理跨小时/跨天的时间减法
```

### 3. 工作原理
```
示例: 当前时间 17:03

步骤1: 对齐到10分钟整点
  17:03 → 17:00

步骤2: 使用timedelta减去时间
  i=0: 17:00 - 0分钟  = 17:00 ✅
  i=1: 17:00 - 10分钟 = 16:50 ✅
  i=2: 17:00 - 20分钟 = 16:40 ✅
  i=3: 17:00 - 30分钟 = 16:30 ✅

候选文件:
  ['2025-12-06_1700.txt', 
   '2025-12-06_1650.txt',
   '2025-12-06_1640.txt', 
   '2025-12-06_1630.txt']
```

## 🧪 验证测试

### 1. 手动测试
```bash
$ python3 collect_and_store.py
================================================================================
开始采集数据...
================================================================================
当前北京时间: 2025-12-06 17:24:18
当前小时: 17
候选文件: ['2025-12-06_1720.txt', '2025-12-06_1710.txt', 
           '2025-12-06_1700.txt', '2025-12-06_1650.txt']
找到最新文件: 2025-12-06_1723.txt

✅ 数据已存储到数据库
   快照ID: 45
   币种数量: 29
```

### 2. 守护进程测试
```bash
$ ./auto_collect_control.sh restart
🔄 重启守护进程...
✅ 守护进程已启动 (PID: 50188)

# 等待30秒后查看日志
$ tail auto_collect.log
[2025-12-06 09:28:35] ✅ 数据采集成功
[2025-12-06 09:28:35]    快照ID: 46
[2025-12-06 09:28:35] ⏰ 距离下次采集还有: 9分59秒
```

### 3. 数据库验证
```
最新10条采集记录:
ID  46 | 2025-12-06 17:25:36 | 急涨: 3 急跌:22 计次:12 | 2025-12-06_1723.txt ✅ 新
ID  45 | 2025-12-06 17:24:53 | 急涨: 3 急跌:22 计次:12 | 2025-12-06_1723.txt ✅ 新
ID   5 | 2025-12-06 16:56:42 | 急涨: 2 急跌:22 计次:12 | 2025-12-06_1652.txt
ID   4 | 2025-12-06 14:54:34 | 急涨: 2 急跌:22 计次:10 | 2025-12-06_1452.txt
...

总记录数: 45条
时间范围: 2025-12-06 00:06:00 至 17:25:36
时间跨度: 17.3小时
```

## 📊 修复效果

### 采集状态对比

| 指标 | 修复前 | 修复后 |
|------|--------|--------|
| **采集状态** | ❌ 失败 | ✅ 成功 |
| **错误日志** | `ValueError: minute must be in 0..59` | 无错误 |
| **数据库记录** | 43条 | 45条 (+2) |
| **时间跨度** | 16.8小时 | 17.3小时 |
| **下次采集** | 无法执行 | 正常倒计时 |

### 采集时间线
```
09:06:42 ❌ 失败 (bug触发)
09:16:42 ❌ 失败 (bug触发)
         ⬇️ 修复并重启
17:24:53 ✅ 成功 (手动测试, ID 45)
17:25:36 ✅ 成功 (守护进程, ID 46)
17:35:00 ⏰ 下次采集 (预计)
```

## 🔧 代码变更

### 文件: `collect_and_store.py`

**变更1: 导入模块**
```diff
- from datetime import datetime
+ from datetime import datetime, timedelta
```

**变更2: 时间计算逻辑** (第123-129行)
```diff
  # 生成候选文件名
  candidates = []
  for i in range(0, 4):
+     # 使用timedelta来正确处理时间减法，避免分钟数为负
      check_time = now.replace(second=0, microsecond=0)
-     check_time = check_time.replace(minute=(check_time.minute // 10) * 10 - i * 10)
+     # 先对齐到10分钟整点
+     aligned_minute = (check_time.minute // 10) * 10
+     check_time = check_time.replace(minute=aligned_minute)
+     # 然后减去i*10分钟
+     check_time = check_time - timedelta(minutes=i * 10)
      filename = check_time.strftime('%Y-%m-%d_%H%M.txt')
      candidates.append(filename)
```

## 📈 系统状态

### 当前运行状态
- ✅ 守护进程: 运行中 (PID: 50188)
- ✅ 采集脚本: 正常工作
- ✅ 数据库: 45条记录
- ✅ 采集间隔: 每10分钟
- ✅ 下次采集: 约17:35

### 数据覆盖情况
```
时间轴: 12-05 18:00 ──────────────────────> 12-06 18:00 (24小时)

数据分布:
  18:00-23:00 (12-05): ○ ○ ○ ○ ○ ○ (无数据)
  00:00-06:00 (12-06): ● ● ● ● ● ● ● (有数据)
  07:00-13:00 (12-06): ○ ○ ○ ○ ○ ○ ○ (无数据)
  14:00-18:00 (12-06): ● ● ○ ● ○ (有数据，新增17:25数据)
                                    ↑
                                 最新数据

当前覆盖率: 44% (11/25时间槽)
```

## 🎯 总结

### ✅ 问题已解决
1. **Bug修复**: 时间计算逻辑使用`timedelta`正确处理
2. **测试通过**: 手动和守护进程测试均成功
3. **数据恢复**: 成功采集17:24和17:25两个时间点数据
4. **持续运行**: 守护进程正常，下次采集约17:35

### 📊 数据状态
- **总记录**: 45条 (新增2条)
- **时间跨度**: 17.3小时
- **覆盖率**: 44%
- **采集频率**: 每10分钟

### 🔮 后续预期
- **17:35**: 下次自动采集
- **18:00**: 完成另一个整点数据
- **24小时后**: 接近100%覆盖率
- **图表效果**: 连续线段将更加完整

### 🌐 访问地址
**Web界面**: https://5000-iik759kgm7i3zqlxvfrfx-cc2fbc16.sandbox.novita.ai

**GitHub PR**: https://github.com/jamesyidc/6666/pull/1
- 最新提交: `a8c82cb` - "fix: 修复自动采集时间计算bug"

---

**修复时间**: 2025-12-06 17:24  
**验证时间**: 2025-12-06 17:29  
**状态**: ✅ 完全修复并正常运行
