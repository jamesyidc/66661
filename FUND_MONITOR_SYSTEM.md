# 资金监控系统 - 完整文档

## 🎯 系统概述

资金监控系统是一个实时监控加密货币成交量的系统，通过分析不同时间周期的成交量并与历史数据对比，及时发现市场资金异常流动。

### 核心功能
1. **实时数据采集**：每5分钟从OKEx获取27个币种的永续合约成交量数据
2. **多周期分析**：自动计算15分钟、30分钟、60分钟的聚合成交量
3. **异常检测**：与过去3天平均量能对比，波动超过阈值时发出预警
4. **可视化展示**：直观的前端界面展示所有币种的成交量和异常状态
5. **灵活配置**：支持动态调整异常阈值、回看天数等参数

## 📊 监控币种（27个）

```
BTC, ETH, XRP, BNB, SOL, LTC, DOGE, SUI, TRX, TON,
ETC, BCH, HBAR, XLM, FIL, LINK, CRO, DOT, AAVE, UNI,
NEAR, APT, CFX, CRV, STX, LDO, TAO
```

## 🏗️ 系统架构

### 1. 数据采集层（fund_monitor_collector.py）
- **采集频率**：每5分钟（300秒，可配置）
- **数据源**：OKEx永续合约API（与V1V2系统共用）
- **数据存储**：SQLite数据库（fund_monitor.db）

### 2. 数据库结构

#### fund_monitor_5min（5分钟原始数据表）
```sql
CREATE TABLE fund_monitor_5min (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL,              -- 币种符号
    timestamp INTEGER NOT NULL,        -- 时间戳（毫秒）
    collect_time TEXT NOT NULL,        -- 采集时间（北京时间）
    volume REAL NOT NULL,              -- 成交量（USDT）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(symbol, timestamp)
)
```

#### fund_monitor_aggregated（聚合数据表）
```sql
CREATE TABLE fund_monitor_aggregated (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL,              -- 币种符号
    timestamp INTEGER NOT NULL,        -- 时间戳（毫秒）
    collect_time TEXT NOT NULL,        -- 采集时间（北京时间）
    interval_type TEXT NOT NULL,       -- 时间周期：15min/30min/60min
    volume REAL NOT NULL,              -- 该周期成交量总和
    avg_3day REAL,                     -- 过去3天平均成交量
    deviation_percent REAL,            -- 偏差百分比
    is_abnormal INTEGER DEFAULT 0,     -- 是否异常（0=正常，1=异常）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(symbol, timestamp, interval_type)
)
```

#### fund_monitor_config（配置表）
```sql
CREATE TABLE fund_monitor_config (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT UNIQUE NOT NULL,          -- 配置键
    value REAL NOT NULL,               -- 配置值
    description TEXT,                  -- 说明
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

### 3. 后端API层（app_new.py）

#### API端点

**1. 获取最新数据**
```
GET /api/fund-monitor/latest
```
返回所有币种、所有时间周期的最新数据

**2. 获取历史数据**
```
GET /api/fund-monitor/history/<symbol>?interval=15min&hours=24
```
参数：
- `symbol`: 币种符号（如BTC）
- `interval`: 时间周期（15min/30min/60min，默认15min）
- `hours`: 查询小时数（默认24）

**3. 获取异常数据**
```
GET /api/fund-monitor/abnormal
```
返回当前所有检测到的异常数据

**4. 配置管理**
```
GET  /api/fund-monitor/config     # 获取配置
POST /api/fund-monitor/config     # 更新配置
```
配置参数：
- `threshold_percentage`: 异常阈值百分比（默认20%）
- `lookback_days`: 回看天数（默认3天）
- `collection_interval`: 采集间隔秒数（默认300秒）

**5. 前端页面**
```
GET /fund-monitor
```
访问完整的资金监控可视化界面

### 4. 前端界面（fund_monitor.html）

#### 主要功能
1. **实时数据展示**
   - 卡片式展示每个币种的成交量数据
   - 自动高亮显示异常币种
   - 实时显示偏差百分比

2. **多维度筛选**
   - 按时间周期切换（15/30/60分钟）
   - 按异常状态筛选（全部/仅异常/仅正常）
   - 按多种方式排序（币种名称/偏差百分比/成交量）

3. **配置管理**
   - 在线调整异常阈值
   - 在线调整回看天数
   - 实时生效

4. **统计面板**
   - 显示各周期异常币种数量
   - 实时更新时间
   - 总监控币种数

## 🚀 部署与运行

### 1. 数据采集服务（PM2管理）
```bash
# 启动采集器
pm2 start fund_monitor_collector.py --name fund-monitor-collector --interpreter python3

