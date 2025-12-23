# K线图表组合标记功能说明

## 功能概述

在K线图表上**自动标记同时满足多个条件的K线**，帮助您快速识别关键交易机会。

### 支持的标记条件

1. **7天最高价** (`is_7d_high`)
2. **7天最低价** (`is_7d_low`)
3. **48小时最高价** (`is_48h_high`)
4. **48小时最低价** (`is_48h_low`)
5. **窄幅震荡** (`is_narrow_range`) - 震荡≤0.5% 且 涨跌<0.25%

### 组合标记规则

当某根K线**同时满足≥2个条件**时，会自动生成**组合标记**，用金色菱形(💎)在图表上高亮显示。

## 标记示例

### 示例1：7天最低 + 窄幅震荡
```
条件：
✓ 7天最低价
✓ 窄幅震荡（涨跌0.08%，震荡0.17%）

显示：金色菱形标记
标签：7天最低 + 窄幅震荡
```

### 示例2：48小时最低 + 7天最低 + 窄幅震荡
```
条件：
✓ 7天最低价
✓ 48小时最低价
✓ 窄幅震荡（涨跌0.05%，震荡0.13%）

显示：金色菱形标记
标签：7天最低 + 48小时最低 + 窄幅震荡
```

## 视觉标识

### 图表标记

- **普通高低点标记**：
  - 7天最高：红色图钉 🔴
  - 7天最低：绿色图钉 🟢
  - 48小时最高：橙色图钉 🟠
  - 48小时最低：蓝色图钉 🔵

- **组合标记**：
  - 图标：金色菱形 💎
  - 大小：20px（比普通标记大）
  - 边框：橙色（`#FFA500`）2px

- **窄幅震荡区域**：
  - 显示：浅灰色背景区域
  - 标注：显示连续K线根数

### 技术指标面板

当鼠标悬停在图表上时，右侧技术指标面板会显示：

#### 组合标记卡片（金色背景）
```
💎 组合标记
满足条件数：3 个
条件列表：7天最低 + 48小时最低 + 窄幅震荡
```

#### 窄幅震荡卡片（橙色边框）
```
🔶 窄幅震荡
连续根数：5 根
涨跌幅：0.068%
震荡幅：0.172%
```

## 数据统计

### 窄幅震荡定义（来自实际数据）

基于BTC-USDT-SWAP的历史数据统计：

- **涨跌幅范围**：0.0000% ~ 0.2498%
- **震荡幅范围**：0.0001% ~ 0.5000%
- **平均涨跌幅**：0.0693%
- **平均震荡幅**：0.1486%

符合您的要求：**震荡≤0.5% 且 涨跌<0.25%**

### 组合标记频率

以BTC-USDT-SWAP（5分钟K线）为例：

| 条件组合 | 出现频率 | 说明 |
|---------|---------|------|
| 单一条件 | 较高 | 仅满足一个条件的K线 |
| 2个条件 | 中等 | 如"最低点 + 窄幅震荡" |
| 3个条件 | 较低 | 如"7天低 + 48h低 + 窄幅" |
| 4个条件 | 罕见 | 多重条件叠加 |

## 使用场景

### 1. 寻找潜在买入点
```
关注：7天最低 + 48小时最低 + 窄幅震荡
含义：价格触及多个时间维度的低点，且波动收窄，可能蓄势待发
```

### 2. 识别盘整区域
```
关注：窄幅震荡 + 连续多根K线
含义：价格在狭窄区间内反复震荡，可能积累能量准备突破
```

### 3. 确认趋势反转点
```
关注：7天高/低 + 48小时高/低（双重确认）
含义：短期和中期高低点重合，增强信号可靠性
```

### 4. 监控异常波动
```
关注：高低点 + 非窄幅震荡
含义：价格创新高/新低但波动剧烈，可能是假突破
```

## 技术实现

### 检测逻辑（JavaScript）

```javascript
function detectComboMarks(data, pageStartIdx, pageEndIdx) {
    const comboMarks = [];
    
    for (let i = pageStartIdx; i < pageEndIdx; i++) {
        const markers = data[i].markers;
        if (!markers) continue;
        
        // 统计满足的条件
        let conditions = [];
        
        if (markers.is_7d_high) conditions.push('7天最高');
        if (markers.is_7d_low) conditions.push('7天最低');
        if (markers.is_48h_high) conditions.push('48小时最高');
        if (markers.is_48h_low) conditions.push('48小时最低');
        if (markers.is_narrow_range) conditions.push('窄幅震荡');
        
        // 同时满足≥2个条件时，添加组合标记
        if (conditions.length >= 2) {
            comboMarks.push({
                name: conditions.join(' + '),
                coord: [pageIdx, markValue],
                value: markValue,
                conditions: conditions,
                itemStyle: { 
                    color: '#FFD700',  // 金色
                    borderColor: '#FFA500',
                    borderWidth: 2
                },
                symbol: 'diamond',  // 菱形
                symbolSize: 20
            });
        }
    }
    
    return comboMarks;
}
```

### 数据来源

所有标记数据均来自`kline_technical_markers`数据表：

- `is_7d_high` / `is_7d_low` - 7天高低点标记
- `is_48h_high` / `is_48h_low` - 48小时高低点标记
- `is_narrow_range` - 窄幅震荡标记（震荡≤0.5% 且 涨跌<0.25%）
- `change_percent` - 涨跌幅百分比
- `range_percent` - 震荡幅度百分比
- `consecutive_count` - 连续窄幅震荡根数

## 测试链接

### 主要币种K线图

- **BTC**: https://5000-iz6uddj6rs3xe48ilsyqq-2e1b9533.sandbox.novita.ai/chart/BTC-USDT-SWAP
- **ETH**: https://5000-iz6uddj6rs3xe48ilsyqq-2e1b9533.sandbox.novita.ai/chart/ETH-USDT-SWAP
- **XRP**: https://5000-iz6uddj6rs3xe48ilsyqq-2e1b9533.sandbox.novita.ai/chart/XRP-USDT-SWAP
- **SOL**: https://5000-iz6uddj6rs3xe48ilsyqq-2e1b9533.sandbox.novita.ai/chart/SOL-USDT-SWAP

### 新币种（已修复布林带数据）

- **TAO**: https://5000-iz6uddj6rs3xe48ilsyqq-2e1b9533.sandbox.novita.ai/chart/TAO-USDT-SWAP
- **HBAR**: https://5000-iz6uddj6rs3xe48ilsyqq-2e1b9533.sandbox.novita.ai/chart/HBAR-USDT-SWAP
- **AAVE**: https://5000-iz6uddj6rs3xe48ilsyqq-2e1b9533.sandbox.novita.ai/chart/AAVE-USDT-SWAP

## 操作提示

1. **清除浏览器缓存**：按 `Ctrl + F5` (Windows/Linux) 或 `Cmd + Shift + R` (Mac)
2. **查看标记详情**：鼠标悬停在K线上，右侧面板会显示完整信息
3. **切换时间周期**：支持5分钟和1小时K线
4. **翻页查看历史**：使用页面底部的分页控件

## Git信息

- **Commit**: 736abbb
- **Branch**: genspark_ai_developer
- **PR**: https://github.com/jamesyidc/66661/pull/1
- **修改文件**: `templates/chart_new.html`

## 相关文档

- **布林带修复报告**: `BOLLINGER_BANDS_FIX_REPORT.md`
- **技术指标完整性**: 所有27个币种均达到90%以上

---

**功能开发时间**: 2025-12-17  
**响应用户需求**: "把连续出现7天/48小时高低点 + 震荡≤0.5% + 涨跌<0.25%的标记出来"
