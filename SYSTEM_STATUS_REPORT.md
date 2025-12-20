# 系统运行状态报告

## 📅 报告时间
**2025-12-09 14:50 (北京时间)**

## ✅ 系统运行状态

### 🌐 Web应用
- **Flask查询页面**: ✅ 运行中 (PID: 12875)
- **访问地址**: https://5000-iypypqmz2wvn9dmtq7ewn-583b4d74.sandbox.novita.ai/query
- **端口**: 5000
- **状态**: 正常响应

### 📊 数据采集器状态

| 采集器 | 状态 | PID | 说明 |
|--------|------|-----|------|
| crypto_index_collector | ✅ 运行中 | 887 | OKEx加密货币指数 |
| position_system_collector | ✅ 运行中 | 894 | 持仓系统数据 |
| price_comparison_collector | ✅ 运行中 | 898 | 价格对比数据 |
| signal_collector | ✅ 运行中 | 904 | 信号数据 |
| panic_wash_collector | ✅ 运行中 | 911 | 恐慌清洗指数 |
| liquidation_amount_collector | ✅ 运行中 | 916 | 清算量数据 |
| v1v2_collector | ✅ 运行中 | 2423 | V1V2数据 |
| price_speed_collector | ✅ 运行中 | 3662 | 价格变化速度 |
| **auto_gdrive_updater** | ✅ 运行中 | 9496 | **Google Drive自动更新** |

**总计**: 9个采集器全部正常运行 ✅

### 📈 数据库状态

#### 今天 (2025-12-09)
- **记录数**: 1条
- **最新记录**: 2025-12-09 12:46:00
  - 急涨: 7
  - 急跌: 7
  - 计次: 6
  - 状态: 震荡无序

#### 历史数据
- 2025-12-09: 1条
- 2025-12-07: 37条
- 2025-12-06: 74条

### 🔄 自动更新器状态

**auto_gdrive_updater.py**:
- ✅ 运行中
- ⏰ 检查频率: 每10分钟
- 📂 目标文件夹: 2025-12-09
- ⚠️  当前状态: 未找到目标文件夹
- 📝 最近检查: 14:43

**检查日志**:
```
2025-12-09 14:43:48 - 检查文件夹: 2025-12-09
2025-12-09 14:43:49 - 未找到文件夹: 2025-12-09
2025-12-09 14:43:49 - 未找到新文件
2025-12-09 14:43:49 - 下次检查时间: 600秒后 (14:53)
```

## 📋 最近更新记录

### Git提交历史 (最近5次)
1. `e9a1eef` - refactor: 删除急涨速、急跌速、正常三个统计项
2. `d8018b7` - revert: 移除补全数据功能，恢复到表格调整后的干净版本
3. `b31edc3` - docs: 添加数据补全状态报告
4. `2f6bfe3` - docs: 添加补全数据进度弹窗详细使用指南
5. `eca1087` - feat: 添加补全数据进度弹窗，显示详细运行流程

### 当前分支
- **分支**: genspark_ai_developer
- **最新提交**: e9a1eef
- **远程状态**: 已同步

## ⚙️ 功能状态

### ✅ 正常功能
- [x] 查询页面访问
- [x] 历史数据查询
- [x] 图表显示
- [x] 时间轴展示
- [x] 29币数据表格
- [x] 优先级计算
- [x] 所有数据采集器
- [x] 自动Google Drive监控

### ⚠️  待改进
- [ ] Google Drive数据源 (2025-12-09文件夹缺失)
- [ ] 今天只有1条数据记录

## 📊 数据更新机制

### 自动更新流程
```
每10分钟 → 检查Google Drive → 发现新文件 → 下载 → 转码(GBK→UTF-8) → 导入数据库 → 前端自动刷新
```

### 当前问题
**Google Drive状态**: ⚠️ 未找到 `2025-12-09` 文件夹

**可能原因**:
1. 今天的数据尚未上传到Google Drive
2. 文件夹命名格式不同
3. 数据源系统暂停或延迟

**系统行为**:
- 自动更新器继续每10分钟检查
- 一旦发现文件夹，自动下载并导入所有数据
- 无需人工干预

## 🔗 访问链接

- **查询页面**: https://5000-iypypqmz2wvn9dmtq7ewn-583b4d74.sandbox.novita.ai/query
- **API接口**: https://5000-iypypqmz2wvn9dmtq7ewn-583b4d74.sandbox.novita.ai/api/latest
- **GitHub PR**: https://github.com/jamesyidc/66661/compare/main...genspark_ai_developer

## 📝 监控命令

### 查看实时日志
```bash
# 自动更新器日志
tail -f /home/user/webapp/auto_gdrive_updater.log

# Flask应用日志
tail -f /home/user/webapp/flask_app.log

# 查看所有后台进程
ps aux | grep python3 | grep collector
```

### 查看数据库状态
```bash
cd /home/user/webapp && python3 -c "
import sqlite3
conn = sqlite3.connect('crypto_data.db')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM crypto_snapshots WHERE date(snapshot_time) = date(\"now\", \"+8 hours\")')
print(f'今天记录数: {cursor.fetchone()[0]}')
conn.close()
"
```

### 手动触发更新
```bash
# 手动检查Google Drive (如果有新文件可用)
cd /home/user/webapp && python3 backfill_today_data.py
```

## 🎯 总结

### 系统健康度: ✅ 良好

- **Web服务**: ✅ 正常
- **采集器**: ✅ 全部运行
- **自动更新**: ✅ 正常监控
- **数据完整性**: ⚠️  等待数据源更新

### 建议

1. ✅ **保持当前状态** - 所有服务正常运行
2. 📋 **监控日志** - 定期查看auto_gdrive_updater.log
3. ⏰ **等待数据源** - 一旦Google Drive更新，系统会自动导入
4. 🔄 **无需干预** - 系统完全自动化

---

**报告生成时间**: 2025-12-09 14:50:31  
**系统状态**: 🟢 运行正常，等待数据源更新  
**下次自动检查**: 每10分钟
