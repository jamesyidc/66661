# 买点3添加支撑压力线系统条件

## 更新时间
2025-12-12

## 需求说明
为买点3（空转多买入）添加第6个必须条件：**支撑压力线系统**

### 新增条件6：支撑压力线系统
- **情况1**：接近支撑2（48小时低点）距离 ≥ 8%
- **情况2**：接近支撑1（7天低点）距离 ≥ 8%

**逻辑**：满足其中任何一个情况即可（OR逻辑）

## 实现方案

### 1. 数据库字段使用
从 `support_resistance_levels` 表中获取：
- `distance_to_support_1`：距离支撑线1（7天最低点）的百分比距离
- `distance_to_support_2`：距离支撑线2（48小时最低点）的百分比距离

### 2. 代码修改

#### A. 更新SQL查询（app_new.py 第5202行）
```python
# 添加 distance_to_support_2 字段
cursor.execute('''
    SELECT symbol, current_price, support_line_1, support_line_2, resistance_line_1,
           distance_to_support_1, distance_to_support_2, distance_to_resistance_1,
           position_s2_r1, record_time
    FROM support_resistance_levels
    WHERE id IN (
        SELECT MAX(id) 
        FROM support_resistance_levels 
        GROUP BY symbol
    )
''')
```

#### B. 添加条件判断逻辑（app_new.py 第5345-5365行）
```python
# 获取距离支撑线1和支撑线2的距离
distance = sr.get('distance_to_support_1')
distance_to_support_2 = sr.get('distance_to_support_2')

# 买点3新增条件6：支撑压力线系统
# 情况1：接近支撑2 >= 8%
# 情况2：接近支撑1 >= 8%
condition_support_system = (
    (distance_to_support_2 is not None and distance_to_support_2 >= 8) or 
    (distance is not None and distance >= 8)
)
```

#### C. 更新买点3判断逻辑（app_new.py 第5372-5393行）
```python
# 买点3: 空转多买入（重新定义条件）
# 6个必须条件：
# 1. 创新低后连续5个5分钟K线不创新低
# 2. 1小时RSI < 15
# 3. 5分钟周期连续3个震荡≤0.5% 且涨跌<0.25%
# 4. SAR空头数量 > 20
# 5. 5分钟SAR在第三象限
# 6. 支撑压力线系统：接近支撑2 >= 8% 或 接近支撑1 >= 8%
if (condition_no_new_low_5m and 
    condition_rsi_1h_low and 
    condition_oscillation_3 and 
    condition_sar_count and 
    condition_sar_quadrant3 and 
    condition_support_system):  # ✅ 新增条件
    buy_point_3 = True
    buy_point_3_count += 1
```

#### D. 更新详细条件显示（app_new.py 第5417-5427行）
```python
'buy_point_3_conditions': {
    'no_new_low_5m': {...},
    'rsi_1h': {...},
    'oscillation_3': {...},
    'sar_count': {...},
    'sar_quadrant': {...},
    'support_system': {  # ✅ 新增
        'value': f'支撑1: {round(distance, 2) if distance else "N/A"}%, 支撑2: {round(distance_to_support_2, 2) if distance_to_support_2 else "N/A"}%', 
        'threshold': '支撑1 ≥ 8% 或 支撑2 ≥ 8%', 
        'pass': condition_support_system, 
        'desc': '支撑压力线系统'
    }
}
```

#### E. 更新买点规则说明（app_new.py 第5546-5557行）
```python
'buy_point_3': {
    'name': '买点3 - 空转多买入',
    'suggested_position': '最多20% (如无开仓逻辑建议)',
    'conditions': [
        {'id': '5分钟不创新低', 'rule': '创新低后连续5个5分钟K线不创新低', 'priority': 'high'},
        {'id': '1h RSI', 'rule': '1小时RSI < 15', 'priority': 'high'},
        {'id': '连续震荡', 'rule': '5分钟周期连续3个震荡≤0.5% 且涨跌<0.25%', 'priority': 'high'},
        {'id': 'SAR空头数', 'rule': 'SAR空头持续数量 > 20', 'priority': 'high'},
        {'id': 'SAR象限', 'rule': '5分钟SAR在第三象限', 'priority': 'high'},
        {'id': '支撑压力线', 'rule': '接近支撑1 ≥ 8% 或 接近支撑2 ≥ 8%', 'priority': 'high'}  # ✅ 新增
    ],
    'description': '极度超卖后的空转多买入机会，严格条件筛选（需远离支撑线）'  # ✅ 更新描述
}
```

## 条件逻辑说明

### 为什么要求距离 ≥ 8%？
买点3是"空转多"买入点，专门捕捉**极度超卖后的反转机会**：

1. **远离支撑线**：价格需要距离支撑线足够远（≥8%），说明已经经历了较大跌幅
2. **避免支撑线反弹**：如果价格接近支撑线（<8%），更适合买点1（支撑线买入）
3. **空转多特征**：价格在低位盘整震荡，但距离支撑线较远，等待空头趋势结束、多头反转

