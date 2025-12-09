# 🚀 加密货币监控系统 - 完整部署报告

## 📅 部署信息
- **部署时间**: 2025-12-09 01:40:00 UTC
- **备份来源**: webapp_full_backup_20251207_154723.tar.gz
- **部署位置**: /home/user/webapp
- **部署状态**: ✅ 成功

## 📊 系统组件状态

### 1. Flask 主应用 ✅
- **进程状态**: 运行中 (PID: 815)
- **监听端口**: 5000
- **公共访问地址**: https://5000-iypypqmz2wvn9dmtq7ewn-583b4d74.sandbox.novita.ai
- **日志文件**: flask_startup.log
- **启动时间**: 2025-12-09 01:23

### 2. 数据采集器状态 ✅

#### a) 加密指数采集器 (Crypto Index Collector)
- **状态**: ✅ 运行中
- **采集间隔**: 5分钟
- **最新指数**: 1018.62 (2025-12-09 09:35:00)
- **币种数量**: 27个
- **日志**: crypto_index_collector.log

#### b) 位置系统采集器 (Position System Collector)
- **状态**: ✅ 运行中
- **采集间隔**: 5分钟
- **最新采集**: 2025-12-09 01:33:34
- **币种数量**: 27个
- **低于1%统计**: 4h: 0/27, 12h: 0/27, 24h: 0/27, 48h: 0/27
- **日志**: position_system_collector.log

#### c) 价格对比采集器 (Price Comparison Collector)
- **状态**: ✅ 运行中
- **采集间隔**: 10分钟
- **币种数量**: 29个
- **突破事件**: 0个 (本次采集)
- **日志**: price_comparison_collector.log

#### d) 信号采集器 (Signal Collector)
- **状态**: ✅ 运行中
- **采集间隔**: 3分钟
- **重试机制**: 3次
- **日志**: signal_collector.log
- **备注**: 数据源可能需要刷新

#### e) 恐慌洗盘采集器 (Panic Wash Collector)
- **状态**: ✅ 运行中
- **采集间隔**: 3分钟
- **最新数据**:
  - 恐慌指数: 7.8%
  - 24小时爆仓: $141,998,428.09
  - 爆仓人数: 72,455人
  - 全网持仓: $9,285,554,146.72
- **日志**: panic_wash_collector.log

#### f) 清算金额采集器 (Liquidation Amount Collector)
- **状态**: ✅ 运行中
- **采集间隔**: 3分钟
- **最新数据**:
  - 1小时爆仓: $437.28万
  - 24小时爆仓: $1.42亿
  - 爆仓人数: 72,527人
  - 全网持仓: $92.88亿
  - 恐慌指数: 7.81%
- **日志**: liquidation_amount_collector.log

## 💾 数据库状态

### 主数据库 (crypto_data.db)
- **文件大小**: 1.60 MB
- **表数量**: 23个
- **总数据行**: 6,374行

### 数据表统计
| 表名 | 数据行数 | 说明 |
|------|---------|------|
| crypto_coin_data | 2,059 | 币种数据 |
| coin_history | 1,827 | 币种历史 |
| position_system | 994 | 位置系统 |
| signal_stats_history | 343 | 信号统计历史 |
| panic_wash_new | 176 | 恐慌洗盘新数据 |
| trading_signals | 173 | 交易信号 |
| panic_wash_index | 165 | 恐慌洗盘指数 |
| panic_wash_history | 124 | 恐慌洗盘历史 |
| crypto_snapshots | 110 | 加密货币快照 |
| signal_history | 64 | 信号历史 |
| panic_history | 64 | 恐慌历史 |
| stats_history | 63 | 统计历史 |
| liquidation_30days | 30 | 30天清算数据 |
| price_comparison | 29 | 价格对比 |
| price_baseline | 29 | 价格基准 |
| crypto_index_base_prices | 27 | 指数基准价格 |
| sqlite_sequence | 18 | SQLite序列 |
| crypto_index_klines | 14 | 指数K线 |
| price_breakthrough_events | 11 | 价格突破事件 |
| position_system_stats | 7 | 位置系统统计 |
| daily_price_records | 0 | 每日价格记录 |
| daily_statistics | 0 | 每日统计 |
| home_data_cache | 0 | 首页数据缓存 |

## 🎨 前端页面

### 可访问页面列表
1. **首页** - https://5000-iypypqmz2wvn9dmtq7ewn-583b4d74.sandbox.novita.ai/
2. **位置系统** - /position-system
3. **价格对比** - /price-comparison
4. **加密指数** - /crypto-index
5. **恐慌指数** - /panic
6. **交易信号** - /signals
7. **星级系统** - /star-system
8. **深度得分** - /depth-score
9. **控制中心** - /control-center

### HTML模板文件 (17个)
- ✅ index.html - 首页
- ✅ position_system.html - 位置系统
- ✅ price_comparison.html - 价格对比
- ✅ crypto_index.html - 加密指数
- ✅ panic_new.html - 恐慌指数
- ✅ signals.html - 交易信号
- ✅ star_system.html - 星级系统
- ✅ depth_score.html - 深度得分
- ✅ control_center.html - 控制中心
- ✅ 其他辅助页面...

