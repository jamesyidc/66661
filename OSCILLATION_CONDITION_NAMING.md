# K线震荡条件命名规范与引用指南

## 📋 标准命名

### 1. 函数命名
```python
check_consecutive_oscillation_5min(symbol)
```
**用途：** 检查5分钟K线是否连续3个周期满足震荡条件

### 2. 变量命名
```python
condition_oscillation_3  # 布尔值：True/False
```
**含义：** 连续3个震荡条件是否满足

### 3. 条件描述
```python
'连续3个震荡≤0.5% 且涨跌<0.25%'
```

### 4. 英文命名
```python
consecutive_oscillation_condition
low_volatility_sequence
```

## 🎯 详细定义

### 中文全称
**"连续3个5分钟K线低波动震荡条件"**

### 简称选项
1. **连续震荡条件** ✅ 推荐
2. **震荡条件3** 
3. **低波动条件**
4. **5分钟震荡序列**

### 核心参数
```javascript
{
    period: '5分钟',          // K线周期
    consecutiveCount: 3,      // 连续数量
    volatilityMax: 0.5,       // 震荡幅度上限 (%)
    changePctMax: 0.25        // 涨跌幅上限 (%)
}
```

## 📚 引用方式

### 1. 在文档中引用
```markdown
**买点3条件5**：连续3个震荡≤0.5% 且涨跌<0.25%
```

### 2. 在代码注释中引用
```python
# 检查连续震荡条件（买点3条件5）
condition_oscillation_3 = check_consecutive_oscillation_5min(coin_name)
```

### 3. 在API返回中引用
```json
{
    "oscillation_3": {
        "value": "是",
        "threshold": "是",
        "pass": true,
        "desc": "连续3个震荡≤0.5% 且涨跌<0.25%"
    }
}
```

### 4. 在前端显示中引用
```html
<div class="condition-tag">
    震荡条件: 连续3个 ✅
</div>
```

### 5. 在说明文档中引用
```
条件5: 连续3个5分钟周期震荡≤0.5% 且涨跌<0.25%
```

## 🔗 关联术语

### 相关概念
| 术语 | 说明 |
|------|------|
| 低波动K线 | 单根K线满足震荡条件 |
| 连续震荡 | 多根K线连续满足震荡条件 |
| 震荡幅度 | (最高价 - 最低价) / 开盘价 |
| 涨跌幅 | (收盘价 - 开盘价) / 开盘价 |

### 英文对照
| 中文 | 英文 |
|------|------|
| 震荡 | Oscillation / Volatility |
| 连续 | Consecutive |
| 低波动 | Low Volatility |
| K线 | Candlestick / Kline |

## 📊 使用场景

### 场景1：买点3判断
```python
# 买点3的6个条件之一
if (condition_no_new_low_5m and 
    condition_rsi_1h_low and 
    condition_oscillation_3 and  # ← 这里
    condition_sar_count and 
    condition_sar_quadrant3 and
    condition6_support_system):
    # 满足买点3
```

### 场景2：K线图标记
```javascript
// 在K线图上标记低波动序列
const lowVolatilityMarkers = [];
for (let i = 0; i < ohlc.length; i++) {
    if (changePct <= 0.25 && volatilityPct <= 0.50) {
        consecutiveCount++;
    }
}
```

### 场景3：交易信号显示
```html
<div class="condition-item">
    <span class="label">震荡条件:</span>
    <span class="value">连续3个 ✅</span>
</div>
```

## 💬 口语化表达

### 正式表达
"该币种满足连续3个5分钟K线低波动震荡条件"

### 简化表达
"震荡条件达标（连续3个）"

### 技术表达
"5min K-line consecutive oscillation condition (3 periods)"

### 中英混合
"连续3个oscillation满足条件"

## 📝 在不同文档中的引用示例

### 在README中
```markdown
## 买点3条件

5. **震荡条件**: 连续3个5分钟K线，震荡幅度≤0.5%，涨跌幅≤0.25%
```

