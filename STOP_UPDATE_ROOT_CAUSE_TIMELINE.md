# 2025-12-21 停止更新完整时间线报告

## 🔴 核心问题
**SQLite WAL 文件异常膨胀导致磁盘空间耗尽，进而引发所有服务崩溃**

---

## 📅 详细时间线（北京时间）

### ✅ 正常运行阶段
- **2025-12-21 02:55:00**: 首页数据(`crypto_snapshots`)最后一次成功更新
  - 记录ID: 863
  - 状态: 数据正常写入数据库
  - 原因: 这时Google Drive配置刚被修复，系统成功采集到12-21数据

### ⚠️ 开始出现问题
- **2025-12-21 14:20-14:21**: 数据库开始报错
  ```
  Error: ENOSPC: no space left on device, write
  ```
  - 影响服务: 
    - `support-resistance-collector` (支撑/阻力位采集)
    - `support-resistance-snapshot-collector` (快照)
    - `v1v2-collector` (V1V2指标)
  - 日志文件:
    - `logs/support-resistance-out-5.log`
    - `logs/support-resistance-snapshot-out-6.log`
    - `logs/flask-error-1.log`

### 🛑 服务全面停止
- **2025-12-21 22:11:00**: 首页数据(`crypto_snapshots`)停止更新
  - 这是该表的最后一条记录
  - 原因: 数据库无法继续写入

- **2025-12-21 晚间**: 所有PM2服务陆续崩溃
  - 磁盘使用率: **100%** (26GB / 26GB 全满)
  - 所有数据采集器停止工作
  - Flask Web服务停止响应
  - 页面无法访问

---

## 🔍 根本原因分析

### 1. WAL文件异常膨胀 (核心原因)
```
crypto_data.db-wal: 9.1GB  ← 异常！正常应该 < 100MB
crypto_data.db:     1.8GB
crypto_data.db-shm: 19MB
```

**为什么WAL文件会膨胀？**
- SQLite默认使用WAL(Write-Ahead Logging)模式
- 正常情况下，WAL文件会定期checkpoint(合并到主数据库)
- 但如果：
  - 长时间没有执行checkpoint
  - 有长时间运行的事务未提交
  - 写入速度 > checkpoint速度
- 结果：WAL文件持续增长，直到磁盘满

### 2. 旧备份文件占用空间
```
crypto_data.db.corrupted: 986MB
crypto_data.db.backup_20251214_055758: 986MB
总计: ~2GB
```

### 3. 日志文件累积
```
logs目录总大小: 437MB
- gdrive-out-3.log: 7.0MB
- flask-error-1.log: 1.7MB
- panic-wash-error-11.log: 1.4MB
等等...
```

### 4. 磁盘空间耗尽的连锁反应
1. WAL文件膨胀至9.1GB
2. 磁盘使用率达到100%
3. 数据库无法写入新数据
4. 所有依赖数据库的服务报错: `ENOSPC: no space left on device`
5. PM2进程崩溃退出
6. Web服务停止响应

---

## ✅ 已采取的修复措施

### 1. 删除旧备份文件 (释放2GB)
```bash
rm -f crypto_data.db.corrupted
rm -f crypto_data.db.backup_20251214_055758
```

### 2. 执行WAL checkpoint (释放9GB)
```bash
sqlite3 crypto_data.db "PRAGMA wal_checkpoint(TRUNCATE);"
```
结果: `crypto_data.db-wal` 从 9.05GB → 16KB

### 3. 清理日志文件 (释放400MB)
```bash
find logs/ -name "*.log" -mtime +7 -delete
```
结果: logs目录从 437MB → 39MB

### 4. 重启所有服务
```bash
pm2 resurrect
```
结果: 14/14 服务全部在线

### 5. 创建定期维护脚本
- `cleanup_logs.sh`: 定期清理7天前的日志
- 建议添加cron任务定期执行

---

## 📊 修复前后对比

| 项目 | 修复前 | 修复后 | 改善 |
|------|--------|--------|------|
| 磁盘使用率 | 100% (26GB/26GB) | 57% (15GB/26GB) | ✅ 释放12GB |
| WAL文件 | 9.1GB | 16KB | ✅ 释放9GB |
| 旧备份 | 2GB | 0 | ✅ 释放2GB |
| 日志文件 | 437MB | 39MB | ✅ 释放400MB |
| PM2服务 | 0/14 (全部停止) | 14/14 (全部在线) | ✅ 完全恢复 |
| 数据更新 | 停止 | 正常 | ✅ 恢复更新 |

---

## 🔐 预防措施

### 1. 定期WAL checkpoint
建议添加到cron:
```bash
0 */6 * * * sqlite3 /home/user/webapp/crypto_data.db "PRAGMA wal_checkpoint(TRUNCATE);" >> /home/user/webapp/logs/wal_checkpoint.log 2>&1
```

### 2. 定期日志清理
```bash
0 2 * * * /home/user/webapp/cleanup_logs.sh >> /home/user/webapp/logs/cleanup.log 2>&1
```

### 3. 磁盘空间监控
添加磁盘空间检查到 `collector_monitor.py`:
```python
def check_disk_space():
    usage = shutil.disk_usage("/")
    used_percent = (usage.used / usage.total) * 100
    if used_percent > 80:
        logging.warning(f"Disk space critical: {used_percent:.1f}% used")
    return used_percent < 90
```

### 4. 数据库自动维护
在 `app_new.py` 或独立脚本中添加:
```python
def auto_db_maintenance():
    """每天凌晨3点自动执行数据库维护"""
    conn = sqlite3.connect('crypto_data.db')
    conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    conn.execute("VACUUM")  # 可选：压缩数据库
    conn.close()
```

---

## 🎯 结论

**停止更新的直接原因**: 2025-12-21 14:20 开始出现磁盘满错误，22:11 首页数据完全停止更新

**根本原因**: SQLite WAL文件异常膨胀至9.1GB，导致磁盘100%满，数据库无法写入

**当前状态**: ✅ 所有问题已解决，系统完全恢复正常运行

**关键教训**: 
1. SQLite WAL模式需要定期checkpoint
2. 日志文件需要自动轮转
3. 磁盘空间需要持续监控
4. 数据库维护需要自动化

---

报告生成时间: 2025-12-22 08:30:00 (北京时间)
报告作者: AI Developer Assistant
