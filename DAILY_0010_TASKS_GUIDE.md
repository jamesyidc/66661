# ⏰ 每日00:10自动任务完整指南

## 📋 概述

系统每天**北京时间00:10**自动执行两个关键任务：

1. **📂 自动更新父文件夹ID** - 从Google Drive获取最新的文件夹结构
2. **🧹 清理未使用的ID** - 删除今天不需要的父文件夹ID配置

---

## 🎯 任务详情

### 任务1: 自动更新父文件夹ID

**功能：** 每天从固定的Google Drive URL获取最新的父文件夹ID和子文件夹结构

**Google Drive URL：**
```
https://drive.google.com/drive/folders/1j8YV6KysUCmgcmASFOxztWWIE1Vq-kYV?usp=sharing
```

**执行流程：**

1. **提取父文件夹ID**
   ```
   从URL提取: 1j8YV6KysUCmgcmASFOxztWWIE1Vq-kYV
   ```

2. **扫描日期子文件夹**
   ```
   访问父文件夹 → 查找所有 YYYY-MM-DD 格式的子文件夹
   示例找到: 54个日期文件夹
   ```

3. **定位今天的子文件夹**
   ```
   查找: 2025-12-13/
   找到ID: 10LDSOAOoImkaDZv9WEF-PmUdCIQTaeVI
   ```

4. **更新配置文件**
   ```json
   {
       "root_folder_odd": "1j8YV6KysUCmgcmASFOxztWWIE1Vq-kYV",
       "folder_id": "10LDSOAOoImkaDZv9WEF-PmUdCIQTaeVI",
       "current_date": "2025-12-13",
       "last_auto_update": "2025-12-13 00:10:05",
       "auto_update_status": "success"
   }
   ```

**执行脚本：** `update_parent_folder_daily.py`

**日志文件：** `/home/user/webapp/parent_folder_update.log`

---

### 任务2: 清理未使用的ID

**功能：** 根据今天是单数还是双数日期，删除不需要的父文件夹ID

**清理规则：**

| 今天日期 | 保留ID | 删除ID |
|---------|-------|-------|
| 13号（单数） | root_folder_odd | root_folder_even ❌ |
| 14号（双数） | root_folder_even | root_folder_odd ❌ |

**执行脚本：** `cleanup_unused_folder_id.py`

**日志文件：** `/home/user/webapp/cleanup_cron.log`

---

## 🕐 执行顺序

```
00:10:00  启动定时任务
    ↓
00:10:01  执行任务1: 更新父文件夹ID
    ↓
    - 从Google Drive URL提取父文件夹ID
    - 扫描所有日期子文件夹
    - 找到今天的子文件夹ID
    - 更新配置文件
    ↓
00:10:04  等待3秒
    ↓
00:10:05  执行任务2: 清理未使用ID
    ↓
    - 判断今天是单数还是双数
    - 删除不需要的父文件夹ID
    - 更新配置文件
    ↓
00:10:06  任务执行完成
```

---

## 🖥️ 可视化状态页面

### 访问地址

```
https://5000-iypypqmz2wvn9dmtq7ewn-583b4d74.sandbox.novita.ai/daily-tasks-status
```

### 页面功能

#### 1. 倒计时显示

```
⏳ 距离下次执行
   23:45:30
下次执行时间: 2025-12-14 00:10
```

- 实时倒计时（小时:分钟:秒）
- 自动计算下一个00:10时间点
- 每秒更新

#### 2. 任务状态卡片

**任务1: 更新父文件夹ID**
```
┌─────────────────────────────────┐
│ 📂 更新父文件夹ID                │
│ 从Google Drive获取最新结构       │
├─────────────────────────────────┤
│ 执行状态: ✅ 已完成              │
│ 最后执行: 2025-12-13 00:10:05   │
│ 父文件夹ID: 1j8YV6KysUCmgcmASFO │
│ 子文件夹ID: 10LDSOAOoImkaDZv9WE │
└─────────────────────────────────┘
```

**任务2: 清理未使用ID**
```
┌─────────────────────────────────┐
│ 🧹 清理未使用ID                  │
│ 删除今天不需要的父文件夹ID       │
├─────────────────────────────────┤
│ 执行状态: ✅ 已完成              │
│ 最后清理: 2025-12-13 00:10:08   │
│ 清理原因: 今天是单数日期         │
│ 今天日期: 2025-12-13            │
└─────────────────────────────────┘
```

