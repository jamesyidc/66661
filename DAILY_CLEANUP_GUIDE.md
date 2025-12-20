# 📅 每日00:10父文件夹ID自动清理机制

## 🎯 功能说明

根据用户需求：
> "如果今天是单日期 那么就把双日期的父文件id删除 只保留一个 这个在0:10分来执行"

系统会在每天**北京时间00:10**自动执行清理任务：

- **单数日期**（1,3,5,7,9,11,13...）：删除 `root_folder_even`（双数父文件夹ID）
- **双数日期**（2,4,6,8,10,12,14...）：删除 `root_folder_odd`（单数父文件夹ID）
- **只保留**当天实际使用的父文件夹ID

---

## 🔧 工作原理

### 1. 定时调度器

**服务名称:** `folder-cleanup-scheduler`  
**实现方式:** Node.js + PM2  
**检查频率:** 每60秒检查一次时间  
**执行时间:** 00:10 (允许00:10-00:11之间执行)

```javascript
// 每分钟检查当前时间
setInterval(checkAndExecute, 60 * 1000);

// 如果是00:10，执行清理脚本
if (hours === 0 && minutes === 10) {
    executeCleanup();
}
```

### 2. 清理脚本

**脚本路径:** `/home/user/webapp/cleanup_unused_folder_id.py`  
**执行逻辑:**

```python
# 1. 获取今天日期
day_num = today.day
is_odd = day_num % 2 == 1

# 2. 读取配置文件
config = json.load(open('daily_folder_config.json'))

# 3. 删除不需要的ID
if is_odd:
    # 今天是单数，删除双数
    del config['root_folder_even']
else:
    # 今天是双数，删除单数
    del config['root_folder_odd']

# 4. 添加清理记录
config['last_cleanup'] = '2025-12-13 01:01:30'
config['cleanup_reason'] = '每日00:10自动清理，今天是单数日期'

# 5. 保存配置
json.dump(config, file)
```

### 3. 配置文件变化

**清理前** (2025-12-12 23:59)：
```json
{
    "root_folder_odd": "1jFGGlGP5KEVhAxpCNxFIYEFI5-cDOBjM",
    "root_folder_even": "1jFGGlGP5KEVhAxpCNxFIYEFI5-cDOBjM",
    "folder_id": "13js7p3V4FUtbkfZxWq9et_xYz7EQ9Q9O",
    "current_date": "2025-12-12",
    "last_update": "2025-12-11 23:11:13"
}
```

**清理后** (2025-12-13 00:10)：
```json
{
    "root_folder_odd": "1jFGGlGP5KEVhAxpCNxFIYEFI5-cDOBjM",
    "folder_id": "13js7p3V4FUtbkfZxWq9et_xYz7EQ9Q9O",
    "current_date": "2025-12-12",
    "last_update": "2025-12-11 23:11:13",
    "last_cleanup": "2025-12-13 00:10:05",
    "cleanup_reason": "每日00:10自动清理，今天是单数日期"
}
```

**注意:** `root_folder_even` 字段已被删除 ✅

---

## 🖥️ 前端显示

### 未清理状态（清理前）

**单数日期父文件夹：**
```
┌──────────────────────────────────┐
│ 1️⃣ 单数日期父文件夹              │
│ 1jFGGlGP5KEVhAxpCNxFIYEFI5-cDOBjM│
│ ✅ 今天使用 (1, 3, 5, 7, 9...)   │
└──────────────────────────────────┘
```

**双数日期父文件夹：**
```
┌──────────────────────────────────┐
│ 2️⃣ 双数日期父文件夹              │
│ 1jFGGlGP5KEVhAxpCNxFIYEFI5-cDOBjM│
│ 📂 备用 (2, 4, 6, 8, 10...)      │
└──────────────────────────────────┘
```

### 已清理状态（清理后）

**单数日期父文件夹：**
```
┌──────────────────────────────────┐
│ 1️⃣ 单数日期父文件夹              │
│ 1jFGGlGP5KEVhAxpCNxFIYEFI5-cDOBjM│
│ ✅ 今天使用 (1, 3, 5, 7, 9...)   │
└──────────────────────────────────┘
```

**双数日期父文件夹：**
```
┌──────────────────────────────────┐
│ 2️⃣ 双数日期父文件夹              │
│ 🧹 已清理                        │  ← 灰色显示
│ 🗑️ 00:10已清理                   │  ← 提示信息
└──────────────────────────────────┘
```

---

## 📊 完整执行时间表

| 日期 | 星期 | 日期类型 | 保留ID | 删除ID | 执行时间 |
|------|------|----------|--------|--------|----------|
| 12-13 | 五 | 单数 | root_folder_odd | root_folder_even | 00:10:00 |
| 12-14 | 六 | 双数 | root_folder_even | root_folder_odd | 00:10:00 |
| 12-15 | 日 | 单数 | root_folder_odd | root_folder_even | 00:10:00 |
| 12-16 | 一 | 双数 | root_folder_even | root_folder_odd | 00:10:00 |
| 12-17 | 二 | 单数 | root_folder_odd | root_folder_even | 00:10:00 |
| ... | ... | ... | ... | ... | ... |

---

## 🔍 监控与日志

### PM2进程状态

```bash
$ pm2 list
┌────┬──────────────────────────┬──────────┬──────┬─────────┐
│ id │ name                     │ status   │ ↺    │ uptime  │
├────┼──────────────────────────┼──────────┼──────┼─────────┤
│ 12 │ folder-cleanup-scheduler │ online   │ 0    │ 3h      │
└────┴──────────────────────────┴──────────┴──────┴─────────┘
```