### 在API文档中
```yaml
oscillation_3:
  type: boolean
  description: 连续3个震荡≤0.5% 且涨跌<0.25%
  required: true
```

### 在需求文档中
```
买点3需要检查"连续震荡条件"：
- 周期: 5分钟
- 连续数: 3个
- 震荡幅度: ≤0.5%
- 涨跌幅: ≤+0.25%
```

### 在Git提交信息中
```bash
feat: 添加连续震荡条件检测
fix: 修正震荡条件判断逻辑
docs: 更新震荡条件说明文档
```

## 🏷️ 标签与关键词

### 核心关键词
- 连续震荡
- 低波动
- 5分钟K线
- 震荡幅度
- 涨跌幅

### 搜索关键词
```
"连续3个震荡"
"oscillation_3"
"check_consecutive_oscillation"
"低波动K线"
"震荡≤0.5%"
"涨跌<0.25%"
```

## 📖 快速引用卡片

```
┌─────────────────────────────────────────┐
│ 条件名称：连续震荡条件                     │
├─────────────────────────────────────────┤
│ 代码变量：condition_oscillation_3        │
│ 函数名称：check_consecutive_oscillation  │
│ 完整描述：连续3个震荡≤0.5% 且涨跌<0.25%  │
├─────────────────────────────────────────┤
│ 应用场景：买点3条件5                      │
│ K线周期：5分钟                           │
│ 连续数量：3个                            │
├─────────────────────────────────────────┤
│ 判断条件：                               │
│  • 震荡幅度 ≤ 0.50%                     │
│  • 涨跌幅 ≤ +0.25%                      │
│  • 连续出现 ≥ 3次                       │
└─────────────────────────────────────────┘
```

## 🔍 系统中的实际位置

### Python后端 (`app_new.py`)
```python
# 第5348行
condition_oscillation_3 = check_consecutive_oscillation_5min(coin_name)

# 第5430行
'oscillation_3': {
    'value': '是' if condition_oscillation_3 else '否',
    'threshold': '是',
    'pass': condition_oscillation_3,
    'desc': '连续3个震荡≤0.5% 且涨跌<0.25%'
}
```

### 前端K线图 (`symbol_detail_v6.html`)
```javascript
// 第738行
// 🔥 检测低波动K线连续序列（涨跌幅≤0.25% 且 震荡幅度≤0.50%）

// 第749行
if (changePct <= 0.25 && volatilityPct <= 0.50) {
    consecutiveCount++;
}

// 第963行
name: `连续${marker.count}根低波动K线`
```

## 💡 建议的统一命名

为了系统一致性，建议在不同场景使用以下命名：

| 场景 | 推荐命名 |
|------|---------|
| Python函数 | `check_consecutive_oscillation_5min()` |
| Python变量 | `condition_oscillation_3` |
| JSON字段 | `oscillation_3` |
| 文档标题 | "连续震荡条件" |
| 前端显示 | "震荡条件3" 或 "连续3个震荡" |
| 用户说明 | "连续3个震荡≤0.5% 且涨跌<0.25%" |
| Git提交 | "连续震荡条件" 或 "oscillation condition" |

## 📞 快速回答

**Q: 这个条件叫什么？**  
A: **"连续震荡条件"** 或 **"连续3个震荡≤0.5% 且涨跌<0.25%"**

**Q: 代码里怎么引用？**  
A: `condition_oscillation_3` 或 `check_consecutive_oscillation_5min()`

**Q: 在文档里怎么说？**  
A: "连续震荡条件（买点3条件5）"

**Q: 跟别人口头表达？**  
A: "震荡条件"或"连续3个震荡"

---

**总结**：这个条件的标准简称是 **"连续震荡条件"**，完整描述是 **"连续3个5分钟K线震荡≤0.5%且涨跌≤0.25%"**