### 条件组合逻辑
| 条件编号 | 条件名称 | 阈值 | 作用 |
|---------|---------|------|------|
| 1 | 5分钟不创新低 | 连续5个K线 | 确认下跌趋势放缓 |
| 2 | 1小时RSI | < 15 | 确认极度超卖 |
| 3 | 连续震荡 | 3个≤0.5% | 确认横盘整理 |
| 4 | SAR空头数量 | > 20 | 确认空头已持续较长时间 |
| 5 | SAR第三象限 | = 3 | 确认空头趋势末期 |
| 6 | 支撑压力线 | ≥ 8% | 确认远离支撑线，空间充足 |

### 距离计算方式
```python
# 距离支撑线的百分比计算（已在support_resistance_collector.py中实现）
distance_to_support = ((current_price - support_line) / support_line) * 100

# 示例：
# 当前价格：100 USDT
# 支撑线1（7天最低）：90 USDT
# 距离 = ((100 - 90) / 90) * 100 = 11.11%  ✅ 满足 ≥ 8%

# 当前价格：100 USDT
# 支撑线2（48h最低）：95 USDT
# 距离 = ((100 - 95) / 95) * 100 = 5.26%  ❌ 不满足 ≥ 8%
```

## 测试验证

### 测试API端点
```bash
curl -s http://localhost:5000/api/trading-signals/analyze | python3 -m json.tool
```

### 预期输出（买点3信号示例）
```json
{
  "symbol": "BTC",
  "buy_point_3": true,
  "detailed_conditions": {
    "buy_point_3_conditions": {
      "no_new_low_5m": {"pass": true, "value": "是"},
      "rsi_1h": {"pass": true, "value": 12.5},
      "oscillation_3": {"pass": true, "value": "是"},
      "sar_count": {"pass": true, "value": 25},
      "sar_quadrant": {"pass": true, "value": 3},
      "support_system": {
        "pass": true,
        "value": "支撑1: 10.5%, 支撑2: 6.8%",
        "threshold": "支撑1 ≥ 8% 或 支撑2 ≥ 8%",
        "desc": "支撑压力线系统"
      }
    }
  }
}
```

### 验证要点
1. ✅ 买点3信号数量是否正确
2. ✅ `support_system` 条件是否正常显示
3. ✅ 距离支撑线的百分比计算是否准确
4. ✅ OR逻辑是否生效（支撑1或支撑2任一满足即可）

## 前端UI更新需求

### 交易信号页面 (templates/trading_signals.html)
需要在买点3的详细条件展示中添加：

```html
<!-- 买点3条件6：支撑压力线系统 -->
<tr>
  <td>6. 支撑压力线系统</td>
  <td>
    <span class="condition-value">{{ support_distance }}</span>
  </td>
  <td>支撑1 ≥ 8% 或 支撑2 ≥ 8%</td>
  <td>
    <span class="badge {{ 'badge-success' if pass else 'badge-danger' }}">
      {{ '✓' if pass else '✗' }}
    </span>
  </td>
</tr>
```

## 影响范围

### 修改的文件
- `app_new.py` - 交易信号分析API逻辑

### 影响的功能
- 买点3（空转多买入）信号筛选
- 交易信号统计数量
- 详细条件透明化显示

### 数据依赖
- `support_resistance_levels` 表的实时数据
- `distance_to_support_1` 和 `distance_to_support_2` 字段

## 部署状态

✅ **已完成**：
1. 代码修改完成
2. Flask应用已重启
3. API测试通过

📋 **待验证**：
1. 实际交易信号测试
2. 前端UI展示更新
3. 条件逻辑验证

## 相关文档

- 支撑压力线系统：`SUPPORT_RESISTANCE_README.md`
- 买点3原始逻辑：`BUY_POINT_3_POSITION_LOGIC.md`
- 交易信号系统：`TRADING_SIGNAL_TRACKING_FEATURE.md`

## 注意事项

1. **距离计算正负**：距离支撑线的值为正数（当前价格 > 支撑线）
2. **NULL值处理**：如果距离为NULL，该条件判断为False
3. **OR逻辑**：支撑1和支撑2任一满足即可，提供更多交易机会
4. **数据时效性**：依赖support_resistance_collector实时更新数据

## 测试场景

### 场景1：满足支撑1条件
```
当前价格：100 USDT
支撑1距离：10%  ✅ ≥ 8%
支撑2距离：5%   ❌ < 8%
→ 结果：满足条件6 ✅
```

### 场景2：满足支撑2条件
```
当前价格：100 USDT
支撑1距离：6%   ❌ < 8%
支撑2距离：9%   ✅ ≥ 8%
→ 结果：满足条件6 ✅
```

### 场景3：两个都满足
```
当前价格：100 USDT
支撑1距离：12%  ✅ ≥ 8%
支撑2距离：10%  ✅ ≥ 8%
→ 结果：满足条件6 ✅
```

### 场景4：两个都不满足
```
当前价格：100 USDT
支撑1距离：5%   ❌ < 8%
支撑2距离：6%   ❌ < 8%
→ 结果：不满足条件6 ❌
```

## 总结

本次更新为买点3添加了支撑压力线系统作为第6个必须条件，要求价格距离支撑线1或支撑线2至少8%，确保空转多信号出现在远离支撑线的区域，提高信号质量并避免与买点1（支撑线买入）的逻辑冲突。