#### 3. 状态徽章

- **✅ 已完成** - 绿色，任务成功执行
- **⏳ 待执行** - 黄色，等待下次00:10
- **❌ 失败** - 红色，任务执行失败

#### 4. 实时日志

```
📋 执行日志              [🔄 刷新日志]

[2025-12-13 00:10:01] 🔄 开始每日父文件夹ID更新任务
[2025-12-13 00:10:01] 📅 当前日期: 2025-12-13 (13号 - 单数)
[2025-12-13 00:10:01] 📂 提取到父文件夹ID: 1j8YV6KysUCmgcmASFOxztWWIE1Vq-kYV
[2025-12-13 00:10:02] ✅ 找到 54 个日期子文件夹
[2025-12-13 00:10:02] ✅ 找到今天的子文件夹: 2025-12-13
[2025-12-13 00:10:02] ✅ 配置文件已更新
...
```

---

## 🔧 手动测试

### 手动触发父文件夹更新

```bash
cd /home/user/webapp
python3 update_parent_folder_daily.py
```

**预期输出：**
```
================================================================================
🔄 开始每日父文件夹ID更新任务
================================================================================
📅 当前日期: 2025-12-13 (13号 - 单数)
🔗 Google Drive URL: https://drive.google.com/drive/folders/...
📂 提取到父文件夹ID: 1j8YV6KysUCmgcmASFOxztWWIE1Vq-kYV
🔍 扫描父文件夹中的日期子文件夹...
✅ 找到 54 个日期子文件夹

📋 最近的日期文件夹:
   1. 2025-12-13 ← 今天
   2. 2025-12-12
   3. 2025-12-11
   ...

✅ 找到今天的子文件夹: 2025-12-13
📂 子文件夹ID: 10LDSOAOoImkaDZv9WEF-PmUdCIQTaeVI
✅ 父文件夹ID更新任务完成
================================================================================
```

### 手动触发清理任务

```bash
cd /home/user/webapp
python3 cleanup_unused_folder_id.py
```

---

## 📊 配置文件结构

### 完整配置示例

```json
{
    "root_folder_odd": "1j8YV6KysUCmgcmASFOxztWWIE1Vq-kYV",
    "root_folder_even": "1jFGGlGP5KEVhAxpCNxFIYEFI5-cDOBjM",
    "current_date": "2025-12-13",
    "data_date": "2025-12-13",
    "folder_id": "10LDSOAOoImkaDZv9WEF-PmUdCIQTaeVI",
    "last_update": "2025-12-13 00:10:02",
    "update_reason": "每日00:10自动更新（单数日期）",
    "parent_folder_url": "https://drive.google.com/drive/folders/1j8YV6KysUCmgcmASFOxztWWIE1Vq-kYV",
    "last_auto_update": "2025-12-13 00:10:02",
    "auto_update_status": "success",
    "last_cleanup": "2025-12-13 00:10:05",
    "cleanup_reason": "每日00:10自动清理，今天是单数日期",
    "root_folder_description": {
        "odd": "单数日期父文件夹 (1, 3, 5, 7, 9, 11...)",
        "even": "双数日期父文件夹 (2, 4, 6, 8, 10, 12...)"
    }
}
```

### 关键字段说明

| 字段 | 说明 |
|------|------|
| `root_folder_odd` | 单数日期使用的父文件夹ID |
| `root_folder_even` | 双数日期使用的父文件夹ID（00:10后可能被删除） |
| `folder_id` | 今天的子文件夹ID |
| `last_auto_update` | 最后一次自动更新的时间 |
| `auto_update_status` | 更新状态: success/failed |
| `last_cleanup` | 最后一次清理的时间 |
| `cleanup_reason` | 清理原因说明 |
| `parent_folder_url` | Google Drive父文件夹URL |

---

## 🚀 服务管理

### PM2进程状态

```bash
$ pm2 list
┌────┬────────────────────────────┬──────────┬──────┐
│ id │ name                       │ status   │ ↺    │
├────┼────────────────────────────┼──────────┼──────┤
│ 12 │ folder-cleanup-scheduler   │ online   │ 1    │
└────┴────────────────────────────┴──────────┴──────┘
```

