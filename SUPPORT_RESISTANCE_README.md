# 支撑压力线系统 - 数据备份与快速部署

## 🎯 快速开始

### 立即备份数据
```bash
# 备份最近30天的数据（推荐）
python3 backup_support_resistance_data.py backup --days 30
```

### 快速部署
```bash
# 一键部署（自动启动采集器）
bash quick_deploy_support_resistance.sh

# 带数据恢复的部署
bash quick_deploy_support_resistance.sh backups/support_resistance_backup_30days_*.json.gz
```

## 📊 数据说明

### 数据库已包含所有曲线图数据
✅ **无需额外保存**，数据库中的 `support_resistance_snapshots` 表已完整保存：

- **4条趋势曲线** (scenario_1_count ~ scenario_4_count)
- **时间序列** (snapshot_time，每3分钟一个点)
- **详细币种信息** (scenario_X_coins JSON格式)
- **历史数据** (当前: 258条记录，覆盖12.7小时)

### 数据结构
```
support_resistance_snapshots 表
├── snapshot_time          # 快照时间 (北京时间)
├── scenario_1_count       # 情况1: 接近支撑2 的币种数
├── scenario_2_count       # 情况2: 接近支撑1 的币种数
├── scenario_3_count       # 情况3: 接近压力2 的币种数
├── scenario_4_count       # 情况4: 接近压力1 的币种数
├── scenario_1_coins       # 情况1币种详情 (JSON)
├── scenario_2_coins       # 情况2币种详情 (JSON)
├── scenario_3_coins       # 情况3币种详情 (JSON)
└── scenario_4_coins       # 情况4币种详情 (JSON)
```

## 🛠️ 工具清单

### 1. 备份工具 (`backup_support_resistance_data.py`)
```bash
# 备份数据
python3 backup_support_resistance_data.py backup [--days N]

# 导出CSV（用于Excel分析）
python3 backup_support_resistance_data.py export-csv [--days N]

# 列出所有备份
python3 backup_support_resistance_data.py list

# 恢复数据
python3 backup_support_resistance_data.py restore --file <backup_file>
```

### 2. 快速部署脚本 (`quick_deploy_support_resistance.sh`)
```bash
# 基本部署
bash quick_deploy_support_resistance.sh

# 带数据恢复的部署
bash quick_deploy_support_resistance.sh <backup_file>
```

### 3. 完整指南 (`SUPPORT_RESISTANCE_BACKUP_GUIDE.md`)
包含：
- 详细使用说明
- 故障排查
- API参考
- 最佳实践

## 📁 文件结构

```
/home/user/webapp/
├── crypto_data.db                             # 主数据库（包含所有曲线图数据）
├── backup_support_resistance_data.py          # 备份工具
├── quick_deploy_support_resistance.sh         # 快速部署脚本
├── support_resistance_snapshot_collector.py   # 数据采集器
├── backups/                                   # 备份目录
│   ├── support_resistance_backup_*.json.gz   # 压缩备份文件
│   └── support_resistance_export_*.csv       # CSV导出文件
└── SUPPORT_RESISTANCE_BACKUP_GUIDE.md        # 完整使用指南
```

## 🔄 常用操作

### 日常备份
```bash
# 每天备份一次（推荐在crontab中配置）
0 2 * * * cd /home/user/webapp && python3 backup_support_resistance_data.py backup --days 30
```

### 查看数据
```bash
# 查看最新快照
sqlite3 crypto_data.db "SELECT * FROM support_resistance_snapshots ORDER BY created_at DESC LIMIT 5"

# 统计数据
sqlite3 crypto_data.db "SELECT COUNT(*) FROM support_resistance_snapshots"
```

### 检查采集器
```bash
# 查看进程
ps aux | grep support_resistance_snapshot_collector

# 查看日志
tail -f support_resistance_snapshot.log

# 重启采集器
bash quick_deploy_support_resistance.sh
```

## 📊 数据统计

**当前状态 (2025-12-14 20:51):**
- 快照总数: 258
- 时间范围: 08:00:00 ~ 20:50:15 (北京时间)
- 监控币种: 27个
- 更新频率: 每3分钟
- 采集器: ✅ 运行中 (PID: 28295)

## 🌐 访问地址

- **页面:** https://5000-iz6uddj6rs3xe48ilsyqq-cbeee0f9.sandbox.novita.ai/support-resistance
- **API:** http://localhost:5000/api/support-resistance/latest
- **历史:** http://localhost:5000/api/support-resistance/snapshots?all=true

## ⚡ 快速恢复场景

### 场景1: 数据库损坏
```bash
# 1. 列出备份
python3 backup_support_resistance_data.py list

# 2. 恢复最新备份
python3 backup_support_resistance_data.py restore --file backups/support_resistance_backup_30days_*.json.gz

# 3. 重启采集器
bash quick_deploy_support_resistance.sh
```

### 场景2: 新服务器部署
```bash
# 1. 复制整个webapp目录
scp -r /home/user/webapp user@new-server:/home/user/

# 2. 快速部署
cd /home/user/webapp
bash quick_deploy_support_resistance.sh

# 3. 启动Flask应用
python3 app_new.py &
```

### 场景3: 数据迁移
```bash
# 源服务器
python3 backup_support_resistance_data.py backup --days 90
scp backups/support_resistance_backup_*.json.gz user@new-server:/home/user/webapp/backups/

# 目标服务器
cd /home/user/webapp
bash quick_deploy_support_resistance.sh backups/support_resistance_backup_*.json.gz
```

## 📈 数据增长估算

- **每天记录数:** 480条 (每3分钟一条)
- **每天数据量:** 约20KB (压缩后)
- **30天数据量:** 约600KB (压缩后)
- **90天数据量:** 约1.8MB (压缩后)

## ✅ 验证清单

部署后检查：
- [ ] 数据库文件存在 (`crypto_data.db`)
- [ ] 快照表有数据 (`support_resistance_snapshots`)
- [ ] 采集器正在运行 (`ps aux | grep collector`)
- [ ] 数据在更新 (最新快照时间<5分钟)
- [ ] API返回正常 (`curl localhost:5000/api/support-resistance/latest`)
- [ ] 页面可访问 (打开浏览器测试)

## 🆘 遇到问题？

1. 查看完整文档: `SUPPORT_RESISTANCE_BACKUP_GUIDE.md`
2. 检查日志: `tail -f support_resistance_snapshot.log`
3. 验证数据库: `sqlite3 crypto_data.db "SELECT COUNT(*) FROM support_resistance_snapshots"`
4. 测试API: `curl http://localhost:5000/api/support-resistance/latest`

## 📞 相关文档

- `SUPPORT_RESISTANCE_BACKUP_GUIDE.md` - 完整使用指南
- `SUPPORT_RESISTANCE_API_FIX.md` - API修复文档
- `support_resistance_snapshot.log` - 采集器日志

---

**最后更新:** 2025-12-14 20:51 Beijing Time  
**版本:** 1.0  
**状态:** ✅ 生产就绪
