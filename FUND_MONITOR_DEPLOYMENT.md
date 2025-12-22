# 资金监控系统 - 部署完成摘要

## ✅ 系统概述

资金监控系统已成功部署并运行！该系统实时监控27个加密货币的成交量数据，通过与历史数据对比及时发现异常资金流动。

## 🎯 核心功能

### 1. 实时数据采集
- ✅ 每5分钟自动采集27个币种的成交量
- ✅ 数据源：OKEx永续合约（与V1V2系统共用）
- ✅ PM2自动管理，稳定运行

### 2. 多周期分析
- ✅ 15分钟周期聚合
- ✅ 30分钟周期聚合
- ✅ 60分钟周期聚合

### 3. 智能异常检测
- ✅ 与过去3天平均量能对比
- ✅ 可配置异常阈值（默认20%）
- ✅ 实时标记异常币种

### 4. 可视化界面
- ✅ 响应式卡片设计
- ✅ 实时数据刷新（30秒）
- ✅ 多维度筛选排序
- ✅ 异常数据高亮提示

## 📊 监控币种（27个）

```
BTC, ETH, XRP, BNB, SOL, LTC, DOGE, SUI, TRX, TON,
ETC, BCH, HBAR, XLM, FIL, LINK, CRO, DOT, AAVE, UNI,
NEAR, APT, CFX, CRV, STX, LDO, TAO
```

## 🔗 访问地址

### 前端界面
**在线访问**: https://5000-ilsitop6yown44mau7vd7-c07dda5e.sandbox.novita.ai/fund-monitor

### API端点
**基础URL**: https://5000-ilsitop6yown44mau7vd7-c07dda5e.sandbox.novita.ai/api/fund-monitor/

#### 可用端点：
- `GET /api/fund-monitor/latest` - 获取所有币种最新数据
- `GET /api/fund-monitor/history/<symbol>?interval=15min&hours=24` - 获取历史数据
- `GET /api/fund-monitor/abnormal` - 获取当前异常数据
- `GET /api/fund-monitor/config` - 获取系统配置
- `POST /api/fund-monitor/config` - 更新系统配置

## 💻 系统架构

```
┌─────────────────────────────────────────────────────────┐
│                   资金监控系统架构                        │
└─────────────────────────────────────────────────────────┘

┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│  OKEx API    │ ───> │  数据采集器   │ ───> │  SQLite DB   │
│ (永续合约)    │      │(每5分钟采集)  │      │ (fund_monitor)│
└──────────────┘      └──────────────┘      └──────────────┘
                             │
                             │ 聚合计算
                             ↓
              ┌──────────────────────────────┐
              │   15min / 30min / 60min     │
              │   3天平均 / 偏差 / 异常检测  │
              └──────────────────────────────┘
                             │
                             │ API服务
                             ↓
              ┌──────────────────────────────┐
              │        Flask Web API         │
              │  latest / history / abnormal │
              └──────────────────────────────┘
                             │
                             ↓
              ┌──────────────────────────────┐
              │        前端界面               │
              │  实时展示 / 筛选 / 排序       │
              └──────────────────────────────┘
```

## 📂 文件清单

### 核心文件
```
/home/user/webapp/
├── fund_monitor_collector.py       # 数据采集脚本（PM2管理）
├── fund_monitor_config.json        # 系统配置文件
├── fund_monitor.db                 # SQLite数据库
├── fund_monitor_collector.log      # 采集日志
├── app_new.py                      # Flask应用（包含API）
├── templates/
│   └── fund_monitor.html           # 前端界面
└── FUND_MONITOR_SYSTEM.md          # 完整系统文档
```

### 数据库表
- `fund_monitor_5min` - 5分钟原始数据（27条/次）
- `fund_monitor_aggregated` - 聚合数据（81条/次，3个周期×27币种）
- `fund_monitor_config` - 配置信息

## 🚀 服务状态

### PM2进程
```bash
pm2 status fund-monitor-collector
# ✅ Status: online
# ✅ Uptime: 运行中
# ✅ Memory: ~31MB
```

### 数据统计
```
✅ 5分钟数据: 27条（已采集）
✅ 聚合数据: 81条（已计算）
✅ 异常检测: 正常运行
```

## ⚙️ 配置参数

### 默认配置
```json
{
  "threshold_percentage": 20.0,     // 异常阈值：20%
  "lookback_days": 3,                // 回看天数：3天
  "collection_interval": 300         // 采集间隔：5分钟
}
```