# 查看状态
pm2 status fund-monitor-collector

# 查看日志
pm2 logs fund-monitor-collector

# 停止服务
pm2 stop fund-monitor-collector

# 重启服务
pm2 restart fund-monitor-collector
```

### 2. Web服务（Flask）
```bash
# Flask应用会自动加载资金监控API
pm2 restart flask-app
```

### 3. 配置文件
**fund_monitor_config.json**
```json
{
  "threshold_percentage": 20.0,    // 异常阈值百分比
  "lookback_days": 3,               // 回看天数
  "collection_interval": 300        // 采集间隔（秒）
}
```

## 📱 访问方式

### 在线访问
- **前端界面**: https://5000-ilsitop6yown44mau7vd7-c07dda5e.sandbox.novita.ai/fund-monitor
- **API基础URL**: https://5000-ilsitop6yown44mau7vd7-c07dda5e.sandbox.novita.ai/api/fund-monitor/

### 本地访问
- **前端界面**: http://localhost:5000/fund-monitor
- **API基础URL**: http://localhost:5000/api/fund-monitor/

## 📈 数据分析逻辑

### 1. 聚合计算
```python
# 15分钟聚合 = 最近3个5分钟数据之和
volume_15min = sum(last_3_records['volume'])

# 30分钟聚合 = 最近6个5分钟数据之和
volume_30min = sum(last_6_records['volume'])

# 60分钟聚合 = 最近12个5分钟数据之和
volume_60min = sum(last_12_records['volume'])
```

### 2. 3天平均计算
```python
# 查询过去3天同时间周期的数据
avg_3day = average(historical_volumes[-3days:])
```

### 3. 异常检测
```python
# 计算偏差百分比
deviation_percent = ((current_volume - avg_3day) / avg_3day) * 100

# 判断是否异常
is_abnormal = abs(deviation_percent) >= threshold_percentage

# 示例：
# 当前成交量: 1,000,000 USDT
# 3日平均:     800,000 USDT
# 偏差百分比:  +25%
# 阈值:         20%
# 结果:         异常（25% > 20%）
```

## 🔧 运维与监控

### 1. 日志文件
- **采集器日志**: `fund_monitor_collector.log`
- **PM2日志**: `~/.pm2/logs/fund-monitor-collector-*.log`

### 2. 数据库维护
```bash
# 查看数据量
python3 -c "
import sqlite3
conn = sqlite3.connect('fund_monitor.db')
c = conn.cursor()
c.execute('SELECT COUNT(*) FROM fund_monitor_5min')
print(f'5分钟数据: {c.fetchone()[0]} 条')
c.execute('SELECT COUNT(*) FROM fund_monitor_aggregated')
print(f'聚合数据: {c.fetchone()[0]} 条')
conn.close()
"

# 定期清理旧数据（可选，保留最近7天）
python3 -c "
import sqlite3
from datetime import datetime, timedelta
conn = sqlite3.connect('fund_monitor.db')
c = conn.cursor()
seven_days_ago = int((datetime.now() - timedelta(days=7)).timestamp() * 1000)
c.execute('DELETE FROM fund_monitor_5min WHERE timestamp < ?', (seven_days_ago,))
c.execute('DELETE FROM fund_monitor_aggregated WHERE timestamp < ?', (seven_days_ago,))
conn.commit()
print(f'已删除7天前的数据')
conn.close()
"
```

### 3. 性能监控
```bash
# 查看采集器资源占用
pm2 monit fund-monitor-collector