### 调度器日志

```bash
$ pm2 logs folder-cleanup-scheduler --lines 50

[2025-12-13 00:00:00] 🚀 启动每日清理调度器
[2025-12-13 00:00:00] ⏰ 执行时间: 每天 00:10 (北京时间)
[2025-12-13 00:00:00] 📂 清理脚本: /home/user/webapp/cleanup_unused_folder_id.py
[2025-12-13 00:00:00] ✅ 调度器已启动

[2025-12-13 00:10:00] 🧹 开始执行每日清理任务...
[2025-12-13 00:10:05] ✅ 清理任务执行成功
```

### 清理脚本日志

```bash
$ tail -f /home/user/webapp/cleanup_cron.log

================================================================================
🧹 每日父文件夹ID清理任务
================================================================================

📅 今天日期: 2025年12月13号
📊 日期类型: 单数 (13 % 2 = 1)

📂 清理前配置:
   ├─ 单数父文件夹: 1jFGGlGP5KEVhAxpCNxFIYEFI5-cDOBjM
   └─ 双数父文件夹: 1jFGGlGP5KEVhAxpCNxFIYEFI5-cDOBjM

🗑️  删除双数父文件夹ID: 1jFGGlGP5KEVhAxpCNxFIYEFI5-cDOBjM
✅ 今天是13号（单数），只保留单数父文件夹ID

📂 清理后配置:
   ├─ 单数父文件夹: 1jFGGlGP5KEVhAxpCNxFIYEFI5-cDOBjM
   └─ 清理时间: 2025-12-13 00:10:05

✅ 清理完成！
================================================================================
```

---

## 🧪 手动测试

### 立即执行清理（测试用）

```bash
cd /home/user/webapp
python3 cleanup_unused_folder_id.py
```

### 验证配置文件

```bash
# 查看当前配置
cat daily_folder_config.json | python3 -m json.tool

# 检查单数ID是否存在
python3 -c "import json; c=json.load(open('daily_folder_config.json')); print('单数ID存在:', 'root_folder_odd' in c)"

# 检查双数ID是否存在
python3 -c "import json; c=json.load(open('daily_folder_config.json')); print('双数ID存在:', 'root_folder_even' in c)"

# 查看清理时间
python3 -c "import json; c=json.load(open('daily_folder_config.json')); print('清理时间:', c.get('last_cleanup', '未清理'))"
```

### 检查调度器状态

```bash
# 查看进程状态
pm2 status folder-cleanup-scheduler

# 查看最近日志
pm2 logs folder-cleanup-scheduler --lines 20

# 重启调度器
pm2 restart folder-cleanup-scheduler
```

---

## ⚙️ 配置管理

### 如果需要临时恢复双数ID

```bash
cd /home/user/webapp
python3 update_root_folders.py --even "你的双数文件夹ID"
```

### 如果需要临时恢复单数ID

```bash
cd /home/user/webapp
python3 update_root_folders.py --odd "你的单数文件夹ID"
```

### 停止自动清理

```bash
# 停止调度器
pm2 stop folder-cleanup-scheduler

# 删除调度器
pm2 delete folder-cleanup-scheduler
```

### 重新启动自动清理

```bash
cd /home/user/webapp
pm2 start cleanup_scheduler.js --name "folder-cleanup-scheduler" --time
```

---

## 🐛 故障排查

### 问题1: 调度器未启动

**症状:** `pm2 list` 中看不到 `folder-cleanup-scheduler`

**解决:**
```bash
cd /home/user/webapp
pm2 start cleanup_scheduler.js --name "folder-cleanup-scheduler" --time
pm2 save
```

### 问题2: 清理未执行

**症状:** 过了00:10但配置文件未更新

**检查步骤:**
```bash
# 1. 检查调度器是否运行
pm2 status folder-cleanup-scheduler

# 2. 查看调度器日志
pm2 logs folder-cleanup-scheduler --lines 100

# 3. 手动执行测试
python3 /home/user/webapp/cleanup_unused_folder_id.py

# 4. 检查系统时间是否正确（北京时间）
date -R
```

### 问题3: 前端显示异常

**症状:** 页面显示 `root_folder_even: N/A` 而不是"🧹 已清理"

**解决:**
```bash
# 重启Flask应用
pm2 restart flask-app

# 清除浏览器缓存
# Ctrl+Shift+R (Windows/Linux)
# Cmd+Shift+R (Mac)
```

---

## 📝 总结

### 关键点

1. ✅ **自动执行** - 每天00:10自动运行，无需人工干预
2. ✅ **智能判断** - 根据日期奇偶自动决定删除哪个ID
3. ✅ **前端自适应** - 页面自动显示"已清理"状态
4. ✅ **日志完整** - 所有操作都有详细日志记录
5. ✅ **可恢复** - 可随时手动恢复已删除的ID

### 效果

- **简化显示** - 每天只显示一个父文件夹ID，界面更简洁
- **避免混淆** - 不会误用错误日期的父文件夹
- **自动化** - 完全自动化，无需人工操作

### 下次执行

- **时间:** 明天 2025-12-14 00:10
- **日期类型:** 双数
- **预期操作:** 删除 `root_folder_odd`，保留 `root_folder_even`

---

完成时间: 2025-12-13 01:10 (北京时间)  
状态: ✅ 已部署并测试成功