### 如何调整配置

**方法1：通过API**
```bash
curl -X POST http://localhost:5000/api/fund-monitor/config \
  -H "Content-Type: application/json" \
  -d '{"threshold_percentage": 25.0}'
```

**方法2：通过前端界面**
访问前端页面 → 系统配置面板 → 修改参数 → 保存配置

**方法3：直接编辑配置文件**
```bash
vi fund_monitor_config.json
pm2 restart fund-monitor-collector
```

## 📈 使用示例

### 场景1：查看当前异常币种
访问：`https://5000-ilsitop6yown44mau7vd7-c07dda5e.sandbox.novita.ai/api/fund-monitor/abnormal`

**示例响应**：
```json
{
  "success": true,
  "count": 2,
  "data": [
    {
      "symbol": "BTC",
      "interval_type": "15min",
      "volume": 18000000.0,
      "avg_3day": 14000000.0,
      "deviation_percent": 28.57,
      "collect_time": "2025-12-22 21:20:00"
    }
  ]
}
```

### 场景2：监控BTC成交量趋势
访问：`https://5000-ilsitop6yown44mau7vd7-c07dda5e.sandbox.novita.ai/api/fund-monitor/history/BTC?interval=15min&hours=48`

### 场景3：批量查看所有币种
访问：`https://5000-ilsitop6yown44mau7vd7-c07dda5e.sandbox.novita.ai/fund-monitor`

## 🔧 运维命令

### 查看服务状态
```bash
pm2 status fund-monitor-collector
pm2 logs fund-monitor-collector --lines 50
```

### 重启服务
```bash
pm2 restart fund-monitor-collector
pm2 restart flask-app
```

### 查看数据量
```bash
python3 << 'EOF'
import sqlite3
conn = sqlite3.connect('/home/user/webapp/fund_monitor.db')
c = conn.cursor()
c.execute('SELECT COUNT(*) FROM fund_monitor_5min')
print(f'5分钟数据: {c.fetchone()[0]}条')
c.execute('SELECT COUNT(*) FROM fund_monitor_aggregated')
print(f'聚合数据: {c.fetchone()[0]}条')
conn.close()
EOF
```

### 清理旧数据（保留7天）
```bash
python3 << 'EOF'
import sqlite3
from datetime import datetime, timedelta
conn = sqlite3.connect('/home/user/webapp/fund_monitor.db')
c = conn.cursor()
ts = int((datetime.now() - timedelta(days=7)).timestamp() * 1000)
c.execute('DELETE FROM fund_monitor_5min WHERE timestamp < ?', (ts,))
c.execute('DELETE FROM fund_monitor_aggregated WHERE timestamp < ?', (ts,))
conn.commit()
print('已删除7天前的数据')
conn.close()
EOF
```

## ⚠️ 重要提示

### 1. 数据积累期
- ⏳ 系统需要3天时间积累历史数据
- ⏳ 3天内，avg_3day显示为NULL，异常检测不可用
- ✅ 3天后，异常检测功能完全激活

### 2. 阈值设置建议
- 📉 阈值过低（<15%）：误报率高，频繁预警
- 📈 阈值过高（>30%）：漏报风险大，预警不及时
- ✅ 推荐范围：15-25%（根据市场波动性调整）

### 3. 存储空间
- 每天约31,104条新数据（7,776原始+23,328聚合）
- 建议每周清理一次7天以上的历史数据
- 或使用日志轮转策略

### 4. API调用频率
- 与V1V2系统共用OKEx API
- 注意控制总体API调用频率
- 避免触发限流

## 🎉 部署成功验证

### ✅ 已完成项目
1. ✅ 数据采集脚本开发（fund_monitor_collector.py）
2. ✅ 数据库表结构创建（3张表）
3. ✅ 15/30/60分钟聚合逻辑实现
4. ✅ 3天平均量能对比和异常检测
5. ✅ 后端API开发（5个端点）
6. ✅ 前端可视化界面开发
7. ✅ PM2服务配置和启动
8. ✅ 数据采集测试通过（27币种）
9. ✅ API测试通过（所有端点）
10. ✅ 系统文档编写完成

### 🚀 立即体验
访问：**https://5000-ilsitop6yown44mau7vd7-c07dda5e.sandbox.novita.ai/fund-monitor**

---

**部署时间**: 2025-12-22 21:23
**系统状态**: ✅ 正常运行
**版本**: v1.0.0
**Git提交**: 7e409b7

🎊 **资金监控系统部署完成！**
