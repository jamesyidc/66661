# 📦 项目完整备份记录

## 备份信息

- **备份日期**: 2025-12-07 15:44:34 UTC
- **备份文件**: `webapp_full_backup_20251207_154423.tar.gz`
- **备份位置**: `/tmp/`
- **备份大小**: 2.8 MB
- **总文件数**: 499 个文件

## 备份内容

### 核心文件
- ✅ 所有Python程序 (169个)
- ✅ 所有HTML模板 (15个)
- ✅ 完整数据库 (5个文件，含WAL和SHM)
- ✅ 所有日志文件 (54个)
- ✅ 历史数据文件
- ✅ 配置文件

### 主要组件
1. **Flask主应用**: app_new.py
2. **数据采集器**: 
   - crypto_index_collector.py (加密指数)
   - position_system_collector.py (位置系统)
   - price_comparison_collector.py (比价系统)
   - 其他采集器...
3. **数据库**:
   - crypto_data.db (主数据库)
   - signal_data.db (信号数据)
   - homepage_data.db (首页缓存)
4. **前端页面**: templates/ 目录下所有HTML

## 恢复方法

### 快速恢复
```bash
# 使用恢复脚本
cd /tmp
bash restore.sh [目标目录]
```

### 手动恢复
```bash
# 1. 解压备份
tar -xzf /tmp/webapp_full_backup_20251207_154423.tar.gz -C /目标目录/

# 2. 安装依赖
cd /目标目录/
pip install -r requirements.txt

# 3. 启动服务
python3 app_new.py &
nohup python3 position_system_collector.py > /dev/null 2>&1 &
nohup python3 crypto_index_collector.py > /dev/null 2>&1 &
nohup python3 price_comparison_collector.py > /dev/null 2>&1 &
```

## 备份文件清单

### 数据库
- crypto_data.db (主数据库)
- crypto_data.db-wal (WAL文件)
- crypto_data.db-shm (共享内存)
- signal_data.db
- homepage_data.db

### 核心程序
- app_new.py (Flask应用)
- crypto_index_collector.py
- position_system_collector.py
- price_comparison_collector.py
- panic_wash_collector.py
- signal_collector.py
- liquidation_amount_collector.py
- 其他采集器和工具...

### HTML模板
- templates/position_system.html (位置系统，含时间轴)
- templates/price_comparison.html (比价系统)
- templates/crypto_index.html (加密指数)
- templates/panic_new.html (恐慌指数)
- templates/index.html (首页)
- 其他页面模板...

### 日志文件
- position_system.log
- crypto_index_collector.log
- price_comparison_collector.log
- 其他日志文件...

## 备份验证

✅ 所有关键文件已验证
✅ 数据库完整性已确认
✅ 可成功解压并恢复

## 附加文件

在 `/tmp/` 目录下还包含:
- `BACKUP_README.md` - 详细备份说明文档
- `restore.sh` - 快速恢复脚本

## 系统状态 (备份时)

### 运行中的服务
- Flask应用 (app_new.py)
- 位置系统采集器
- 加密指数采集器  
- 比价系统采集器

### 最新功能
- ✅ 位置系统历史数据时间轴
- ✅ 比价系统自动创新低检测
- ✅ 加密指数27币种加权
- ✅ 统计数据存储和查询

## 注意事项

1. 备份包含完整的SQLite数据库文件（包括WAL和SHM）
2. 恢复后需要重新启动所有采集器
3. 确保Python依赖已安装
4. Flask默认运行在5000端口

---

**备份创建**: 2025-12-07
**备份类型**: 完整备份 (Full Backup)
**备份状态**: ✅ 已验证
