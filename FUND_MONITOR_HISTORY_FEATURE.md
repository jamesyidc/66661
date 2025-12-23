# 资金监控系统 - 异常数据历史记录功能

## 🎯 新增功能概述

现在资金监控系统支持**异常数据历史记录**功能，可以按日期查询历史异常数据，并通过时间轴方式展示。

---

## 📊 数据库结构

### 新增表：fund_monitor_abnormal_history

用于记录所有检测到的异常数据，便于后续分析和回溯。

```sql
CREATE TABLE fund_monitor_abnormal_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL,              -- 币种符号
    interval_type TEXT NOT NULL,       -- 时间周期（15min/30min/60min）
    timestamp INTEGER NOT NULL,        -- 时间戳（毫秒）
    collect_time TEXT NOT NULL,        -- 采集时间（北京时间 YYYY-MM-DD HH:MM:SS）
    collect_date TEXT NOT NULL,        -- 采集日期（YYYY-MM-DD，用于快速按日期查询）
    volume REAL NOT NULL,              -- 当前成交量
    avg_3day REAL NOT NULL,            -- 过去3天平均成交量
    deviation_percent REAL NOT NULL,   -- 偏差百分比
    deviation_type TEXT NOT NULL,      -- 偏差类型：surge（激增）或drop（骤降）
    severity TEXT NOT NULL,            -- 严重程度：critical（严重）/ high（高）/ medium（中等）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 索引
- `idx_abnormal_date` - 按日期索引（DESC）
- `idx_abnormal_symbol_date` - 按币种+日期复合索引
- `idx_abnormal_timestamp` - 按时间戳索引

---

## 🚀 功能特性

### 1. 自动记录异常数据
- ✅ 采集器检测到异常时自动记录到历史表
- ✅ 记录偏差类型（激增/骤降）
- ✅ 自动判定严重程度（严重/高/中等）
  - **严重**：偏差 ≥ 50%
  - **高**：偏差 ≥ 30%
  - **中等**：偏差 ≥ 阈值（默认20%）

### 2. 按日期查询
- ✅ 查看有异常数据的日期列表
- ✅ 显示每个日期的统计信息：
  - 异常次数
  - 涉及币种数
  - 平均偏差百分比

### 3. 时间轴展示
- ✅ 选择日期后显示该日的异常时间轴
- ✅ 按小时分组展示
- ✅ 视觉化异常严重程度
- ✅ 详细显示每次异常的具体数据

### 4. 多维度筛选
支持按以下条件筛选异常数据：
- 📅 **日期**：单日或日期范围
- 💰 **币种**：27个币种任选
- ⏱️ **时间周期**：15min/30min/60min
- 📈 **异常类型**：激增/骤降
- ⚠️ **严重程度**：严重/高/中等

---

## 🔗 访问方式

### 前端页面
**历史查询页面**: https://5000-ilsitop6yown44mau7vd7-c07dda5e.sandbox.novita.ai/fund-monitor-history

从实时监控页面也可以直接跳转到历史查询。

### API端点

#### 1. 获取有异常数据的日期列表
```
GET /api/fund-monitor/abnormal-dates
```

**响应示例**：
```json
{
  "success": true,
  "dates": [
    {
      "date": "2025-12-22",
      "count": 78,
      "affected_coins": 26,
      "avg_deviation": 177.03
    }
  ]
}
```

#### 2. 查询异常数据历史
```
GET /api/fund-monitor/abnormal-history?date=YYYY-MM-DD
GET /api/fund-monitor/abnormal-history?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD
GET /api/fund-monitor/abnormal-history?symbol=BTC&interval=15min
```

**查询参数**：
- `date`: 查询指定日期
- `start_date`: 开始日期
- `end_date`: 结束日期
- `symbol`: 币种（BTC, ETH等）
- `interval`: 时间周期（15min, 30min, 60min）
- `severity`: 严重程度（critical, high, medium）
- `type`: 异常类型（surge, drop）
- `limit`: 返回记录数（默认100）

**响应示例**：
```json
{
  "success": true,
  "total_count": 78,
  "returned_count": 78,
  "data": [
    {
      "id": 1,
      "symbol": "BTC",
      "interval_type": "15min",
      "timestamp": 1734854400000,
      "collect_time": "2025-12-22 20:00:00",
      "collect_date": "2025-12-22",
      "volume": 45000000.00,
      "avg_3day": 15000000.00,
      "deviation_percent": 200.00,
      "deviation_type": "surge",
      "severity": "critical"
    }
  ]
}
```

#### 3. 获取指定日期的时间轴
```
GET /api/fund-monitor/abnormal-timeline?date=YYYY-MM-DD
```

**响应示例**：
```json
{
  "success": true,
  "date": "2025-12-22",
  "timeline": [
    {
      "hour": "2025-12-22 20",
      "count": 5,
      "events": [
        {
          "symbol": "BTC",
          "interval_type": "15min",
          "time": "2025-12-22 20:15:00",
          "volume": 45000000.00,
          "avg_3day": 15000000.00,
          "deviation_percent": 200.00,
          "deviation_type": "surge",
          "severity": "critical"
        }
      ]
    }
  ]
}
```

---

## 💻 使用示例

### 场景1：查看今天有哪些异常
1. 访问历史查询页面
2. 点击"查看日期列表"
3. 点击今天的日期卡片
4. 查看时间轴上的所有异常事件

### 场景2：查询BTC的所有异常记录
1. 访问历史查询页面
2. 选择币种：BTC
3. 点击"查询"按钮
4. 查看结果列表

### 场景3：查询本周的严重异常
1. 设置开始日期和结束日期
2. 选择严重程度：严重
3. 点击"查询"按钮

### 场景4：使用API查询
```bash
# 查询12月22日BTC的异常
curl "http://localhost:5000/api/fund-monitor/abnormal-history?date=2025-12-22&symbol=BTC"

