# Google Drive TXT文件更新检测器

## 功能说明

这是一个**独立的功能模块**，专门用于监控Google Drive上的TXT文件更新。

### 核心功能

1. **持续监控**: 每30秒检查一次Google Drive文件
2. **更新检测**: 通过时间戳变化判断是否有新数据
3. **清晰日志**: 详细记录每次检查结果
4. **独立运行**: 不依赖其他模块，可单独部署

---

## 文件结构

```
gdrive_txt_detector.py      # 检测器主程序
import_latest_txt.py         # 数据导入模块
start_gdrive_detector.sh     # 启动脚本
gdrive_txt_detector.log      # 运行日志
```

---

## 使用方法

### 方式1: 使用启动脚本（推荐）

```bash
bash start_gdrive_detector.sh
```

### 方式2: 直接运行Python脚本

```bash
python3 gdrive_txt_detector.py
```

### 方式3: 后台运行

```bash
nohup python3 gdrive_txt_detector.py > detector.log 2>&1 &
```

---

## 查看运行状态

### 检查进程是否运行

```bash
ps aux | grep gdrive_txt_detector | grep -v grep
```

### 查看实时日志

```bash
tail -f /home/user/webapp/gdrive_txt_detector.log
```

### 查看最近的日志

```bash
tail -50 /home/user/webapp/gdrive_txt_detector.log
```

---

## 停止检测器

```bash
pkill -f gdrive_txt_detector.py
```

---

## 手动导入数据

如果检测到新数据，可以手动运行导入：

```bash
python3 import_latest_txt.py
```

---

## 配置说明

### 修改检查间隔

编辑 `gdrive_txt_detector.py`，修改：

```python
CHECK_INTERVAL_SECONDS = 30  # 改为你想要的秒数
```

### 修改Google Drive文件ID

编辑 `gdrive_txt_detector.py`，修改：

```python
GOOGLE_DRIVE_FILE_ID = "你的文件ID"
```

---

## 日志说明

### 正常检查日志

```
2025-12-09 19:00:00 [INFO] ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
2025-12-09 19:00:00 [INFO] 检查 #10 | 2025-12-09 19:00:00
2025-12-09 19:00:00 [INFO] ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
2025-12-09 19:00:01 [INFO] 📄 文件时间戳: 2025-12-09 18:08:00
2025-12-09 19:00:01 [INFO] ✓ 数据正常 (延迟 52 分钟)
```

### 发现新数据日志

```
2025-12-09 19:20:00 [INFO] ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
2025-12-09 19:20:00 [INFO] 检查 #15 | 2025-12-09 19:20:00
2025-12-09 19:20:00 [INFO] ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
2025-12-09 19:20:01 [INFO] 📄 文件时间戳: 2025-12-09 19:18:00
2025-12-09 19:20:01 [INFO] 
2025-12-09 19:20:01 [INFO] 🎉🎉🎉 检测到新数据更新! 🎉🎉🎉
2025-12-09 19:20:01 [INFO] 
2025-12-09 19:20:01 [INFO] 旧时间戳: 2025-12-09 18:08:00
2025-12-09 19:20:01 [INFO] 新时间戳: 2025-12-09 19:18:00
2025-12-09 19:20:01 [INFO] 
2025-12-09 19:20:01 [INFO] ================================================================
2025-12-09 19:20:01 [INFO] 📢 触发新数据处理流程
2025-12-09 19:20:01 [INFO] ================================================================
```

### 延迟警告日志

```
2025-12-09 19:00:00 [WARNING] ⏰ 数据延迟 52 分钟
```

---

## 工作原理

1. **下载文件**: 从Google Drive下载TXT文件（带防缓存header）
2. **提取时间戳**: 从文件内容中提取时间戳（格式：YYYY-MM-DD HH:MM:SS）
3. **对比变化**: 与上次记录的时间戳对比
4. **触发回调**: 如果时间戳变化，说明有新数据

---

## 与旧监控器的区别

| 特性 | 旧监控器 | 新检测器 |
|------|---------|---------|
| 功能定位 | 监控+导入一体 | **仅检测**，功能单一 |
| 代码结构 | 混合在一起 | **模块化**，职责清晰 |
| 日志输出 | 简单 | **详细**，易于调试 |
| 配置方式 | 代码内配置 | **集中配置区** |
| 独立性 | 依赖其他模块 | **完全独立** |
| 可维护性 | 中等 | **高** |

---

## 故障排查

### 检测器没有运行

```bash
# 检查进程
ps aux | grep gdrive_txt_detector

# 查看启动日志
cat gdrive_detector_startup.log

# 手动运行看错误
python3 gdrive_txt_detector.py
```

### 无法下载文件

- 检查网络连接
- 检查Google Drive文件ID是否正确
- 查看日志中的错误信息

### 时间戳提取失败

- 检查TXT文件格式是否正确
- 查看日志中的详细错误信息

---

## 集成到自动化流程

### 结合crontab定时导入

```bash
# 编辑crontab
crontab -e

# 添加：每10分钟导入一次
*/10 * * * * cd /home/user/webapp && python3 import_latest_txt.py >> import_cron.log 2>&1
```

### 结合systemd服务

创建 `/etc/systemd/system/gdrive-detector.service`:

```ini
[Unit]
Description=Google Drive TXT Detector
After=network.target

[Service]
Type=simple
User=user
WorkingDirectory=/home/user/webapp
ExecStart=/usr/bin/python3 /home/user/webapp/gdrive_txt_detector.py
Restart=always

[Install]
WantedBy=multi-user.target
```

---

## 当前运行状态

- **检测器**: ✅ 运行中
- **检查间隔**: 30秒
- **监控文件**: 1eyYiU6lU8n7SwWUvFtm_kUIvaZI0SO4U
- **日志文件**: /home/user/webapp/gdrive_txt_detector.log

---

## 技术细节

### 防缓存策略

使用HTTP headers确保获取最新数据：

```python
headers = {
    'Cache-Control': 'no-cache, no-store, must-revalidate',
    'Pragma': 'no-cache',
    'Expires': '0'
}
```

### 时间戳提取

使用正则表达式从文件内容提取：

```python
timestamps = re.findall(r'(\d{4}-\d{2}-\d{2}) (\d{2}:\d{2}:\d{2})', content)
```

### 更新判断逻辑

```
如果 当前时间戳 ≠ 上次时间戳:
    触发新数据回调
否则:
    记录延迟信息
```

---

## 维护建议

1. **定期查看日志**: 确保检测器正常运行
2. **监控延迟**: 如果延迟持续超过30分钟，检查上游数据源
3. **日志轮转**: 定期清理或归档旧日志文件
4. **配置备份**: 保存配置文件的备份

---

## 版本信息

- **版本**: 1.0.0
- **创建日期**: 2025-12-09
- **作者**: GenSpark AI Developer
- **更新日期**: 2025-12-09

---

## 联系与支持

- GitHub: https://github.com/jamesyidc/66661
- 分支: genspark_ai_developer
- 日志文件: gdrive_txt_detector.log