# 查看采集成功率
tail -f fund_monitor_collector.log | grep "采集完成"
```

## 🎨 前端界面特性

### 1. 响应式设计
- 自适应不同屏幕尺寸
- 卡片式布局，易于浏览

### 2. 实时更新
- 每30秒自动刷新数据
- 手动刷新按钮

### 3. 视觉提示
- 异常数据红色高亮
- 脉冲动画提示
- 正负偏差颜色区分（绿色/红色）

### 4. 交互功能
- 点击切换时间周期
- 下拉筛选和排序
- 悬停显示详细信息

## 🔍 使用示例

### 1. 查看当前异常币种
访问：`/api/fund-monitor/abnormal`

返回示例：
```json
{
  "success": true,
  "count": 2,
  "data": [
    {
      "symbol": "BTC",
      "interval_type": "15min",
      "collect_time": "2025-12-22 21:20:00",
      "volume": 18000000.0,
      "avg_3day": 14000000.0,
      "deviation_percent": 28.57
    },
    {
      "symbol": "ETH",
      "interval_type": "30min",
      "collect_time": "2025-12-22 21:20:00",
      "volume": 52000000.0,
      "avg_3day": 40000000.0,
      "deviation_percent": 30.0
    }
  ]
}
```

### 2. 调整异常阈值
```bash
curl -X POST http://localhost:5000/api/fund-monitor/config \
  -H "Content-Type: application/json" \
  -d '{
    "threshold_percentage": 25.0
  }'
```

### 3. 查询BTC历史数据
访问：`/api/fund-monitor/history/BTC?interval=15min&hours=48`

## ⚠️ 注意事项

1. **数据依赖**
   - 系统依赖OKEx API，需确保网络连接正常
   - 与V1V2系统共用数据源，API调用频率需控制

2. **存储空间**
   - 27个币种，每5分钟1条记录
   - 每天约7,776条原始数据 + 23,328条聚合数据
   - 建议定期清理7天以上的历史数据

3. **异常阈值设置**
   - 阈值过低：误报率高
   - 阈值过高：漏报风险大
   - 建议根据市场波动性调整（推荐15-25%）

4. **冷启动问题**
   - 系统启动前3天，avg_3day为NULL
   - 建议等待至少3天积累数据后再依赖异常检测

## 🔄 系统更新

### 修改采集频率
编辑 `fund_monitor_config.json`:
```json
{
  "collection_interval": 600  // 改为10分钟（600秒）
}
```
然后重启采集器：`pm2 restart fund-monitor-collector`

### 添加新币种
1. 修改 `fund_monitor_collector.py` 的 `COINS` 列表
2. 重启采集器：`pm2 restart fund-monitor-collector`

## 📞 技术支持

### 问题排查
1. **采集失败**
   - 检查OKEx API连接
   - 查看 `fund_monitor_collector.log`

2. **前端无数据**
   - 确认Flask服务正常：`pm2 status flask-app`
   - 检查数据库是否有数据

3. **异常检测不准**
   - 检查配置文件中的阈值设置
   - 确认已有足够的历史数据（至少3天）

### 文件清单
```
/home/user/webapp/
├── fund_monitor_collector.py          # 数据采集脚本
├── fund_monitor_config.json            # 配置文件
├── fund_monitor.db                     # 数据库
├── fund_monitor_collector.log          # 采集日志
├── app_new.py                          # Flask应用（包含API）
└── templates/
    └── fund_monitor.html               # 前端页面
```

---

**系统状态**: ✅ 运行中
**最后更新**: 2025-12-22 21:23:00
**版本**: 1.0.0
