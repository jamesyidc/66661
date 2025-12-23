# 📁 每日文件夹自动更新系统使用指南

## 🎯 系统概述

这个系统可以自动扫描Google Drive"首页数据"文件夹，找到今天日期的子文件夹，并更新配置文件，确保检测器始终使用最新的文件夹ID。

### 核心组件

1. **`auto_update_today_folder.py`** - 核心更新脚本
   - 扫描父文件夹 (`1j8YV6KysUCmgcmASFOxztWWIE1Vq-kYV`)
   - 找到今天的日期文件夹
   - 更新配置文件 (`daily_folder_config.json`)
   - 重启检测器

2. **`setup_daily_cron.py`** - 定时任务设置工具
   - 配置每天00:10自动运行
   - 管理cron任务

3. **Web监控页面** - 可视化监控界面
   - 访问: `http://localhost:5000/folder-update-monitor`
   - 实时查看状态
   - 手动触发更新

---

## 🚀 快速开始

### 方法1: Web界面（推荐）

1. **打开监控页面**
   ```
   https://5000-iz6uddj6rs3xe48ilsyqq-cbeee0f9.sandbox.novita.ai/folder-update-monitor
   ```

2. **查看当前状态**
   - 页面会显示配置日期、最新文件等信息
   - 自动检测是否需要更新

3. **手动触发更新**
   - 点击"⚡ 立即更新"按钮
   - 等待更新完成（通常10-30秒）
   - 查看更新结果

### 方法2: 命令行手动运行

```bash
cd /home/user/webapp

# 直接运行更新脚本
python3 auto_update_today_folder.py

# 脚本会自动:
# 1. 检查是否需要更新
# 2. 扫描父文件夹
# 3. 找到今天的文件夹
# 4. 更新配置
# 5. 重启检测器
```

### 方法3: 设置定时任务

```bash
cd /home/user/webapp

# 运行设置工具
python3 setup_daily_cron.py

# 选择选项1: 设置定时任务
# 系统会自动配置每天00:10运行
```

---

## 📋 详细使用说明

### 1️⃣ 核心更新脚本

#### 功能特点
- ✅ 智能检测：只在需要时才更新
- ✅ 自动扫描：从父文件夹找到最新日期文件夹
- ✅ 验证内容：检查文件夹是否包含TXT文件
- ✅ 完整日志：记录所有操作步骤
- ✅ 自动重启：更新后自动重启检测器

#### 使用方法

```bash
# 基本用法
python3 auto_update_today_folder.py

# 脚本输出示例
======================================================================
                    🔄 每日文件夹自动更新脚本 🔄
======================================================================

[2025-12-14 11:53:02] ℹ️  脚本启动
[2025-12-14 11:53:02] 📋 检查是否需要更新
[2025-12-14 11:53:02] 📋 扫描父文件夹: 1j8YV6KysUCmgcmASFOxztWWIE1Vq-kYV
[2025-12-14 11:53:02] ✅ 父文件夹访问成功
[2025-12-14 11:53:02] ℹ️  找到 55 个子文件夹
[2025-12-14 11:53:02] 📋 查找今天的文件夹: 2025-12-14
[2025-12-14 11:53:02] ✅ 找到今天的文件夹: 2025-12-14
[2025-12-14 11:53:02] 📋 验证文件夹内容
[2025-12-14 11:53:02] ℹ️  找到 71 个TXT文件
[2025-12-14 11:53:02] 🎯 最新文件: 2025-12-14_1148.txt
[2025-12-14 11:53:02] 📋 更新配置文件
[2025-12-14 11:53:02] ✅ 配置文件更新成功
[2025-12-14 11:53:02] 📋 准备重启检测器
[2025-12-14 11:53:02] ✅ 检测器已重启

======================================================================
                            🔄 更新完成 🔄
======================================================================
[2025-12-14 11:53:02] ✅ 所有步骤完成
```

#### 日志文件
```bash
# 查看日志
cat /home/user/webapp/auto_update_folder.log

# 查看最新50行
tail -50 /home/user/webapp/auto_update_folder.log

# 实时查看
tail -f /home/user/webapp/auto_update_folder.log
```

---

### 2️⃣ 定时任务设置

#### 使用setup_daily_cron.py

```bash
python3 setup_daily_cron.py
```

**菜单选项:**

1. **设置定时任务** - 配置每天00:10自动运行
   - 添加cron任务
   - 自动设置权限
   - 验证配置

