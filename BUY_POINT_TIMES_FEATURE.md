# 买点分批买入次数功能文档

## 功能概述

在交易信号系统中，为每个买点设置了分批买入次数（Buy Times），帮助用户合理分散风险，实现更精细的仓位管理。

## 买入次数配置

### 买点1 - 支撑线买入
- **买入次数**: 3次
- **建议仓位**: 30%
- **说明**: 分3次买入，每次买入约10%仓位（30% ÷ 3）

### 买点2 - 回调买入  
- **买入次数**: 2次
- **建议仓位**: 20%
- **说明**: 分2次买入，每次买入约10%仓位（20% ÷ 2）

### 买点3 - 空转多买入
- **买入次数**: 2次
- **建议仓位**: 最多20% (如无开仓逻辑建议) 或 最高70% (开仓逻辑建议 + 20%)
- **说明**: 分2次买入，每次买入约为总建议仓位的50%

## 实施逻辑

### 后端实现 (`app_new.py`)

```python
buy_times = None  # 分批买入次数

if buy_point_1:
    buy_point_type = 'buy_point_1'
    suggested_position = '30%'
    buy_times = 3  # 买点1分3次买入
    position_calculation_note = '买点1固定仓位，分3次买入'
    
elif buy_point_3:
    buy_point_type = 'buy_point_3'
    buy_times = 2  # 买点3分2次买入
    if opening_can_long and opening_position_percent > 0:
        bp3_position = min(opening_position_percent + 20, 70)
        suggested_position = f'{int(bp3_position)}%'
        position_calculation_note = f'开仓逻辑{int(opening_position_percent)}% + 买点3加成20% = {int(bp3_position)}% (上限70%)，分2次买入'
    else:
        suggested_position = '20%'
        position_calculation_note = '开仓逻辑不允许，买点3可额外开20%，分2次买入'
        
elif buy_point_2:
    buy_point_type = 'buy_point_2'
    suggested_position = '20%'
    buy_times = 2  # 买点2分2次买入
    position_calculation_note = '买点2固定仓位，分2次买入'

signals.append({
    'symbol': coin_name,
    'suggested_position': suggested_position,
    'buy_times': buy_times,  # 新增字段
    'position_calculation_note': position_calculation_note
})
```

### 前端显示 (`trading_signals.html`)

#### 1. 统计卡片显示
```html
<div class="stat-card">
    <h3>买点1信号</h3>
    <div class="value buy" id="buyPoint1Count">-</div>
    <div style="font-size: 12px; color: rgba(255,255,255,0.6); margin-top: 5px;">
        建议仓位30% (分3次买入)
    </div>
</div>
```

#### 2. 信号列表表格
新增"买入次数"列，显示每个信号的分批买入次数：

```javascript
<td style="color: #fbbf24; font-weight: bold; font-size: 16px; text-align: center;">
    ${signal.buy_times ? signal.buy_times + '次' : '-'}
</td>
```

#### 3. 图例说明
```html
<div class="legend-item">
    <span class="legend-label">买点1:</span>
    <span>达到支撑线1 (距离<5%) + 条件1-4 【建议仓位30%，分3次买入】</span>
</div>
```

## 使用场景

### 场景1：买点1信号触发
- 币种触发买点1（达到支撑线1）
- 系统建议仓位：30%
- 买入次数：3次
- 实际操作：
  - 第1次买入：10%
  - 第2次买入：10%  
  - 第3次买入：10%

### 场景2：买点2信号触发  
- 币种触发买点2（回调买入）
- 系统建议仓位：20%
- 买入次数：2次
- 实际操作：
  - 第1次买入：10%
  - 第2次买入：10%

### 场景3：买点3信号触发（开仓逻辑允许）
- 币种触发买点3（空转多买入）
- 开仓逻辑建议：50%
- 系统建议仓位：50% + 20% = 70%（上限）
- 买入次数：2次
- 实际操作：
  - 第1次买入：35%
  - 第2次买入：35%

### 场景4：买点3信号触发（开仓逻辑不允许）
- 币种触发买点3（空转多买入）
- 开仓逻辑：不允许
- 系统建议仓位：20%（买点3可额外开仓）
- 买入次数：2次
- 实际操作：
  - 第1次买入：10%
  - 第2次买入：10%

## 显示位置

### 交易信号页面 (`/trading-signals`)

1. **顶部统计卡片**
   - 买点1信号：显示 "建议仓位30% (分3次买入)"
   - 买点2信号：显示 "建议仓位20% (分2次买入)"
   - 买点3信号：显示 "最多20% (分2次买入)"

2. **信号列表表格**
   - 新增"买入次数"列（在"建议仓位"和"首次开仓"之间）
   - 显示格式：`3次`、`2次`

3. **图例说明**
   - 每个买点的说明中包含分批买入次数信息

## 优势

1. **风险分散**: 通过分批买入降低单次买入的风险
2. **价格平滑**: 在不同价位买入，获得更优的平均成本
3. **心理优势**: 避免一次性满仓带来的心理压力
4. **灵活调整**: 根据市场变化灵活调整后续买入计划

## API返回示例

```json
{
    "success": true,
    "data": {
        "buy_point_1_count": 2,
        "buy_point_2_count": 1,
        "buy_point_3_count": 3,
        "signals": [
            {
                "symbol": "BTC",
                "suggested_position": "30%",
                "buy_times": 3,
                "position_calculation_note": "买点1固定仓位，分3次买入",
                "buy_point_1": true,
                "buy_point_2": false,
                "buy_point_3": false
            },
            {
                "symbol": "ETH",
                "suggested_position": "20%",
                "buy_times": 2,
                "position_calculation_note": "买点2固定仓位，分2次买入",
                "buy_point_1": false,
                "buy_point_2": true,
                "buy_point_3": false
            }
        ]
    }
}
```

## 访问地址

- 交易信号页面：https://5000-iypypqmz2wvn9dmtq7ewn-583b4d74.sandbox.novita.ai/trading-signals
- API接口：https://5000-iypypqmz2wvn9dmtq7ewn-583b4d74.sandbox.novita.ai/api/trading-signals/analyze

## 版本信息

- 功能版本：v2.0
- 更新日期：2025-12-12
- 更新内容：添加买点分批买入次数显示功能

## 相关文档

- `BUY_POINT_3_SUPPORT_CONDITION_CORRECTED.md` - 买点3支撑线系统条件
- `BUY_POINT_3_POSITION_LOGIC.md` - 买点3仓位计算逻辑
- `OPENING_LOGIC_SYSTEM.md` - 开仓逻辑系统说明
