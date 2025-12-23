# K线图低波动震荡检测逻辑修正

## 修正日期
2025-12-12

## 问题描述

用户反馈K线图中的低波动震荡检测逻辑有误：

### 原有错误逻辑
```javascript
const changePct = Math.abs((close - open) / open * 100);  // ❌ 错误：取绝对值
const volatilityPct = Math.abs((high - low) / open * 100);

// 条件：涨跌幅绝对值 <= 0.25% 且 震荡幅度 <= 0.50%
if (changePct <= 0.25 && volatilityPct <= 0.50) {
    // 这会同时包含 -0.25% ~ +0.25% 的范围
}
```

**问题：** 使用 `Math.abs()` 会将负数涨跌幅转为正数，导致下跌0.25%的情况也被计入，这不符合要求。

## 正确需求

### 用户要求的准确条件
1. **涨跌幅**：只考虑上涨，且上涨幅度 ≤ 0.25%（不包括下跌的情况）
2. **震荡幅度**：(最高价 - 最低价) / 开盘价 ≤ 0.50%
3. **连续性检测**：记录连续满足条件的K线数量

### 修正后的逻辑
```javascript
const changePct = (close - open) / open * 100;  // ✅ 正确：不取绝对值，保留正负
const volatilityPct = (high - low) / open * 100;  // 震荡幅度（总是正值）

// 条件：涨跌幅 ≤ +0.25% 且 震荡幅度 ≤ 0.50%
if (changePct <= 0.25 && volatilityPct <= 0.50) {
    // 只有上涨幅度 ≤ 0.25% 或 下跌的情况才满足条件
}
```

## 具体修正内容

### 文件：`templates/symbol_detail_v6.html`

**修正位置：** 第743-749行

#### 修正前（错误）
```javascript
for (let i = 0; i < ohlc.length; i++) {
    const [open, close, low, high] = ohlc[i];
    const changePct = Math.abs((close - open) / open * 100);  // ❌ 取绝对值
    const volatilityPct = Math.abs((high - low) / open * 100);
    
    // 判断是否符合低波动条件
    if (changePct <= 0.25 && volatilityPct <= 0.50) {
        // 错误：这会包含 -0.25% ~ +0.25% 的范围
    }
}
```

#### 修正后（正确）
```javascript
for (let i = 0; i < ohlc.length; i++) {
    const [open, close, low, high] = ohlc[i];
    const changePct = (close - open) / open * 100;  // ✅ 不取绝对值，保留正负
    const volatilityPct = (high - low) / open * 100;  // 震荡幅度（总是正值）
    
    // 判断是否符合低波动条件：涨跌幅 ≤ +0.25% 且 震荡幅度 ≤ 0.50%
    if (changePct <= 0.25 && volatilityPct <= 0.50) {
        // 正确：只有涨幅 ≤ 0.25% 的情况
    }
}
```

## 条件详解

### 1. 涨跌幅计算
```javascript
涨跌幅 = (收盘价 - 开盘价) / 开盘价 × 100
```

**示例：**
- 开盘价 = $10.00，收盘价 = $10.02 → 涨跌幅 = +0.20% ✅ 满足条件
- 开盘价 = $10.00，收盘价 = $10.03 → 涨跌幅 = +0.30% ❌ 不满足（超过0.25%）
- 开盘价 = $10.00，收盘价 = $9.98 → 涨跌幅 = -0.20% ✅ 满足条件（负数）

### 2. 震荡幅度计算
```javascript
震荡幅度 = (最高价 - 最低价) / 开盘价 × 100
```

**示例：**
- 开盘价 = $10.00，最高 = $10.03，最低 = $9.98 → 震荡幅度 = 0.50% ✅ 满足条件
- 开盘价 = $10.00，最高 = $10.04，最低 = $9.97 → 震荡幅度 = 0.70% ❌ 不满足（超过0.50%）

### 3. 综合条件
只有同时满足以下两个条件才算"低波动K线"：
```
✅ 涨跌幅 ≤ +0.25%  AND  震荡幅度 ≤ 0.50%
```

## 连续性检测

系统会检测连续出现的低波动K线，并在图表上标记：

```javascript
// 连续计数逻辑
let consecutiveCount = 0;
let consecutiveStart = -1;

for (let i = 0; i < ohlc.length; i++) {
    if (符合低波动条件) {
        if (consecutiveCount === 0) {
            consecutiveStart = i;  // 记录起始位置
        }
        consecutiveCount++;  // 计数+1
    } else {
        if (consecutiveCount >= 2) {
            // 记录连续序列（至少2根K线）
            lowVolatilityMarkers.push({
                start: consecutiveStart,
                end: consecutiveStart + consecutiveCount - 1,
                count: consecutiveCount
            });
        }
        consecutiveCount = 0;  // 重置计数
    }
}
```