2. **立即测试运行** - 测试脚本是否正常工作
   - 运行一次更新
   - 查看输出
   - 验证功能

3. **查看手动设置说明** - 显示手动配置步骤
   - 详细的cron配置说明
   - 适合高级用户

4. **查看当前定时任务** - 列出已设置的cron任务
   - 显示当前配置
   - 验证任务存在

5. **删除定时任务** - 移除自动更新任务
   - 清理cron配置
   - 恢复手动模式

#### 手动配置cron任务

如果自动设置失败，可以手动添加:

```bash
# 1. 编辑crontab
crontab -e

# 2. 添加以下行（每天00:10运行）
10 0 * * * /usr/bin/python3 /home/user/webapp/auto_update_today_folder.py >> /home/user/webapp/cron_auto_update.log 2>&1

# 3. 保存并退出 (Ctrl+O, Enter, Ctrl+X)

# 4. 验证
crontab -l
```

#### Cron表达式说明
```
10 0 * * * = 每天00:10运行

分 时 日 月 周
│  │  │  │  │
│  │  │  │  └─ 周几 (0-7, 0和7都是周日)
│  │  │  └──── 月份 (1-12)
│  │  └─────── 日期 (1-31)
│  └────────── 小时 (0-23)
└───────────── 分钟 (0-59)
```

---

### 3️⃣ Web监控页面

#### 访问地址
```
本地: http://localhost:5000/folder-update-monitor
外网: https://5000-iz6uddj6rs3xe48ilsyqq-cbeee0f9.sandbox.novita.ai/folder-update-monitor
```

#### 功能特点
- 📊 实时状态监控
- 🔄 手动触发更新
- 📁 查看文件夹列表
- 📝 查看执行日志
- ⏱️ 自动刷新（每30秒）

#### 状态显示
```
✅ 正常 - 配置日期与今天匹配
⚠️ 需要更新 - 配置日期与今天不匹配
❌ 错误 - 系统异常
```

#### 使用步骤

1. **打开页面**
   - 浏览器访问监控页面
   - 页面自动加载当前状态

2. **查看状态**
   - 配置日期
   - 今天日期
   - 当前文件夹ID
   - 最新TXT文件
   - 文件数量

3. **手动更新**
   - 点击"⚡ 立即更新"
   - 等待扫描完成
   - 查看更新结果
   - 自动刷新状态

4. **查看文件夹**
   - 点击"📁 查看文件夹列表"
   - 显示最近10天的文件夹
   - 今天的文件夹高亮显示

5. **查看日志**
   - 点击"📝 查看日志"
   - 显示最近200行日志
   - 滚动查看历史记录

---

## 🔧 工作原理

### 文件夹结构
```
爷爷文件夹 (1U5VjRis2FYnBJvtR_8mmPrmFcJCMPGrH)
  └── 首页数据 (1j8YV6KysUCmgcmASFOxztWWIE1Vq-kYV) ← 固定不变
       ├── 2025-12-14/ (1VtHIpSvUpoDi-QxKWYaaId-mG0Y32tbL) 🎯 今天
       │    ├── 2025-12-14_0001.txt
       │    ├── 2025-12-14_0011.txt
       │    ├── ...
       │    └── 2025-12-14_1148.txt (最新)
       ├── 2025-12-13/ (10LDSOAOoImkaDZv9WEF-PmUdCIQTaeVI)
       ├── 2025-12-12/ (13js7p3V4FUtbkfZxWq9et_xYz7EQ9Q9O)
       └── ...
```

### 更新流程
```
1. 检查配置日期
   ↓
2. 扫描父文件夹 (首页数据)
   ↓
3. 查找今天的日期文件夹
   ↓
4. 验证文件夹内容（TXT文件）
   ↓
5. 更新 daily_folder_config.json
   ↓
6. 重启 gdrive_final_detector.py
   ↓
7. 完成 ✅
```

### 配置文件
```json
{
  "root_folder_odd": "1j8YV6KysUCmgcmASFOxztWWIE1Vq-kYV",
  "root_folder_even": "1j8YV6KysUCmgcmASFOxztWWIE1Vq-kYV",
  "folder_id": "1VtHIpSvUpoDi-QxKWYaaId-mG0Y32tbL",
  "current_date": "2025-12-14",
  "last_updated": "2025-12-14 11:53:02",
  "latest_txt": "2025-12-14_1148.txt",
  "txt_count": 71
}
```

---

## 📝 常见问题