# 查询最近3天的所有严重异常
curl "http://localhost:5000/api/fund-monitor/abnormal-history?start_date=2025-12-20&end_date=2025-12-22&severity=critical"

# 查询ETH在15分钟周期的激增异常
curl "http://localhost:5000/api/fund-monitor/abnormal-history?symbol=ETH&interval=15min&type=surge"
```

---

## 📈 数据分析价值

### 1. 市场行为分析
- 识别历史上的重大资金流动事件
- 分析异常波动的时间规律
- 发现哪些币种容易出现异常

### 2. 策略优化
- 根据历史异常调整监控阈值
- 识别虚假信号的特征
- 优化交易策略的进出场时机

### 3. 风险管理
- 回溯重大市场事件
- 评估系统预警的准确性
- 建立风险预警模型

---

## 🎨 前端界面特性

### 日期列表视图
- 📅 卡片式展示有异常的日期
- 📊 显示每日统计信息
- 🖱️ 点击日期查看详细时间轴

### 时间轴视图
- ⏰ 按小时分组显示
- 🔴 视觉化严重程度（红色点大小和动画）
- 📋 详细的事件卡片
- 🎨 激增（绿色）/骤降（红色）颜色区分

### 搜索筛选面板
- 🔍 多维度筛选条件
- 📊 实时统计显示
- 🔄 一键清空筛选

---

## 🔧 技术实现

### 数据记录机制
```python
# 在store_aggregated_data函数中
if abs(deviation_percent) >= CONFIG['threshold_percentage']:
    is_abnormal = 1
    # 记录到异常历史表
    store_abnormal_history(conn, symbol, timestamp, interval_minutes, 
                           volume, avg_3day, deviation_percent)
```

### 严重程度判定
```python
abs_deviation = abs(deviation_percent)
if abs_deviation >= 50:
    severity = 'critical'  # 严重
elif abs_deviation >= 30:
    severity = 'high'  # 高
else:
    severity = 'medium'  # 中等
```

### 查询优化
- 使用日期索引加速按日期查询
- 复合索引支持币种+日期联合查询
- 时间戳索引支持时间范围查询

---

## 📊 统计数据示例

**当前系统状态（2025-12-22）**：
- ✅ 已记录异常数据：78条
- ✅ 涉及币种：26个
- ✅ 平均偏差：177.03%
- ✅ 历史记录表运行正常

---

## ⚙️ 配置说明

### 阈值影响
- 阈值越低，记录的异常数据越多
- 阈值越高，只记录明显的异常
- 建议：根据历史数据调整到合适的敏感度

### 存储空间
- 每条异常记录约150字节
- 每天预计100-200条记录
- 建议定期归档6个月以上的数据

---

## 🔄 系统集成

### 与实时监控的关系
- ✅ 实时监控：关注当前状态
- ✅ 历史查询：分析过去趋势
- ✅ 互相补充，形成完整的监控体系

### 未来扩展
- [ ] 导出历史数据为Excel/CSV
- [ ] 异常事件的图表分析
- [ ] 自动生成异常报告
- [ ] 异常事件关联分析
- [ ] 机器学习预测异常

---

## 📱 快速链接

- **实时监控**: https://5000-ilsitop6yown44mau7vd7-c07dda5e.sandbox.novita.ai/fund-monitor
- **历史查询**: https://5000-ilsitop6yown44mau7vd7-c07dda5e.sandbox.novita.ai/fund-monitor-history
- **API文档**: `/api/fund-monitor/abnormal-*`

---

**更新时间**: 2025-12-22 21:35
**版本**: v1.1.0
**状态**: ✅ 已部署并运行