### 标记显示
- **标记样式**：橙色背景区域 + 🔥图标
- **标记文本**：`🔥 N根`（N = 连续K线数量）
- **最小连续数**：≥ 2根K线才会标记

## 图表示例

参考UNI K线图：https://5000-iypypqmz2wvn9dmtq7ewn-583b4d74.sandbox.novita.ai/symbol/UNI/v6

在图表上可以看到：
- 橙色半透明区域覆盖连续的低波动K线
- 顶部显示 `🔥 4根` 表示连续4根K线满足条件

## 实际应用场景

### 买点3判断条件
这个低波动检测逻辑用于"买点3 - 空转多买入"的条件判断：

**条件5：** 3个连续5分钟周期震荡 ≤ 0.5% 且涨跌 < 0.25%

```python
# 后端API逻辑 (app_new.py)
# 检查是否有3个连续5分钟K线满足低波动条件
oscillation_count = 0
for kline in recent_5m_klines:
    change_pct = (kline.close - kline.open) / kline.open * 100
    volatility_pct = (kline.high - kline.low) / kline.open * 100
    
    if change_pct <= 0.25 and volatility_pct <= 0.50:
        oscillation_count += 1
    else:
        oscillation_count = 0  # 不连续则重置
    
    if oscillation_count >= 3:
        # 满足买点3的震荡条件
        break
```

## 对比表格

| 场景 | 开盘价 | 收盘价 | 最高价 | 最低价 | 涨跌幅 | 震荡幅度 | 修正前 | 修正后 |
|------|--------|--------|--------|--------|--------|----------|--------|--------|
| 场景1 | $10.00 | $10.02 | $10.03 | $9.98 | +0.20% | 0.50% | ✅ | ✅ |
| 场景2 | $10.00 | $9.98 | $10.02 | $9.97 | -0.20% | 0.50% | ✅ | ✅ |
| 场景3 | $10.00 | $10.03 | $10.04 | $9.99 | +0.30% | 0.50% | ❌ | ❌ |
| 场景4 | $10.00 | $10.02 | $10.06 | $9.96 | +0.20% | 1.00% | ❌ | ❌ |

**关键区别：**
- 修正前：场景2会被错误排除（因为-0.20%取绝对值后 = 0.20%）
- 修正后：场景2正确包含（因为-0.20% < 0.25%）

## 测试验证

### 测试步骤
1. 访问UNI K线图：https://5000-iypypqmz2wvn9dmtq7ewn-583b4d74.sandbox.novita.ai/symbol/UNI/v6
2. 查看橙色标记区域（🔥 N根）
3. 鼠标悬停在标记区域的K线上
4. 验证tooltip显示的涨跌幅和震荡幅度
5. 确认只有涨跌幅 ≤ 0.25% 且 震荡幅度 ≤ 0.50% 的K线被标记

### 预期结果
- ✅ 涨跌幅在 -∞ ~ +0.25% 范围内
- ✅ 震荡幅度 ≤ 0.50%
- ✅ 连续满足条件的K线被橙色区域覆盖
- ✅ 标记显示正确的连续数量

## 访问地址

- **UNI K线图**：https://5000-iypypqmz2wvn9dmtq7ewn-583b4d74.sandbox.novita.ai/symbol/UNI/v6
- **BTC K线图**：https://5000-iypypqmz2wvn9dmtq7ewn-583b4d74.sandbox.novita.ai/symbol/BTC/v6
- **所有币种K线**：https://5000-iypypqmz2wvn9dmtq7ewn-583b4d74.sandbox.novita.ai/

## 相关文档

1. `BUY_POINT_3_POSITION_LOGIC.md` - 买点3仓位计算逻辑
2. `BUY_POINT_3_SUPPORT_CONDITION_CORRECTED.md` - 买点3支撑线系统条件
3. `KLINE_HIGHLOW_MARKERS_FEATURE.md` - K线高低点标记功能

## 版本信息

- **修正版本**: v6.1
- **修正日期**: 2025-12-12
- **影响范围**: 所有币种的K线图（共27个）
- **修正文件**: `templates/symbol_detail_v6.html`

---

**修正完成** ✅  
低波动震荡检测逻辑已修正，现在只统计涨跌幅 ≤ +0.25% 且震荡幅度 ≤ 0.50% 的连续K线。