## 📂 文件结构

### 核心程序文件
```
/home/user/webapp/
├── app_new.py (117KB) - Flask主应用
├── crypto_data.db (1.6MB) - 主数据库
├── requirements.txt - Python依赖
│
├── 数据采集器/
│   ├── crypto_index_collector.py - 加密指数采集
│   ├── position_system_collector.py - 位置系统采集
│   ├── price_comparison_collector.py - 价格对比采集
│   ├── signal_collector.py - 信号采集
│   ├── panic_wash_collector.py - 恐慌洗盘采集
│   └── liquidation_amount_collector.py - 清算金额采集
│
├── templates/ - HTML模板目录
│   └── (17个模板文件)
│
└── logs/ - 日志目录
    └── (多个日志文件)
```

## 🔧 Python依赖包

已安装的关键依赖：
- ✅ Flask 3.0.0 - Web框架
- ✅ Flask-CORS 4.0.0 - 跨域支持
- ✅ APScheduler 3.10.4 - 定时任务
- ✅ google-api-python-client 2.108.0 - Google API
- ✅ pytz 2023.3 - 时区处理
- ✅ requests - HTTP请求

## 🌐 访问地址

### 主要访问入口
**🌍 公共访问地址**: https://5000-iypypqmz2wvn9dmtq7ewn-583b4d74.sandbox.novita.ai

### API端点示例
- GET `/` - 首页
- GET `/api/position_system_stats` - 位置系统统计
- GET `/api/crypto_index` - 加密指数数据
- GET `/api/price_comparison` - 价格对比数据
- GET `/api/panic_wash` - 恐慌洗盘数据
- GET `/api/signals` - 交易信号数据

## 📝 操作日志

### 部署步骤记录
1. ✅ 解压备份文件到 /home/user/webapp
2. ✅ 验证核心文件完整性
3. ✅ 安装Python依赖包
4. ✅ 验证数据库完整性 (23个表, 6,374行数据)
5. ✅ 启动Flask主应用 (端口5000)
6. ✅ 启动加密指数采集器
7. ✅ 启动位置系统采集器
8. ✅ 启动价格对比采集器
9. ✅ 启动信号采集器
10. ✅ 启动恐慌洗盘采集器
11. ✅ 启动清算金额采集器
12. ✅ 验证所有服务运行状态
13. ✅ 测试API端点可访问性

## 🎯 系统功能验证

### 已验证功能
- ✅ Flask应用正常启动和响应
- ✅ 数据库连接正常
- ✅ 所有数据采集器正常运行
- ✅ 前端页面可正常访问
- ✅ API端点响应正常
- ✅ 日志系统正常记录

### 数据采集验证
- ✅ 加密指数: 每5分钟更新
- ✅ 位置系统: 每5分钟更新, 27个币种
- ✅ 价格对比: 每10分钟更新, 29个币种
- ✅ 信号采集: 每3分钟更新
- ✅ 恐慌洗盘: 每3分钟更新, 实时恐慌指数
- ✅ 清算金额: 每3分钟更新, 爆仓数据

## ⚙️ 进程管理

### 运行中的进程
```bash
# Flask应用
PID: 815 - python3 app_new.py

# 数据采集器
PID: 887 - python3 crypto_index_collector.py
PID: 894 - python3 position_system_collector.py
PID: 898 - python3 price_comparison_collector.py
PID: 904 - python3 signal_collector.py
PID: 911 - python3 panic_wash_collector.py
PID: 916 - python3 liquidation_amount_collector.py
```

### 进程控制命令
```bash
# 查看所有进程
ps aux | grep -E "app_new|collector" | grep -v grep

# 停止Flask应用
kill $(cat flask.pid)

# 停止所有采集器
pkill -f "python3.*collector"

# 查看日志
tail -f flask_startup.log
tail -f crypto_index_collector.log
```

## 📈 监控建议

### 需要定期检查
1. **数据采集频率**: 确保采集器按预期间隔运行
2. **数据库增长**: 监控数据库文件大小
3. **日志文件**: 定期清理过大的日志文件
4. **API响应**: 监控API端点响应时间
5. **错误日志**: 检查是否有持续性错误

### 健康检查脚本
```bash
# 检查所有服务状态
cd /home/user/webapp
ps aux | grep -E "app_new|collector" | grep -v grep | wc -l
# 预期输出: 7 (1个Flask + 6个采集器)

# 检查最新数据更新时间
python3 << EOF
import sqlite3
from datetime import datetime

conn = sqlite3.connect('crypto_data.db')
cursor = conn.cursor()

# 检查各表最新数据
tables_to_check = [
    'crypto_index_klines',
    'position_system',
    'price_comparison',
    'trading_signals',
    'panic_wash_index',
    'liquidation_30days'
]

for table in tables_to_check:
    try:
        cursor.execute(f"SELECT MAX(timestamp) FROM {table}")
        latest = cursor.fetchone()[0]
        print(f"{table}: {latest}")
    except:
        print(f"{table}: N/A")

conn.close()
