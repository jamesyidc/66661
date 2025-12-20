# 支撑/压力线数据显示 $0.000000 问题修复

## 问题描述

支撑/压力线系统页面显示所有币种的支撑/压力线数据都是 `$0.000000`,如下:
```
符号: BTCUSDT
价格: $89,848.30
支撑1: $0.000000
支撑2: $0.000000
压力1: $0.000000
压力2: $0.000000
```

## 问题原因

API `/api/support-resistance/latest` 在查询 `support_resistance_levels` 表时,使用了错误的币种格式:

1. **代码使用的格式**: `BTC-USDT-SWAP` (带 `-USDT-SWAP` 后缀)
2. **数据库中的格式**: `BTCUSDT` (不带后缀)

由于格式不匹配,查询返回空结果,导致所有支撑/压力线数据都显示为 0。

## 修复方案

在 `app_new.py` 第 5901-5917 行,修改币种格式转换逻辑:

### 修改前
```python
# 直接使用 MONITORED_SYMBOLS (格式: 'BTC-USDT-SWAP')
cursor.execute(f'''
    SELECT symbol, support_line_1, support_line_2, resistance_line_1, resistance_line_2
    FROM support_resistance_levels
    WHERE symbol IN ({placeholders})
''', MONITORED_SYMBOLS)
```

### 修改后
```python
# 先将币种格式从 'BTC-USDT-SWAP' 转换为 'BTCUSDT'
symbols_for_levels = [s.replace('-USDT-SWAP', 'USDT') for s in MONITORED_SYMBOLS]
placeholders_levels = ','.join(['?' for _ in symbols_for_levels])

cursor.execute(f'''
    SELECT symbol, support_line_1, support_line_2, resistance_line_1, resistance_line_2
    FROM support_resistance_levels
    WHERE symbol IN ({placeholders_levels})
''', symbols_for_levels)
```

## 修复验证

### 修复前 API 返回
```json
{
  "symbol": "BTCUSDT",
  "current_price": 89848.3,
  "support_line_1": 0,
  "support_line_2": 0,
  "resistance_line_1": 0,
  "resistance_line_2": 0
}
```

### 修复后 API 返回
```json
{
  "symbol": "BTCUSDT",
  "current_price": 89715.50,
  "support_line_1": 89715.50,
  "support_line_2": 89715.50,
  "resistance_line_1": 90600.00,
  "resistance_line_2": 90600.00
}
```

### 所有币种数据验证

```
=== 支撑/压力线数据验证 (共27个币种) ===

✅ BTCUSDT: S1=$89715.50, S2=$89715.50, R1=$90600.00, R2=$90600.00
✅ ETHUSDT: S1=$3076.66, S2=$3076.66, R1=$3134.13, R2=$3134.13
✅ BNBUSDT: S1=$886.50, S2=$886.50, R1=$904.40, R2=$904.40
✅ XRPUSDT: S1=$1.97, S2=$1.97, R1=$2.02, R2=$2.02
✅ SOLUSDT: S1=$128.00, S2=$128.00, R1=$133.50, R2=$133.50
✅ DOGEUSDT: S1=$0.31, S2=$0.31, R1=$0.32, R2=$0.32
❌ ADAUSDT: 所有值都是 0 (数据库中无数据)
... (共22个币种有数据,5个币种无数据)

=== 统计 ===
有效数据: 22/27
数据为0: 5/27
更新时间: 2025-12-14 21:38:15
```

**注**: 5个币种数据为 0 是因为这些币种在 `support_resistance_levels` 表中没有历史数据,这是正常的。

## 影响范围

- **修复文件**: `app_new.py`
- **影响 API**: `/api/support-resistance/latest`
- **影响页面**: `https://[domain]/support-resistance`
- **影响币种**: 所有 27 个监控币种
- **数据覆盖**: 22/27 币种有完整数据

## 测试方法

1. **访问页面**:
   ```
   https://5000-iz6uddj6rs3xe48ilsyqq-cbeee0f9.sandbox.novita.ai/support-resistance
   ```

2. **测试 API**:
   ```bash
   curl http://localhost:5000/api/support-resistance/latest | jq '.data[:3]'
   ```

3. **验证数据**: 查看各币种的支撑1/支撑2/压力1/压力2 数值是否正常显示(不再是 $0.000000)

## 修复时间

- **发现时间**: 2025-12-14 21:30 (北京时间)
- **修复时间**: 2025-12-14 21:38 (北京时间)
- **紧急程度**: 🔴 高(直接影响用户查看关键交易数据)
- **修复状态**: ✅ 已完成并验证

## 相关文档

- `SUPPORT_RESISTANCE_API_FIX.md` - 支撑/压力快照 API 修复
- `SUPPORT_RESISTANCE_CHART_FIX.md` - 曲线图堆叠问题修复
- `SUPPORT_RESISTANCE_BACKUP_GUIDE.md` - 数据备份与恢复指南