### Q1: 什么时候需要更新？
**A:** 以下情况需要更新:
- 配置日期不是今天
- 当前文件夹无法访问
- 文件夹中没有TXT文件
- 检测器获取不到最新数据

### Q2: 如何判断是否需要更新？
**A:** 三种方式:
1. Web页面显示"⚠️ 需要更新"
2. 运行脚本自动检测
3. 检查配置文件中的`current_date`

### Q3: 更新失败怎么办？
**A:** 排查步骤:
1. 检查网络连接
2. 确认父文件夹ID正确
3. 查看错误日志
4. 手动访问父文件夹URL
5. 联系管理员

### Q4: 定时任务没有运行？
**A:** 检查项:
1. `crontab -l` 查看任务是否存在
2. 检查脚本权限 (`ls -la auto_update_today_folder.py`)
3. 查看cron日志 (`cat cron_auto_update.log`)
4. 确认cron服务运行 (`service cron status`)

### Q5: 为什么选择00:10运行？
**A:** 原因:
- 避开00:00服务器高峰
- 确保新文件夹已创建
- 在数据产生前完成更新
- 给系统预留10分钟缓冲

---

## 🛠️ 故障排除

### 问题1: 脚本无法执行
```bash
# 检查权限
ls -la auto_update_today_folder.py

# 添加执行权限
chmod +x auto_update_today_folder.py

# 测试运行
python3 auto_update_today_folder.py
```

### 问题2: 找不到今天的文件夹
```bash
# 手动访问父文件夹
https://drive.google.com/drive/folders/1j8YV6KysUCmgcmASFOxztWWIE1Vq-kYV?usp=sharing

# 检查今天的日期文件夹是否存在
# 如果不存在，脚本会使用最近的文件夹
```

### 问题3: 配置文件损坏
```bash
# 备份当前配置
cp daily_folder_config.json daily_folder_config.json.bak

# 手动重建配置
cat > daily_folder_config.json << 'EOF'
{
  "root_folder_odd": "1j8YV6KysUCmgcmASFOxztWWIE1Vq-kYV",
  "root_folder_even": "1j8YV6KysUCmgcmASFOxztWWIE1Vq-kYV",
  "folder_id": "YOUR_FOLDER_ID_HERE",
  "current_date": "2025-12-14"
}
EOF

# 运行更新脚本
python3 auto_update_today_folder.py
```

### 问题4: 检测器未重启
```bash
# 检查检测器进程
ps aux | grep gdrive_final_detector

# 手动停止
pkill -f gdrive_final_detector.py

# 手动启动
cd /home/user/webapp
nohup python3 gdrive_final_detector.py > gdrive_detector.log 2>&1 &
```

---

## 📊 监控与维护

### 日常检查
```bash
# 1. 查看最新日志
tail -20 /home/user/webapp/auto_update_folder.log

# 2. 检查配置文件
cat /home/user/webapp/daily_folder_config.json | jq

# 3. 验证检测器运行
ps aux | grep gdrive_final_detector

# 4. 查看API状态
curl http://localhost:5000/api/folder-update-status | jq
```

### 定期维护
- **每周**: 检查日志文件大小，必要时清理
- **每月**: 验证定时任务正常运行
- **季度**: 检查父文件夹ID是否变更

### 日志管理
```bash
# 清理旧日志（保留最近1000行）
tail -1000 auto_update_folder.log > auto_update_folder.log.tmp
mv auto_update_folder.log.tmp auto_update_folder.log

# 归档日志
cp auto_update_folder.log auto_update_folder_$(date +%Y%m%d).log
> auto_update_folder.log
```

---

## 🔗 相关链接

- **Web监控页面**: https://5000-iz6uddj6rs3xe48ilsyqq-cbeee0f9.sandbox.novita.ai/folder-update-monitor
- **检测器页面**: https://5000-iz6uddj6rs3xe48ilsyqq-cbeee0f9.sandbox.novita.ai/gdrive-detector
- **父文件夹**: https://drive.google.com/drive/folders/1j8YV6KysUCmgcmASFOxztWWIE1Vq-kYV?usp=sharing

---

## 📚 相关文档

- `FINAL_SUCCESS_REPORT.md` - 系统配置成功报告
- `DAILY_FOLDER_ID_UPDATE_GUIDE.md` - 每日更新详细指南
- `CURRENT_STATUS_REPORT.md` - 当前系统状态

---

**最后更新**: 2025-12-14  
**版本**: v1.0  
**维护者**: WebApp v3.8 Team
