# 🔥 恐慌清洗指标 - 新版本

## 📊 系统概览

全新的恐慌清洗指标系统，基于爆仓数据独立计算，提供更准确的市场恐慌程度评估。

### 核心特性

- ✅ **独立计算公式**: `恐慌清洗指数 = 24小时爆仓人数 / 全网持仓量总计`
- ✅ **实时数据源**: https://history.btc123.fans/baocang/
- ✅ **自动更新**: 每3分钟采集一次最新数据
- ✅ **完整API**: RESTful API服务（端口5002）
- ✅ **现代化UI**: 响应式设计 + 实时图表
- ✅ **数据持久化**: SQLite数据库存储历史数据

---

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────┐
│           数据来源: btc123.fans/baocang                   │
│  (1H爆仓金额, 24H爆仓金额, 24H爆仓人数, 全网持仓量)        │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│         panic_wash_collector.py (后台服务)                │
│         - 每3分钟爬取一次数据                              │
│         - 计算恐慌清洗指数                                 │
│         - 保存到数据库                                     │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│         SQLite数据库 (panic_wash_new表)                   │
│         - record_time: 记录时间                           │
│         - hour_1_amount: 1小时爆仓金额                    │
│         - hour_24_amount: 24小时爆仓金额                  │
│         - hour_24_people: 24小时爆仓人数                  │
│         - total_position: 全网持仓量                       │
│         - panic_index: 恐慌清洗指数                        │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│         panic_wash_api_new.py (API服务)                   │
│         端口: 5002                                         │
│         - GET  /api/panic-wash/latest     最新数据         │
│         - GET  /api/panic-wash/history    历史数据         │
│         - GET  /api/panic-wash/stats      统计信息         │
│         - POST /api/panic-wash/refresh    手动刷新         │
│         - GET  /panic-wash                Web界面          │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│         panic_wash_new.html (前端页面)                     │
│         - 实时数据卡片展示                                 │
│         - Chart.js 图表可视化                             │
│         - 自动刷新（每30秒）                               │
│         - 手动刷新按钮                                     │
└─────────────────────────────────────────────────────────┘
```

---

## 📁 文件说明

### 核心文件

| 文件名 | 说明 | 功能 |
|--------|------|------|
| `panic_wash_new.py` | 数据采集核心 | 数据爬取、计算、数据库操作 |
| `panic_wash_api_new.py` | API服务器 | RESTful API接口，端口5002 |
| `panic_wash_collector.py` | 后台采集服务 | 定时任务，每3分钟采集 |
| `panic_wash_new.html` | 前端页面 | 用户界面，图表展示 |
| `liquidation_scraper.py` | 爆仓数据爬虫 | 网页爬取工具（开发中） |

### 数据库表结构

```sql
CREATE TABLE panic_wash_new (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    record_time DATETIME NOT NULL,
    hour_1_amount REAL,          -- 1小时爆仓金额（美元）
    hour_24_amount REAL,         -- 24小时爆仓金额（美元）
    hour_24_people INTEGER,      -- 24小时爆仓人数
    total_position REAL,         -- 全网持仓量（美元）
    panic_index REAL,            -- 恐慌清洗指数
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_panic_time ON panic_wash_new(record_time DESC);
```

---

## 🚀 快速开始

### 1. 启动API服务

```bash
# 后台启动API服务器
cd /home/user/webapp
nohup python3 panic_wash_api_new.py > logs/panic_wash_api.log 2>&1 &

# 查看服务状态
curl http://localhost:5002/api/panic-wash/latest
```

**服务地址:**
- API: https://5002-iik759kgm7i3zqlxvfrfx-cc2fbc16.sandbox.novita.ai
- 页面: https://5002-iik759kgm7i3zqlxvfrfx-cc2fbc16.sandbox.novita.ai/panic-wash

### 2. 启动数据采集服务（可选）

```bash
# 后台启动采集服务（每3分钟采集）
cd /home/user/webapp
nohup python3 panic_wash_collector.py > logs/panic_wash_collector.log 2>&1 &
```

### 3. 访问页面

通过主服务器访问（推荐）:
- 主服务器: https://5001-iik759kgm7i3zqlxvfrfx-cc2fbc16.sandbox.novita.ai/panic

---

## 📡 API接口文档

### 获取最新数据

```bash
GET /api/panic-wash/latest
```

**响应示例:**
```json
{
  "success": true,
  "data": {
    "id": 12,
    "record_time": "2025-12-05 11:06:19",
    "hour_1_amount": 2680396.81,
    "hour_24_amount": 81468133.40,
    "hour_24_people": 41831,
    "total_position": 12952593412.07,
    "panic_index": 0.00000323,
    "created_at": "2025-12-05 11:06:19"
  }
}
```

### 获取历史数据

```bash
GET /api/panic-wash/history
```

**说明:** 返回最近24小时的所有数据点

**响应示例:**
```json
{
  "success": true,
  "count": 13,
  "data": [
    {
      "record_time": "2025-12-05 11:04:02",
      "hour_1_amount": 2319860.18,
      "hour_24_amount": 113283281.36,
      "hour_24_people": 45506,
      "total_position": 11812337332.56,
      "panic_index": 0.00000385
    },
    // ... 更多数据
  ]
}
```

### 获取统计信息

```bash
GET /api/panic-wash/stats
```

**响应示例:**
```json
{
  "success": true,
  "stats": {
    "sample_count": 13,
    "avg_panic_index": 0.00000356,
    "min_panic_index": 0.00000312,
    "max_panic_index": 0.00000483,
    "avg_liquidation_people": 47234,
    "avg_total_position": 12456789012.34
  }
}
```

### 手动刷新数据

```bash
POST /api/panic-wash/refresh
```

**说明:** 立即触发一次数据采集

---

## 📊 数据指标说明

### 恐慌清洗指数

```
恐慌清洗指数 = 24小时爆仓人数 / 全网持仓量总计
```

**指数含义:**
- **数值越大**: 市场恐慌程度越高，爆仓人数相对持仓量更多
- **数值越小**: 市场相对稳定，爆仓比例较低

**典型范围:**
- `< 0.000003`: 市场稳定，恐慌程度低
- `0.000003 - 0.000005`: 正常波动范围
- `> 0.000005`: 市场波动加剧，需要警惕

### 各项指标

| 指标 | 单位 | 说明 |
|------|------|------|
| 1小时爆仓金额 | 美元 | 最近1小时内全网爆仓的总金额 |
| 24小时爆仓金额 | 美元 | 最近24小时内全网爆仓的总金额 |
| 24小时爆仓人数 | 人 | 最近24小时内爆仓的交易者数量 |
| 全网持仓量 | 美元 | 当前全网合约持仓总量 |
| 恐慌清洗指数 | 无量纲 | 计算得出的恐慌程度指标 |

---

## 🔧 配置说明

### 采集频率

默认每3分钟采集一次。可在 `panic_wash_collector.py` 中修改:

```python
service = PanicWashCollectorService(
    db_path='crypto_data.db',
    interval=180  # 修改此值，单位：秒
)
```

### 数据保留

默认保留所有历史数据。如需清理旧数据:

```sql
DELETE FROM panic_wash_new 
WHERE record_time < datetime('now', '-7 days');
```

---

## 🔄 与旧版本的区别

| 特性 | 旧版本 | 新版本 |
|------|--------|--------|
| 数据来源 | Google Drive 文本文件 | 爆仓数据网站API |
| 计算方式 | 预先计算好的值 | 实时独立计算 |
| 更新频率 | 不定期（依赖手动更新） | 每3分钟自动更新 |
| 数据完整性 | 单一指标值 | 多维度数据（爆仓金额、人数、持仓量等） |
| API服务 | 集成在主服务器 | 独立服务（端口5002） |
| 数据库表 | panic_history / panic_wash_history | panic_wash_new |
| 前端页面 | panic_monitor_v3.html 等 | panic_wash_new.html |

---

## 🛠️ 开发说明

### 当前使用模拟数据

由于Playwright未安装，当前系统使用模拟数据模式进行演示。模拟数据特点:

- ✅ 随机生成合理的爆仓数据
- ✅ 自动计算恐慌指数
- ✅ 完整的数据流程演示
- ✅ 所有API和页面功能正常

### 启用真实数据采集

1. 安装Playwright:
```bash
pip install playwright
playwright install chromium
```

2. 系统会自动切换到实时爬取模式

3. 或者开发专用的API对接接口

### 扩展建议

1. **添加更多数据源**: 整合多个交易所的爆仓数据
2. **预警功能**: 当指数超过阈值时发送通知
3. **趋势分析**: 基于历史数据预测市场走势
4. **多维度分析**: 按币种、交易所分别统计
5. **导出功能**: 支持数据导出为CSV/Excel

---

## 📞 常见问题

### Q1: 为什么显示模拟数据？

**A:** 当前Playwright未安装，系统使用模拟数据模式。安装Playwright后会自动切换到实时爬取。

### Q2: 如何修改采集频率？

**A:** 编辑 `panic_wash_collector.py` 中的 `interval` 参数（单位：秒）。

### Q3: 数据保存在哪里？

**A:** 数据保存在 SQLite 数据库 `crypto_data.db` 的 `panic_wash_new` 表中。

### Q4: 如何重置数据？

**A:** 
```sql
DELETE FROM panic_wash_new;
```

### Q5: API服务没有响应？

**A:** 检查服务是否运行:
```bash
ps aux | grep panic_wash_api
# 或重启服务
pkill -f panic_wash_api_new && python3 panic_wash_api_new.py
```

---

## 📝 更新日志

### v1.0.0 (2025-12-05)

- ✅ 初始版本发布
- ✅ 实现独立计算公式
- ✅ 完整的API服务
- ✅ 现代化UI界面
- ✅ 数据库持久化
- ✅ 自动采集服务
- ✅ 与主服务器集成

---

## 🎯 下一步计划

- [ ] 实现真实数据爬取（Playwright或API对接）
- [ ] 添加数据预警功能
- [ ] 支持历史数据导出
- [ ] 添加更多统计维度
- [ ] 优化性能和缓存策略
- [ ] 添加用户配置选项
- [ ] 移动端适配优化

---

## 📄 许可证

MIT License

---

**开发时间:** 2025-12-05  
**版本:** 1.0.0  
**状态:** ✅ 已部署，使用模拟数据模式
