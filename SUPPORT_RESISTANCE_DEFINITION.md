# 支撑/压力线定义说明

## 定义确认

本系统中的支撑/压力线定义**完全正确**,符合用户要求:

### 📊 支撑线定义

- **支撑线1 (support_line_1)** = **7天最低价**
  - 计算方法: 取最近 7天(168小时) 所有5分钟K线的最低价(low)的最小值
  - 代码位置: `support_resistance_collector.py` 第120行
  - 代码: `support_line_1 = min([k['low'] for k in klines_7d])`

- **支撑线2 (support_line_2)** = **48小时最低价**
  - 计算方法: 取最近 48小时 所有5分钟K线的最低价(low)的最小值
  - 代码位置: `support_resistance_collector.py` 第132行
  - 代码: `support_line_2 = min([k['low'] for k in klines_48h])`

### 📈 压力线定义

- **压力线1 (resistance_line_1)** = **7天最高价**
  - 计算方法: 取最近 7天(168小时) 所有5分钟K线的最高价(high)的最大值
  - 代码位置: `support_resistance_collector.py` 第121行
  - 代码: `resistance_line_1 = max([k['high'] for k in klines_7d])`

- **压力线2 (resistance_line_2)** = **48小时最高价**
  - 计算方法: 取最近 48小时 所有5分钟K线的最高价(high)的最大值
  - 代码位置: `support_resistance_collector.py` 第133行
  - 代码: `resistance_line_2 = max([k['high'] for k in klines_48h])`

## 数据来源

- **数据源**: OKX 永续合约市场 (OKX SWAP)
- **K线周期**: 5分钟
- **更新频率**: 每5分钟采集一次
- **采集器**: `support_resistance_collector.py`
- **存储表**: `support_resistance_levels`

## 逻辑关系验证

根据定义,应该满足以下逻辑关系:

1. **支撑线关系**: `支撑线2(48h最低) >= 支撑线1(7天最低)`
   - 原因: 48小时是7天的子集,48小时的最低价不可能低于7天的最低价

2. **压力线关系**: `压力线2(48h最高) <= 压力线1(7天最高)`
   - 原因: 48小时是7天的子集,48小时的最高价不可能高于7天的最高价

## 实际数据示例

### 示例1: BTCUSDT (2025-12-14 21:50:15)
```
当前价格: $89,848.30
支撑线1(7天最低): $88,503.30
支撑线2(48h最低): $88,503.30
压力线1(7天最高): $90,450.00
压力线2(48h最高): $90,450.00

✅ 逻辑验证: 
  - 48h最低 ($88,503.30) >= 7天最低 ($88,503.30) ✅
  - 48h最高 ($90,450.00) <= 7天最高 ($90,450.00) ✅
```

### 示例2: ETHUSDT (2025-12-14 21:50:15)
```
当前价格: $3,102.39
支撑线1(7天最低): $3,046.55
支撑线2(48h最低): $3,046.55
压力线1(7天最高): $3,128.28
压力线2(48h最高): $3,128.28

✅ 逻辑验证:
  - 48h最低 ($3,046.55) >= 7天最低 ($3,046.55) ✅
  - 48h最高 ($3,128.28) <= 7天最高 ($3,128.28) ✅
```

### 示例3: CFXUSDT (2025-12-14 21:50:13)
```
当前价格: $0.0733
支撑线1(7天最低): $0.0718
支撑线2(48h最低): $0.0718
压力线1(7天最高): $0.0772
压力线2(48h最高): $0.0772

✅ 逻辑验证:
  - 48h最低 ($0.0718) >= 7天最低 ($0.0718) ✅
  - 48h最高 ($0.0772) <= 7天最高 ($0.0772) ✅
```

## 采集器状态

### 当前运行状态
```bash
# 检查采集器是否运行
ps aux | grep support_resistance_collector

# 查看采集日志
tail -f support_resistance_collector.log
```

### 采集器输出示例
```
[2025-12-14 21:50:17] ✅ 采集完成! 成功: 27, 失败: 0
[2025-12-14 21:50:17] ⏳ 等待5分钟后进行下一次采集...
```

### 手动启动采集器
```bash
cd /home/user/webapp
nohup python3 support_resistance_collector.py > support_resistance_collector.log 2>&1 &
```

## API 访问

### API 端点
```
GET /api/support-resistance/latest
```

### 返回示例
```json
{
  "success": true,
  "count": 27,
  "update_time": "2025-12-14 21:50:15",
  "data": [
    {
      "symbol": "BTCUSDT",
      "current_price": 89848.30,
      "support_line_1": 88503.30,   // 7天最低价
      "support_line_2": 88503.30,   // 48小时最低价
      "resistance_line_1": 90450.00, // 7天最高价
      "resistance_line_2": 90450.00, // 48小时最高价
      ...
    },
    ...
  ]
}
```

## 页面展示

支撑/压力线系统页面地址:
```
https://5000-iz6uddj6rs3xe48ilsyqq-cbeee0f9.sandbox.novita.ai/support-resistance
```

页面会显示:
- 所有27个监控币种的实时价格
- 支撑线1(7天最低)和支撑线2(48小时最低)
- 压力线1(7天最高)和压力线2(48小时最高)
- 各币种在支撑/压力区间的位置百分比
- 4种情况的警报信号

## 数据库表结构

### support_resistance_levels 表
```sql
CREATE TABLE support_resistance_levels (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL,
    current_price REAL,
    support_line_1 REAL,     -- 7天最低价
    support_line_2 REAL,     -- 48小时最低价
    resistance_line_1 REAL,  -- 7天最高价
    resistance_line_2 REAL,  -- 48小时最高价
    distance_to_support_1 REAL,
    distance_to_support_2 REAL,
    distance_to_resistance_1 REAL,
    distance_to_resistance_2 REAL,
    position_s2_r1 REAL,
    position_s1_r2 REAL,
    position_s1_r2_upper REAL,
    position_s1_r1 REAL,
    alert_scenario_1 INTEGER,
    alert_scenario_2 INTEGER,
    alert_scenario_3 INTEGER,
    alert_scenario_4 INTEGER,
    alert_triggered INTEGER,
    record_time TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 总结

✅ **支撑线1** = 7天最低价 (定义正确)  
✅ **支撑线2** = 48小时最低价 (定义正确)  
✅ **压力线1** = 7天最高价 (定义正确)  
✅ **压力线2** = 48小时最高价 (定义正确)  

**采集器状态**: ✅ 正常运行  
**数据更新**: ✅ 每5分钟自动更新  
**逻辑验证**: ✅ 所有数据符合逻辑关系  
**API 访问**: ✅ 正常返回最新数据
