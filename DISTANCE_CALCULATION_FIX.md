# 支撑/压力线距离计算修复报告

## 问题描述

支撑/压力线系统页面显示的"距离支撑线"和"距离压力线"百分比都显示为 `+0.00%` 或 `-0.00%`,用户无法看到当前价格距离支撑/压力线的实际距离。

![问题截图](https://www.genspark.ai/api/files/s/NKyoFRNn)

如图所示,所有币种的距离百分比都是:
- 距离支撑1(7天低): `+0.00%`
- 距离支撑2(48h低): `-0.00%`
- 距离压力1(7天高): `+0.00%`
- 距离压力2(48h高): `+0.00%`

## 问题原因

在 `app_new.py` 的 `/api/support-resistance/latest` API 中,`distance_to_support_1` 等字段被硬编码为 `0`:

```python
# 原代码 (错误)
coin_data = {
    'symbol': symbol_usdt,
    'current_price': current_price,
    'support_line_1': support_1,
    'support_line_2': support_2,
    'resistance_line_1': resistance_1,
    'resistance_line_2': resistance_2,
    'distance_to_support_1': 0,  # ❌ 硬编码为0
    'distance_to_support_2': 0,  # ❌ 硬编码为0
    'distance_to_resistance_1': 0,  # ❌ 硬编码为0
    'distance_to_resistance_2': 0,  # ❌ 硬编码为0
    ...
}
```

## 修复方案

### 距离计算公式

根据 `support_resistance_collector.py` 中的正确公式,添加实时距离计算:

**支撑线距离** (正值表示在支撑线上方):
```python
distance_to_support_1 = ((当前价 - 支撑线1) / 支撑线1) × 100%
distance_to_support_2 = ((当前价 - 支撑线2) / 支撑线2) × 100%
```

**压力线距离** (正值表示在压力线下方):
```python
distance_to_resistance_1 = ((压力线1 - 当前价) / 当前价) × 100%
distance_to_resistance_2 = ((压力线2 - 当前价) / 当前价) × 100%
```

### 修复后的代码

**文件**: `app_new.py` 第 5937-5952 行

```python
# 计算距离百分比（使用实时价格）
distance_to_support_1 = ((current_price - support_1) / support_1) * 100 if support_1 > 0 else 0
distance_to_support_2 = ((current_price - support_2) / support_2) * 100 if support_2 > 0 else 0
distance_to_resistance_1 = ((resistance_1 - current_price) / current_price) * 100 if current_price > 0 else 0
distance_to_resistance_2 = ((resistance_2 - current_price) / current_price) * 100 if current_price > 0 else 0

coin_data = {
    'symbol': symbol_usdt,
    'current_price': current_price,
    'support_line_1': support_1,
    'support_line_2': support_2,
    'resistance_line_1': resistance_1,
    'resistance_line_2': resistance_2,
    'distance_to_support_1': distance_to_support_1,  # ✅ 实时计算
    'distance_to_support_2': distance_to_support_2,  # ✅ 实时计算
    'distance_to_resistance_1': distance_to_resistance_1,  # ✅ 实时计算
    'distance_to_resistance_2': distance_to_resistance_2,  # ✅ 实时计算
    ...
}
```

## 验证结果

### API 测试结果

**更新时间**: 2025-12-14 21:53:15

#### BTCUSDT
```
当前价: $89,848.30
支撑线1(7天最低): $88,503.30, 距离: +1.52% ✅
压力线1(7天最高): $90,450.00, 距离: +0.67% ✅
```
**验证**: 手动计算 `(89848.30 - 88503.30) / 88503.30 × 100 = 1.52%` ✅

#### ETHUSDT
```
当前价: $3,102.39
支撑线1(7天最低): $3,046.55, 距离: +1.83% ✅
压力线1(7天最高): $3,128.28, 距离: +0.83% ✅
```
**验证**: 手动计算 `(3102.39 - 3046.55) / 3046.55 × 100 = 1.83%` ✅

#### XRPUSDT
```
当前价: $2.01
支撑线1(7天最低): $1.99, 距离: +0.83% ✅
压力线1(7天最高): $2.04, 距离: +1.74% ✅
```

#### BNBUSDT
```
当前价: $890.20
支撑线1(7天最低): $884.00, 距离: +0.70% ✅
压力线1(7天最高): $904.40, 距离: +1.60% ✅
```

#### SOLUSDT
```
当前价: $131.68
支撑线1(7天最低): $130.05, 距离: +1.25% ✅
压力线1(7天最高): $133.74, 距离: +1.56% ✅
```

### 所有币种验证

✅ 所有27个币种的距离计算都正确  
✅ 距离百分比准确反映当前价格位置  
✅ 正值/负值显示正确(支撑线上方为正,压力线下方为正)

## 更新机制

### 数据更新流程

1. **K线价格更新**:
   - K线数据每5分钟从OKX采集一次
   - 存储到 `okex_kline_ohlc` 表

2. **支撑/压力线更新**:
   - `support_resistance_collector.py` 每5分钟采集一次
   - 基于7天和48小时K线计算支撑/压力线
   - 存储到 `support_resistance_levels` 表

3. **API 实时计算**:
   - `/api/support-resistance/latest` 获取最新K线价格
   - 获取最新支撑/压力线数据
   - **实时计算距离百分比** (不存储,每次请求时计算)
   - 每30秒自动刷新

4. **前端显示**:
   - 页面每30秒调用 API
   - 显示实时距离百分比
   - 根据正负值显示不同颜色

### 更新频率

- **K线数据**: 每 5分钟更新
- **支撑/压力线**: 每 5分钟更新
- **API 调用**: 每 30秒刷新
- **距离计算**: 实时计算(每次API请求)

## 距离百分比含义

### 支撑线距离

- **正值** (绿色): 当前价格在支撑线**上方**
  - 例如: `+1.52%` 表示价格比支撑线高 1.52%
  - 距离越大,说明离支撑线越远,支撑作用越弱

- **负值** (红色): 当前价格在支撑线**下方**
  - 例如: `-0.50%` 表示价格跌破支撑线 0.50%
  - 可能需要关注支撑失效

### 压力线距离

- **正值** (绿色): 当前价格在压力线**下方**
  - 例如: `+0.67%` 表示价格距离压力线还有 0.67%
  - 距离越小,说明接近压力线,可能面临阻力

- **负值** (红色): 当前价格在压力线**上方**
  - 例如: `-1.20%` 表示价格突破压力线 1.20%
  - 可能形成新的上涨趋势

## 测试方法

1. **访问页面**:
   ```
   https://5000-iz6uddj6rs3xe48ilsyqq-cbeee0f9.sandbox.novita.ai/support-resistance
   ```

2. **清除浏览器缓存**: 按 `Ctrl + F5` (Windows) 或 `Cmd + Shift + R` (Mac)

3. **验证距离显示**:
   - 查看"距离支撑1"、"距离支撑2"列
   - 查看"距离压力1"、"距离压力2"列
   - 确认显示的是实际百分比(不是 0.00%)
   - 确认颜色显示正确(正值绿色,负值红色)

4. **等待30秒**: 观察距离百分比是否随价格变化实时更新

## 影响范围

- **修改文件**: `app_new.py`
- **影响 API**: `/api/support-resistance/latest`
- **影响页面**: 支撑/压力线系统页面
- **影响数据**: 所有27个监控币种的4个距离字段

## Git 信息

- **提交 Hash**: `97e511b`
- **分支**: `genspark_ai_developer`
- **PR 链接**: https://github.com/jamesyidc/66661/pull/1

## 修复时间

- **发现时间**: 2025-12-14 21:55 (北京时间)
- **修复时间**: 2025-12-14 22:05 (北京时间)
- **紧急程度**: 🔴 高 (直接影响用户判断买卖时机)
- **修复状态**: ✅ **已完成并验证**

## 相关文档

- `SUPPORT_RESISTANCE_DEFINITION.md` - 支撑/压力线定义说明
- `SUPPORT_RESISTANCE_DATA_FIX.md` - 数据显示问题修复
- `COIN_LIST_FIX.md` - 币种列表修复

## 总结

✅ 距离计算公式正确  
✅ 实时使用最新K线价格  
✅ 每30秒自动更新  
✅ 所有27个币种距离显示正常  
✅ 页面数据准确反映价格位置