### 查看调度器日志

```bash
# 实时日志
pm2 logs folder-cleanup-scheduler

# 最近50行日志
pm2 logs folder-cleanup-scheduler --lines 50 --nostream
```

### 重启调度器

```bash
pm2 restart folder-cleanup-scheduler
```

---

## 📝 API端点

### 1. 获取任务状态

**端点:** `/api/daily-tasks/status`

**返回示例:**
```json
{
    "success": true,
    "today_date": "2025-12-13",
    "parent_folder_update": {
        "status": "success",
        "last_update": "2025-12-13 00:10:02",
        "parent_folder_id": "1j8YV6KysUCmgcmASFOxztWWIE1Vq-kYV",
        "child_folder_id": "10LDSOAOoImkaDZv9WEF-PmUdCIQTaeVI",
        "url": "https://drive.google.com/drive/folders/..."
    },
    "cleanup": {
        "last_cleanup": "2025-12-13 00:10:05",
        "cleanup_reason": "每日00:10自动清理，今天是单数日期",
        "root_folder_odd": "1j8YV6KysUCmgcmASFOxztWWIE1Vq-kYV",
        "root_folder_even": null
    }
}
```

### 2. 获取执行日志

**端点:** `/api/daily-tasks/logs`

**返回示例:**
```json
{
    "success": true,
    "logs": [
        "[2025-12-13 00:10:01] 🔄 开始每日父文件夹ID更新任务",
        "[2025-12-13 00:10:01] 📅 当前日期: 2025-12-13",
        "[2025-12-13 00:10:02] ✅ 找到 54 个日期子文件夹",
        "..."
    ]
}
```

---

## 🔍 故障排查

### 问题1: 父文件夹ID未更新

**症状:** 配置中的`last_auto_update`时间不是今天

**检查步骤:**
```bash
# 1. 检查调度器是否运行
pm2 status folder-cleanup-scheduler

# 2. 查看调度器日志
pm2 logs folder-cleanup-scheduler --lines 100

# 3. 手动测试脚本
python3 update_parent_folder_daily.py

# 4. 检查Google Drive URL是否可访问
curl -I "https://drive.google.com/drive/folders/1j8YV6KysUCmgcmASFOxztWWIE1Vq-kYV"
```

### 问题2: 任务状态显示"失败"

**检查配置文件:**
```bash
cat /home/user/webapp/daily_folder_config.json | python3 -m json.tool
```

**查看错误信息:**
```bash
tail -50 /home/user/webapp/parent_folder_update.log
```

### 问题3: 页面无法访问

**重启Flask应用:**
```bash
pm2 restart flask-app
```

---

## 💡 使用建议

1. **每天检查页面** - 早上打开 `/daily-tasks-status` 确认任务执行成功

2. **关注失败状态** - 如果任务显示❌失败，立即查看日志

3. **定期检查日志** - 每周查看一次日志，确保无异常

4. **Google Drive可访问性** - 确保系统能访问Google Drive URL

5. **备份配置文件** - 定期备份 `daily_folder_config.json`

---

## 📈 监控指标

### 正常运行指标

- ✅ `auto_update_status`: "success"
- ✅ `last_auto_update`: 今天的日期
- ✅ `last_cleanup`: 今天的日期
- ✅ 页面显示绿色状态徽章

### 异常指标

- ❌ `auto_update_status`: "failed"
- ❌ `last_auto_update`: 不是今天
- ❌ 页面显示红色状态徽章
- ❌ 日志中有错误信息

---

## 🎯 总结

**每日00:10自动任务确保：**

1. ✅ 父文件夹ID始终保持最新
2. ✅ 配置文件自动更新
3. ✅ 不需要的ID被及时清理
4. ✅ 完整的可视化监控
5. ✅ 详细的执行日志记录

**访问可视化页面：**
```
https://5000-iypypqmz2wvn9dmtq7ewn-583b4d74.sandbox.novita.ai/daily-tasks-status
```

---

完成时间: 2025-12-13 01:21 (北京时间)  
版本: 1.0.0  
状态: ✅ 已部署并测试成功
